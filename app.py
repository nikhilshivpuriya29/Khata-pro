from flask import Flask, redirect, url_for, request, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from auth import auth_bp
from routes import main_bp
from reports import reports_bp
from bulk_import import import_bp
from translations import TRANSLATIONS, get_text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(import_bp)

    with app.app_context():
        db.create_all()

    # Language switch route
    @app.route("/set-lang/<lang>")
    def set_lang(lang):
        if lang in TRANSLATIONS:
            session["lang"] = lang
        return redirect(request.referrer or url_for("main.dashboard"))

    # Inject translation helper + lang into all templates
    @app.context_processor
    def inject_translations():
        lang = session.get("lang", "en")
        def t(key):
            return get_text(lang, key)
        return dict(t=t, current_lang=lang)

    # Jinja filters
    @app.template_filter("inr")
    def inr_format(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
