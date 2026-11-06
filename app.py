import os
from flask import Flask, render_template, send_from_directory
from backend.config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.documents import documents_bp
from backend.routes.approvals import approvals_bp
from backend.routes.verification import verification_bp
from backend.routes.admin import admin_bp
from backend.utils.security import get_current_user
from backend.fixtures import seed_database

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "templates"))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "static"))
    
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.config.from_object(Config)

    # Ensure all upload directories exist immediately
    for folder in [
        app.config["UPLOAD_FOLDER"],
        app.config["DOCS_FOLDER"],
        app.config["FINAL_FOLDER"],
        app.config["ASSETS_FOLDER"],
        app.config["QR_FOLDER"]
    ]:
        os.makedirs(folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Route Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(admin_bp)

    # Global template context processor
    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    # SEO Crawling Endpoints
    @app.route("/robots.txt")
    def robots_txt():
        return send_from_directory(app.static_folder, "robots.txt", mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap_xml():
        return send_from_directory(app.static_folder, "sitemap.xml", mimetype="application/xml")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html", error=str(e)), 500

    # Initialize database & seed fixtures
    with app.app_context():
        db.create_all()
        seed_database(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
