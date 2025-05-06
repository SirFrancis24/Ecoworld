from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from app import db
from models import Nation, Resource, Technology
from datetime import datetime, timedelta
from utils.auth import easy_login_required
from utils.technology_handler import (
    initialize_technologies, 
    get_available_technologies, 
    start_research, 
    cancel_research, 
    update_research_progress,
    get_technology_tree,
    get_tech_details,
    get_tech_effects,
    get_technologies_by_tier,
    get_tech_name_by_id,
    get_prerequisites_names
)
from data.technologies import TECHNOLOGIES

technology = Blueprint('technology', __name__)

# Create a Jinja filter to convert tech ID to name
@technology.app_template_filter('tech_name_from_id')
def tech_name_from_id_filter(tech_id):
    """Convert a technology ID to its name for Jinja templates."""
    return get_tech_name_by_id(tech_id)

# Create a Jinja filter to get tech data from ID
@technology.app_template_filter('tech_data_from_id')
def tech_data_from_id_filter(tech_id):
    """Get full technology data from ID for Jinja templates."""
    return get_tech_details(tech_id)

@technology.route('/technology')
@easy_login_required
def technology_view():
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    # Check if technologies are initialized for this nation
    tech_count = Technology.query.filter_by(nation_id=nation.id).count()
    if tech_count == 0:
        # Initialize technologies for new nation
        result = initialize_technologies(nation)
        flash(f'Technologies initialized: {result}', 'info')
    
    # Get technologies for this nation
    researched_techs = Technology.query.filter(Technology.nation_id == nation.id, Technology.level > 0).all()
    in_progress_techs = Technology.query.filter_by(nation_id=nation.id, researching=True).all()
    
    # Get available technologies to research
    available_techs = get_available_technologies(nation)
    
    # Organize technologies by tier (for progressive display)
    tech_by_tier = get_technologies_by_tier(nation)
    
    # Update research progress - force update on page load
    update_result = update_research_progress()
    
    # Get updated technologies after changes
    in_progress_techs = Technology.query.filter_by(nation_id=nation.id, researching=True).all()
    
    # Log the current state for debugging
    for tech in in_progress_techs:
        progress_percent = (tech.research_points_current / tech.research_points_required) * 100
        now = datetime.utcnow()
        remaining_seconds = (tech.estimated_completion - now).total_seconds() if tech.estimated_completion else 0
        print(f"TECH TIMER DEBUG: {tech.name} - Progress: {progress_percent:.2f}% - Time remaining: {remaining_seconds:.0f} seconds")
    
    # Flash messages for completed technologies
    if update_result["completed_count"] > 0:
        flash(f'{update_result["completed_count"]} research projects completed!', 'success')
    elif update_result["updated_count"] > 0:
        # Log that progress was updated but not completed
        print(f"Updated {update_result['updated_count']} research projects")
    
    # Get technology categories
    categories = {}
    for tech in TECHNOLOGIES:
        category = tech["category"]
        if category not in categories:
            categories[category] = {
                "name": category,
                "description": f"Technologies related to {category.lower()}",
                "techs": []
            }
    
    # Get the full tech tree for visualization
    tech_tree = get_technology_tree(nation)
    
    # Get all technologies for this nation for template use
    technologies = Technology.query.filter_by(nation_id=nation.id).all()
    
    # Create a consolidated tech list by name for category processing
    tech_by_name = {}
    for tech in technologies:
        if tech.category and tech.name:
            # Initialize if first time seeing this tech name
            if tech.name not in tech_by_name:
                tech_by_name[tech.name] = {
                    'name': tech.name,
                    'category': tech.category,
                    'id': tech.id,
                    'level': tech.level,
                    'max_level': tech.max_level,
                    'description': tech.description,
                    'researching': tech.researching,
                    'instances': [tech]
                }
            else:
                # Add levels from duplicates
                tech_by_name[tech.name]['level'] += tech.level
                tech_by_name[tech.name]['instances'].append(tech)
                
                print(f"Found duplicate technology: {tech.name} (ID: {tech.id}, Level: {tech.level}). " +
                      f"Combined level: {tech_by_name[tech.name]['level']}")
    
    # Build technology_categories dictionary for the template
    tech_categories = {}
    for tech_name, tech_data in tech_by_name.items():
        category = tech_data['category']
        if category not in tech_categories:
            tech_categories[category] = []
        
        # Create a display tech with combined levels
        display_tech = tech_data['instances'][0]  # Use first instance as base
        
        # In SQLAlchemy we can't use .update() on model objects, so we set the attribute directly
        # We'll use a custom attribute that won't be saved to the database
        setattr(display_tech, 'combined_level', tech_data['level'])
        tech_categories[category].append(display_tech)
    
    # Get effects for each technology and organize by tier
    tech_effects = {}
    for tech in technologies:
        # Get effects for all technologies, not just researched ones
        effects = get_tech_effects(nation, tech.id, max(1, tech.level))
        tech_effects[tech.id] = effects
    
    # Current time is already imported at the top
    return render_template('technology.html',
                          nation=nation,
                          resources=resources,
                          researched_techs=researched_techs,
                          in_progress_techs=in_progress_techs,
                          available_techs=available_techs,
                          tech_tree=tech_tree, 
                          categories=categories,
                          technologies=technologies,
                          tech_effects=tech_effects,
                          tech_by_tier=tech_by_tier,
                          tech_categories=tech_categories,  # Add the consolidated tech categories
                          now=datetime.utcnow())

