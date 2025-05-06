from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from app import db
from models import Nation, Alliance, War
from datetime import datetime
from utils.auth import easy_login_required
from utils.diplomacy_handler import (
    get_available_actions,
    perform_diplomatic_action,
    get_diplomatic_stance,
    calculate_diplomatic_influence,
    get_transit_rights,
    check_transit_rights,
    grant_transit_rights,
    revoke_transit_rights
)
from data.diplomacy import DIPLOMATIC_ACTIONS, RELATION_STATES

diplomacy = Blueprint('diplomacy', __name__)

@diplomacy.route('/diplomacy')
@easy_login_required
def diplomacy_view():
    """Main diplomacy page showing relations with other nations."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get all other nations
    other_nations = Nation.query.filter(Nation.id != nation.id).all()
    
    # Check if user has a nation
    if not nation:
        flash("You need to create a nation first!", "warning")
        return redirect(url_for('game.dashboard'))
    
    # Get diplomatic data
    diplomatic_data = {
        "alliances": [],
        "wars": []
    }
    
    # Calculate diplomatic influence
    diplomatic_influence = calculate_diplomatic_influence(nation)
    
    # Get active wars
    active_wars = War.query.filter(
        ((War.aggressor_id == nation.id) | (War.defender_id == nation.id)),
        War.is_active == True
    ).all()
    
    # Get alliances
    alliances = Alliance.query.filter(
        ((Alliance.nation1_id == nation.id) | (Alliance.nation2_id == nation.id)),
        Alliance.is_active == True
    ).all()
    
    # Format relation data for each nation
    relations = []
    for other_nation in other_nations:
        relation = get_diplomatic_stance(nation.id, other_nation.id)
        
        # Add nation info to relation data including map coordinates
        relation["nation"] = {
            "id": other_nation.id,
            "name": other_nation.name,
            "description": other_nation.description,
            "economic_rank": other_nation.economic_rank,
            "military_rank": other_nation.military_rank,
            "technology_rank": other_nation.technology_rank,
            "overall_rank": other_nation.overall_rank,
            "map_x": other_nation.map_x,
            "map_y": other_nation.map_y,
            "continent": other_nation.continent
        }
        
        # Debug print to see the coordinates
        print(f"DEBUG: Nation {other_nation.name}: x={other_nation.map_x}, y={other_nation.map_y}")
        
        relations.append(relation)
    
    return render_template('diplomacy.html',
                         nation=nation,
                         diplomatic_data=diplomatic_data,
                         diplomatic_influence=diplomatic_influence,
                         relations=relations,
                         active_wars=active_wars,
                         alliances=alliances,
                         relation_states=RELATION_STATES)

@diplomacy.route('/diplomacy/nation/<int:target_id>')
@easy_login_required
def nation_relations(target_id):
    """View diplomatic relations with a specific nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get target nation
    target_nation = Nation.query.get(target_id)
    
    if not target_nation:
        flash("Nation not found.", "danger")
        return redirect(url_for('diplomacy.diplomacy_view'))
    
    if target_nation.id == nation.id:
        flash("You cannot perform diplomatic actions with your own nation.", "warning")
        return redirect(url_for('diplomacy.diplomacy_view'))
    
    # Get diplomatic stance between nations
    relation = get_diplomatic_stance(nation.id, target_nation.id)
    
    # Get available diplomatic actions
    available_actions = get_available_actions(nation, target_nation)
    
    # Check for active war
    war = War.query.filter(
        ((War.aggressor_id == nation.id) & (War.defender_id == target_nation.id)) |
        ((War.aggressor_id == target_nation.id) & (War.defender_id == nation.id)),
        War.is_active == True
    ).first()
    
    # Check for alliance
    alliance = Alliance.query.filter(
        ((Alliance.nation1_id == nation.id) & (Alliance.nation2_id == target_nation.id)) |
        ((Alliance.nation1_id == target_nation.id) & (Alliance.nation2_id == nation.id)),
        Alliance.is_active == True
    ).first()
    
    # Get history of wars
    past_wars = War.query.filter(
        ((War.aggressor_id == nation.id) & (War.defender_id == target_nation.id)) |
        ((War.aggressor_id == target_nation.id) & (War.defender_id == nation.id)),
        War.is_active == False
    ).order_by(War.end_date.desc()).all()
    
    return render_template('diplomacy_nation.html',
                         nation=nation,
                         target_nation=target_nation,
                         relation=relation,
                         available_actions=available_actions,
                         active_war=war,
                         alliance=alliance,
                         past_wars=past_wars,
                         diplomatic_actions=DIPLOMATIC_ACTIONS)

