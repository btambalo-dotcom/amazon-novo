from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Station(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    hub = db.Column(db.String(80), nullable=True)

class ScheduledRide(db.Model):
    __tablename__ = "rides"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=True)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    horas = db.Column(db.Float, nullable=False, default=0.0)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    gorjeta = db.Column(db.Float, nullable=False, default=0.0)
    exclude_from_reports = db.Column(db.Boolean, nullable=False, default=False)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=True)
    station = db.relationship("Station", backref=db.backref("rides", lazy=True))

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(50), nullable=False, default="combustivel")  # combustivel|pedagio|outros
    descricao = db.Column(db.String(200), nullable=True)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), nullable=False)
    ride = db.relationship("ScheduledRide", backref=db.backref("despesas", lazy=True, cascade="all, delete-orphan"))

def ensure_schema():
    db.create_all()
