import os
from taskmanager import app, db


if __name__ == "__main__":
    if os.environ.get("DEVELOPMENT") == "True":
        with app.app_context():
            db.create_all()
        print("Tables created.")
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=os.environ.get("DEBUG")
    )