@technology.route('/technology/research', methods=['POST'])
@easy_login_required
def research_technology():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    tech_id = int(request.form.get('technology_id'))
    
    # Use the technology handler to start research
    result = start_research(nation, tech_id)
    
    if result["success"]:
        flash(result["message"], 'success')
    else:
        flash(result["message"], 'danger')
    
    return redirect(url_for('technology.technology_view'))

@technology.route('/technology/cancel', methods=['POST'])
@easy_login_required
def cancel_research_route():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    tech_id = int(request.form.get('technology_id'))
    
    # Use the technology handler to cancel research
    result = cancel_research(nation, tech_id)
    
    if result["success"]:
        flash(result["message"], 'info')
    else:
        flash(result["message"], 'danger')
    
    return redirect(url_for('technology.technology_view'))

@technology.route('/api/technology/tree')
@easy_login_required
def get_tech_tree():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get the technology tree using the handler
    tech_tree = get_technology_tree(nation)
    
    return jsonify(tech_tree)

@technology.route('/api/technology/<int:tech_id>')
@easy_login_required
def get_technology_details(tech_id):
    """Get detailed information about a specific technology."""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    tech = Technology.query.filter_by(id=tech_id, nation_id=nation.id).first()
    
    if not tech:
        return jsonify({"error": "Technology not found"}), 404
    
    # Get the technology details from the data file
    tech_data = get_tech_details(tech_id)
    
    if not tech_data:
        return jsonify({"error": "Technology data not found"}), 404
    
    # Get effects at current level
    effects = get_tech_effects(nation, tech_id, tech.level)
    
    # Combine database and data file information
    tech_info = {
        "id": tech.id,
        "name": tech.name,
        "description": tech.description,
        "category": tech.category,
        "level": tech.level,
        "max_level": tech.max_level,
        "researching": tech.researching,
        "prerequisites": [int(x) for x in tech.prerequisites.split(',') if x],
        "flavor_text": tech_data.get("flavor_text", ""),
        "effects": effects
    }
    
    if tech.researching:
        # Add research progress information
        tech_info["research_started"] = tech.research_started.strftime("%Y-%m-%d %H:%M:%S")
        tech_info["estimated_completion"] = tech.estimated_completion.strftime("%Y-%m-%d %H:%M:%S")
        tech_info["progress"] = tech.research_points_current / tech.research_points_required
        
        # Calculate time remaining
        now = datetime.utcnow()
        if tech.estimated_completion > now:
            remaining = tech.estimated_completion - now
            tech_info["time_remaining"] = str(remaining).split('.')[0]  # Format as HH:MM:SS
        else:
            tech_info["time_remaining"] = "Completing soon"
    
    return jsonify(tech_info)

@technology.route('/technology/details/<int:tech_id>')
@easy_login_required
def technology_details_page(tech_id):
    """Render a detailed page for a specific technology."""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    tech = Technology.query.filter_by(id=tech_id, nation_id=nation.id).first()
    
    if not tech:
        flash('Technology not found.', 'danger')
        return redirect(url_for('technology.technology_view'))
    
    # Get full technology data
    tech_data = get_tech_details(tech_id)
    effects = get_tech_effects(nation, tech_id, tech.level)
    
    # Get prerequisites with user-friendly names
    prerequisites = []
    if tech.prerequisites:
        # Use the utility function to get readable prerequisite names
        prereq_info_list = get_prerequisites_names(tech.prerequisites)
        
        for prereq_info in prereq_info_list:
            prereq_id = prereq_info["id"]
            prereq = Technology.query.filter_by(id=prereq_id, nation_id=nation.id).first()
            if prereq:
                prerequisites.append({
                    "id": prereq.id,
                    "name": prereq.name,
                    "level": prereq.level,
                    "researched": prereq.level > 0
                })
    
    # Get technologies that have this as a prerequisite
    dependents = []
    all_techs = Technology.query.filter_by(nation_id=nation.id).all()
    for potential_dep in all_techs:
        if potential_dep.prerequisites:
            prereq_ids = [int(x) for x in potential_dep.prerequisites.split(',') if x]
            if tech.id in prereq_ids:
                dependents.append({
                    "id": potential_dep.id,
                    "name": potential_dep.name,
                    "level": potential_dep.level,
                    "researched": potential_dep.level > 0
                })
    
    return render_template('technology_details.html',
                          nation=nation,
                          tech=tech,
                          tech_data=tech_data,
                          effects=effects,
                          prerequisites=prerequisites,
                          dependents=dependents)