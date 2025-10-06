from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

db = SQLAlchemy()

class Station(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, default="")
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

def _colunas_existentes(table):
    # Funciona em SQLite; em Postgres, create_all cobre alterações maiores.
    try:
        rows = db.session.execute(text(f"PRAGMA table_info({table})")).all()
        return {r[1] for r in rows}
    except Exception:
        return set()

def _add_col_if_missing(table, col_sql):
    # col_sql: e.g. "ALTER TABLE expenses ADD COLUMN tipo VARCHAR(50) DEFAULT 'combustivel' NOT NULL"
    try:
        db.session.execute(text(col_sql))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[MIGRA] ignorando erro ao adicionar coluna: {e}")

def ensure_schema():
    db.create_all()
    # Tentativa de migração leve em SQLite para bancos antigos
    cols = _colunas_existentes("expenses")
    if cols:
        if "tipo" not in cols:
            _add_col_if_missing("expenses", "ALTER TABLE expenses ADD COLUMN tipo VARCHAR(50) DEFAULT 'combustivel' NOT NULL")
        if "descricao" not in cols:
            _add_col_if_missing("expenses", "ALTER TABLE expenses ADD COLUMN descricao VARCHAR(200)")
    cols_s = _colunas_existentes("stations")
    if cols_s:
        if "nome" not in cols_s:
            _add_col_if_missing("stations", "ALTER TABLE stations ADD COLUMN nome VARCHAR(120) DEFAULT '' NOT NULL")
        if "hub" not in cols_s:
            _add_col_if_missing("stations", "ALTER TABLE stations ADD COLUMN hub VARCHAR(80)")
