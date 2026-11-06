"""
ApproveHub — Application Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask application factory for the ApproveHub institutional document
approval and cryptographic verification platform.

This module creates and configures the Flask application instance,
registers all route blueprints, initialises the database, and seeds
institutional fixture data.

Author: Shreeyash Solunke
Institution: VIT Pune, Department of Information Technology
"""

import os
import logging
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

# Configure application-wide logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("approvehub")


def create_app():
    """
    Application factory that creates and configures the Flask application.

    Returns:
        Flask: Fully configured Flask application instance with all
        blueprints registered, database initialised, and fixtures seeded.
    """
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "templates"))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "static"))

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.config.from_object(Config)

    # Ensure all upload directories exist on startup
    for folder in [
        app.config["UPLOAD_FOLDER"],
        app.config["DOCS_FOLDER"],
        app.config["FINAL_FOLDER"],
        app.config["ASSETS_FOLDER"],
        app.config["QR_FOLDER"]
    ]:
        os.makedirs(folder, exist_ok=True)

    # Initialise database extension
    db.init_app(app)

    # Register route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(admin_bp)
    logger.info("All route blueprints registered successfully.")

    # Global template context processor — injects current user and
    # Google Search Console verification token into every template
    @app.context_processor
    def inject_user():
        return {
            "current_user": get_current_user(),
            "google_site_verification": os.environ.get("GOOGLE_SITE_VERIFICATION", "")
        }

    # SEO crawling endpoints — serve robots.txt and sitemap.xml
    # with correct MIME types for search engine indexing
    @app.route("/robots.txt")
    def robots_txt():
        """Serve robots.txt for search engine crawlers."""
        return send_from_directory(app.static_folder, "robots.txt", mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap_xml():
        """Serve XML sitemap for search engine indexing."""
        return send_from_directory(app.static_folder, "sitemap.xml", mimetype="application/xml")

    # Custom error handlers with professional error pages
    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 Forbidden errors."""
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 Not Found errors."""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 Internal Server errors."""
        logger.error("Internal server error: %s", str(e))
        return render_template("500.html", error=str(e)), 500

    # Initialise database schema and seed institutional fixtures
    with app.app_context():
        db.create_all()
        seed_database(app)
        logger.info("Database initialised and fixtures seeded.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
