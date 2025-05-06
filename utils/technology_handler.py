"""
Technology handler for managing technology research and implementation.
"""
from datetime import datetime, timedelta
from app import db
from models import Technology, Nation, Resource
from data.technologies import TECHNOLOGIES
import math

def initialize_technologies(nation):
    """Create initial technologies for a new nation."""
    tech_count = 0
    
    # Check if nation already has technologies
    existing_techs = Technology.query.filter_by(nation_id=nation.id).count()
    if existing_techs > 0:
        return f"Nation {nation.name} already has {existing_techs} technologies."
    
    # Add all technologies from the data file
    for tech_data in TECHNOLOGIES:
        # Create technology with initial level 0 (undiscovered)
        # Basic techs with no prerequisites start at level 1
        initial_level = 0
        if not tech_data["prerequisites"]:
            initial_level = 1
        
        technology = Technology(
            nation_id=nation.id,
            name=tech_data["name"],
            description=tech_data["description"],
            category=tech_data["category"],
            level=initial_level,
            max_level=tech_data["max_level"],
            prerequisites=",".join(str(x) for x in tech_data["prerequisites"]) if tech_data["prerequisites"] else "",
            research_points_required=tech_data["research_points_required"],
            research_points_current=0,
            researching=False
        )
        db.session.add(technology)
        tech_count += 1
    
    db.session.commit()
    return f"Added {tech_count} technologies to nation {nation.name}"

def get_available_technologies(nation):
    """Get technologies that are available for research."""
    # Get all technologies for this nation
    all_techs = Technology.query.filter_by(nation_id=nation.id).all()
    
    # Create a name-based lookup dictionary for techs
    tech_name_dict = {}
    for tech in all_techs:
        tech_name_dict.setdefault(tech.name, []).append(tech)
    
    # Regular ID-based lookup
    tech_dict = {tech.id: tech for tech in all_techs}
    
    # Also get researched techs by name for prerequisite matching
    researched_techs_by_name = {}
    for tech in all_techs:
        if tech.level > 0:
            researched_techs_by_name[tech.name] = tech
    
    available_techs = []
    for tech in all_techs:
        # Skip if already max level
        if tech.level >= tech.max_level:
            print(f"Tech {tech.id} ({tech.name}) already at max level: {tech.level}/{tech.max_level}")
            continue
            
        # Skip if already researching
        if tech.researching:
            print(f"Tech {tech.id} ({tech.name}) currently being researched")
            continue
            
        # If no prerequisites or already researched, it's available for further research
        if not tech.prerequisites or tech.prerequisites.strip() == "":
            print(f"Tech {tech.id} ({tech.name}) has no prerequisites - available")
            available_techs.append(tech)
            continue
            
        # Try to find prerequisite by ID or name
        prereqs_met = True
        missing_prereqs = []
        
        # Find prerequisites for this tech from the data file to get names
        tech_data = None
        for t_data in TECHNOLOGIES:
            if t_data["name"] == tech.name:
                tech_data = t_data
                break
                
        # If we found tech data, get prerequisite names
        prereq_names = []
        if tech_data:
            for prereq_id in tech_data["prerequisites"]:
                for t_data in TECHNOLOGIES:
                    if t_data["id"] == prereq_id:
                        prereq_names.append(t_data["name"])
                        break
                        
        # Try both ID-based and name-based prerequisite checking
        if prereq_names:
            # Check if all prerequisite technologies by name are researched
            for prereq_name in prereq_names:
                if prereq_name not in researched_techs_by_name:
                    prereqs_met = False
                    missing_prereqs.append(f"Tech '{prereq_name}' not researched")
        else:
            # Fall back to ID-based checking from the database
            for prereq_id_str in tech.prerequisites.split(','):
                if not prereq_id_str.strip():
                    continue
                
                try:
                    prereq_id = int(prereq_id_str.strip())
                    
                    if prereq_id not in tech_dict:
                        # Try to find any tech with this ID prefix
                        found = False
                        for tech_id in tech_dict:
                            if str(tech_id).endswith(str(prereq_id)):
                                if tech_dict[tech_id].level > 0:
                                    found = True
                                    break
                                
                        if not found:
                            prereqs_met = False
                            missing_prereqs.append(f"Tech {prereq_id} not found or not researched")
                    elif tech_dict[prereq_id].level == 0:
                        prereqs_met = False
                        missing_prereqs.append(f"Tech {prereq_id} ({tech_dict[prereq_id].name}) level 0")
                except (ValueError, TypeError) as e:
                    print(f"Error parsing prerequisite ID '{prereq_id_str}' for tech {tech.id}: {e}")
                    continue
                
        if prereqs_met:
            print(f"Tech {tech.id} ({tech.name}) has all prerequisites met - available")
            available_techs.append(tech)
        else:
            print(f"Tech {tech.id} ({tech.name}) missing prerequisites: {', '.join(missing_prereqs)}")
    
    # Print summary
    print(f"\nFound {len(available_techs)} available technologies out of {len(all_techs)} total")
    
    return available_techs

