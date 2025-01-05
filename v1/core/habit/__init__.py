from .habit_blueprint import habit  # Import the auth blueprint

def register_habit_blueprint(app):

    # Register the blueprint
    app.register_blueprint(habit, url_prefix='/habit')

__all__ = ['habit'] # Explicitly export the blueprint
