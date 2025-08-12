from datetime import datetime
from sqlalchemy import desc
from app import db
from models import Nation, Resource, Technology, Military, War, BattleReport
import random
import math

def update_resources(nation):
    """Update a nation's resources based on time elapsed since last update"""
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    now = datetime.utcnow()
    
    # Calculate time elapsed in hours
    elapsed_hours = 0
    if resources.last_updated:
        time_diff = now - resources.last_updated
        elapsed_hours = time_diff.total_seconds() / 3600  # Convert to hours
    else:
        # Initialize the timestamp on the first update so future calls work correctly
        resources.last_updated = now
        db.session.commit()
        return

    if elapsed_hours > 0:
        # Calculate production rates based on population distribution and technology
        raw_materials_rate = get_production_rate(nation, 'raw_materials')
        food_rate = get_production_rate(nation, 'food')
        energy_rate = get_production_rate(nation, 'energy')
        tech_rate = get_production_rate(nation, 'technology')
        currency_rate = get_production_rate(nation, 'currency')
        
        # Calculate consumption rates
        raw_materials_consumption = get_consumption_rate(nation, 'raw_materials')
        food_consumption = get_consumption_rate(nation, 'food')
        energy_consumption = get_consumption_rate(nation, 'energy')
        
        # Update production rates
        resources.raw_materials_production = raw_materials_rate
        resources.food_production = food_rate
        resources.energy_production = energy_rate
        resources.technology_production = tech_rate
        resources.currency_production = currency_rate
        
        # Update consumption rates
        resources.raw_materials_consumption = raw_materials_consumption
        resources.food_consumption = food_consumption
        resources.energy_consumption = energy_consumption
        
        # Calculate net production (per hour)
        net_raw_materials = raw_materials_rate - raw_materials_consumption
        net_food = food_rate - food_consumption
        net_energy = energy_rate - energy_consumption
        
        # Update resource amounts
        resources.raw_materials += net_raw_materials * elapsed_hours
        resources.food += net_food * elapsed_hours
        resources.energy += net_energy * elapsed_hours
        resources.technology_points += tech_rate * elapsed_hours
        resources.currency += currency_rate * elapsed_hours
        
        # Ensure no negative resources
        resources.raw_materials = max(0, resources.raw_materials)
        resources.food = max(0, resources.food)
        resources.energy = max(0, resources.energy)
        
        # Update last updated timestamp
        resources.last_updated = now
        
        db.session.commit()

def get_production_rate(nation, resource_type):
    """Calculate production rate for a specific resource"""
    # Base production rates
    base_rates = {
        'raw_materials': 150,  # Aumentato da 100 a 150
        'food': 150,           # Aumentato da 100 a 150
        'energy': 150,         # Aumentato da 100 a 150
        'technology': 20,      # Aumentato da 10 a 20
        'currency': 1000
    }
    
    # Population distribution affects production
    population_factors = {
        'raw_materials': nation.industry_population / 100,
        'food': nation.agriculture_population / 100,
        'energy': nation.energy_population / 100,
        'technology': nation.research_population / 100,
        'currency': (nation.industry_population + nation.agriculture_population) / 200  # Both contribute to GDP
    }
    
    # Get technology multipliers
    tech_multiplier = get_technology_multiplier(nation, resource_type)
    
    # Calculate production rate
    base_rate = base_rates[resource_type]
    population_factor = population_factors[resource_type]
    population_scale = nation.total_population / 1000000  # Scale by population size
    
    production_rate = base_rate * population_factor * population_scale * tech_multiplier
    
    return production_rate