@diplomacy.route('/diplomacy/action', methods=['POST'])
@easy_login_required
def diplomatic_action():
    """Perform a diplomatic action towards another nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get form data
    action_id = int(request.form.get('action_id'))
    target_nation_id = int(request.form.get('target_id', request.form.get('target_nation_id')))
    
    # Perform the diplomatic action
    result = perform_diplomatic_action(nation, target_nation_id, action_id)
    
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "danger")
    
    return redirect(url_for('diplomacy.nation_relations', target_id=target_nation_id))

@diplomacy.route('/api/diplomacy/relations')
@easy_login_required
def api_relations():
    """API endpoint to get diplomatic relations data."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get all other nations
    other_nations = Nation.query.filter(Nation.id != nation.id).all()
    
    # Format relation data for each nation
    relations = []
    for other_nation in other_nations:
        relation = get_diplomatic_stance(nation.id, other_nation.id)
        
        # Add nation info to relation data
        relation["nation"] = {
            "id": other_nation.id,
            "name": other_nation.name,
            "continent": other_nation.continent,
            "economic_rank": other_nation.economic_rank,
            "military_rank": other_nation.military_rank,
            "map_x": other_nation.map_x,
            "map_y": other_nation.map_y
        }
        
        relations.append(relation)
    
    return jsonify({
        'success': True,
        'current_nation': {
            'id': nation.id,
            'name': nation.name,
            'continent': nation.continent,
            'map_x': nation.map_x,
            'map_y': nation.map_y
        },
        'relations': relations
    })

@diplomacy.route('/diplomacy/wars')
@easy_login_required
def wars_view():
    """View all current wars in the world."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get all active wars
    active_wars = War.query.filter(War.is_active == True).all()
    
    # Process war data to include nation objects
    for war in active_wars:
        war.aggressor = Nation.query.get(war.aggressor_id)
        war.defender = Nation.query.get(war.defender_id)
    
    # Get your wars
    your_wars = [war for war in active_wars if war.aggressor_id == nation.id or war.defender_id == nation.id]
    
    # Get other wars
    other_wars = [war for war in active_wars if war.aggressor_id != nation.id and war.defender_id != nation.id]
    
    return render_template('diplomacy_wars.html',
                         nation=nation,
                         your_wars=your_wars,
                         other_wars=other_wars)

@diplomacy.route('/diplomacy/alliances')
@easy_login_required
def alliances_view():
    """View all current alliances in the world."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get all active alliances
    active_alliances = Alliance.query.filter(Alliance.is_active == True).all()
    
    # Process alliance data to include nation objects
    for alliance in active_alliances:
        alliance.nation1 = Nation.query.get(alliance.nation1_id)
        alliance.nation2 = Nation.query.get(alliance.nation2_id)
    
    # Get your alliances
    your_alliances = [alliance for alliance in active_alliances if alliance.nation1_id == nation.id or alliance.nation2_id == nation.id]
    
    # Get other alliances
    other_alliances = [alliance for alliance in active_alliances if alliance.nation1_id != nation.id and alliance.nation2_id != nation.id]
    
    return render_template('diplomacy_alliances.html',
                         nation=nation,
                         your_alliances=your_alliances,
                         other_alliances=other_alliances)

