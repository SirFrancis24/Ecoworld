"""
Espionage handler for managing spy operations and intelligence gathering.
"""
from datetime import datetime, timedelta
from app import db
from models import Nation, Military, Resource, Technology
from data.espionage import ESPIONAGE_MISSIONS
import random
import math

class EspionageManager:
    """Class for managing a nation's espionage activities."""
    def __init__(self, nation):
        self.nation = nation
        self.military = Military.query.filter_by(nation_id=nation.id).first()
        self.resources = Resource.query.filter_by(nation_id=nation.id).first()
        
        # Current missions
        self.active_missions = getattr(self.military, "active_espionage_missions", [])
        
        # Past missions
        self.completed_missions = getattr(self.military, "completed_espionage_missions", [])
        
        # Intel points (a measure of intelligence gathered)
        self.intel_points = getattr(self.military, "intel_points", 0)
        
        # Counter-intelligence level
        self.counter_intel = getattr(self.military, "counter_intelligence", 0)
    
    def get_available_missions(self):
        """Get missions available based on technology and resources."""
        available_missions = []
        
        for mission in ESPIONAGE_MISSIONS:
            # Check requirements
            meets_requirements = True
            
            # Check technology requirements
            for tech_id in mission["requirements"].get("technologies", []):
                # In a real implementation, check if the nation has the required technology
                # For now, just assume they have all required technologies
                pass
            
            # Check resource requirements
            for resource_type, amount in mission["requirements"].get("resources", {}).items():
                if not hasattr(self.resources, resource_type):
                    meets_requirements = False
                    break
                
                if getattr(self.resources, resource_type) < amount:
                    meets_requirements = False
                    break
            
            # Check spy requirements
            if "spies" in mission["requirements"]:
                required_spies = mission["requirements"]["spies"]
                available_spies = self.military.spies if hasattr(self.military, "spies") else 0
                
                # Exclude spies already on missions
                spies_on_missions = sum(mission.get("spies_assigned", 0) for mission in self.active_missions)
                available_spies -= spies_on_missions
                
                if available_spies < required_spies:
                    meets_requirements = False
            
            # Check other special requirements
            if "counter_intelligence" in mission["requirements"]:
                required_counter_intel = mission["requirements"]["counter_intelligence"]
                if self.counter_intel < required_counter_intel:
                    meets_requirements = False
            
            # If all requirements met, add to available missions
            if meets_requirements:
                available_missions.append(mission)
        
        return available_missions
    
    def launch_espionage_mission(self, mission_id, target_nation_id, spies_count=None):
        """Launch an espionage mission against another nation."""
        # Validate mission exists
        mission = next((m for m in ESPIONAGE_MISSIONS if m["id"] == mission_id), None)
        if not mission:
            return {"success": False, "message": "Invalid espionage mission."}
        
        # Validate target nation exists
        target_nation = Nation.query.get(target_nation_id)
        if not target_nation:
            return {"success": False, "message": "Target nation not found."}
        
        # Validate target is not self
        if target_nation.id == self.nation.id:
            return {"success": False, "message": "Cannot spy on your own nation."}
        
        # Check requirements
        # Technology requirements
        for tech_id in mission["requirements"].get("technologies", []):
            # In a real implementation, check if the nation has the technology
            pass
        
        # Resource requirements
        for resource_type, amount in mission["requirements"].get("resources", {}).items():
            if not hasattr(self.resources, resource_type):
                return {"success": False, "message": f"Missing resource type: {resource_type}"}
            
            current_amount = getattr(self.resources, resource_type)
            if current_amount < amount:
                return {"success": False, "message": f"Not enough {resource_type}. Need {amount}, have {current_amount}."}
        
        # Spy requirements
        required_spies = mission["requirements"].get("spies", 0)
        if spies_count is None:
            spies_count = required_spies
        
        if spies_count < required_spies:
            return {"success": False, "message": f"Need at least {required_spies} spies for this mission."}
        
        available_spies = self.military.spies if hasattr(self.military, "spies") else 0
        spies_on_missions = sum(mission.get("spies_assigned", 0) for mission in self.active_missions)
        available_spies -= spies_on_missions
        
        if available_spies < spies_count:
            return {"success": False, "message": f"Not enough available spies. Need {spies_count}, have {available_spies}."}
        
        # Other special requirements
        if "counter_intelligence" in mission["requirements"]:
            required_counter_intel = mission["requirements"]["counter_intelligence"]
            if self.counter_intel < required_counter_intel:
                return {"success": False, "message": f"Need counter-intelligence level {required_counter_intel}."}
        
        # Preparation time
        prep_time = mission["requirements"].get("preparation_time", 0)
        mission_duration = random.randint(1, 3)  # 1-3 days based on mission complexity
        completion_date = datetime.utcnow() + timedelta(days=prep_time + mission_duration)
        
        # Deduct resources
        for resource_type, amount in mission["requirements"].get("resources", {}).items():
            current_amount = getattr(self.resources, resource_type)
            setattr(self.resources, resource_type, current_amount - amount)
        
        # Create mission record
        new_mission = {
            "id": mission["id"],
            "name": mission["name"],
            "target_nation_id": target_nation_id,
            "target_nation_name": target_nation.name,
            "spies_assigned": spies_count,
            "start_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "completion_date": completion_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "in_progress",
            "success_chance": self.calculate_success_chance(mission, target_nation, spies_count)
        }
        
        # Add to active missions
        if not hasattr(self.military, "active_espionage_missions") or self.military.active_espionage_missions is None:
            self.military.active_espionage_missions = []
        
        self.military.active_espionage_missions.append(new_mission)
        self.active_missions = self.military.active_espionage_missions
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Launched espionage mission: {mission['name']} against {target_nation.name}.",
            "completion_date": completion_date.strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_success_chance": new_mission["success_chance"]
        }
    
    def calculate_success_chance(self, mission, target_nation, spies_count):
        """Calculate the chance of success for a mission based on various factors."""
        # Base success rate from mission
        base_chance = mission["success_rate_base"]
        
        # Target's counter-intelligence
        target_military = Military.query.filter_by(nation_id=target_nation.id).first()
        target_counter_intel = target_military.counter_intelligence if target_military else 0
        
        # Counter-intelligence factor (higher target counter-intel reduces success)
        counter_intel_factor = 1.0 - (target_counter_intel * 0.05)  # Each point reduces success by 5%
        counter_intel_factor = max(0.2, counter_intel_factor)  # Minimum 20% of original chance
        
        # Spy count factor (more spies increase success)
        required_spies = mission["requirements"].get("spies", 1)
        spy_factor = min(2.0, math.sqrt(spies_count / required_spies))  # Diminishing returns
        
        # Technology advantage (simplified)
        tech_factor = 1.0
        
        # Calculate total chance
        success_chance = base_chance * counter_intel_factor * spy_factor * tech_factor
        
        # Limit to 0-95% range (always some chance of failure)
        success_chance = min(0.95, max(0.05, success_chance))
        
        return round(success_chance * 100, 1)  # Convert to percentage with 1 decimal
    
    def check_mission_outcomes(self):
        """Check outcomes for completed missions and process results."""
        if not hasattr(self.military, "active_espionage_missions") or not self.military.active_espionage_missions:
            return {"success": True, "message": "No active missions to check.", "completed": 0}
        
        now = datetime.utcnow()
        completed_count = 0
        results = []
        
        still_active = []
        for mission in self.military.active_espionage_missions:
            # Check if mission is complete
            completion_date = datetime.strptime(mission["completion_date"], "%Y-%m-%d %H:%M:%S")
            if now >= completion_date:
                # Process mission outcome
                result = self.process_mission_outcome(mission)
                results.append(result)
                completed_count += 1
                
                # Add to completed missions
                if not hasattr(self.military, "completed_espionage_missions") or self.military.completed_espionage_missions is None:
                    self.military.completed_espionage_missions = []
                
                self.military.completed_espionage_missions.append({
                    **mission,
                    "outcome": result
                })
            else:
                # Mission still in progress
                still_active.append(mission)
        
        # Update active missions
        self.military.active_espionage_missions = still_active
        self.active_missions = still_active
        self.completed_missions = self.military.completed_espionage_missions
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Processed {completed_count} completed missions.",
            "completed": completed_count,
            "results": results
        }
    
    def process_mission_outcome(self, mission):
        """Process the outcome of a completed mission."""
        # Get mission details
        mission_data = next((m for m in ESPIONAGE_MISSIONS if m["id"] == mission["id"]), None)
        if not mission_data:
            return {"success": False, "message": "Invalid mission data."}
        
        # Get target nation
        target_nation = Nation.query.get(mission["target_nation_id"])
        if not target_nation:
            return {"success": False, "message": "Target nation not found."}
        
        # Determine success or failure
        success_chance = mission["success_chance"] / 100  # Convert from percentage
        success = random.random() < success_chance
        
        result = {
            "mission_id": mission["id"],
            "mission_name": mission["name"],
            "target_nation": target_nation.name,
            "success": success,
            "intel_gained": 0,
            "effects": [],
            "spies_lost": 0
        }
        
        if success:
            # Mission succeeded
            # Award intel points
            intel_gained = mission_data["rewards"].get("intel_points", 0)
            self.intel_points += intel_gained
            result["intel_gained"] = intel_gained
            
            # Apply mission-specific rewards
            if mission["id"] == 1:  # Intelligence Gathering
                # Basic stats about target nation
                result["target_info"] = {
                    "gdp": target_nation.gdp,
                    "population": target_nation.total_population,
                    "military_rank": target_nation.military_rank
                }
                result["effects"].append("Gained basic information about target nation")
            
            elif mission["id"] == 2:  # Economic Espionage
                # Economic boost and information
                result["target_info"] = {
                    "gdp": target_nation.gdp,
                    "tax_rate": target_nation.tax_rate,
                    "inflation_rate": getattr(target_nation, "inflation_rate", 0.02),
                    "resources": self.get_target_resources(target_nation)
                }
                
                # Technology boost
                self.resources.technology_points += 50
                result["effects"].append("Gained detailed economic information")
                result["effects"].append("Gained 50 technology points")
                
                # Currency gain
                currency_gain = mission_data["rewards"].get("currency", 0)
                self.resources.currency += currency_gain
                result["effects"].append(f"Gained {currency_gain} currency")
            
            elif mission["id"] == 3:  # Military Intelligence
                # Military information
                target_military = Military.query.filter_by(nation_id=target_nation.id).first()
                if target_military:
                    result["target_info"] = {
                        "infantry": target_military.infantry,
                        "tanks": target_military.tanks,
                        "aircraft": target_military.aircraft,
                        "navy": target_military.navy,
                        "missiles": target_military.missiles,
                        "offensive_power": target_military.offensive_power,
                        "defensive_power": target_military.defensive_power
                    }
                
                # Military advantage
                military_advantage = mission_data["rewards"].get("military_advantage", 0)
                result["military_advantage"] = military_advantage
                result["effects"].append("Gained detailed military intelligence")
                result["effects"].append(f"Gained {military_advantage * 100}% military advantage against this nation")
            
            elif mission["id"] == 4:  # Technology Theft
                # Technology points and boost
                tech_points = mission_data["rewards"].get("technology_points", 0)
                self.resources.technology_points += tech_points
                
                # Identify a random technology to boost
                techs = Technology.query.filter_by(nation_id=self.nation.id, level__gt=0).all()
                if techs:
                    tech = random.choice(techs)
                    tech_boost = mission_data["rewards"].get("specific_technology_boost", 0)
                    result["technology_boosted"] = tech.name
                    result["technology_boost"] = tech_boost * 100  # Convert to percentage
                    result["effects"].append(f"Gained {tech_points} technology points")
                    result["effects"].append(f"Boosted research on {tech.name} by {tech_boost * 100}%")
            
            elif mission["id"] == 5:  # Sabotage Resources
                # Reduce target resources
                target_resources = Resource.query.filter_by(nation_id=target_nation.id).first()
                if target_resources:
                    reduction = mission_data["rewards"].get("target_resource_reduction", 0)
                    
                    # Choose a random resource to sabotage
                    resource_types = ["raw_materials", "food", "energy"]
                    resource_type = random.choice(resource_types)
                    
                    current = getattr(target_resources, resource_type)
                    new_value = current * (1 - reduction)
                    setattr(target_resources, resource_type, new_value)
                    
                    result["sabotaged_resource"] = resource_type
                    result["reduction_percent"] = reduction * 100  # Convert to percentage
                    result["effects"].append(f"Reduced target's {resource_type} by {reduction * 100}%")
            
            # More mission types would be handled here
        
        else:
            # Mission failed
            result["message"] = "Mission failed"
            
            # Determine spy losses (higher risk missions have higher chance of losing spies)
            risk_level = mission_data["risk_level"]
            spy_capture_risk = mission_data["penalties"].get("spy_capture_risk", risk_level * 0.1)
            
            # For each spy, check if captured
            spies_assigned = mission["spies_assigned"]
            spies_lost = 0
            for _ in range(spies_assigned):
                if random.random() < spy_capture_risk:
                    spies_lost += 1
            
            # Apply spy losses
            if spies_lost > 0:
                self.military.spies -= spies_lost
                result["spies_lost"] = spies_lost
                result["effects"].append(f"Lost {spies_lost} spies in the operation")
            
            # Diplomatic penalty if caught (higher risk missions more likely to cause diplomatic incident)
            caught_chance = risk_level * 0.2
            if random.random() < caught_chance:
                # In a real implementation, this would affect diplomatic relations
                diplomatic_penalty = mission_data["penalties"].get("diplomatic_penalty", 0)
                result["diplomatic_penalty"] = diplomatic_penalty
                result["effects"].append(f"Operation was detected, causing diplomatic tension")
                
                # Possible counter-espionage alert
                if mission_data["penalties"].get("counter_espionage_alert", False):
                    # Target nation becomes more vigilant
                    if target_military:
                        target_military.counter_intelligence += 1
                        result["effects"].append("Target nation has increased counter-intelligence")
        
        # Update military's intel points
        self.military.intel_points = self.intel_points
        
        # Commit changes
        db.session.commit()
        
        return result
    
    def get_target_resources(self, target_nation):
        """Get resource information about a target nation."""
        target_resources = Resource.query.filter_by(nation_id=target_nation.id).first()
        if not target_resources:
            return {}
        
        return {
            "raw_materials": target_resources.raw_materials,
            "food": target_resources.food,
            "energy": target_resources.energy,
            "technology_points": target_resources.technology_points,
            "currency": target_resources.currency
        }
    
    def get_mission_history(self):
        """Get history of completed missions."""
        if not hasattr(self.military, "completed_espionage_missions") or not self.military.completed_espionage_missions:
            return []
        
        # Sort by completion date (newest first)
        sorted_missions = sorted(
            self.military.completed_espionage_missions,
            key=lambda m: datetime.strptime(m["completion_date"], "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        return sorted_missions
    
    def train_spies(self, count=1):
        """Train new spies."""
        # Check if military has spies attribute
        if not hasattr(self.military, "spies"):
            self.military.spies = 0
        
        # Calculate cost per spy
        cost_per_spy = 5000  # Currency
        total_cost = cost_per_spy * count
        
        # Check if nation has enough currency
        if self.resources.currency < total_cost:
            return {"success": False, "message": f"Not enough currency. Need {total_cost}."}
        
        # Deduct cost
        self.resources.currency -= total_cost
        
        # Add spies
        self.military.spies += count
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Trained {count} new spies.",
            "total_spies": self.military.spies
        }
    
    def improve_counter_intelligence(self, levels=1):
        """Improve counter-intelligence capabilities."""
        # Check if military has counter_intelligence attribute
        if not hasattr(self.military, "counter_intelligence"):
            self.military.counter_intelligence = 0
        
        # Calculate cost per level
        current_level = self.military.counter_intelligence
        cost_per_level = 10000 * (1 + current_level * 0.5)  # Increasing cost
        total_cost = sum(cost_per_level * (1 + i * 0.5) for i in range(levels))
        
        # Check if nation has enough currency
        if self.resources.currency < total_cost:
            return {"success": False, "message": f"Not enough currency. Need {total_cost}."}
        
        # Deduct cost
        self.resources.currency -= total_cost
        
        # Improve counter-intelligence
        self.military.counter_intelligence += levels
        
        # Update counter_intel
        self.counter_intel = self.military.counter_intelligence
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Improved counter-intelligence by {levels} levels.",
            "new_level": self.military.counter_intelligence
        }