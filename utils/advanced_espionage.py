"""
Advanced espionage system that handles spy deployment, missions, and counter-intelligence.
"""
from datetime import datetime, timedelta
import random
import json
import logging
from flask import current_app

from app import db
from models import Nation, Military, DeployedSpy, SpyMission, SpyReport, Technology

# Configure logger
logger = logging.getLogger(__name__)

class AdvancedEspionageSystem:
    """Handles all espionage operations for a nation."""
    
    def __init__(self, nation):
        self.nation = nation
        self.military = Military.query.filter_by(nation_id=nation.id).first()
        
        if not self.military:
            raise ValueError(f"No military record found for nation {nation.id}")
    
    def get_available_spies(self):
        """Get number of spies available for deployment."""
        # Total spies
        total_spies = self.military.spies
        
        # Count deployed spies
        deployed_spies = DeployedSpy.query.filter_by(
            owner_nation_id=self.nation.id,
            is_active=True
        ).count()
        
        return total_spies - deployed_spies
    
    def get_max_spies(self):
        """Get maximum number of spies a nation can have."""
        return self.military.max_spies
    
    def train_spy(self, specialization='general'):
        """Train a new spy."""
        # Check if nation is at max spies
        if self.military.spies >= self.military.max_spies:
            return {
                "success": False,
                "message": f"You have reached your maximum spy capacity of {self.military.max_spies}."
            }
        
        # Cost to train a spy
        currency_cost = 5000
        technology_cost = 50
        
        # Check resources
        from models import Resource
        resources = Resource.query.filter_by(nation_id=self.nation.id).first()
        
        if not resources:
            return {"success": False, "message": "No resources found for your nation."}
        
        if resources.currency < currency_cost:
            return {"success": False, "message": f"Not enough currency. Need {currency_cost}."}
        
        if resources.technology_points < technology_cost:
            return {"success": False, "message": f"Not enough technology points. Need {technology_cost}."}
        
        # Deduct resources
        resources.currency -= currency_cost
        resources.technology_points -= technology_cost
        
        # Add spy
        self.military.spies += 1
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Successfully trained a new spy specializing in {specialization}.",
            "total_spies": self.military.spies,
            "available_spies": self.get_available_spies()
        }
    
    def deploy_spy(self, target_nation_id, specialization='general'):
        """Deploy a spy to a target nation."""
        # Check if target nation exists
        target_nation = Nation.query.get(target_nation_id)
        if not target_nation:
            return {"success": False, "message": "Target nation not found."}
        
        # Check if there's an available spy
        if self.get_available_spies() <= 0:
            return {"success": False, "message": "No spies available for deployment."}
        
        # Create deployed spy record
        spy = DeployedSpy(
            owner_nation_id=self.nation.id,
            target_nation_id=target_nation_id,
            specialization=specialization,
            skill_level=1  # Start at lowest skill level
        )
        
        db.session.add(spy)
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Spy deployed to {target_nation.name}.",
            "spy_id": spy.id,
            "available_spies": self.get_available_spies()
        }
    
    def recall_spy(self, spy_id):
        """Recall a spy from deployment."""
        spy = DeployedSpy.query.filter_by(
            id=spy_id,
            owner_nation_id=self.nation.id,
            is_active=True
        ).first()
        
        if not spy:
            return {"success": False, "message": "Spy not found or already recalled."}
        
        # Check if spy is currently on a mission
        active_mission = SpyMission.query.filter_by(
            spy_id=spy.id,
            is_completed=False
        ).first()
        
        if active_mission:
            return {"success": False, "message": "Cannot recall spy while on an active mission."}
        
        # Recall the spy (set to inactive, but keep the record for history)
        spy.is_active = False
        
        # Generate final report if the spy was not discovered
        if not spy.is_discovered:
            # Create a final intelligence report
            self._generate_spy_report(spy)
        
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Spy recalled from {spy.target_nation.name}.",
            "available_spies": self.get_available_spies()
        }
    
    def assign_spy_mission(self, spy_id, mission_type):
        """Assign a mission to a deployed spy."""
        spy = DeployedSpy.query.filter_by(
            id=spy_id,
            owner_nation_id=self.nation.id,
            is_active=True
        ).first()
        
        if not spy:
            return {"success": False, "message": "Spy not found or not active."}
        
        # Check if spy is already on a mission
        active_mission = SpyMission.query.filter_by(
            spy_id=spy.id,
            is_completed=False
        ).first()
        
        if active_mission:
            return {"success": False, "message": "Spy is already on a mission."}
        
        # Check if spy has been discovered
        if spy.is_discovered:
            return {"success": False, "message": "This spy has been discovered and cannot conduct missions."}
        
        # Set mission duration and success chance based on type and spy skill
        mission_duration = 0
        success_base_chance = 0
        
        if mission_type == 'gather_intel':
            # Gathering intel is quicker and safer
            mission_duration = 6 + (random.randint(0, 4))  # 6-10 hours
            success_base_chance = 70 + (spy.skill_level * 5)  # 75-95% based on skill
            
        elif mission_type == 'sabotage_resources':
            # Sabotage takes longer and is riskier
            mission_duration = 12 + (random.randint(0, 8))  # 12-20 hours
            success_base_chance = 50 + (spy.skill_level * 5)  # 55-75% based on skill
            
        elif mission_type == 'sabotage_military':
            # Military sabotage is the riskiest
            mission_duration = 18 + (random.randint(0, 6))  # 18-24 hours
            success_base_chance = 40 + (spy.skill_level * 5)  # 45-65% based on skill
            
        elif mission_type == 'steal_technology':
            # Tech theft takes time but has moderate risk
            mission_duration = 24 + (random.randint(0, 12))  # 24-36 hours
            success_base_chance = 30 + (spy.skill_level * 5)  # 35-55% based on skill
            
        elif mission_type == 'monitor_diplomacy':
            # Monitoring diplomacy is safer but takes time
            mission_duration = 12 + (random.randint(0, 12))  # 12-24 hours
            success_base_chance = 60 + (spy.skill_level * 5)  # 65-85% based on skill
            
        else:
            return {"success": False, "message": "Invalid mission type."}
        
        # Adjust for counter-intelligence of target nation
        target_military = Military.query.filter_by(nation_id=spy.target_nation_id).first()
        
        if target_military:
            counter_intel = target_military.counter_intelligence
            # Reduce success chance based on target's counter-intelligence
            success_base_chance -= (counter_intel * 3)
        
        # Ensure chance stays within 10-95% range
        success_base_chance = max(10, min(95, success_base_chance))
        
        # Create the mission
        completion_date = datetime.utcnow() + timedelta(hours=mission_duration)
        
        mission = SpyMission(
            spy_id=spy.id,
            mission_type=mission_type,
            completion_date=completion_date,
            success_chance=success_base_chance
        )
        
        db.session.add(mission)
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Spy assigned to {mission_type} mission.",
            "mission_id": mission.id,
            "estimated_completion": completion_date.strftime("%Y-%m-%d %H:%M:%S"),
            "success_chance": success_base_chance
        }
    
    def check_mission_outcomes(self):
        """Check for completed missions and process results."""
        # Get all active missions for this nation's spies
        now = datetime.utcnow()
        
        # Find all active spies owned by this nation
        active_spies = DeployedSpy.query.filter_by(
            owner_nation_id=self.nation.id,
            is_active=True
        ).all()
        
        spy_ids = [spy.id for spy in active_spies]
        
        if not spy_ids:
            return {"success": True, "message": "No active spies to check.", "completed": 0}
        
        # Check for completed but unprocessed missions
        completed_missions = SpyMission.query.filter(
            SpyMission.spy_id.in_(spy_ids),
            SpyMission.completion_date <= now,
            SpyMission.is_completed == False
        ).all()
        
        if not completed_missions:
            return {"success": True, "message": "No completed missions to process.", "completed": 0}
        
        # Process each completed mission
        results = []
        for mission in completed_missions:
            result = self._process_mission_outcome(mission)
            results.append(result)
            
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Processed {len(completed_missions)} mission outcomes.",
            "completed": len(completed_missions),
            "results": results
        }
    
    def _process_mission_outcome(self, mission):
        """Process the outcome of a completed mission."""
        spy = mission.spy
        target_nation = spy.target_nation
        
        # Determine success based on mission's success chance
        is_successful = random.random() * 100 < mission.success_chance
        
        # Mark mission as completed
        mission.is_completed = True
        mission.is_successful = is_successful
        
        # Initialize result
        result = {
            "mission_id": mission.id,
            "spy_id": spy.id,
            "mission_type": mission.mission_type,
            "target_nation": target_nation.name,
            "success": is_successful,
            "effects": []
        }
        
        # Decrease cover strength (more for failed missions)
        cover_reduction = 5 if is_successful else 15
        spy.cover_strength = max(0, spy.cover_strength - cover_reduction)
        
        # Check for discovery based on remaining cover and mission risk
        discovery_threshold = 100 - spy.cover_strength
        discovery_roll = random.random() * 100
        
        # Add mission-specific risk factors
        if mission.mission_type == 'sabotage_military':
            discovery_roll += 15  # Higher risk for military sabotage
        elif mission.mission_type == 'sabotage_resources':
            discovery_roll += 10  # Medium risk for resource sabotage
        elif mission.mission_type == 'steal_technology':
            discovery_roll += 20  # Highest risk for tech theft
        
        # If spy is discovered
        if discovery_roll > discovery_threshold:
            spy.is_discovered = True
            result["discovered"] = True
            mission.diplomatic_incident = True
            result["effects"].append("Spy has been discovered!")
            
            # TODO: Handle diplomatic consequences here
            # This would involve creating a diplomatic incident record
            # and potentially affecting relations between nations
        else:
            result["discovered"] = False
        
        # Handle successful mission outcomes
        if is_successful:
            # Increase spy skill if mission was successful
            if spy.skill_level < 5:  # Max skill is 5
                spy.skill_level += 1
                result["effects"].append(f"Spy skill increased to level {spy.skill_level}")
            
            # Process based on mission type
            if mission.mission_type == 'gather_intel':
                # Generate intel report
                intel_gained = 20 + (spy.skill_level * 5)
                self.military.intel_points += intel_gained
                mission.intel_gained = intel_gained
                
                # Create detailed intel report
                self._generate_spy_report(spy, mission)
                
                result["intel_gained"] = intel_gained
                result["effects"].append(f"Gained {intel_gained} intel points")
                
            elif mission.mission_type == 'sabotage_resources':
                # Sabotage target's resources
                from models import Resource
                target_resources = Resource.query.filter_by(nation_id=target_nation.id).first()
                
                if target_resources:
                    # Choose a resource to sabotage
                    resource_types = ['raw_materials', 'food', 'energy']
                    resource_type = random.choice(resource_types)
                    
                    # Calculate amount to reduce (5-15% based on spy skill)
                    sabotage_rate = 0.05 + (spy.skill_level * 0.02)
                    current_amount = getattr(target_resources, resource_type)
                    reduced_amount = int(current_amount * sabotage_rate)
                    
                    # Apply reduction
                    setattr(target_resources, resource_type, max(0, current_amount - reduced_amount))
                    
                    result["effects"].append(f"Sabotaged {reduced_amount} {resource_type} from target nation")
                    mission.outcome_description = f"Sabotaged {reduced_amount} {resource_type}"
                
            elif mission.mission_type == 'sabotage_military':
                # Sabotage target's military units
                target_military = Military.query.filter_by(nation_id=target_nation.id).first()
                
                if target_military:
                    # Choose a military unit to sabotage
                    unit_types = ['infantry', 'tanks', 'aircraft', 'navy', 'missiles']
                    unit_type = random.choice(unit_types)
                    
                    # Calculate amount to reduce (5-15% based on spy skill)
                    sabotage_rate = 0.05 + (spy.skill_level * 0.02)
                    current_amount = getattr(target_military, unit_type)
                    reduced_amount = int(current_amount * sabotage_rate)
                    
                    # Apply reduction
                    setattr(target_military, unit_type, max(0, current_amount - reduced_amount))
                    
                    result["effects"].append(f"Sabotaged {reduced_amount} {unit_type} from target military")
                    mission.outcome_description = f"Sabotaged {reduced_amount} {unit_type}"
                
            elif mission.mission_type == 'steal_technology':
                # Steal technology
                steal_success = self._steal_technology(spy, target_nation)
                
                if steal_success:
                    result["effects"].append("Successfully stole technology blueprints")
                    mission.outcome_description = "Stole technology blueprints"
                else:
                    result["effects"].append("Failed to find valuable technology blueprints")
                    mission.outcome_description = "No valuable technology found"
                
            elif mission.mission_type == 'monitor_diplomacy':
                # Monitor diplomatic activities
                self._monitor_diplomacy(spy, target_nation)
                
                result["effects"].append("Gathered diplomatic intelligence")
                mission.outcome_description = "Diplomatic monitoring successful"
            
            # Increase intel level of spy
            spy.intel_level += 1
        else:
            # Failed mission
            mission.outcome_description = "Mission failed"
            result["effects"].append("Mission failed")
        
        # If spy is discovered and mission failed, they may be captured or escape
        if spy.is_discovered and not is_successful:
            # 50% chance of capture vs escape when discovered during a failed mission
            if random.random() < 0.5:
                # Spy is captured - lost forever
                spy.is_active = False
                result["effects"].append("Spy was captured!")
                mission.outcome_description = "Spy captured during mission"
                
                # Reduce spy count
                self.military.spies -= 1
            else:
                # Spy escapes but is compromised
                result["effects"].append("Spy was discovered but managed to escape!")
                mission.outcome_description = "Spy escaped after being discovered"
        
        return result
    
    def _generate_spy_report(self, spy, mission=None):
        """Generate an intelligence report from a spy."""
        target_nation = spy.target_nation
        
        # Determine report quality based on spy's intel level and skill
        intel_quality = min(5, 1 + (spy.intel_level // 3) + (spy.skill_level // 2))
        
        # Determine report type based on specialization or mission
        if mission:
            if mission.mission_type == 'gather_intel':
                report_type = 'general'
            elif mission.mission_type == 'sabotage_resources':
                report_type = 'economic'
            elif mission.mission_type == 'sabotage_military':
                report_type = 'military'
            elif mission.mission_type == 'steal_technology':
                report_type = 'technological'
            elif mission.mission_type == 'monitor_diplomacy':
                report_type = 'diplomatic'
            else:
                report_type = 'general'
        else:
            # Based on spy specialization
            if spy.specialization == 'general':
                report_type = 'general'
            else:
                report_type = spy.specialization
        
        # Generate report content based on type and quality
        report_content = self._generate_report_content(target_nation, report_type, intel_quality)
        
        # Create report record
        report = SpyReport(
            nation_id=self.nation.id,
            spy_id=spy.id,
            mission_id=mission.id if mission else None,
            target_nation_id=target_nation.id,
            report_type=report_type,
            intel_quality=intel_quality,
            report_content=json.dumps(report_content)
        )
        
        db.session.add(report)
        return report
    
    def _generate_report_content(self, target_nation, report_type, intel_quality):
        """Generate content for an intelligence report."""
        # Basic content available at all quality levels
        content = {
            "nation_name": target_nation.name,
            "continent": target_nation.continent,
            "intel_quality": intel_quality
        }
        
        # Add specific content based on report type and quality
        if report_type == 'military' or report_type == 'general':
            target_military = Military.query.filter_by(nation_id=target_nation.id).first()
            
            if target_military:
                # Level 1: Basic military power
                if intel_quality >= 1:
                    content["military_power"] = {
                        "offensive": int(target_military.offensive_power),
                        "defensive": int(target_military.defensive_power)
                    }
                
                # Level 2: Basic unit counts (with slight inaccuracy)
                if intel_quality >= 2:
                    accuracy = 0.7 + (intel_quality * 0.06)  # 82-100% accuracy based on quality
                    
                    def fuzz_number(number):
                        """Add slight inaccuracy to numbers based on intel quality."""
                        fuzz_factor = 1 + ((random.random() * 2 - 1) * (1 - accuracy))
                        return int(number * fuzz_factor)
                    
                    content["military_units"] = {
                        "infantry": fuzz_number(target_military.infantry),
                        "tanks": fuzz_number(target_military.tanks),
                        "aircraft": fuzz_number(target_military.aircraft)
                    }
                
                # Level 3: More unit details
                if intel_quality >= 3:
                    content["military_units"]["navy"] = fuzz_number(target_military.navy)
                    content["military_units"]["missiles"] = fuzz_number(target_military.missiles)
                
                # Level 4: Defensive structures
                if intel_quality >= 4:
                    content["defensive_structures"] = {
                        "bunkers": fuzz_number(target_military.bunkers),
                        "anti_air": fuzz_number(target_military.anti_air),
                        "coastal_defenses": fuzz_number(target_military.coastal_defenses)
                    }
                
                # Level 5: Counter-intelligence capabilities
                if intel_quality >= 5:
                    content["counter_intelligence"] = target_military.counter_intelligence
                    content["espionage_power"] = int(target_military.espionage_power)
        
        if report_type == 'economic' or report_type == 'general':
            from models import Resource
            target_resources = Resource.query.filter_by(nation_id=target_nation.id).first()
            
            if target_resources:
                # Level 1: GDP and tax rate
                if intel_quality >= 1:
                    content["economic"] = {
                        "gdp": int(target_nation.gdp),
                        "tax_rate": target_nation.tax_rate
                    }
                
                # Level 2: Basic resource amounts
                if intel_quality >= 2:
                    accuracy = 0.7 + (intel_quality * 0.06)
                    
                    def fuzz_number(number):
                        fuzz_factor = 1 + ((random.random() * 2 - 1) * (1 - accuracy))
                        return int(number * fuzz_factor)
                    
                    content["resources"] = {
                        "raw_materials": fuzz_number(target_resources.raw_materials),
                        "food": fuzz_number(target_resources.food),
                        "energy": fuzz_number(target_resources.energy)
                    }
                
                # Level 3: Production rates
                if intel_quality >= 3:
                    content["production_rates"] = {
                        "raw_materials": fuzz_number(target_resources.raw_materials_production),
                        "food": fuzz_number(target_resources.food_production),
                        "energy": fuzz_number(target_resources.energy_production)
                    }
                
                # Level 4: Currency and tech points
                if intel_quality >= 4:
                    content["resources"]["currency"] = fuzz_number(target_resources.currency)
                    content["resources"]["technology_points"] = fuzz_number(target_resources.technology_points)
                
                # Level 5: Consumption rates and population distribution
                if intel_quality >= 5:
                    content["consumption_rates"] = {
                        "raw_materials": fuzz_number(target_resources.raw_materials_consumption),
                        "food": fuzz_number(target_resources.food_consumption),
                        "energy": fuzz_number(target_resources.energy_consumption)
                    }
                    
                    content["population_distribution"] = {
                        "agriculture": target_nation.agriculture_population,
                        "industry": target_nation.industry_population,
                        "energy": target_nation.energy_population,
                        "research": target_nation.research_population,
                        "military": target_nation.military_population
                    }
        
        if report_type == 'technological' or report_type == 'general':
            # Get target nation's technologies
            technologies = Technology.query.filter_by(nation_id=target_nation.id).all()
            
            if technologies:
                # Level 1: Count of researched technologies
                if intel_quality >= 1:
                    researched_count = sum(1 for tech in technologies if tech.level > 0)
                    content["technology"] = {
                        "researched_count": researched_count,
                        "total_count": len(technologies)
                    }
                
                # Level 2: Basic research categories
                if intel_quality >= 2:
                    categories = {}
                    for tech in technologies:
                        if tech.level > 0:
                            if tech.category not in categories:
                                categories[tech.category] = 0
                            categories[tech.category] += 1
                    
                    content["technology"]["categories"] = categories
                
                # Level 3: Some specific technology names
                if intel_quality >= 3:
                    researched_techs = [tech for tech in technologies if tech.level > 0]
                    sample_size = min(3 + intel_quality, len(researched_techs))
                    sample_techs = random.sample(researched_techs, sample_size) if researched_techs else []
                    
                    content["technology"]["sample_techs"] = [
                        {"name": tech.name, "level": tech.level} for tech in sample_techs
                    ]
                
                # Level 4: Current research
                if intel_quality >= 4:
                    researching_techs = [tech for tech in technologies if tech.researching]
                    if researching_techs:
                        content["technology"]["current_research"] = [
                            {
                                "name": tech.name,
                                "progress": tech.research_points_current / tech.research_points_required if tech.research_points_required > 0 else 0,
                                "estimated_completion": tech.estimated_completion.strftime("%Y-%m-%d %H:%M:%S") if tech.estimated_completion else None
                            } for tech in researching_techs
                        ]
                
                # Level 5: Detailed tech tree with levels
                if intel_quality >= 5:
                    content["technology"]["tech_tree"] = [
                        {
                            "name": tech.name,
                            "category": tech.category,
                            "level": tech.level,
                            "max_level": tech.max_level,
                            "description": tech.description
                        } for tech in technologies if tech.level > 0
                    ]
        
        if report_type == 'diplomatic' or report_type == 'general':
            # Level 1: Basic diplomatic status (wars and alliances count)
            if intel_quality >= 1:
                from models import War, Alliance
                
                active_wars = War.query.filter(
                    (War.aggressor_id == target_nation.id) | (War.defender_id == target_nation.id),
                    War.is_active == True
                ).count()
                
                alliances = Alliance.query.filter(
                    (Alliance.nation1_id == target_nation.id) | (Alliance.nation2_id == target_nation.id),
                    Alliance.is_active == True
                ).count()
                
                content["diplomacy"] = {
                    "active_wars": active_wars,
                    "alliances": alliances
                }
            
            # Level 2: War details
            if intel_quality >= 2:
                wars = War.query.filter(
                    (War.aggressor_id == target_nation.id) | (War.defender_id == target_nation.id),
                    War.is_active == True
                ).all()
                
                if wars:
                    content["diplomacy"]["wars"] = []
                    for war in wars:
                        opponent_id = war.defender_id if war.aggressor_id == target_nation.id else war.aggressor_id
                        opponent = Nation.query.get(opponent_id)
                        
                        war_info = {
                            "opponent": opponent.name if opponent else "Unknown",
                            "is_aggressor": war.aggressor_id == target_nation.id,
                            "start_date": war.start_date.strftime("%Y-%m-%d")
                        }
                        
                        content["diplomacy"]["wars"].append(war_info)
            
            # Level 3: Alliance details
            if intel_quality >= 3:
                alliances = Alliance.query.filter(
                    (Alliance.nation1_id == target_nation.id) | (Alliance.nation2_id == target_nation.id),
                    Alliance.is_active == True
                ).all()
                
                if alliances:
                    content["diplomacy"]["alliances"] = []
                    for alliance in alliances:
                        ally_id = alliance.nation2_id if alliance.nation1_id == target_nation.id else alliance.nation1_id
                        ally = Nation.query.get(ally_id)
                        
                        alliance_info = {
                            "ally": ally.name if ally else "Unknown",
                            "formed_date": alliance.formed_date.strftime("%Y-%m-%d")
                        }
                        
                        content["diplomacy"]["alliances"].append(alliance_info)
            
            # Level 4: Transit rights
            if intel_quality >= 4:
                from models import TransitRights
                
                transit_rights = TransitRights.query.filter(
                    (TransitRights.grantor_id == target_nation.id) | (TransitRights.receiver_id == target_nation.id),
                    TransitRights.is_active == True
                ).all()
                
                if transit_rights:
                    content["diplomacy"]["transit_rights"] = []
                    for tr in transit_rights:
                        other_id = tr.receiver_id if tr.grantor_id == target_nation.id else tr.grantor_id
                        other_nation = Nation.query.get(other_id)
                        
                        tr_info = {
                            "nation": other_nation.name if other_nation else "Unknown",
                            "is_grantor": tr.grantor_id == target_nation.id,
                            "granted_date": tr.granted_date.strftime("%Y-%m-%d")
                        }
                        
                        content["diplomacy"]["transit_rights"].append(tr_info)
            
            # Level 5: War casualties and peace proposals
            if intel_quality >= 5 and "wars" in content.get("diplomacy", {}):
                wars = War.query.filter(
                    (War.aggressor_id == target_nation.id) | (War.defender_id == target_nation.id),
                    War.is_active == True
                ).all()
                
                for i, war in enumerate(wars):
                    if war.aggressor_id == target_nation.id:
                        casualties = war.aggressor_casualties
                    else:
                        casualties = war.defender_casualties
                    
                    content["diplomacy"]["wars"][i]["casualties"] = casualties
                    content["diplomacy"]["wars"][i]["peace_proposed"] = war.peace_proposed
        
        return content
    
    def _steal_technology(self, spy, target_nation):
        """Attempt to steal technology from target nation."""
        # Get a random researched technology from target
        researched_techs = Technology.query.filter(
            Technology.nation_id == target_nation.id,
            Technology.level > 0
        ).all()
        
        if not researched_techs:
            return False  # No technologies to steal
        
        # Pick a random technology
        stolen_tech = random.choice(researched_techs)
        
        # Check if we already have this technology
        our_tech = Technology.query.filter_by(
            nation_id=self.nation.id,
            name=stolen_tech.name
        ).first()
        
        if our_tech and our_tech.level >= stolen_tech.level:
            # We already have this tech at same or higher level
            return False
        
        # Boost our research on this technology
        if our_tech:
            # If we're researching it, add a significant boost
            if our_tech.researching:
                our_tech.research_points_current += our_tech.research_points_required * 0.5
                
                # If this completes the research, level up the tech
                if our_tech.research_points_current >= our_tech.research_points_required:
                    our_tech.level += 1
                    our_tech.researching = False
                    our_tech.research_points_current = 0
            else:
                # If we're not researching it, add tech points to our nation
                from models import Resource
                resources = Resource.query.filter_by(nation_id=self.nation.id).first()
                if resources:
                    # Add significant tech points
                    resources.technology_points += 250 * stolen_tech.level
        else:
            # We don't have this tech at all - add tech points
            from models import Resource
            resources = Resource.query.filter_by(nation_id=self.nation.id).first()
            if resources:
                resources.technology_points += 500 * stolen_tech.level
        
        return True
    
    def _monitor_diplomacy(self, spy, target_nation):
        """Monitor the diplomatic activities of the target nation."""
        from models import War, Alliance, TransitRights
        
        # Create a diplomatic report regardless of whether there's activity
        self._generate_spy_report(spy, None)
        
        # Also gain intel points
        intel_gained = 15 + (spy.skill_level * 3)
        self.military.intel_points += intel_gained
        
        return True
    
    def improve_counter_intelligence(self, levels=1):
        """Improve counter-intelligence capabilities."""
        # Cost increases with current level
        base_cost = 5000  # Base currency cost
        tech_cost = 200   # Base technology points cost
        
        current_level = self.military.counter_intelligence
        total_currency_cost = base_cost * levels * (current_level + 1)
        total_tech_cost = tech_cost * levels
        
        # Check resources
        from models import Resource
        resources = Resource.query.filter_by(nation_id=self.nation.id).first()
        
        if not resources:
            return {"success": False, "message": "No resources found for your nation."}
        
        if resources.currency < total_currency_cost:
            return {"success": False, "message": f"Not enough currency. Need {total_currency_cost}."}
        
        if resources.technology_points < total_tech_cost:
            return {"success": False, "message": f"Not enough technology points. Need {total_tech_cost}."}
        
        # Deduct resources
        resources.currency -= total_currency_cost
        resources.technology_points -= total_tech_cost
        
        # Improve counter-intelligence
        self.military.counter_intelligence += levels
        
        # Update espionage power
        self.update_espionage_power()
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Counter-intelligence improved to level {self.military.counter_intelligence}.",
            "counter_intelligence": self.military.counter_intelligence
        }
    
    def update_espionage_power(self):
        """Update the nation's espionage power based on spies and counter-intelligence."""
        # Get count of active spies
        active_spy_count = DeployedSpy.query.filter_by(
            owner_nation_id=self.nation.id,
            is_active=True
        ).count()
        
        # Calculate average skill level of spies
        active_spies = DeployedSpy.query.filter_by(
            owner_nation_id=self.nation.id,
            is_active=True
        ).all()
        
        avg_skill = 1
        if active_spies:
            avg_skill = sum(spy.skill_level for spy in active_spies) / len(active_spies)
        
        # Calculate espionage power
        spy_power = (self.military.spies * 50) + (active_spy_count * 100 * avg_skill)
        counter_intel_power = self.military.counter_intelligence * 150
        
        total_power = spy_power + counter_intel_power
        
        # Apply technology bonuses if any
        tech_bonus = 1.0
        technologies = Technology.query.filter_by(nation_id=self.nation.id).all()
        for tech in technologies:
            if tech.level > 0 and tech.espionage_bonus > 0:
                tech_bonus += (tech.espionage_bonus * tech.level * 0.1)
        
        total_power *= tech_bonus
        
        # Update the military record
        self.military.espionage_power = total_power
        
        return total_power
    
    def get_intel_reports(self, target_nation_id=None, report_type=None, limit=10):
        """Get intelligence reports for this nation."""
        query = SpyReport.query.filter_by(nation_id=self.nation.id)
        
        if target_nation_id:
            query = query.filter_by(target_nation_id=target_nation_id)
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        
        # Get the most recent reports
        reports = query.order_by(SpyReport.report_date.desc()).limit(limit).all()
        
        # Process reports for display
        processed_reports = []
        for report in reports:
            # Parse the JSON content
            content = json.loads(report.report_content)
            
            # Get target nation name
            target_nation = Nation.query.get(report.target_nation_id)
            target_name = target_nation.name if target_nation else "Unknown"
            
            # Process report
            processed_report = {
                "id": report.id,
                "target_nation": target_name,
                "report_date": report.report_date.strftime("%Y-%m-%d %H:%M"),
                "report_type": report.report_type,
                "intel_quality": report.intel_quality,
                "content": content
            }
            
            processed_reports.append(processed_report)
        
        return processed_reports
    
    def run_counter_intelligence_sweep(self):
        """Actively search for foreign spies in your nation."""
        # Cost of running a sweep
        currency_cost = 2000
        energy_cost = 50
        
        # Check resources
        from models import Resource
        resources = Resource.query.filter_by(nation_id=self.nation.id).first()
        
        if not resources:
            return {"success": False, "message": "No resources found for your nation."}
        
        if resources.currency < currency_cost:
            return {"success": False, "message": f"Not enough currency. Need {currency_cost}."}
        
        if resources.energy < energy_cost:
            return {"success": False, "message": f"Not enough energy. Need {energy_cost}."}
        
        # Deduct resources
        resources.currency -= currency_cost
        resources.energy -= energy_cost
        
        # Find foreign spies in our nation
        foreign_spies = DeployedSpy.query.filter_by(
            target_nation_id=self.nation.id,
            is_active=True,
            is_discovered=False
        ).all()
        
        if not foreign_spies:
            return {
                "success": True,
                "message": "Counter-intelligence sweep completed. No foreign spies detected.",
                "spies_found": 0
            }
        
        # Check each spy for discovery
        discovered_spies = []
        for spy in foreign_spies:
            # Calculate discovery chance based on our counter-intel vs spy's cover
            counter_intel_bonus = self.military.counter_intelligence * 5
            cover_strength = spy.cover_strength
            
            discovery_chance = 20 + counter_intel_bonus - (cover_strength * 0.2)
            discovery_chance = max(5, min(95, discovery_chance))  # Clamp between 5-95%
            
            # Roll for discovery
            if random.random() * 100 < discovery_chance:
                # Spy discovered!
                spy.is_discovered = True
                discovered_spies.append(spy)
                
                # Create a diplomatic incident
                # This would be implemented in a real diplomatic system
        
        db.session.commit()
        
        if discovered_spies:
            spy_nations = {}
            for spy in discovered_spies:
                owner = Nation.query.get(spy.owner_nation_id)
                if owner:
                    if owner.name not in spy_nations:
                        spy_nations[owner.name] = 0
                    spy_nations[owner.name] += 1
            
            nations_str = ", ".join([f"{count} from {nation}" for nation, count in spy_nations.items()])
            
            return {
                "success": True,
                "message": f"Counter-intelligence sweep successful! Discovered {len(discovered_spies)} foreign spies ({nations_str}).",
                "spies_found": len(discovered_spies),
                "spy_nations": spy_nations
            }
        else:
            return {
                "success": True,
                "message": "Counter-intelligence sweep completed. No foreign spies detected.",
                "spies_found": 0
            }


def check_active_missions():
    """Background task to check for completed missions across all nations."""
    with current_app.app_context():
        try:
            # Get all nations
            nations = Nation.query.all()
            total_completed = 0
            
            for nation in nations:
                try:
                    # Process missions for this nation
                    espionage_system = AdvancedEspionageSystem(nation)
                    result = espionage_system.check_mission_outcomes()
                    
                    if result["completed"] > 0:
                        total_completed += result["completed"]
                        logger.info(f"Processed {result['completed']} missions for {nation.name}")
                except Exception as e:
                    logger.error(f"Error processing missions for nation {nation.id}: {str(e)}")
            
            if total_completed > 0:
                logger.info(f"Completed {total_completed} spy missions across all nations")
            
            return {"success": True, "total_completed": total_completed}
        except Exception as e:
            logger.error(f"Error in check_active_missions: {str(e)}")
            return {"success": False, "error": str(e)}


def update_spy_cover_and_intel():
    """Background task to update spy cover and intel levels for all deployed spies."""
    with current_app.app_context():
        try:
            # Get all active deployed spies
            active_spies = DeployedSpy.query.filter_by(is_active=True).all()
            
            for spy in active_spies:
                try:
                    # Decrease cover over time (more if spy has been discovered)
                    cover_decay = 0.5 if not spy.is_discovered else 2.0
                    spy.cover_strength = max(0, spy.cover_strength - cover_decay)
                    
                    # If cover reaches 0, spy is automatically discovered
                    if spy.cover_strength <= 0 and not spy.is_discovered:
                        spy.is_discovered = True
                        # TODO: Create diplomatic incident
                    
                    # Increase intel level over time (if not discovered)
                    if not spy.is_discovered:
                        # Intel gain is based on skill level
                        intel_gain = 0.2 * spy.skill_level
                        spy.intel_level += intel_gain
                        
                        # Generate periodic reports from long-term spies
                        # Every 14 days (336 hours) of deployment, generate a report
                        hours_deployed = (datetime.utcnow() - spy.deployment_date).total_seconds() / 3600
                        if hours_deployed > 0 and hours_deployed % 336 < 1:  # Within 1 hour of the 14-day mark
                            try:
                                # Get the spy's nation
                                nation = Nation.query.get(spy.owner_nation_id)
                                if nation:
                                    espionage_system = AdvancedEspionageSystem(nation)
                                    # Generate a report
                                    espionage_system._generate_spy_report(spy)
                                    logger.info(f"Generated periodic report for spy {spy.id} in {spy.target_nation_id}")
                            except Exception as e:
                                logger.error(f"Error generating periodic report for spy {spy.id}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error updating spy {spy.id}: {str(e)}")
            
            db.session.commit()
            return {"success": True, "spies_updated": len(active_spies)}
        except Exception as e:
            logger.error(f"Error in update_spy_cover_and_intel: {str(e)}")
            db.session.rollback()
            return {"success": False, "error": str(e)}