def get_technologies_by_tier(nation):
    """
    Organize technologies into tiers based on prerequisites.
    Tier 0: No prerequisites
    Tier 1: Only requires Tier 0 technologies
    Tier 2: Requires at least one Tier 1 technology
    And so on...
    
    This version uses technology data files to ensure consistent tier calculation,
    even with database ID inconsistencies.
    """
    # Get all technologies for this nation
    all_techs = Technology.query.filter_by(nation_id=nation.id).all()
    
    # Create name based mappings for lookup since DB IDs may differ from data file IDs
    tech_by_name = {}
    for tech in all_techs:
        tech_by_name[tech.name] = tech
    
    # Map for storing tech_name -> tier
    tech_name_tiers = {}
    
    # First, assign Tier 0 to technologies with no prerequisites in the data file
    for tech_data in TECHNOLOGIES:
        if not tech_data.get("prerequisites") or len(tech_data["prerequisites"]) == 0:
            tech_name_tiers[tech_data["name"]] = 0
    
    # Function to determine the tier of a technology by name
    def get_tier_by_name(tech_name):
        # If we've already calculated this tech's tier, return it
        if tech_name in tech_name_tiers:
            return tech_name_tiers[tech_name]
        
        # Find the tech data
        tech_data = None
        for t in TECHNOLOGIES:
            if t["name"] == tech_name:
                tech_data = t
                break
        
        if not tech_data:
            return -1  # Tech not found in data file
        
        # If no prerequisites, it's Tier 0
        if not tech_data.get("prerequisites") or len(tech_data["prerequisites"]) == 0:
            tech_name_tiers[tech_name] = 0
            return 0
        
        # Get the max tier of prerequisites + 1
        max_prereq_tier = -1
        for prereq_id in tech_data["prerequisites"]:
            # Find name of prerequisite
            prereq_name = None
            for t in TECHNOLOGIES:
                if t["id"] == prereq_id:
                    prereq_name = t["name"]
                    break
            
            if prereq_name and prereq_name in tech_by_name:
                prereq_tier = get_tier_by_name(prereq_name)
                max_prereq_tier = max(max_prereq_tier, prereq_tier)
        
        # If all prerequisites were invalid or not found, default to Tier 1
        if max_prereq_tier < 0:
            tier = 1
        else:
            # This tech's tier is one higher than its highest prerequisite
            tier = max_prereq_tier + 1
            
        tech_name_tiers[tech_name] = tier
        return tier
    
    # Calculate tier for each technology using data file as source of truth
    for tech in all_techs:
        if tech.name not in tech_name_tiers:
            get_tier_by_name(tech.name)
    
    # Debug information for tier assignment
    print("\nTechnology Tier Assignment (Using data file mappings):")
    for tech_name, tier in tech_name_tiers.items():
        if tech_name in tech_by_name:
            tech = tech_by_name[tech_name]
            print(f"Tech '{tech_name}' (DB ID: {tech.id}): Tier {tier}")
    
    # Map DB techs to tiers
    tech_tiers = {}
    for tech in all_techs:
        if tech.name in tech_name_tiers:
            tech_tiers[tech.id] = tech_name_tiers[tech.name]
        else:
            # If tech not found in mappings, default to tier based on prerequisites in DB
            if not tech.prerequisites or tech.prerequisites == "":
                tech_tiers[tech.id] = 0
            else:
                # Assume tier 1 for any tech with prerequisites but no mapping
                tech_tiers[tech.id] = 1
    
    # Organize technologies by tier
    tech_by_tier = {}
    for tech_id, tier in tech_tiers.items():
        if tier not in tech_by_tier:
            tech_by_tier[tier] = []
        for tech in all_techs:
            if tech.id == tech_id:
                tech_by_tier[tier].append(tech)
                break
    
    # Count technologies in each tier for debugging
    print("\nTier Distribution:")
    for tier in range(6):
        tech_count = len(tech_by_tier.get(tier, []))
        print(f"Tier {tier}: {tech_count} technologies")
    
    # Ensure we have at least empty arrays for tiers 0-5 for visualization
    for tier in range(6):
        if tier not in tech_by_tier:
            tech_by_tier[tier] = []
    
    return tech_by_tier

