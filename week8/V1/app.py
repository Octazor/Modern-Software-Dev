"""
Entry point — run with:  flask --app app run  (or  python app.py  for dev)
"""
from app import create_app

app = create_app()


# ── Custom error pages ─────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    from flask import render_template
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    from flask import render_template
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
