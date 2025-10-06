\
import os
from flask import Flask
from .models import db, ensure_schema
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True, template_folder="../templates", static_folder="../static")

    # Configuração
    # Configuração
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")

    # Banco persistente no Render Disk (/data) ou PostgreSQL se houver DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        db_file = os.getenv("DB_FILE", "app.db")
        data_dir = "/data"
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            print(f"[WARN] Não foi possível criar /data: {e}")
        db_path = os.path.join(data_dir, db_file)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        print(f"[INFO] Usando SQLite persistente em {db_path}")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init DB
    db.init_app(app)

    with app.app_context():
        # Habilita FK no SQLite
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        db.create_all()
        ensure_schema()

    # Blueprints
    from .routes.stations import bp as stations_bp
    from .routes.rides import bp as rides_bp
    from .routes.expenses import bp as expenses_bp
    from .routes.relatorios import bp as relatorios_bp

    app.register_blueprint(stations_bp)
    app.register_blueprint(rides_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(relatorios_bp)

    @app.get("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("rides.index"))

    @app.get("/saude")
    def saude():
        return {"ok": True, "version": "v1.0.0"}

    return app