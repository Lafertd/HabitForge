from flask import Flask, redirect
from config import app
from v1.core.habit import register_habit_blueprint

@app.route("/docs", methods=['GET'], endpoint="docs", strict_slashes=False)
@app.route("/home", methods=['GET'], endpoint="home", strict_slashes=False)
@app.route("/", methods=['GET'], endpoint="/", strict_slashes=False)

def home():
    # Redirect to Postman documentation URL
    return redirect("https://documenter.getpostman.com/view/40761275/2sAYJAfdpY")
if __name__ == "__main__":
    app.run()

