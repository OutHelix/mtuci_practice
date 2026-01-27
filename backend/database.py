from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DetectionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)
    total_animals = db.Column(db.Integer, default=0)
    cats_count = db.Column(db.Integer, default=0)
    dogs_count = db.Column(db.Integer, default=0)
    confidence = db.Column(db.Float, default=0.25)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_time': self.upload_time.isoformat(),
            'processing_time': self.processing_time,
            'total_animals': self.total_animals,
            'cats_count': self.cats_count,
            'dogs_count': self.dogs_count,
            'confidence': self.confidence
        }

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///detections.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()