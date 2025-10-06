from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Station

bp = Blueprint("stations", __name__, url_prefix="/estacoes")

@bp.route("/")
def index():
    items = Station.query.order_by(Station.nome).all()
    return render_template("stations/index.html", items=items)

@bp.route("/nova", methods=["GET","POST")
def nova():
    if request.method == "POST":
        s = Station(nome=request.form["nome".strip(), hub=request.form.get("hub") or None)
        db.session.add(s)
        db.session.commit()
        flash("Estação criada!", "success")
        return redirect(url_for("stations.index"))
    return render_template("stations/form.html")