def get_consumption_rate(nation, resource_type):
    """Calculate consumption rate for a specific resource"""
    # Base consumption rates
    base_rates = {
        'raw_materials': 10,  # Ridotto drasticamente da 20 a 10
        'food': 10,           # Ridotto drasticamente da 20 a 10
        'energy': 10          # Ridotto drasticamente da 20 a 10
    }
    
    # Population consumes resources
    population_scale = nation.total_population / 1000000
    
    # Military consumes resources
    military = Military.query.filter_by(nation_id=nation.id).first()
    military_factor = 1.0
    if military:
        # More military units = higher consumption
        unit_count = (
            military.infantry * 0.25 +    # Ridotto ulteriormente l'impatto (prima era 0.5)
            military.tanks * 2.5 +        # Ridotto ulteriormente l'impatto (prima era 5)
            military.aircraft * 5 +       # Ridotto ulteriormente l'impatto (prima era 10)
            military.navy * 7.5 +         # Ridotto ulteriormente l'impatto (prima era 15)
            military.missiles * 1.25      # Ridotto ulteriormente l'impatto (prima era 2.5)
        )
        military_factor += unit_count / 40000  # Ridotto ulteriormente l'impatto (prima era 20000)
    
    # Technology can improve efficiency (reduce consumption)
    tech_efficiency = get_technology_efficiency(nation, resource_type)
    
    # Garantire un'efficienza minima anche senza tecnologie
    tech_efficiency = max(tech_efficiency, 1.2)  # Minimo 20% di efficienza
    
    # Calculate consumption rate
    base_rate = base_rates[resource_type]
    consumption_rate = base_rate * population_scale * military_factor / tech_efficiency
    
    return consumption_rate

def get_technology_multiplier(nation, resource_type):
    """Get the production multiplier from technologies"""
    multiplier = 1.2  # Bonus base di produzione del 20%
    
    # Get relevant technologies
    technologies = Technology.query.filter(Technology.nation_id == nation.id, Technology.level > 0).all()
    
    for tech in technologies:
        if tech.category == 'Production':
            multiplier *= tech.production_multiplier
    
    return multiplier

def get_technology_efficiency(nation, resource_type):
    """Get the consumption efficiency from technologies"""
    efficiency = 1.0
    
    # Get relevant technologies
    technologies = Technology.query.filter(Technology.nation_id == nation.id, Technology.level > 0).all()
    
    for tech in technologies:
        if tech.category == 'Efficiency':
            efficiency *= tech.consumption_efficiency
    
    return efficiency

def calculate_rankings():
    """Calculate and update rankings for all nations"""
    nations = Nation.query.all()
    
    # Calculate economic rankings
    economic_list = sorted(nations, key=lambda n: n.gdp, reverse=True)
    for i, nation in enumerate(economic_list):
        nation.economic_rank = i + 1
    
    # Calculate military rankings
    military_list = []
    for nation in nations:
        military = Military.query.filter_by(nation_id=nation.id).first()
        if military:
            military_power = military.offensive_power + military.defensive_power
            military_list.append((nation, military_power))
    
    military_list.sort(key=lambda x: x[1], reverse=True)
    for i, (nation, _) in enumerate(military_list):
        nation.military_rank = i + 1
    
    # Calculate technology rankings
    tech_list = []
    for nation in nations:
        tech_level_sum = 0
        technologies = Technology.query.filter_by(nation_id=nation.id).all()
        for tech in technologies:
            tech_level_sum += tech.level
        tech_list.append((nation, tech_level_sum))
    
    tech_list.sort(key=lambda x: x[1], reverse=True)
    for i, (nation, _) in enumerate(tech_list):
        nation.technology_rank = i + 1
    
    # Calculate overall rankings (average of all three)
    for nation in nations:
        if nation.economic_rank and nation.military_rank and nation.technology_rank:
            overall_score = (nation.economic_rank + nation.military_rank + nation.technology_rank) / 3
            nation.overall_rank = math.ceil(overall_score)
    
    db.session.commit()

