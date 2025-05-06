from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
import json
from datetime import datetime

from app import db
from models import Nation, Military, DeployedSpy, SpyMission, SpyReport
from utils.advanced_espionage import AdvancedEspionageSystem
from utils.auth_helpers import easy_login_required

espionage = Blueprint('espionage', __name__)

@espionage.route('/espionage')
@easy_login_required
def espionage_view():
    """Espionage main view"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Get military info
    military = Military.query.filter_by(nation_id=nation.id).first()
    
    # Get active deployed spies
    deployed_spies = DeployedSpy.query.filter_by(
        owner_nation_id=nation.id,
        is_active=True
    ).all()
    
    # Process spies for display
    spy_data = []
    for spy in deployed_spies:
        target_nation = Nation.query.get(spy.target_nation_id)
        
        # Get any active mission
        active_mission = SpyMission.query.filter_by(
            spy_id=spy.id,
            is_completed=False
        ).first()
        
        spy_info = {
            'id': spy.id,
            'target_nation': target_nation.name if target_nation else 'Unknown',
            'deployed_since': spy.deployment_date.strftime('%Y-%m-%d'),
            'days_deployed': (datetime.utcnow() - spy.deployment_date).days,
            'cover_strength': spy.cover_strength,
            'intel_level': spy.intel_level,
            'specialization': spy.specialization,
            'skill_level': spy.skill_level,
            'is_discovered': spy.is_discovered,
            'active_mission': None
        }
        
        if active_mission:
            # Calculate progress percentage
            total_time = (active_mission.completion_date - active_mission.start_date).total_seconds()
            elapsed_time = (datetime.utcnow() - active_mission.start_date).total_seconds()
            progress = min(100, (elapsed_time / total_time) * 100) if total_time > 0 else 0
            
            spy_info['active_mission'] = {
                'id': active_mission.id,
                'type': active_mission.mission_type,
                'start_date': active_mission.start_date.strftime('%Y-%m-%d %H:%M'),
                'completion_date': active_mission.completion_date.strftime('%Y-%m-%d %H:%M'),
                'progress': progress,
                'success_chance': active_mission.success_chance
            }
        
        spy_data.append(spy_info)
    
    # Get completed missions (last 10)
    completed_missions = SpyMission.query.join(DeployedSpy).filter(
        DeployedSpy.owner_nation_id == nation.id,
        SpyMission.is_completed == True
    ).order_by(SpyMission.completion_date.desc()).limit(10).all()
    
    # Process missions for display
    mission_data = []
    for mission in completed_missions:
        spy = mission.spy
        target_nation = Nation.query.get(spy.target_nation_id) if spy else None
        
        mission_info = {
            'id': mission.id,
            'type': mission.mission_type,
            'target_nation': target_nation.name if target_nation else 'Unknown',
            'completion_date': mission.completion_date.strftime('%Y-%m-%d %H:%M'),
            'success': mission.is_successful,
            'outcome': mission.outcome_description
        }
        
        mission_data.append(mission_info)
    
    # Get intel reports (last 10)
    intel_reports = SpyReport.query.filter_by(
        nation_id=nation.id
    ).order_by(SpyReport.report_date.desc()).limit(10).all()
    
    # Process reports for display
    report_data = []
    for report in intel_reports:
        target_nation = Nation.query.get(report.target_nation_id)
        
        report_info = {
            'id': report.id,
            'target_nation': target_nation.name if target_nation else 'Unknown',
            'report_date': report.report_date.strftime('%Y-%m-%d %H:%M'),
            'report_type': report.report_type,
            'intel_quality': report.intel_quality,
            'content': json.loads(report.report_content) if report.report_content else {}
        }
        
        report_data.append(report_info)
    
    # Get potential target nations
    potential_targets = Nation.query.filter(
        Nation.id != nation.id
    ).all()
    
    return render_template('espionage.html',
                           nation=nation,
                           military=military,
                           deployed_spies=spy_data,
                           available_spies=espionage_system.get_available_spies(),
                           max_spies=espionage_system.get_max_spies(),
                           missions=mission_data,
                           intel_reports=report_data,
                           potential_targets=potential_targets,
                           counter_intelligence=military.counter_intelligence)

@espionage.route('/espionage/train_spy', methods=['POST'])
@easy_login_required
def train_spy():
    """Train a new spy"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    specialization = request.form.get('specialization', 'general')
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Train spy
    result = espionage_system.train_spy(specialization)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/espionage/deploy_spy', methods=['POST'])
@easy_login_required
def deploy_spy():
    """Deploy a spy to a target nation"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    target_nation_id = request.form.get('target_nation_id')
    specialization = request.form.get('specialization', 'general')
    
    if not target_nation_id:
        flash('No target nation selected!', 'danger')
        return redirect(url_for('espionage.espionage_view'))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Deploy spy
    result = espionage_system.deploy_spy(target_nation_id, specialization)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/espionage/recall_spy', methods=['POST'])
@easy_login_required
def recall_spy():
    """Recall a spy from their mission"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    spy_id = request.form.get('spy_id')
    
    if not spy_id:
        flash('No spy selected!', 'danger')
        return redirect(url_for('espionage.espionage_view'))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Recall spy
    result = espionage_system.recall_spy(spy_id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/espionage/assign_mission', methods=['POST'])
@easy_login_required
def assign_mission():
    """Assign a mission to a deployed spy"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    spy_id = request.form.get('spy_id')
    mission_type = request.form.get('mission_type')
    
    if not spy_id or not mission_type:
        flash('Missing required information!', 'danger')
        return redirect(url_for('espionage.espionage_view'))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Assign mission
    result = espionage_system.assign_spy_mission(spy_id, mission_type)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/espionage/improve_counter_intelligence', methods=['POST'])
@easy_login_required
def improve_counter_intelligence():
    """Improve nation's counter-intelligence capabilities"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    levels = int(request.form.get('levels', 1))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Improve counter-intelligence
    result = espionage_system.improve_counter_intelligence(levels)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/espionage/run_sweep', methods=['POST'])
@easy_login_required
def run_counter_intelligence_sweep():
    """Run a counter-intelligence sweep to detect foreign spies"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        flash('You need to create a nation first!', 'warning')
        return redirect(url_for('game.dashboard'))
    
    # Initialize espionage system
    espionage_system = AdvancedEspionageSystem(nation)
    
    # Run sweep
    result = espionage_system.run_counter_intelligence_sweep()
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('espionage.espionage_view'))

@espionage.route('/api/espionage/report/<int:report_id>')
@easy_login_required
def api_report_details(report_id):
    """API endpoint to get detailed report data"""
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if not nation:
        return jsonify({'success': False, 'message': 'No nation found'})
    
    # Get report
    report = SpyReport.query.filter_by(
        id=report_id,
        nation_id=nation.id
    ).first()
    
    if not report:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    target_nation = Nation.query.get(report.target_nation_id)
    
    # Format report data
    report_data = {
        'id': report.id,
        'target_nation': target_nation.name if target_nation else 'Unknown',
        'report_date': report.report_date.strftime('%Y-%m-%d %H:%M'),
        'report_type': report.report_type,
        'intel_quality': report.intel_quality,
        'content': json.loads(report.report_content) if report.report_content else {}
    }
    
    return jsonify({
        'success': True,
        'report': report_data
    })