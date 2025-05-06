"""
Economy handler for managing economic aspects, including inflation,
population happiness, and economic events.
"""
from datetime import datetime, timedelta
from app import db
from models import Nation, Resource
from data.economy import (
    ECONOMIC_POLICIES, 
    INFLATION_FACTORS,
    INFLATION_EFFECTS,
    POPULATION_HAPPINESS_FACTORS,
    HAPPINESS_EFFECTS,
    ECONOMIC_EVENTS
)
import random
import math

class EconomyManager:
    """Class for managing a nation's economy."""
    def __init__(self, nation):
        self.nation = nation
        self.resources = Resource.query.filter_by(nation_id=nation.id).first()
        
        # Current economic policy (default to Mixed Economy if none set)
        self.policy = next((p for p in ECONOMIC_POLICIES if p["id"] == getattr(nation, "economic_policy_id", 2)), ECONOMIC_POLICIES[1])
        
        # Calculate current inflation
        self.inflation_rate = self.calculate_inflation_rate()
        
        # Calculate population happiness
        self.happiness = self.calculate_happiness()
        
        # Active economic events
        self.active_events = getattr(nation, "economic_events", [])
    
    def calculate_inflation_rate(self):
        """Calculate current inflation rate based on various factors."""
        # Base rate (from policy)
        base_rate = self.policy["effects"].get("inflation_rate", 0.02)
        
        # Money supply factor
        money_growth_factor = 0
        if hasattr(self.resources, "currency_production") and hasattr(self.resources, "currency"):
            # Annual growth rate of currency
            annual_production = self.resources.currency_production * 365
            money_growth_rate = annual_production / max(1, self.resources.currency)
            
            # Effect depends on how far from optimal range
            optimal_min, optimal_max = INFLATION_FACTORS["money_supply_growth"]["optimal_range"]
            if money_growth_rate < optimal_min:
                # Below optimal - deflationary pressure
                money_growth_factor = (optimal_min - money_growth_rate) * -0.5
            elif money_growth_rate > optimal_max:
                # Above optimal - inflationary pressure
                money_growth_factor = (money_growth_rate - optimal_max) * 1.0
                
                # Extra penalty if above danger threshold
                danger = INFLATION_FACTORS["money_supply_growth"]["danger_threshold"]
                if money_growth_rate > danger:
                    money_growth_factor *= 1.5
        
        # Resource scarcity factor
        resource_factor = 0
        for resource_type in INFLATION_FACTORS["resource_scarcity"]["affected_by"]:
            if hasattr(self.resources, resource_type) and hasattr(self.resources, f"{resource_type}_production"):
                # Days of supply
                daily_production = getattr(self.resources, f"{resource_type}_production")
                current_amount = getattr(self.resources, resource_type)
                days_supply = current_amount / max(1, daily_production)
                
                # Scarcity increases inflation (less than 30 days supply)
                if days_supply < 30:
                    resource_factor += (30 - days_supply) * 0.001
        
        # Production capacity factor (simplified)
        production_factor = 0
        if hasattr(self.nation, "industry_population"):
            # Higher industrial capacity reduces inflation
            production_factor = -0.01 * (self.nation.industry_population / 10)
        
        # Combine factors with appropriate weights
        inflation_rate = base_rate
        inflation_rate += money_growth_factor * INFLATION_FACTORS["money_supply_growth"]["base_effect"]
        inflation_rate += resource_factor * INFLATION_FACTORS["resource_scarcity"]["base_effect"]
        inflation_rate += production_factor * INFLATION_FACTORS["production_capacity"]["base_effect"]
        
        # Apply active event modifiers
        for event in self.active_events:
            event_data = next((e for e in ECONOMIC_EVENTS if e["id"] == event["id"]), None)
            if event_data and "inflation_rate" in event_data.get("effects", {}):
                inflation_rate += event_data["effects"]["inflation_rate"]
        
        # Ensure inflation is within reasonable bounds (-5% to 100%)
        inflation_rate = max(-0.05, min(1.0, inflation_rate))
        
        return inflation_rate
    
    def get_inflation_effects(self):
        """Get the effects of current inflation on the economy."""
        # Determine inflation category
        for category, info in INFLATION_EFFECTS.items():
            min_val, max_val = info["range"]
            if min_val <= self.inflation_rate < max_val:
                return {
                    "category": category,
                    "description": info["description"],
                    "effects": info["effects"],
                    "rate": self.inflation_rate,
                    "flavor_text": info["flavor_text"]
                }
        
        # Default to moderate if no category matches
        return {
            "category": "moderate",
            "description": INFLATION_EFFECTS["moderate"]["description"],
            "effects": INFLATION_EFFECTS["moderate"]["effects"],
            "rate": self.inflation_rate,
            "flavor_text": INFLATION_EFFECTS["moderate"]["flavor_text"]
        }
    
    def calculate_happiness(self):
        """Calculate population happiness based on various factors."""
        # Initialize factor scores
        factor_scores = {}
        for factor, info in POPULATION_HAPPINESS_FACTORS.items():
            factor_scores[factor] = 0.5  # Default to middle (0.5 out of 1.0)
        
        # Economic prosperity
        if hasattr(self.nation, "gdp") and hasattr(self.nation, "total_population"):
            gdp_per_capita = self.nation.gdp / max(1, self.nation.total_population)
            # Scale appropriately - example assumes 50,000 is excellent GDP per capita
            factor_scores["economic_prosperity"] = min(1.0, gdp_per_capita / 50000)
        
        # Public services (based on tax rate)
        if hasattr(self.nation, "tax_rate"):
            # Higher tax rate assumed to fund better services
            factor_scores["public_services"] = min(1.0, self.nation.tax_rate / 35)
        
        # Inflation factor
        if self.inflation_rate < 0.03:
            # Low inflation is good
            factor_scores["economic_prosperity"] *= 1.1
        elif self.inflation_rate > 0.1:
            # High inflation is bad
            factor_scores["economic_prosperity"] *= max(0.5, 1.0 - (self.inflation_rate * 2))
        
        # War effect on security situation
        if hasattr(self.nation, "military") and hasattr(self.nation.military, "at_war"):
            if self.nation.military.at_war:
                factor_scores["security_situation"] *= 0.5
        
        # Apply policy effects
        if "public_satisfaction" in self.policy["effects"]:
            # Direct satisfaction modifier from policy
            overall_modifier = self.policy["effects"]["public_satisfaction"]
            for factor in factor_scores:
                factor_scores[factor] *= (1 + overall_modifier)
        
        # Calculate weighted average
        happiness = 0
        for factor, info in POPULATION_HAPPINESS_FACTORS.items():
            factor_value = factor_scores.get(factor, 0.5)
            happiness += factor_value * info["weight"]
        
        # Ensure happiness is within bounds (0 to 1)
        happiness = max(0.0, min(1.0, happiness))
        
        return happiness
    
    def get_happiness_effects(self):
        """Get the effects of current happiness on the nation."""
        # Determine happiness category
        for category, info in HAPPINESS_EFFECTS.items():
            min_val, max_val = info["range"]
            if min_val <= self.happiness < max_val:
                return {
                    "category": category,
                    "effects": info["effects"],
                    "value": self.happiness,
                    "flavor_text": info["flavor_text"]
                }
        
        # Default to neutral if no category matches
        return {
            "category": "neutral",
            "effects": HAPPINESS_EFFECTS["neutral"]["effects"],
            "value": self.happiness,
            "flavor_text": HAPPINESS_EFFECTS["neutral"]["flavor_text"]
        }
    
    def change_economic_policy(self, policy_id):
        """Change the nation's economic policy."""
        # Validate policy exists
        policy = next((p for p in ECONOMIC_POLICIES if p["id"] == policy_id), None)
        if not policy:
            return {"success": False, "message": "Invalid economic policy."}
        
        # Check requirements (simplified)
        for tech_id in policy["requirements"].get("technologies", []):
            # In a real implementation, check if the nation has the required technology
            pass
        
        # Change policy
        self.nation.economic_policy_id = policy_id
        
        # Record policy change time
        self.nation.last_policy_change = datetime.utcnow()
        
        # Update other attributes that might be affected
        self.nation.last_updated = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        # Update current policy
        self.policy = policy
        
        # Return success
        return {
            "success": True,
            "message": f"Economic policy changed to {policy['name']}.",
            "effects": policy["effects"]
        }
    
    def trigger_economic_event(self, event_id=None):
        """Trigger an economic event, randomly or specified."""
        if event_id:
            # Trigger specific event
            event = next((e for e in ECONOMIC_EVENTS if e["id"] == event_id), None)
            if not event:
                return {"success": False, "message": "Invalid economic event."}
        else:
            # Random event based on probabilities
            candidate_events = []
            for event in ECONOMIC_EVENTS:
                # Check prerequisites (simplified)
                prerequisites_met = True
                
                # Check economic policy requirement
                if "economic_policy" in event["prerequisites"]:
                    if self.nation.economic_policy_id not in event["prerequisites"]["economic_policy"]:
                        prerequisites_met = False
                
                # Check economic stability requirement
                if "min_economic_stability" in event["prerequisites"]:
                    # Assume stability is calculated elsewhere
                    stability = getattr(self.nation, "economic_stability", 0.5)
                    if stability < event["prerequisites"]["min_economic_stability"]:
                        prerequisites_met = False
                
                if "max_economic_stability" in event["prerequisites"]:
                    stability = getattr(self.nation, "economic_stability", 0.5)
                    if stability > event["prerequisites"]["max_economic_stability"]:
                        prerequisites_met = False
                
                # If prerequisites met, add to candidate events with weight based on probability
                if prerequisites_met:
                    weight = event["probability"] * 100  # Convert to percentage
                    candidate_events.extend([event] * int(weight))
            
            # If no candidates, return error
            if not candidate_events:
                return {"success": False, "message": "No valid economic events available."}
            
            # Randomly select event
            event = random.choice(candidate_events)
        
        # Determine duration
        if isinstance(event["duration"], list):
            duration = random.randint(event["duration"][0], event["duration"][1])
        else:
            duration = event["duration"]
        
        # Calculate end date (if not permanent)
        end_date = None
        if duration > 0:
            end_date = datetime.utcnow() + timedelta(days=duration)
        
        # Add event to active events
        new_event = {
            "id": event["id"],
            "name": event["name"],
            "start_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
            "effects": event["effects"]
        }
        
        if not hasattr(self.nation, "economic_events") or self.nation.economic_events is None:
            self.nation.economic_events = []
        
        self.nation.economic_events.append(new_event)
        
        # Apply immediate effects
        for effect_key, effect_value in event["effects"].items():
            # Update appropriate attributes
            # This would be more detailed in a real implementation
            if effect_key == "gdp_growth":
                self.nation.gdp *= (1 + effect_value)
        
        # Commit changes
        db.session.commit()
        
        # Update active events
        self.active_events = self.nation.economic_events
        
        # Return event details
        return {
            "success": True,
            "message": f"Economic event '{event['name']}' has occurred.",
            "event": new_event,
            "flavor_text": event["flavor_text"]
        }
    
    def update_economy(self):
        """Update the economy for the current turn."""
        # Calculate time since last update
        now = datetime.utcnow()
        last_update = self.nation.last_updated or (now - timedelta(days=1))
        days_passed = (now - last_update).total_seconds() / 86400  # Convert to days
        
        # Apply inflation to prices and values
        if self.inflation_rate != 0:
            # Compound inflation for the period
            inflation_multiplier = math.pow(1 + self.inflation_rate, days_passed / 365)  # Annualized
            
            # Apply to GDP
            self.nation.gdp *= inflation_multiplier
            
            # Apply to currency production and costs
            if hasattr(self.resources, "currency_production"):
                self.resources.currency_production *= inflation_multiplier
        
        # Apply happiness effects
        happiness_effects = self.get_happiness_effects()["effects"]
        
        # Productivity effect on production
        if "productivity" in happiness_effects:
            productivity_modifier = 1 + happiness_effects["productivity"]
            
            # Apply to all production rates
            for resource_type in ["raw_materials", "food", "energy", "technology_points"]:
                if hasattr(self.resources, f"{resource_type}_production"):
                    current_production = getattr(self.resources, f"{resource_type}_production")
                    setattr(self.resources, f"{resource_type}_production", current_production * productivity_modifier)
        
        # Population growth/decline
        if "population_growth" in happiness_effects:
            growth_rate = happiness_effects["population_growth"]
            self.nation.total_population *= (1 + growth_rate * days_passed / 365)  # Annualized
        
        if "emigration_rate" in happiness_effects:
            emigration_rate = happiness_effects["emigration_rate"]
            self.nation.total_population *= (1 - emigration_rate * days_passed / 365)  # Annualized
        
        # Update active economic events
        if hasattr(self.nation, "economic_events") and self.nation.economic_events:
            active_events = []
            for event in self.nation.economic_events:
                # Check if event has expired
                if event["end_date"]:
                    end_date = datetime.strptime(event["end_date"], "%Y-%m-%d")
                    if now > end_date:
                        continue  # Skip expired events
                
                active_events.append(event)
            
            self.nation.economic_events = active_events
            self.active_events = active_events
        
        # Update last update time
        self.nation.last_updated = now
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": "Economy updated successfully.",
            "days_passed": days_passed,
            "inflation_rate": self.inflation_rate,
            "happiness": self.happiness,
            "active_events": len(self.active_events)
        }
    
    def get_economic_statistics(self):
        """Get detailed economic statistics for the nation."""
        # Calculate various statistics
        gdp_per_capita = self.nation.gdp / max(1, self.nation.total_population)
        
        # Tax revenue
        annual_tax_revenue = self.nation.gdp * (self.nation.tax_rate / 100)
        
        # Production statistics
        production_stats = {}
        for resource_type in ["raw_materials", "food", "energy", "technology_points"]:
            if hasattr(self.resources, resource_type) and hasattr(self.resources, f"{resource_type}_production"):
                current_amount = getattr(self.resources, resource_type)
                production_rate = getattr(self.resources, f"{resource_type}_production")
                consumption_rate = getattr(self.resources, f"{resource_type}_consumption", 0)
                
                days_supply = "∞" if consumption_rate == 0 else current_amount / max(0.1, consumption_rate)
                if isinstance(days_supply, float):
                    days_supply = round(days_supply, 1)
                
                production_stats[resource_type] = {
                    "amount": current_amount,
                    "production": production_rate,
                    "consumption": consumption_rate,
                    "net_change": production_rate - consumption_rate,
                    "days_supply": days_supply
                }
        
        # Return comprehensive statistics
        return {
            "gdp": self.nation.gdp,
            "gdp_per_capita": gdp_per_capita,
            "tax_rate": self.nation.tax_rate,
            "annual_tax_revenue": annual_tax_revenue,
            "inflation_rate": self.inflation_rate,
            "inflation_category": self.get_inflation_effects()["category"],
            "population": self.nation.total_population,
            "happiness": self.happiness,
            "happiness_category": self.get_happiness_effects()["category"],
            "economic_policy": self.policy["name"],
            "policy_effects": self.policy["effects"],
            "production": production_stats,
            "active_events": self.active_events,
            "economic_rank": self.nation.economic_rank
        }
    
    def get_economic_forecast(self, turns=10):
        """Get economic forecast for the next several turns."""
        # Start with current values
        gdp = self.nation.gdp
        population = self.nation.total_population
        inflation = self.inflation_rate
        happiness = self.happiness
        
        # Happiness category and effects
        happiness_data = self.get_happiness_effects()
        happiness_effects = happiness_data["effects"]
        
        # Policy effects
        policy_effects = self.policy["effects"]
        
        # Base growth factors
        gdp_growth = policy_effects.get("gdp_growth", 0.02)  # Default 2% annual
        population_growth = happiness_effects.get("population_growth", 0.005)  # Default 0.5% annual
        
        # Forecast data
        forecast = []
        
        for turn in range(1, turns + 1):
            # Apply growth factors
            gdp *= (1 + gdp_growth / 4)  # Quarterly growth
            population *= (1 + population_growth / 4)  # Quarterly growth
            
            # Adjust inflation (tends toward policy target)
            target_inflation = policy_effects.get("inflation_rate", 0.02)
            inflation = inflation * 0.9 + target_inflation * 0.1  # Gradual adjustment
            
            # Adjust happiness (based on various factors)
            # This would be more complex in a real implementation
            happiness_target = 0.5
            if gdp_growth > 0.03:
                happiness_target += 0.1
            if inflation > 0.1:
                happiness_target -= 0.2
            
            happiness = happiness * 0.9 + happiness_target * 0.1  # Gradual adjustment
            
            # Add to forecast
            forecast.append({
                "turn": turn,
                "gdp": round(gdp, 2),
                "population": round(population),
                "inflation": round(inflation * 100, 1),
                "happiness": round(happiness * 100, 1)
            })
        
        return forecast