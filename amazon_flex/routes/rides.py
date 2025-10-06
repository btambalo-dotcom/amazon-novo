from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date, timedelta
from ..models import db, ScheduledRide, Station, Expense

bp = Blueprint("rides", __name__, url_prefix="/corridas")

def parse_dt(v: str):
    return datetime.strptime(v, "%Y-%m-%dT%H:%M")

def calcular_horas(i: datetime, f: datetime) -> float:
    if not i or not f or f <= i: return 0.0
    return round((f-i).total_seconds()/3600.0, 2)


@bp.route("/")
def index():
    rows = db.session.query(ScheduledRide, Station).outerjoin(Station, ScheduledRide.station_id==Station.id)        .order_by(ScheduledRide.inicio.desc()).limit(200).all()
    return render_template("rides/index.html", rides=rows)

@bp.route("/calendario")
def calendar():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    first = date(year, month, 1)

    prev_month = (first.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (first.replace(day=28) + timedelta(days=10)).replace(day=1)

    start = first - timedelta(days=(first.weekday()))
    end = (first.replace(day=28) + timedelta(days=10))
    last = date(end.year, end.month, 1) - timedelta(days=1)
    grid_end = last + timedelta(days=(6-last.weekday()))

    rides = ScheduledRide.query.filter(ScheduledRide.inicio >= start, ScheduledRide.inicio < grid_end+timedelta(days=1)).all()

    by_day = {}
    for r in rides:
        d = r.inicio.date()
        by_day.setdefault(d, []).append(r)

    weeks = []
    cur = start
    for _ in range(6):
        wk = []
        for _ in range(7):
            wk.append({"date": cur, "rides": by_day.get(cur, [])})
            cur += timedelta(days=1)
        weeks.append(wk)

    return render_template("rides/calendar.html", year=year, month=month, first=first, weeks=weeks,
                           prev_month=prev_month, next_month=next_month)

@bp.route("/nova", methods=["GET","POST"])
def nova():
    estacoes = Station.query.order_by(Station.nome).all()
    if request.method == "POST":
        inicio = parse_dt(request.form["inicio"])
        fim = parse_dt(request.form["fim"])
        ride = ScheduledRide(
            titulo=request.form.get("titulo") or None,
            inicio=inicio,
            fim=fim,
            horas=calcular_horas(inicio,fim),
            valor=float(request.form.get("valor") or 0),
            gorjeta=float(request.form.get("gorjeta") or 0),
            station_id=int(request.form.get("station_id")) if request.form.get("station_id") else None,
            exclude_from_reports=bool(request.form.get("exclude_from_reports"))
        )
        db.session.add(ride)
        db.session.commit()
        flash("Corrida criada!", "success")
        return redirect(url_for("rides.view", ride_id=ride.id))
    return render_template("rides/form.html", estacoes=estacoes, ride=None)

@bp.route("/<int:ride_id>", methods=["GET","POST"])
def view(ride_id):
    ride = ScheduledRide.query.get_or_404(ride_id)
    estacoes = Station.query.order_by(Station.nome).all()
    if request.method == "POST":
        ride.titulo = request.form.get("titulo") or None
        ride.inicio = parse_dt(request.form["inicio"])
        ride.fim = parse_dt(request.form["fim"])
        ride.horas = calcular_horas(ride.inicio, ride.fim)
        ride.valor = float(request.form.get("valor") or 0)
        ride.gorjeta = float(request.form.get("gorjeta") or 0)
        ride.station_id = int(request.form.get("station_id")) if request.form.get("station_id") else None
        ride.exclude_from_reports = bool(request.form.get("exclude_from_reports"))
        db.session.commit()
        flash("Corrida atualizada!", "success")
        return redirect(url_for("rides.view", ride_id=ride.id))
    despesas = Expense.query.filter_by(ride_id=ride.id).order_by(Expense.data.desc()).all()
    return render_template("rides/view.html", ride=ride, estacoes=estacoes, despesas=despesas)

@bp.post("/<int:ride_id>/despesa")
def add_expense(ride_id):
    ride = ScheduledRide.query.get_or_404(ride_id)
    data = request.form.get("data") or datetime.utcnow().date().isoformat()
    tipo = request.form.get("tipo") or "combustivel"
    descricao = request.form.get("descricao") or None
    valor = float(request.form.get("valor") or 0)
    exp = Expense(
        data=datetime.fromisoformat(data).date(),
        tipo=tipo,
        descricao=descricao,
        valor=valor,
        ride_id=ride.id
    )
    db.session.add(exp)
    db.session.commit()
    flash("Despesa adicionada!", "success")
    return redirect(url_for("rides.view", ride_id=ride.id))

@bp.post("/<int:ride_id>/despesa/<int:exp_id>/del")
def del_expense(ride_id, exp_id):
    exp = Expense.query.get_or_404(exp_id)
    db.session.delete(exp)
    db.session.commit()
    flash("Despesa removida.", "warning")
    return redirect(url_for("rides.view", ride_id=ride_id))


@bp.post("/<int:ride_id>/delete")
def delete(ride_id):
    r = ScheduledRide.query.get_or_404(ride_id)
    db.session.delete(r)
    db.session.commit()
    flash("Corrida excluída.", "warning")
    return redirect(url_for("rides.calendar"))



@bp.route("/agenda")
def agenda():
    # mesma navegação de mês do calendário
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    first = date(year, month, 1)
    if month == 12:
        nxt = date(year+1, 1, 1)
    else:
        nxt = date(year, month+1, 1)

    # busca corridas do mês
    rows = db.session.query(ScheduledRide, Station).outerjoin(Station, ScheduledRide.station_id==Station.id)        .filter(ScheduledRide.inicio >= first, ScheduledRide.inicio < nxt)        .order_by(ScheduledRide.inicio.asc()).all()

    # agrupa por dia
    grouped = {}
    for r, s in rows:
        d = r.inicio.date()
        grouped.setdefault(d, []).append((r, s))

    # ordenar chaves
    days = sorted(grouped.keys())
    return render_template("rides/agenda.html", year=year, month=month, days=days, grouped=grouped)

