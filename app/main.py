import os

from flask import Flask, jsonify, request

_bookmarks = {}
_next_id = 1


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return jsonify({"service": "bookmarks-demo", "version": "1.0.0"})

    @app.get("/health")
    def health():
        if os.environ.get("FAIL_PUBLIC_HEALTH") and "--" not in request.host:
            return jsonify({"status": "down"}), 503
        return jsonify({"status": "ok"}), 200

    @app.get("/bookmarks")
    def list_bookmarks():
        return jsonify(list(_bookmarks.values()))

    @app.post("/bookmarks")
    def create_bookmark():
        global _next_id
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        url = data.get("url")

        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "title must be a non-empty string"}), 400
        if not isinstance(url, str) or not url.strip():
            return jsonify({"error": "url must be a non-empty string"}), 400
        if not (url.startswith("http://") or url.startswith("https://")):
            return jsonify({"error": "url must start with http:// or https://"}), 400

        item = {"id": _next_id, "title": title, "url": url}
        _bookmarks[_next_id] = item
        _next_id += 1
        return jsonify(item), 201

    @app.delete("/bookmarks/<int:bookmark_id>")
    def delete_bookmark(bookmark_id):
        if bookmark_id not in _bookmarks:
            return jsonify({"error": "not found"}), 404
        del _bookmarks[bookmark_id]
        return "", 204

    return app


def reset_store():
    global _next_id
    _bookmarks.clear()
    _next_id = 1


if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "8080"))
    application = create_app()
    application.run(host=host, port=port, debug=False)
