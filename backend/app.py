import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"
os.environ["ABSL_MIN_LOG_LEVEL"]    = "3"

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

from routes.auth            import auth_bp
from routes.mood            import mood_bp
from routes.recommendations import rec_bp
from routes.journey         import journey_bp
from routes.social          import social_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"]      = Config.DEBUG

    # ── CORS — allow all origins in development ───────────────────────────────
    CORS(app,
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=False,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.register_blueprint(auth_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(rec_bp)
    app.register_blueprint(journey_bp)
    app.register_blueprint(social_bp)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status" : "ok",
            "model"  : "tfidf",
            "groq"   : bool(Config.GROQ_API_KEY),
            "spotify": bool(Config.SPOTIFY_CLIENT_ID),
            "tmdb"   : bool(Config.TMDB_API_KEY),
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error", "detail": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)