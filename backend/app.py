from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import time
from datetime import datetime

from config import Config, UPLOAD_FOLDER, RESULTS_FOLDER, MODELS_FOLDER
from detection_logic import AnimalDetector
from database import db, DetectionHistory, init_db
from pdf_generator import PDFGenerator
from excel_generator import ExcelGenerator

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

init_db(app)
detector = None
pdf_generator = PDFGenerator()
excel_generator = ExcelGenerator()

def get_available_models():
    models = []
    if os.path.exists(MODELS_FOLDER):
        for file in os.listdir(MODELS_FOLDER):
            if file.endswith(('.pt', '.pth', '.onnx')):
                models.append(file)
    return sorted(models)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/results/<path:filename>')
def serve_result(filename):
    return send_from_directory(RESULTS_FOLDER, filename)

@app.route('/')
def index():
    return jsonify({"message": "Animal Detection API is running"})

@app.route('/api/models', methods=['GET'])
def get_models():
    try:
        models = get_available_models()
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if '.' not in file.filename:
            return jsonify({'error': 'Invalid file type'}), 400
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = file.filename.replace(' ', '_')
        original_filename = f"original_{timestamp}_{safe_filename}"
        original_path = os.path.join(UPLOAD_FOLDER, original_filename)
        
        file.save(original_path)
        
        confidence = float(request.form.get('confidence', 0.25))
        model_name = request.form.get('model', '')
        
        if not model_name:
            return jsonify({'error': 'No model selected'}), 400
        
        model_path = os.path.join(MODELS_FOLDER, model_name)
        if not os.path.exists(model_path):
            return jsonify({'error': f'Model not found: {model_name}'}), 400
        
        detector = AnimalDetector(model_path)
        
        start_time = time.time()
        result = detector.detect_on_image(
            image_path=original_path,
            conf_threshold=confidence,
            save_output=True,
            output_dir=RESULTS_FOLDER
        )
        processing_time = time.time() - start_time
        
        result_filename = os.path.basename(result.get('result_path', ''))
        
        import json
        detections_json = json.dumps(result['detections'])
        
        history_entry = DetectionHistory(
            filename=original_filename,
            result_filename=result_filename,
            processing_time=round(processing_time, 2),
            total_animals=result['stats']['total_animals'],
            cats_count=result['stats']['cats'],
            dogs_count=result['stats']['dogs'],
            confidence=confidence,
            model_name=model_name,
            detections_json=detections_json
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        response = {
            'success': True,
            'original_filename': original_filename,
            'result_filename': result_filename,
            'processing_time': round(processing_time, 2),
            'detections': result['detections'],
            'stats': result['stats'],
            'confidence': confidence,
            'model_name': model_name,
            'history_id': history_entry.id
        }
        
        return jsonify(response)
        
    except Exception as e:
        if 'original_path' in locals() and os.path.exists(original_path):
            os.remove(original_path)
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history = DetectionHistory.query.order_by(DetectionHistory.upload_time.desc()).all()
        history_data = [entry.to_dict() for entry in history]
        return jsonify(history_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:id>', methods=['GET'])
def get_history_item(id):
    try:
        entry = DetectionHistory.query.get_or_404(id)
        return jsonify(entry.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    try:
        total_entries = DetectionHistory.query.count()
        total_animals = db.session.query(db.func.sum(DetectionHistory.total_animals)).scalar() or 0
        total_cats = db.session.query(db.func.sum(DetectionHistory.cats_count)).scalar() or 0
        total_dogs = db.session.query(db.func.sum(DetectionHistory.dogs_count)).scalar() or 0
        
        stats = {
            'total_images': total_entries,
            'total_animals': total_animals,
            'total_cats': total_cats,
            'total_dogs': total_dogs
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    try:
        history = DetectionHistory.query.all()
        pdf_buffer = pdf_generator.generate_full_report(history)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'animal_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf/<int:id>', methods=['GET'])
def export_pdf_single(id):
    try:
        entry = DetectionHistory.query.get_or_404(id)
        pdf_buffer = pdf_generator.generate_single_report(entry)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'detection_report_{entry.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    try:
        history = DetectionHistory.query.all()
        excel_buffer = excel_generator.generate_full_report(history)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'animal_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/excel/<int:id>', methods=['GET'])
def export_excel_single(id):
    try:
        entry = DetectionHistory.query.get_or_404(id)
        excel_buffer = excel_generator.generate_single_report(entry)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'detection_report_{entry.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    try:
        entries = DetectionHistory.query.all()
        
        for entry in entries:
            if entry.filename:
                original_path = os.path.join(UPLOAD_FOLDER, entry.filename)
                if os.path.exists(original_path):
                    os.remove(original_path)
            
            if entry.result_filename:
                result_path = os.path.join(RESULTS_FOLDER, entry.result_filename)
                if os.path.exists(result_path):
                    os.remove(result_path)
        
        num_deleted = DetectionHistory.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Cleared {num_deleted} records and associated files'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'OK',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')