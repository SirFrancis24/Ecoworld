from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from app import db
from models import Nation, Resource, Military, War, Alliance, BattleReport
from datetime import datetime
from utils.game_logic import calculate_military_power, conduct_attack, conduct_espionage
from utils.auth import easy_login_required

military = Blueprint('military', __name__)

@military.route('/military')
@easy_login_required
def military_view():
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    military_forces = Military.query.filter_by(nation_id=nation.id).first()
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    # Get active wars
    active_wars_as_aggressor = War.query.filter_by(aggressor_id=nation.id, is_active=True).all()
    active_wars_as_defender = War.query.filter_by(defender_id=nation.id, is_active=True).all()
    
    # Get possible nations to attack (exclude allies and nations already at war with)
    all_nations = Nation.query.filter(Nation.id != nation.id).all()
    at_war_with = [war.defender_id for war in active_wars_as_aggressor] + [war.aggressor_id for war in active_wars_as_defender]
    allies = [ally.id for ally in nation.allies]
    
    potential_targets = [n for n in all_nations if n.id not in at_war_with and n.id not in allies]
    
    # Update military power calculations
    military_forces.offensive_power = calculate_military_power(military_forces, 'offensive')
    military_forces.defensive_power = calculate_military_power(military_forces, 'defensive')
    military_forces.espionage_power = calculate_military_power(military_forces, 'espionage')
    
    # Calculate military limits based on population
    military_limits = get_military_limits(nation)
    
    db.session.commit()
    
    return render_template('military.html',
                          nation=nation,
                          military=military_forces,
                          resources=resources,
                          military_limits=military_limits,
                          active_wars_as_aggressor=active_wars_as_aggressor,
                          active_wars_as_defender=active_wars_as_defender,
                          potential_targets=potential_targets,
                          datetime=datetime)

def get_military_limits(nation):
    """Calculate the military limits based on population"""
    # Get demographics info
    total_population = nation.total_population
    
    # Only a portion of the population is eligible for military service
    # Typically 18-45 years old, roughly 40% of the population
    eligible_population = total_population * 0.4
    
    # Population already assigned to industry, agriculture etc.
    workforce_percentage = nation.agriculture_population + nation.industry_population + \
                          nation.energy_population + nation.research_population
    
    # The military population percentage determines how many can serve in armed forces
    military_percentage = nation.military_population
    
    # Calculate maximum military personnel based on demographics
    max_military_personnel = int(eligible_population * (military_percentage / 100.0))
    
    # Limits for each unit type
    limits = {
        'infantry': int(max_military_personnel * 0.70),  # 70% can be infantry
        'tanks': int(max_military_personnel * 0.05),     # 5% can operate tanks (1 tank = 4 crew)
        'aircraft': int(max_military_personnel * 0.01),  # 1% can operate aircraft (1 aircraft = 6-10 crew)
        'navy': int(max_military_personnel * 0.02),      # 2% can operate naval vessels (1 ship = many crew)
        'missiles': int(max_military_personnel * 0.01),  # 1% can operate missile systems
        'bunkers': int(max_military_personnel * 0.05),   # 5% can man bunkers
        'anti_air': int(max_military_personnel * 0.03),  # 3% can operate anti-air systems
        'coastal_defenses': int(max_military_personnel * 0.02),  # 2% can operate coastal defenses
        'spies': min(nation.military.max_spies, 20),     # Maximum spies based on nation's tech level
        'counter_intelligence': int(max_military_personnel * 0.01)  # 1% can work in counter-intelligence
    }
    
    # Ensure minimum values for game balance (we don't want zeros)
    for key in limits:
        limits[key] = max(limits[key], 5)
    
    return limits

