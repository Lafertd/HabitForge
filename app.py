from flask import Flask, redirect, request, jsonify
from config import app
from v1.core.habit import register_habit_blueprint

@app.route("/docs", methods=['GET'], endpoint="docs", strict_slashes=False)
@app.route("/home", methods=['GET'], endpoint="home", strict_slashes=False)
@app.route("/", methods=['GET'], endpoint="/", strict_slashes=False)
def home():

    # Check if the request expects JSON
    if request.headers.get("Accept") == "application/json":
        # Return JSON response for Postman
        return jsonify({
            "status": "success",
            "message": "Documentation page is returned successfully.",
            "redirect_url": "https://documenter.getpostman.com/view/40761275/2sAYQUotVp"
        })
    else:
        # Redirect to Postman documentation URL for browsers
        return redirect("https://documenter.getpostman.com/view/40761275/2sAYQUotVp")

if __name__ == "__main__":
    app.run()

