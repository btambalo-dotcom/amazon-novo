from flask import Blueprint, render_template, request
from datetime import date, datetime
from sqlalchemy import func
from ..models import db, ScheduledRide, Expense, Station

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

def parse_date(s, default):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return default

@bp.route("/")
def index():
    today = date.today()
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    if start_str or end_str:
        start = parse_date(start_str, date(today.year, today.month, 1))
        end = parse_date(end_str, today)
    else:
        start = date(year, month, 1)
        end = date(year+1, 1, 1) if month == 12 else date(year, month+1, 1)

    q = db.session.query(
        func.count(ScheduledRide.id),
        func.coalesce(func.sum(ScheduledRide.horas), 0.0),
        func.coalesce(func.sum(ScheduledRide.valor), 0.0),
        func.coalesce(func.sum(ScheduledRide.gorjeta), 0.0),
    ).filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < end)
    count, horas, valor, gorjeta = q.one()

    despesas = db.session.query(
        Expense.tipo, func.coalesce(func.sum(Expense.valor), 0.0)
    ).filter(Expense.data >= start, Expense.data < end).group_by(Expense.tipo).all()
    despesas_map = {k:v for k,v in despesas}
    total_despesas = sum(despesas_map.values())
    lucro = (valor + gorjeta) - total_despesas

    media_hora = (valor + gorjeta) / horas if horas else 0.0
    media_corrida = (valor + gorjeta) / count if count else 0.0

    # by station
    por_estacao = db.session.query(
        Station.nome.label("estacao"),
        func.coalesce(func.count(ScheduledRide.id), 0),
        func.coalesce(func.sum(ScheduledRide.horas), 0.0),
        func.coalesce(func.sum(ScheduledRide.valor + ScheduledRide.gorjeta), 0.0),
    ).outerjoin(ScheduledRide, ScheduledRide.station_id == Station.id
    ).filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < end
    ).group_by(Station.nome).order_by(Station.nome.asc()).all()

    corridas = db.session.query(ScheduledRide, Station).outerjoin(Station, ScheduledRide.station_id == Station.id)        .filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < end)        .order_by(ScheduledRide.inicio.asc()).all()

    return render_template("relatorios/index.html",
        start=start, end=end, year=year, month=month,
        count=count, horas=horas, valor=valor, gorjeta=gorjeta,
        despesas=despesas_map, total_despesas=total_despesas, lucro=lucro,
        media_hora=media_hora, media_corrida=media_corrida,
        por_estacao=por_estacao, corridas=corridas
    )