@military.route('/military/build', methods=['POST'])
@easy_login_required
def build_military():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    military_forces = Military.query.filter_by(nation_id=nation.id).first()
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    unit_type = request.form.get('unit_type')
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Define costs for each unit type
    unit_costs = {
        'infantry': {'raw_materials': 10, 'energy': 5, 'currency': 100},
        'tanks': {'raw_materials': 100, 'energy': 50, 'currency': 1000},
        'aircraft': {'raw_materials': 200, 'energy': 150, 'currency': 5000},
        'navy': {'raw_materials': 500, 'energy': 300, 'currency': 10000},
        'missiles': {'raw_materials': 300, 'energy': 200, 'currency': 7500},
        'bunkers': {'raw_materials': 1000, 'energy': 100, 'currency': 5000},
        'anti_air': {'raw_materials': 500, 'energy': 200, 'currency': 3000},
        'coastal_defenses': {'raw_materials': 800, 'energy': 200, 'currency': 4000},
        'spies': {'raw_materials': 0, 'energy': 50, 'currency': 2000},
        'counter_intelligence': {'raw_materials': 0, 'energy': 100, 'currency': 3000}
    }
    
    if unit_type not in unit_costs:
        flash('Invalid unit type.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Calculate total costs
    total_raw_materials = unit_costs[unit_type]['raw_materials'] * quantity
    total_energy = unit_costs[unit_type]['energy'] * quantity
    total_currency = unit_costs[unit_type]['currency'] * quantity
    
    # Check if the nation has enough resources
    if resources.raw_materials < total_raw_materials:
        flash('Not enough raw materials.', 'danger')
        return redirect(url_for('military.military_view'))
    if resources.energy < total_energy:
        flash('Not enough energy.', 'danger')
        return redirect(url_for('military.military_view'))
    if resources.currency < total_currency:
        flash('Not enough currency.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Check military limits based on population
    military_limits = get_military_limits(nation)
    current_amount = getattr(military_forces, unit_type)
    max_allowed = military_limits[unit_type]
    
    if current_amount + quantity > max_allowed:
        flash(f'Cannot build {quantity} {unit_type}. Your maximum limit is {max_allowed} (currently have {current_amount}).', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Deduct resources
    resources.raw_materials -= total_raw_materials
    resources.energy -= total_energy
    resources.currency -= total_currency
    
    # Add units
    setattr(military_forces, unit_type, current_amount + quantity)
    
    db.session.commit()
    
    flash(f'Successfully built {quantity} {unit_type}.', 'success')
    return redirect(url_for('military.military_view'))

@military.route('/military/declare_war', methods=['POST'])
@easy_login_required
def declare_war():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    target_id = int(request.form.get('target_nation'))
    
    # Check if the target nation exists
    target_nation = Nation.query.get_or_404(target_id)
    
    # Check if already at war with this nation
    existing_war = War.query.filter(
        ((War.aggressor_id == nation.id) & (War.defender_id == target_id)) |
        ((War.aggressor_id == target_id) & (War.defender_id == nation.id)),
        War.is_active == True
    ).first()
    
    if existing_war:
        flash('You are already at war with this nation.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Check if this nation is an ally
    if target_nation in nation.allies:
        flash('You cannot declare war on an ally. You must dissolve the alliance first.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Create new war record
    new_war = War(
        aggressor_id=nation.id,
        defender_id=target_id,
        start_date=datetime.utcnow(),
        is_active=True
    )
    
    # Set at_war flag for both nations' military
    aggressor_military = Military.query.filter_by(nation_id=nation.id).first()
    defender_military = Military.query.filter_by(nation_id=target_id).first()
    
    aggressor_military.at_war = True
    defender_military.at_war = True
    
    db.session.add(new_war)
    db.session.commit()
    
    flash(f'War declared against {target_nation.name}!', 'warning')
    return redirect(url_for('military.military_view'))

@military.route('/military/attack', methods=['POST'])
@easy_login_required
def attack():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    war_id = int(request.form.get('war_id'))
    attack_type = request.form.get('attack_type')  # 'infantry', 'tanks', 'aircraft', 'navy', 'missiles'
    
    # Check if the war exists and this nation is the aggressor
    war = War.query.filter_by(id=war_id, aggressor_id=nation.id, is_active=True).first()
    
    if not war:
        flash('Invalid war or you are not the aggressor.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Conduct the attack
    result = conduct_attack(nation.id, war.defender_id, attack_type, war_id)
    
    flash(result['message'], result['status'])
    
    # If there's a battle report ID, redirect to display it
    if 'battle_report_id' in result:
        return redirect(url_for('military.view_battle_report', report_id=result['battle_report_id']))
    
    return redirect(url_for('military.military_view'))


@military.route('/military/battle-report/<int:report_id>')
@easy_login_required
def view_battle_report(report_id):
    """View a specific battle report"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    battle_report = BattleReport.query.get_or_404(report_id)
    war = War.query.get(battle_report.war_id)
    
    # Security check: user must be involved in the war
    if nation.id != war.aggressor_id and nation.id != war.defender_id:
        flash('Access denied: You are not authorized to view this battle report.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Check if user is aggressor or defender
    is_aggressor = (nation.id == war.aggressor_id)
    
    return render_template('battle_report.html',
                          nation=nation,
                          battle_report=battle_report,
                          war=war,
                          is_aggressor=is_aggressor,
                          datetime=datetime)

@military.route('/military/espionage', methods=['POST'])
@easy_login_required
def espionage():
    # This function is deprecated, redirecting to the new espionage page
    flash('Espionage operations have been moved to the Espionage page.', 'info')
    return redirect(url_for('espionage.espionage_view'))

@military.route('/military/propose_alliance', methods=['POST'])
@easy_login_required
def propose_alliance():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    target_id = int(request.form.get('target_nation'))
    
    # Check if the target nation exists
    target_nation = Nation.query.get_or_404(target_id)
    
    # Check if already allies
    if target_nation in nation.allies:
        flash('You are already allies with this nation.', 'warning')
        return redirect(url_for('military.military_view'))
    
    # Check if at war
    existing_war = War.query.filter(
        ((War.aggressor_id == nation.id) & (War.defender_id == target_id)) |
        ((War.aggressor_id == target_id) & (War.defender_id == nation.id)),
        War.is_active == True
    ).first()
    
    if existing_war:
        flash('You cannot propose an alliance while at war.', 'danger')
        return redirect(url_for('military.military_view'))
    
    # Create alliance in both directions
    nation.allies.append(target_nation)
    
    # Create an alliance record
    new_alliance = Alliance(
        nation1_id=nation.id,
        nation2_id=target_id,
        formed_date=datetime.utcnow(),
        is_active=True
    )
    
    db.session.add(new_alliance)
    db.session.commit()
    
    flash(f'Alliance formed with {target_nation.name}!', 'success')
    return redirect(url_for('military.military_view'))