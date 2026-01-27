from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from detection_logic import AnimalDetector
from database import db, DetectionHistory, init_db
from datetime import datetime
import os
import time
import base64
from io import BytesIO
import pandas as pd

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

init_db(app)

detector = AnimalDetector('models/yolo11n.pt')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# API
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    confidence = float(request.form.get('confidence', 0.25))
    
    start_time = time.time()
    try:
        result = detector.detect_on_image(
            image_path=filepath,
            conf_threshold=confidence
        )
        processing_time = time.time() - start_time
        
        # Save 
        history_entry = DetectionHistory(
            filename=filename,
            processing_time=round(processing_time, 2),
            total_animals=result['stats']['total_animals'],
            cats_count=result['stats']['cats'],
            dogs_count=result['stats']['dogs'],
            confidence=confidence
        )
        db.session.add(history_entry)
        db.session.commit()
        
        # Convert image to base64
        result_image_base64 = base64.b64encode(result['result_image']).decode('utf-8')
        
        response = {
            'success': True,
            'filename': filename,
            'processing_time': round(processing_time, 2),
            'detections': result['detections'],
            'stats': result['stats'],
            'result_image': f"data:image/jpeg;base64,{result_image_base64}",
            'history_id': history_entry.id
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    history = DetectionHistory.query.order_by(DetectionHistory.upload_time.desc()).all()
    history_data = [entry.to_dict() for entry in history]
    return jsonify(history_data)

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    total_entries = DetectionHistory.query.count()
    total_animals = db.session.query(db.func.sum(DetectionHistory.total_animals)).scalar() or 0
    total_cats = db.session.query(db.func.sum(DetectionHistory.cats_count)).scalar() or 0
    total_dogs = db.session.query(db.func.sum(DetectionHistory.dogs_count)).scalar() or 0
    
    return jsonify({
        'total_images': total_entries,
        'total_animals': total_animals,
        'total_cats': total_cats,
        'total_dogs': total_dogs
    })

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    history = DetectionHistory.query.all()
    
    data = []
    for entry in history:
        data.append({
            'ID': entry.id,
            'File': entry.filename,
            'Upload Time': entry.upload_time,
            'Processing Time (s)': entry.processing_time,
            'Total Animals': entry.total_animals,
            'Cats': entry.cats_count,
            'Dogs': entry.dogs_count,
            'Confidence': entry.confidence
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='History')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlforms-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'detection_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/api/clear', methods=['POST'])
def clear_history():
    try:
        DetectionHistory.query.delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)