def get_tech_details(tech_id):
    """Get technology details from the data file."""
    for tech in TECHNOLOGIES:
        if tech["id"] == tech_id:
            return tech
    return None

def get_tech_name_by_id(tech_id):
    """Get technology name from its ID using the data file."""
    tech_data = get_tech_details(int(tech_id) if isinstance(tech_id, str) else tech_id)
    if tech_data:
        return tech_data["name"]
    return f"Unknown Tech (ID: {tech_id})"

def get_prerequisites_names(prerequisites_str):
    """Convert prerequisite IDs string to readable names."""
    if not prerequisites_str:
        return []
    
    names = []
    for prereq_id in prerequisites_str.split(','):
        if not prereq_id:
            continue
            
        try:
            prereq_id = int(prereq_id)
            name = get_tech_name_by_id(prereq_id)
            names.append({"id": prereq_id, "name": name})
        except ValueError:
            # Skip invalid ID
            continue
            
    return names

def get_tech_effects(nation, tech_id, level=1):
    """Get the effects of a technology at a specific level."""
    tech_data = get_tech_details(tech_id)
    if not tech_data:
        return {}
        
    # Scale effects based on level
    effects = {}
    base_effects = tech_data.get("effects", {})
    
    for effect_key, effect_value in base_effects.items():
        if isinstance(effect_value, (int, float)):
            # Scale effect by level (diminishing returns)
            scale_factor = 1 + (math.log(level + 1) / math.log(10))
            effects[effect_key] = effect_value * scale_factor
        else:
            # Non-numeric effects don't scale
            effects[effect_key] = effect_value
            
    return effects

