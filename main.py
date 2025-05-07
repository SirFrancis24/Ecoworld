from app import app, db  # noqa: F401
from flask import redirect, url_for, Flask
from flask_login import login_user
from models import User, Nation, Resource, Military, Technology
from datetime import datetime
import traceback

# Add a direct route to login page
@app.route('/play')
def play_redirect():
    """Redirect to login page"""
    # Make sure we're not redirecting to guest login
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)