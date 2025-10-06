from flask import Blueprint, render_template, request
from datetime import date, datetime, timedelta
from sqlalchemy import func
from ..models import db, ScheduledRide, Expense

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

def month_range(year, month):
    first = date(year, month, 1)
    if month == 12:
        nxt = date(year+1, 1, 1)
    else:
        nxt = date(year, month+1, 1)
    return first, nxt

@bp.route("/")
def index():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    start, end = month_range(year, month)

    # Resumo corridas
    q = db.session.query(
        func.count(ScheduledRide.id),
        func.coalesce(func.sum(ScheduledRide.horas), 0.0),
        func.coalesce(func.sum(ScheduledRide.valor), 0.0),
        func.coalesce(func.sum(ScheduledRide.gorjeta), 0.0),
    ).filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < end)
    count, horas, valor, gorjeta = q.one()

    # Despesas por tipo
    despesas = db.session.query(
        Expense.tipo, func.coalesce(func.sum(Expense.valor), 0.0)
    ).filter(Expense.data >= start, Expense.data < end).group_by(Expense.tipo).all()
    despesas_map = {k:v for k,v in despesas}
    total_despesas = sum(despesas_map.values())
    lucro = (valor + gorjeta) - total_despesas

    # Média por hora / por corrida
    media_hora = (valor + gorjeta) / horas if horas else 0.0
    media_corrida = (valor + gorjeta) / count if count else 0.0

    # Lista de corridas
    corridas = ScheduledRide.query.filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < end).order_by(ScheduledRide.inicio.asc()).all()

    return render_template("relatorios/index.html",
        year=year, month=month, start=start, end=end,
        count=count, horas=horas, valor=valor, gorjeta=gorjeta,
        despesas=despesas_map, total_despesas=total_despesas, lucro=lucro,
        media_hora=media_hora, media_corrida=media_corrida,
        corridas=corridas
    )
