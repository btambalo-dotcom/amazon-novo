from flask import Blueprint, render_template
from ..models import Expense, ScheduledRide

bp = Blueprint("expenses", __name__, url_prefix="/despesas")

@bp.route("/")
def index():
    despesas = Expense.query.order_by(Expense.data.desc()).limit(200).all()
    rides = ScheduledRide.query.order_by(ScheduledRide.inicio.desc()).limit(100).all()
    return render_template("expenses/index.html", despesas=despesas, rides=rides)