def calculate_military_power(military, power_type):
    """Calculate military power for a specific type (offensive, defensive, espionage)"""
    if power_type == 'offensive':
        # Offensive power calculation
        infantry_power = military.infantry * 1
        tank_power = military.tanks * 10
        aircraft_power = military.aircraft * 20
        navy_power = military.navy * 30
        missile_power = military.missiles * 50
        
        total_power = infantry_power + tank_power + aircraft_power + navy_power + missile_power
        return total_power
    
    elif power_type == 'defensive':
        # Defensive power calculation
        infantry_power = military.infantry * 0.5
        bunker_power = military.bunkers * 100
        anti_air_power = military.anti_air * 50
        coastal_defense_power = military.coastal_defenses * 80
        
        total_power = infantry_power + bunker_power + anti_air_power + coastal_defense_power
        return total_power
    
    elif power_type == 'espionage':
        # Espionage power calculation
        spy_power = military.spies * 100
        counter_intel_power = military.counter_intelligence * 50
        
        total_power = spy_power + counter_intel_power
        return total_power
    
    return 0

def conduct_attack(attacker_id, defender_id, attack_type, war_id):
    """Conduct an attack in a war"""
    # Get attacker and defender
    attacker_military = Military.query.filter_by(nation_id=attacker_id).first()
    defender_military = Military.query.filter_by(nation_id=defender_id).first()
    
    if not attacker_military or not defender_military:
        return {'message': 'Military forces not found.', 'status': 'danger'}
    
    # Get the war
    war = War.query.get(war_id)
    if not war or not war.is_active:
        return {'message': 'War not found or inactive.', 'status': 'danger'}
    
    # Validate attack type
    valid_attack_types = ['infantry', 'tanks', 'aircraft', 'navy', 'missiles']
    if attack_type not in valid_attack_types:
        return {'message': 'Invalid attack type.', 'status': 'danger'}
    
    # Check if attacker has units of this type
    attacker_units = getattr(attacker_military, attack_type)
    if attacker_units <= 0:
        return {'message': f'You have no {attack_type} units to attack with.', 'status': 'danger'}
    
    # Calculate attack strength based on unit type
    attack_strength_multipliers = {
        'infantry': 1,
        'tanks': 10,
        'aircraft': 20,
        'navy': 30,
        'missiles': 50
    }
    
    attack_strength = attacker_units * attack_strength_multipliers[attack_type]
    
    # Calculate defense strength
    defense_strength = defender_military.defensive_power
    
    # Determine outcome (with randomness)
    attack_roll = random.random() * attack_strength
    defense_roll = random.random() * defense_strength
    
    attacker_casualties = 0
    defender_casualties = 0
    resources_plundered = 0
    raw_materials_plundered = 0
    food_plundered = 0
    energy_plundered = 0
    
    # Create a battle report
    battle_report = BattleReport(
        war_id=war_id,
        battle_date=datetime.utcnow(),
        attack_type=attack_type,
        is_attacker_victory=(attack_roll > defense_roll),
        attacker_strength=attack_strength,
        defender_strength=defense_strength
    )
    db.session.add(battle_report)
    
    if attack_roll > defense_roll:
        # Attack succeeds
        # Destroy some defender units and plunder resources
        success_margin = attack_roll / defense_roll if defense_roll > 0 else 2.0
        
        # Defender loses units
        defender_infantry_loss = min(defender_military.infantry, int(defender_military.infantry * 0.1 * success_margin))
        defender_military.infantry -= defender_infantry_loss
        defender_casualties += defender_infantry_loss
        
        # Destroy some defense structures
        defender_anti_air_loss = 0
        defender_coastal_loss = 0
        if attack_type in ['aircraft', 'missiles']:
            defender_anti_air_loss = min(defender_military.anti_air, int(defender_military.anti_air * 0.2 * success_margin))
            defender_military.anti_air -= defender_anti_air_loss
        
        if attack_type in ['navy', 'missiles']:
            defender_coastal_loss = min(defender_military.coastal_defenses, int(defender_military.coastal_defenses * 0.2 * success_margin))
            defender_military.coastal_defenses -= defender_coastal_loss
        
        # Plunder resources
        defender_resources = Resource.query.filter_by(nation_id=defender_id).first()
        attacker_resources = Resource.query.filter_by(nation_id=attacker_id).first()
        
        if defender_resources and attacker_resources:
            plunder_rate = 0.05 * success_margin  # 5-10% of resources based on success
            
            raw_materials_plundered = defender_resources.raw_materials * plunder_rate
            food_plundered = defender_resources.food * plunder_rate
            energy_plundered = defender_resources.energy * plunder_rate
            
            # Defender loses resources
            defender_resources.raw_materials -= raw_materials_plundered
            defender_resources.food -= food_plundered
            defender_resources.energy -= energy_plundered
            
            # Attacker gains resources
            attacker_resources.raw_materials += raw_materials_plundered
            attacker_resources.food += food_plundered
            attacker_resources.energy += energy_plundered
            
            resources_plundered = raw_materials_plundered + food_plundered + energy_plundered
        
        # Attacker also loses some units (less than defender)
        attacker_loss_rate = 0.05  # 5% casualties for attacker
        attacker_unit_loss = min(attacker_units, int(attacker_units * attacker_loss_rate))
        setattr(attacker_military, attack_type, attacker_units - attacker_unit_loss)
        attacker_casualties += attacker_unit_loss
        
        # Reduce population based on casualties
        attacker_nation = Nation.query.get(attacker_id)
        defender_nation = Nation.query.get(defender_id)
        
        # Different unit types represent different numbers of personnel
        personnel_per_unit = {
            'infantry': 1,
            'tanks': 4,
            'aircraft': 8,
            'navy': 50,
            'missiles': 3
        }
        
        # Calculate population loss
        attacker_population_loss = attacker_unit_loss * personnel_per_unit.get(attack_type, 1)
        defender_population_loss = defender_infantry_loss  # Infantry are 1:1 with population
        
        # Reduce populations (minimum 100 people)
        attacker_nation.total_population = max(100, attacker_nation.total_population - attacker_population_loss)
        defender_nation.total_population = max(100, defender_nation.total_population - defender_population_loss)
        
        # Update war statistics
        war.aggressor_casualties += attacker_casualties
        war.defender_casualties += defender_casualties
        war.resources_plundered += resources_plundered
        war.aggressor_population_lost += attacker_population_loss
        war.defender_population_lost += defender_population_loss
        
        # Update battle report with details
        battle_report.attacker_casualties = attacker_casualties
        battle_report.defender_casualties = defender_casualties
        battle_report.attacker_population_lost = attacker_population_loss
        battle_report.defender_population_lost = defender_population_loss
        battle_report.resources_plundered = resources_plundered
        battle_report.raw_materials_plundered = raw_materials_plundered
        battle_report.food_plundered = food_plundered
        battle_report.energy_plundered = energy_plundered
        
        # Create detailed battle description
        battle_description = f"""
        The forces of {attacker_nation.name} launched a {attack_type} attack against {defender_nation.name}.
        
        The attack was successful!
        
        {attacker_nation.name} lost {attacker_casualties} {attack_type} units and {attacker_population_loss} population.
        {defender_nation.name} lost {defender_casualties} infantry units, {defender_anti_air_loss} anti-air defenses, 
        {defender_coastal_loss} coastal defenses, and {defender_population_loss} population.
        
        {attacker_nation.name} plundered:
        - {int(raw_materials_plundered)} raw materials
        - {int(food_plundered)} food
        - {int(energy_plundered)} energy
        
        Total resources plundered: {int(resources_plundered)}
        """
        battle_report.battle_description = battle_description
        
        # Check if defender has been defeated (lost all military)
        if defender_military.infantry <= 0 and defender_military.tanks <= 0 and defender_military.aircraft <= 0 and defender_military.navy <= 0:
            war.is_active = False
            war.end_date = datetime.utcnow()
            war.aggressor_victory = True
            
            # Reset at_war flags
            attacker_military.at_war = False
            defender_military.at_war = False
            
            message = f'Victory! You have defeated {Nation.query.get(defender_id).name} and plundered {int(resources_plundered)} resources. Check the detailed report for more information.'
            status = 'success'
        else:
            message = f'Attack successful! You destroyed {defender_casualties} enemy units and plundered {int(resources_plundered)} resources. You lost {attacker_casualties} {attack_type}. Check the detailed report for more information.'
            status = 'success'
    else:
        # Attack fails
        failure_margin = defense_roll / attack_roll
        
        # Attacker loses more units when attack fails
        attacker_loss_rate = 0.1 * failure_margin  # 10-20% casualties based on failure
        attacker_unit_loss = min(attacker_units, int(attacker_units * attacker_loss_rate))
        setattr(attacker_military, attack_type, attacker_units - attacker_unit_loss)
        attacker_casualties += attacker_unit_loss
        
        # Defender might lose a small number of units
        defender_infantry_loss = min(defender_military.infantry, int(defender_military.infantry * 0.02))
        defender_military.infantry -= defender_infantry_loss
        defender_casualties += defender_infantry_loss
        
        # Reduce population based on casualties
        attacker_nation = Nation.query.get(attacker_id)
        defender_nation = Nation.query.get(defender_id)
        
        # Different unit types represent different numbers of personnel
        personnel_per_unit = {
            'infantry': 1,
            'tanks': 4,
            'aircraft': 8,
            'navy': 50,
            'missiles': 3
        }
        
        # Higher casualties when attack fails
        attacker_population_loss = attacker_unit_loss * personnel_per_unit.get(attack_type, 1)
        defender_population_loss = defender_infantry_loss  # Infantry are 1:1 with population
        
        # Reduce populations (minimum 100 people)
        attacker_nation.total_population = max(100, attacker_nation.total_population - attacker_population_loss)
        defender_nation.total_population = max(100, defender_nation.total_population - defender_population_loss)
        
        # Update war statistics
        war.aggressor_casualties += attacker_casualties
        war.defender_casualties += defender_casualties
        war.aggressor_population_lost += attacker_population_loss
        war.defender_population_lost += defender_population_loss
        
        # Update battle report with details
        battle_report.attacker_casualties = attacker_casualties
        battle_report.defender_casualties = defender_casualties
        battle_report.attacker_population_lost = attacker_population_loss
        battle_report.defender_population_lost = defender_population_loss
        
        # Create detailed battle description
        battle_description = f"""
        The forces of {attacker_nation.name} launched a {attack_type} attack against {defender_nation.name}.
        
        The attack was repelled!
        
        {attacker_nation.name} lost {attacker_casualties} {attack_type} units and {attacker_population_loss} population.
        {defender_nation.name} lost {defender_casualties} infantry units and {defender_population_loss} population.
        
        No resources were plundered.
        """
        battle_report.battle_description = battle_description
        
        message = f'Attack failed! You lost {attacker_casualties} {attack_type} units. The enemy lost {defender_casualties} infantry. Check the detailed report for more information.'
        status = 'warning'
    
    db.session.commit()
    return {'message': message, 'status': status, 'battle_report_id': battle_report.id}

