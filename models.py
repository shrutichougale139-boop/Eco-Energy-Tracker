from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device= db.Column(db.String(50), nullable=False)
    watts= db.Column(db.Float, nullable=False)
    timestamp= db.Column(db.DateTime, default=datetime.utcnow, index=True)


    def to_dict(self):
        return{
            "id": self.id,
            "device": self.device,
            "watts": self.watts,
            "timestamp": self.timestamp.isoformat()
        }