def start_research(nation, technology_id):
    """Start researching a technology."""
    # Validate technology exists and belongs to this nation
    technology = Technology.query.filter_by(id=technology_id, nation_id=nation.id).first()
    if not technology:
        return {"success": False, "message": "Technology not found or does not belong to your nation."}
    
    # Check if already researching
    if technology.researching:
        return {"success": False, "message": "Already researching this technology."}
    
    # Check if already at max level
    if technology.level >= technology.max_level:
        return {"success": False, "message": "This technology is already at maximum level."}
    
    # Get the nation's resources
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    if not resources:
        return {"success": False, "message": "Nation resources not found."}
    
    # Calculate research cost (increases with level)
    level_multiplier = 1 + (technology.level * 0.5)
    raw_materials_cost = 100 * level_multiplier
    energy_cost = 100 * level_multiplier
    currency_cost = 500 * level_multiplier
    
    # Check if nation has enough resources
    if resources.raw_materials < raw_materials_cost:
        return {"success": False, "message": f"Not enough raw materials. Need {raw_materials_cost}."}
    
    if resources.energy < energy_cost:
        return {"success": False, "message": f"Not enough energy. Need {energy_cost}."}
    
    if resources.currency < currency_cost:
        return {"success": False, "message": f"Not enough currency. Need {currency_cost}."}
    
    # Deduct resources
    resources.raw_materials -= raw_materials_cost
    resources.energy -= energy_cost
    resources.currency -= currency_cost
    
    # Calculate research time based on points required and production
    # Make first levels much quicker, with more moderate growth for higher levels
    # Reduced quadratic factor from 0.3 to 0.15 for more manageable scaling
    level_factor = 1 + (technology.level * 0.15)**2  
    points_required = technology.research_points_required * level_factor
    
    # Increase production points based on nation's research capability
    # Increased base daily points from 50 to 200 for faster early research
    daily_points = 200 + (resources.technology_points * 0.2) + (nation.research_population * 3.0)
    
    # Calculate days needed for research
    days_needed = points_required / daily_points
    
    # Set a minimum and maximum research time
    min_minutes = 60  # 60 minutes minimum for level 0 (more realistic timer)
    max_days = 4.0    # 4 days maximum for highest levels
    
    # Clamp the research time between min and max
    hours_needed = days_needed * 24
    minutes_needed = hours_needed * 60
    minutes_needed = max(min_minutes, min(minutes_needed, max_days * 24 * 60))
    days_needed = minutes_needed / (24 * 60)
    
    # Set technology as researching
    technology.researching = True
    technology.research_points_required = points_required
    technology.research_points_current = 0
    technology.research_started = datetime.utcnow()
    technology.estimated_completion = datetime.utcnow() + timedelta(days=days_needed)
    
    db.session.commit()
    
    return {
        "success": True,
        "message": f"Started research on {technology.name}. Estimated completion in {days_needed:.1f} days.",
        "days_estimate": days_needed,
        "completion_date": technology.estimated_completion.strftime("%Y-%m-%d %H:%M:%S")
    }

def cancel_research(nation, technology_id):
    """Cancel researching a technology and refund some resources."""
    # Validate technology exists and belongs to this nation
    technology = Technology.query.filter_by(id=technology_id, nation_id=nation.id, researching=True).first()
    if not technology:
        return {"success": False, "message": "Technology not found, does not belong to your nation, or is not being researched."}
    
    # Get the nation's resources
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    if not resources:
        return {"success": False, "message": "Nation resources not found."}
    
    # Calculate original research cost
    level_multiplier = 1 + (technology.level * 0.5)
    raw_materials_cost = 100 * level_multiplier
    energy_cost = 100 * level_multiplier
    currency_cost = 500 * level_multiplier
    
    # Calculate refund (50% of original cost)
    raw_materials_refund = raw_materials_cost * 0.5
    energy_refund = energy_cost * 0.5
    currency_refund = currency_cost * 0.5
    
    # Refund resources
    resources.raw_materials += raw_materials_refund
    resources.energy += energy_refund
    resources.currency += currency_refund
    
    # Reset research status
    technology.researching = False
    technology.research_points_current = 0
    technology.research_started = None
    technology.estimated_completion = None
    
    db.session.commit()
    
    return {
        "success": True,
        "message": f"Research on {technology.name} canceled. You received a partial refund of resources.",
        "refunds": {
            "raw_materials": raw_materials_refund,
            "energy": energy_refund,
            "currency": currency_refund
        }
    }

