from database import db


class Carrot(db.Model):
    __tablename__ = 'carrots'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)

    potatoes = db.relationship('Potato', backref='carrot', lazy=True)


class Potato(db.Model):
    __tablename__ = 'potatoes'
    id = db.Column(db.Integer, primary_key=True)
    carrot_id = db.Column(
        db.Integer, db.ForeignKey('carrots.id'), nullable=False
    )
    sensitive_data = db.Column(db.String(255), nullable=False)
    classification = db.Column(db.String(50), nullable=False)
