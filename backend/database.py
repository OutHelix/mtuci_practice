from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class DetectionHistory(db.Model):    
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    result_filename = db.Column(db.String(255))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)
    total_animals = db.Column(db.Integer, default=0)
    cats_count = db.Column(db.Integer, default=0)
    dogs_count = db.Column(db.Integer, default=0)
    confidence = db.Column(db.Float, default=0.25)
    model_name = db.Column(db.String(100), default='')
    detections_json = db.Column(db.Text, default='[]')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'result_filename': self.result_filename,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'processing_time': self.processing_time,
            'total_animals': self.total_animals,
            'cats_count': self.cats_count,
            'dogs_count': self.dogs_count,
            'confidence': self.confidence,
            'model_name': self.model_name,
            'detections': json.loads(self.detections_json) if self.detections_json else []
        }

def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        db.create_all()