def conduct_espionage(spy_nation_id, target_nation_id, mission_type):
    """Conduct an espionage mission"""
    # Get spy and target nations
    spy_military = Military.query.filter_by(nation_id=spy_nation_id).first()
    target_military = Military.query.filter_by(nation_id=target_nation_id).first()
    
    if not spy_military or not target_military:
        return {'message': 'Military forces not found.', 'status': 'danger'}
    
    # Check if the spy nation has spies
    if spy_military.spies <= 0:
        return {'message': 'You have no spies to conduct espionage.', 'status': 'danger'}
    
    # Calculate espionage success chance
    spy_power = spy_military.espionage_power
    counter_intel_power = target_military.counter_intelligence * 50
    
    base_success_chance = 0.5  # 50% base chance
    power_ratio = spy_power / (counter_intel_power + 1)  # Prevent division by zero
    success_chance = min(0.9, base_success_chance + (power_ratio * 0.2))  # Max 90% chance
    
    # Roll for success
    success = random.random() < success_chance
    
    # Mission outcomes
    if mission_type == 'gather_intel':
        if success:
            # Get target nation's data
            target_nation = Nation.query.get(target_nation_id)
            target_resources = Resource.query.filter_by(nation_id=target_nation_id).first()
            
            # Format intel report
            intel = {
                'nation_name': target_nation.name,
                'population': target_nation.total_population,
                'military': {
                    'infantry': target_military.infantry,
                    'tanks': target_military.tanks,
                    'aircraft': target_military.aircraft,
                    'navy': target_military.navy,
                    'missiles': target_military.missiles,
                    'defensive_power': target_military.defensive_power
                },
                'resources': {
                    'raw_materials': int(target_resources.raw_materials),
                    'food': int(target_resources.food),
                    'energy': int(target_resources.energy),
                    'currency': int(target_resources.currency)
                }
            }
            
            # There's a small chance of losing a spy
            if random.random() < 0.1:
                spy_military.spies -= 1
                message = f'Intelligence gathered on {target_nation.name}, but one of your spies was captured!'
            else:
                message = f'Intelligence gathered on {target_nation.name}. They have {target_military.infantry} infantry, {target_military.tanks} tanks, and {int(target_resources.currency)} currency.'
            
            db.session.commit()
            return {'message': message, 'status': 'success', 'intel': intel}
        else:
            # Failed mission - lose a spy
            spy_military.spies -= 1
            db.session.commit()
            return {'message': 'Your spy was captured! Mission failed.', 'status': 'danger'}
    
    elif mission_type == 'sabotage_resources':
        if success:
            # Sabotage target's resources
            target_resources = Resource.query.filter_by(nation_id=target_nation_id).first()
            
            # Reduce resources by 5-10%
            sabotage_rate = 0.05 + (random.random() * 0.05)
            
            raw_materials_reduced = target_resources.raw_materials * sabotage_rate
            food_reduced = target_resources.food * sabotage_rate
            energy_reduced = target_resources.energy * sabotage_rate
            
            target_resources.raw_materials -= raw_materials_reduced
            target_resources.food -= food_reduced
            target_resources.energy -= energy_reduced
            
            # There's a chance of losing a spy
            if random.random() < 0.3:
                spy_military.spies -= 1
                message = f'Sabotage successful! Target lost resources, but one of your spies was captured!'
            else:
                message = f'Sabotage successful! Target lost approximately {int(sabotage_rate * 100)}% of their resources.'
            
            db.session.commit()
            return {'message': message, 'status': 'success'}
        else:
            # Failed mission - lose a spy
            spy_military.spies -= 1
            db.session.commit()
            return {'message': 'Your spy was captured during the sabotage attempt! Mission failed.', 'status': 'danger'}
    
    elif mission_type == 'sabotage_military':
        if success:
            # Sabotage target's military
            
            # Randomly choose which military asset to sabotage
            assets = ['infantry', 'tanks', 'aircraft', 'navy', 'missiles', 'bunkers', 'anti_air', 'coastal_defenses']
            asset_to_sabotage = random.choice(assets)
            
            # Reduce by 5-15%
            sabotage_rate = 0.05 + (random.random() * 0.1)
            current_value = getattr(target_military, asset_to_sabotage)
            reduced_amount = int(current_value * sabotage_rate)
            
            setattr(target_military, asset_to_sabotage, current_value - reduced_amount)
            
            # There's a higher chance of losing a spy in military sabotage
            if random.random() < 0.4:
                spy_military.spies -= 1
                message = f'Military sabotage successful! Target lost {reduced_amount} {asset_to_sabotage}, but one of your spies was captured!'
            else:
                message = f'Military sabotage successful! Target lost {reduced_amount} {asset_to_sabotage}.'
            
            db.session.commit()
            return {'message': message, 'status': 'success'}
        else:
            # Failed mission - lose a spy
            spy_military.spies -= 1
            db.session.commit()
            return {'message': 'Your spy was captured during the military sabotage attempt! Mission failed.', 'status': 'danger'}
    
    return {'message': 'Invalid mission type.', 'status': 'danger'}
