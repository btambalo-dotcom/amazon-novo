\
from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from sqlalchemy import func
from ..models import db, ScheduledRide, Expense, Station

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")

@bp.route("/", methods=["GET"])
def index():
    # período padrão: últimos 30 dias
    fim = datetime.utcnow().date()
    inicio = fim - timedelta(days=30)
    s_in = request.args.get("inicio")
    s_fi = request.args.get("fim")
    station_id = request.args.get("station_id") or None

    if s_in and s_fi:
        inicio = parse_date(s_in).date()
        fim = parse_date(s_fi).date()

    # Consulta corridas
    q_rides = ScheduledRide.query.filter(
        ScheduledRide.inicio >= datetime.combine(inicio, datetime.min.time()),
        ScheduledRide.fim <= datetime.combine(fim, datetime.max.time()),
        ScheduledRide.exclude_from_reports.is_(False)
    )
    if station_id:
        q_rides = q_rides.filter(ScheduledRide.station_id == int(station_id))

    rides = q_rides.order_by(ScheduledRide.inicio.asc()).all()

    # Totais receita
    receita_valor = db.session.query(func.coalesce(func.sum(ScheduledRide.valor),0.0)).filter(q_rides.whereclause).scalar()
    receita_tips  = db.session.query(func.coalesce(func.sum(ScheduledRide.gorjeta),0.0)).filter(q_rides.whereclause).scalar()
    receita = float(receita_valor) + float(receita_tips)

    # Despesas no período (todas, independente de estação)
    despesas_total = db.session.query(func.coalesce(func.sum(Expense.valor),0.0)).filter(
        Expense.data >= datetime.combine(inicio, datetime.min.time()),
        Expense.data <= datetime.combine(fim, datetime.max.time()),
    ).scalar()

    custo = float(despesas_total)
    lucro = receita - custo
    margem = (lucro/receita*100.0) if receita > 0 else 0.0

    estacoes = Station.query.order_by(Station.nome).all()

    return render_template("relatorios/index.html",
                           inicio=inicio, fim=fim,
                           rides=rides,
                           receita=round(receita,2),
                           custo=round(custo,2),
                           lucro=round(lucro,2),
                           margem=round(margem,2),
                           estacoes=estacoes,
                           station_id=int(station_id) if station_id else None)
