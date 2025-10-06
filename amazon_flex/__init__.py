import os
from flask import Flask, redirect, url_for
from .models import db, ensure_schema
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        db_file = os.getenv("DB_FILE", "app.db")
        data_dir = "/data"
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            print(f"[WARN] /data: {e}")
        db_path = os.path.join(data_dir, db_file)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        print(f"[INFO] SQLite em {db_path}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        ensure_schema()
    from .routes.rides import bp as rides_bp
    from .routes.stations import bp as stations_bp
    from .routes.expenses import bp as expenses_bp
    app.register_blueprint(rides_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(expenses_bp)
    @app.route("/")
    def home():
        return redirect(url_for("rides.calendar"))
    return app
