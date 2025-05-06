from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Nation, Resource, Military
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    # Redirect to homepage without auto-login
    return redirect(url_for('game.home'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('game.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash(f'No user found with username: {username}', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.check_password(password):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        try:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            
            # Check if the user has a nation
            nation = Nation.query.filter_by(user_id=user.id).first()
            if not nation:
                flash('Your account is missing a nation. Creating one now...', 'warning')
                # Create a default nation
                new_nation = Nation(
                    user_id=user.id,
                    name=f"{user.username}'s Nation",
                    description=f"Default nation for {user.username}."
                )
                db.session.add(new_nation)
                db.session.commit()
                
                # Create initial resources for the nation
                initial_resources = Resource(nation_id=new_nation.id)
                db.session.add(initial_resources)
                
                # Create initial military for the nation
                initial_military = Military(nation_id=new_nation.id)
                db.session.add(initial_military)
                
                db.session.commit()
                flash('Default nation created successfully.', 'success')
                
            return redirect(url_for('game.dashboard'))
        except Exception as e:
            flash(f'Error during login: {str(e)}', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('game.dashboard'))
    
    # Lista completa delle nazioni predefinite con i loro territori
    predefined_nations = [
        # Nord America
        {"id": "canada", "name": "Canada", "territory": "Nord America", "map_x": 150, "map_y": 110},
        {"id": "usa", "name": "United States", "territory": "Nord America", "map_x": 160, "map_y": 170},
        {"id": "greenland", "name": "Groenlandia", "territory": "Nord America", "map_x": 280, "map_y": 80},
        {"id": "mexico", "name": "Messico", "territory": "Nord America", "map_x": 130, "map_y": 200},
        {"id": "alaska", "name": "Alaska", "territory": "Nord America", "map_x": 60, "map_y": 90},
        
        # Sud America
        {"id": "brazil", "name": "Brasile", "territory": "Sud America", "map_x": 220, "map_y": 330},
        {"id": "argentina", "name": "Argentina", "territory": "Sud America", "map_x": 190, "map_y": 390},
        {"id": "colombia", "name": "Colombia", "territory": "Sud America", "map_x": 180, "map_y": 260},
        {"id": "chile", "name": "Cile", "territory": "Sud America", "map_x": 150, "map_y": 410},
        
        # Europa Occidentale
        {"id": "france", "name": "Francia", "territory": "Europa Occidentale", "map_x": 410, "map_y": 180},
        {"id": "germany", "name": "Germania", "territory": "Europa Occidentale", "map_x": 440, "map_y": 150},
        {"id": "uk", "name": "Regno Unito", "territory": "Europa Occidentale", "map_x": 405, "map_y": 140},
        {"id": "italy", "name": "Italia", "territory": "Europa Occidentale", "map_x": 440, "map_y": 215},
        {"id": "spain", "name": "Spagna", "territory": "Europa Occidentale", "map_x": 380, "map_y": 210},
        
        # Europa Orientale
        {"id": "russia", "name": "Russia", "territory": "Europa Orientale", "map_x": 580, "map_y": 110},
        {"id": "ukraine", "name": "Ucraina", "territory": "Europa Orientale", "map_x": 510, "map_y": 190},
        {"id": "poland", "name": "Polonia", "territory": "Europa Orientale", "map_x": 470, "map_y": 160},
        
        # Africa
        {"id": "egypt", "name": "Egitto", "territory": "Africa", "map_x": 460, "map_y": 250},
        {"id": "nigeria", "name": "Nigeria", "territory": "Africa", "map_x": 415, "map_y": 300},
        {"id": "south_africa", "name": "Sudafrica", "territory": "Africa", "map_x": 450, "map_y": 380},
        
        # Medio Oriente
        {"id": "saudi_arabia", "name": "Arabia Saudita", "territory": "Medio Oriente", "map_x": 510, "map_y": 265},
        {"id": "iran", "name": "Iran", "territory": "Medio Oriente", "map_x": 545, "map_y": 230},
        
        # Asia
        {"id": "china", "name": "Cina", "territory": "Asia", "map_x": 670, "map_y": 150},
        {"id": "india", "name": "India", "territory": "Asia", "map_x": 620, "map_y": 210},
        {"id": "japan", "name": "Giappone", "territory": "Asia", "map_x": 760, "map_y": 150},
        {"id": "south_korea", "name": "Corea del Sud", "territory": "Asia", "map_x": 735, "map_y": 185},
        
        # Oceania
        {"id": "australia", "name": "Australia", "territory": "Oceania", "map_x": 810, "map_y": 350},
        {"id": "new_zealand", "name": "Nuova Zelanda", "territory": "Oceania", "map_x": 885, "map_y": 375},
        
        # Regione Extra
        {"id": "antarctica", "name": "Antartide", "territory": "Regione Extra", "map_x": 600, "map_y": 585},
    ]
        
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            selected_nation_id = request.form.get('nation_select')
            custom_nation_name = request.form.get('custom_nation_name')
            
            # Find the selected predefined nation or use custom name
            selected_nation = None
            for nation in predefined_nations:
                if nation["id"] == selected_nation_id:
                    selected_nation = nation
                    break
            
            # Use either the selected nation or the custom name
            if selected_nation:
                nation_name = selected_nation["name"]
                territory = selected_nation["territory"]
                map_x = selected_nation["map_x"]
                map_y = selected_nation["map_y"]
            else:
                nation_name = custom_nation_name
                territory = "Custom"
                # Random position for custom nations
                import random
                map_x = random.randint(100, 900)
                map_y = random.randint(100, 500)
            
            if not username or not email or not password or not nation_name:
                flash('All fields are required.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Check if username or email already exists
            user_check = User.query.filter_by(username=username).first()
            if user_check:
                flash('Username already exists.', 'danger')
                return redirect(url_for('auth.register'))
                
            email_check = User.query.filter_by(email=email).first()
            if email_check:
                flash('Email already exists.', 'danger')
                return redirect(url_for('auth.register'))
                
            # Create new user
            new_user = User(
                username=username,
                email=email
            )
            new_user.set_password(password)
            
            # Add user to database first
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully.', 'success')
            
            # Create new nation
            new_nation = Nation(
                user_id=new_user.id,
                name=nation_name,
                description=f"The nation of {nation_name}, founded by {username}.",
                continent=territory,
                map_x=map_x,
                map_y=map_y
            )
            
            # Add nation to database
            db.session.add(new_nation)
            db.session.commit()
            flash('Nation created successfully.', 'success')
            
            # Create initial resources for the nation
            initial_resources = Resource(nation_id=new_nation.id)
            db.session.add(initial_resources)
            
            # Create initial military for the nation
            initial_military = Military(nation_id=new_nation.id)
            db.session.add(initial_military)
            
            db.session.commit()
            flash('Nation resources and military initialized.', 'success')
            
            # Optionally, login the user automatically
            # login_user(new_user)
            # return redirect(url_for('game.dashboard'))
            
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
            db.session.rollback()  # Rollback any failed transactions
            return redirect(url_for('auth.register'))
    
    # For GET requests, render the template with predefined nations
    return render_template('register.html', predefined_nations=predefined_nations)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

@auth.route('/test_login', methods=['GET', 'POST'])
def test_login():
    """A test page for debugging login issues"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Log the request details
        print(f"TEST LOGIN ATTEMPT - Username: {username}")
        
        # Try to find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            flash(f'Test login failed: No user found with username: {username}', 'danger')
            return redirect(url_for('auth.test_login'))
        
        # Check the password hash directly
        print(f"TEST PASSWORD CHECK - Hash: {user.password_hash[:20]}...")
        
        # Try to verify the password
        if user.check_password(password):
            try:
                # Try to login
                login_user(user)
                flash('Test login successful!', 'success')
                
                # Check if the user is authenticated
                if current_user.is_authenticated:
                    print("TEST LOGIN - User is authenticated")
                else:
                    print("TEST LOGIN - User is NOT authenticated after login_user")
                
                return redirect(url_for('game.dashboard'))
            except Exception as e:
                flash(f'Test login error: {str(e)}', 'danger')
                return redirect(url_for('auth.test_login'))
        else:
            flash('Test login failed: Incorrect password', 'danger')
            return redirect(url_for('auth.test_login'))
    
    # Get all users for debugging
    users = User.query.all()
    return render_template('test_login.html', users=users)

# Auto-login features have been removed as they are no longer needed

# Francis auto-login removed
        
# Fede auto-login removed

# Generic auto-login by user ID removed

# Auto-login create user feature has been removed as it is no longer needed
