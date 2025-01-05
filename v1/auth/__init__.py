from .auth_blueprint import auth # Import auth blueprint

def register_auth_blueprint(app):

    # Register the blueprint
    app.register_blueprint(auth, url_prefix='/auth')

__all__ = ['auth'] # Explicitly export the blueprint