@diplomacy.route('/diplomacy/propose-peace/<int:war_id>', methods=['POST'])
@easy_login_required
def propose_peace(war_id):
    """Propose peace in an active war."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get the war
    war = War.query.get(war_id)
    
    if not war or not war.is_active:
        flash("War not found or already ended.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if user is part of this war
    if war.aggressor_id != nation.id and war.defender_id != nation.id:
        flash("You are not part of this war.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if peace is already proposed
    if war.peace_proposed:
        flash("Peace has already been proposed for this war.", "info")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Propose peace
    war.peace_proposed = True
    db.session.commit()
    
    # Get the enemy nation
    enemy_id = war.defender_id if war.aggressor_id == nation.id else war.aggressor_id
    enemy_nation = Nation.query.get(enemy_id)
    
    flash(f"You have proposed peace to {enemy_nation.name}. Wait for their response.", "success")
    return redirect(url_for('diplomacy.wars_view'))

@diplomacy.route('/diplomacy/accept-peace/<int:war_id>', methods=['POST'])
@easy_login_required
def accept_peace(war_id):
    """Accept a peace proposal."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get the war
    war = War.query.get(war_id)
    
    if not war or not war.is_active:
        flash("War not found or already ended.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if user is part of this war
    if war.aggressor_id != nation.id and war.defender_id != nation.id:
        flash("You are not part of this war.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if peace is proposed
    if not war.peace_proposed:
        flash("No peace has been proposed for this war.", "warning")
        return redirect(url_for('diplomacy.wars_view'))
    
    # End the war
    war.is_active = False
    war.end_date = datetime.utcnow()
    war.aggressor_victory = None  # Draw
    db.session.commit()
    
    # Get the enemy nation
    enemy_id = war.defender_id if war.aggressor_id == nation.id else war.aggressor_id
    enemy_nation = Nation.query.get(enemy_id)
    
    # Perform peace treaty action to improve relations
    result = perform_diplomatic_action(nation, enemy_id, 15)  # ID 15 is "Propose Peace Treaty"
    
    flash(f"You have accepted peace with {enemy_nation.name}. The war is now over.", "success")
    return redirect(url_for('diplomacy.wars_view'))

@diplomacy.route('/diplomacy/reject-peace/<int:war_id>', methods=['POST'])
@easy_login_required
def reject_peace(war_id):
    """Reject a peace proposal."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get the war
    war = War.query.get(war_id)
    
    if not war or not war.is_active:
        flash("War not found or already ended.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if user is part of this war
    if war.aggressor_id != nation.id and war.defender_id != nation.id:
        flash("You are not part of this war.", "danger")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Check if peace is proposed
    if not war.peace_proposed:
        flash("No peace has been proposed for this war.", "warning")
        return redirect(url_for('diplomacy.wars_view'))
    
    # Reject peace
    war.peace_proposed = False
    db.session.commit()
    
    # Get the enemy nation
    enemy_id = war.defender_id if war.aggressor_id == nation.id else war.aggressor_id
    enemy_nation = Nation.query.get(enemy_id)
    
    flash(f"You have rejected the peace proposal from {enemy_nation.name}. The war continues.", "info")
    return redirect(url_for('diplomacy.wars_view'))


@diplomacy.route('/diplomacy/transit')
@easy_login_required
def transit_rights_view():
    """View and manage transit rights."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get transit rights data
    transit_data = get_transit_rights(nation.id)
    
    # Get all other nations for granting rights
    other_nations = Nation.query.filter(Nation.id != nation.id).all()
    
    return render_template('diplomacy_transit.html',
                         nation=nation,
                         transit_data=transit_data,
                         other_nations=other_nations)


@diplomacy.route('/diplomacy/transit/grant', methods=['POST'])
@easy_login_required
def grant_transit_rights_action():
    """Grant transit rights to another nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get form data
    receiver_id = int(request.form.get('nation_id'))
    duration = request.form.get('duration')
    
    # Parse duration to days if provided
    duration_days = None
    if duration and duration.isdigit():
        duration_days = int(duration)
    
    # Grant transit rights
    result = grant_transit_rights(nation.id, receiver_id, duration_days)
    
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "danger")
    
    return redirect(url_for('diplomacy.transit_rights_view'))


@diplomacy.route('/diplomacy/transit/revoke/<int:receiver_id>', methods=['POST'])
@easy_login_required
def revoke_transit_rights_action(receiver_id):
    """Revoke transit rights from another nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Revoke transit rights (locally import to avoid naming conflicts)
    from utils.diplomacy_handler import revoke_transit_rights as revoke_transit_rights_util
    result = revoke_transit_rights_util(nation.id, receiver_id)
    
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "danger")
    
    return redirect(url_for('diplomacy.transit_rights_view'))


@diplomacy.route('/diplomacy/request-transit/<int:target_id>', methods=['POST'])
@easy_login_required
def request_transit_rights(target_id):
    """Request transit rights from another nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get target nation
    target_nation = Nation.query.get(target_id)
    
    if not target_nation:
        flash("Nation not found.", "danger")
        return redirect(url_for('diplomacy.diplomacy_view'))
    
    # Check if nations are neighbors
    from utils.diplomacy_handler import are_nations_neighbors
    if are_nations_neighbors(nation.id, target_id):
        flash("Transit rights are not needed for neighboring nations.", "warning")
        return redirect(url_for('diplomacy.nation_relations', target_id=target_id))
    
    # Check for existing transit rights
    from utils.diplomacy_handler import get_transit_rights
    if get_transit_rights(nation.id, target_id):
        flash("You already have transit rights from this nation.", "info")
        return redirect(url_for('diplomacy.nation_relations', target_id=target_id))
    
    # Check if nations are at war
    war = War.query.filter(
        ((War.aggressor_id == nation.id) & (War.defender_id == target_id)) |
        ((War.aggressor_id == target_id) & (War.defender_id == nation.id)),
        War.is_active == True
    ).first()
    
    if war:
        flash("You cannot request transit rights from a nation you are at war with.", "danger")
        return redirect(url_for('diplomacy.nation_relations', target_id=target_id))
    
    # Send diplomatic request for transit rights
    # Use diplomatic action ID 5 (Request Military Access)
    result = perform_diplomatic_action(nation, target_id, 5)
    
    if result["success"]:
        flash(f"You have requested transit rights from {target_nation.name}.", "success")
    else:
        flash(result["message"], "danger")
    
    return redirect(url_for('diplomacy.nation_relations', target_id=target_id))


@diplomacy.route('/diplomacy/revoke-transit/<int:target_id>', methods=['POST'])
@easy_login_required
def revoke_my_transit_rights(target_id):
    """Revoke your transit rights to another nation."""
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get target nation
    target_nation = Nation.query.get(target_id)
    
    if not target_nation:
        flash("Nation not found.", "danger")
        return redirect(url_for('diplomacy.diplomacy_view'))
    
    # Check for existing transit rights
    from utils.diplomacy_handler import get_transit_rights
    if not get_transit_rights(nation.id, target_id):
        flash("You don't have transit rights from this nation.", "warning")
        return redirect(url_for('diplomacy.nation_relations', target_id=target_id))
    
    # Revoke transit rights (import locally to avoid name conflicts)
    from utils.diplomacy_handler import revoke_transit_rights as revoke_transit_rights_util
    result = revoke_transit_rights_util(target_id, nation.id)
    
    if result["success"]:
        flash(f"You have revoked your transit rights from {target_nation.name}.", "success")
    else:
        flash(result["message"], "danger")
    
    return redirect(url_for('diplomacy.nation_relations', target_id=target_id))