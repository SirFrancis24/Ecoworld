from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user
from models import User, Nation, Resource, Military
from app import db

# Create a blueprint
landing = Blueprint('landing', __name__)

@landing.route('/')
def index():
    """Landing page for the game"""
    return render_template('landing.html')

@landing.route('/start_game', methods=['GET'])
def start_game():
    """Redirect to the login page instead of auto-creating a guest account"""
    # Redirect to the login page instead of auto-creating a guest account
    return redirect(url_for('auth.login'))