def update_research_progress():
    """Update research progress for all technologies in progress.
    This function is intended to be run periodically (e.g. hourly)."""
    updated_count = 0
    completed_count = 0
    
    now = datetime.utcnow()
    research_in_progress = Technology.query.filter_by(researching=True).all()
    
    for tech in research_in_progress:
        nation = Nation.query.get(tech.nation_id)
        if not nation:
            continue
        
        # Check if research is complete
        if tech.estimated_completion and now >= tech.estimated_completion:
            # Research complete - increase level
            tech.level += 1
            tech.researching = False
            # Set research points to the maximum to show 100% in UI
            tech.research_points_current = tech.research_points_required
            
            # Apply technology effects (in a real implementation)
            
            completed_count += 1
            print(f"Research completed: {tech.name} - level {tech.level}")
        else:
            # Calculate progress
            if tech.research_started:
                elapsed = now - tech.research_started
                total_time = tech.estimated_completion - tech.research_started
                if total_time.total_seconds() > 0:  # Prevent division by zero
                    progress_percent = elapsed.total_seconds() / total_time.total_seconds()
                    # Round up to 100% if we're very close to completion (99.9%+)
                    if progress_percent > 0.999:
                        tech.research_points_current = tech.research_points_required
                        # Mark as completed and update level immediately to fix timer issues
                        tech.level += 1
                        tech.researching = False
                        completed_count += 1
                        print(f"Research complete (fixed): {tech.name} - 100.00% - new level {tech.level}")
                    else:
                        # Ensure progress reflects correctly by setting points based on time elapsed
                        tech.research_points_current = min(
                            tech.research_points_required * progress_percent,
                            tech.research_points_required
                        )
                        updated_count += 1
                        print(f"Research progress: {tech.name} - {progress_percent*100:.2f}%")
    
    db.session.commit()
    
    return {
        "updated_count": updated_count,
        "completed_count": completed_count
    }

def get_technology_tree(nation):
    """Get the complete technology tree for visualization."""
    technologies = Technology.query.filter_by(nation_id=nation.id).all()
    
    # Get additional details from the data file
    tech_tree = []
    for tech in technologies:
        tech_data = get_tech_details(tech.id)
        
        # Skip if not found in data file
        if not tech_data:
            continue
            
        # Create node for the tech tree
        node = {
            "id": tech.id,
            "name": tech.name,
            "category": tech.category,
            "level": tech.level,
            "max_level": tech.max_level,
            "description": tech.description,
            "researching": tech.researching,
            "progress": tech.research_points_current / tech.research_points_required if tech.researching and tech.research_points_required > 0 else 0,
            "prerequisites": [int(x) for x in tech.prerequisites.split(',') if x],
            "flavor_text": tech_data.get("flavor_text", ""),
            "effects": get_tech_effects(nation, tech.id, tech.level)
        }
        
        if tech.researching:
            node["estimated_completion"] = tech.estimated_completion.strftime("%Y-%m-%d %H:%M:%S") if tech.estimated_completion else None
            node["days_remaining"] = (tech.estimated_completion - datetime.utcnow()).days if tech.estimated_completion else None
        
        tech_tree.append(node)
    
    return tech_tree

def apply_technology_effects(nation):
    """Apply the effects of all researched technologies to a nation."""
    # This would be called when calculating production rates, military strength, etc.
    technologies = Technology.query.filter(Technology.nation_id == nation.id, Technology.level > 0).all()
    
    effects = {
        "food_production": 1.0,
        "raw_materials_production": 1.0,
        "energy_production": 1.0,
        "technology_points": 1.0,
        "military_strength": 1.0,
        "defensive_power": 1.0,
        "espionage_power": 1.0,
        "research_efficiency": 1.0,
        "resource_consumption": 1.0,
        "diplomatic_influence": 1.0
    }
    
    for tech in technologies:
        tech_data = get_tech_details(tech.id)
        if not tech_data:
            continue
            
        tech_effects = get_tech_effects(nation, tech.id, tech.level)
        
        for effect_key, effect_value in tech_effects.items():
            if effect_key in effects and isinstance(effect_value, (int, float)):
                # Multiplicative effects
                effects[effect_key] *= effect_value
    
    return effects