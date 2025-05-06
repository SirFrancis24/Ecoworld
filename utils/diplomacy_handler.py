"""
Diplomacy handler for managing diplomatic relations and actions.
"""
from datetime import datetime, timedelta
from app import db
from models import Nation, Alliance, War, TransitRights
from data.diplomacy import DIPLOMATIC_ACTIONS, RELATION_STATES
import random

# Maximum diplomatic influence a nation can have
MAX_DIPLOMATIC_INFLUENCE = 100

class DiplomaticRelation:
    """Class for tracking and managing relations between nations."""
    def __init__(self, nation1_id, nation2_id):
        self.nation1_id = nation1_id
        self.nation2_id = nation2_id
        
        # Check for existing alliance
        self.alliance = Alliance.query.filter(
            ((Alliance.nation1_id == nation1_id) & (Alliance.nation2_id == nation2_id)) |
            ((Alliance.nation1_id == nation2_id) & (Alliance.nation2_id == nation1_id)),
            Alliance.is_active == True
        ).first()
        
        # Check for existing war
        self.war = War.query.filter(
            ((War.aggressor_id == nation1_id) & (War.defender_id == nation2_id)) |
            ((War.aggressor_id == nation2_id) & (War.defender_id == nation1_id)),
            War.is_active == True
        ).first()
        
        # Initialize relation value based on alliance/war status
        if self.alliance:
            self.value = 80  # Allied nations start with high relation
        elif self.war:
            self.value = -80  # Nations at war start with low relation
        else:
            self.value = 0  # Neutral by default
        
        # Relation modifiers
        self.modifiers = []
        
        # Diplomatic actions in progress
        self.active_actions = []
    
    def get_relation_state(self):
        """Get the current state of relations based on value."""
        for state in RELATION_STATES:
            if state["range"][0] <= self.value <= state["range"][1]:
                return state
        
        # Default to neutral if no matching range found
        return next(state for state in RELATION_STATES if state["name"] == "Neutral")
    
    def apply_action(self, action_id, initiator_id, target_id, resources=None):
        """Apply a diplomatic action and its effects."""
        # Find the action in the data
        action = next((a for a in DIPLOMATIC_ACTIONS if a["id"] == action_id), None)
        if not action:
            return {"success": False, "message": "Invalid diplomatic action."}
        
        # Check if this nation is initiating the action
        if initiator_id != self.nation1_id and initiator_id != self.nation2_id:
            return {"success": False, "message": "Nation is not part of this relationship."}
        
        # Get the nation objects
        initiator = Nation.query.get(initiator_id)
        target = Nation.query.get(target_id)
        if not initiator or not target:
            return {"success": False, "message": "Nation not found."}
        
        # Check relation requirements
        if "minimum_relation" in action["requirements"] and self.value < action["requirements"]["minimum_relation"]:
            return {"success": False, "message": f"Relation too negative. Need at least {action['requirements']['minimum_relation']}."}
        
        if "maximum_relation" in action["requirements"] and self.value > action["requirements"]["maximum_relation"]:
            return {"success": False, "message": f"Relation too positive. Need at most {action['requirements']['maximum_relation']}."}
        
        # Check if at war (for actions that require war)
        if action["requirements"].get("war_state", False) and not self.war:
            return {"success": False, "message": "Nations must be at war for this action."}
        
        # Check prerequisites
        prereq_ids = action["requirements"].get("prerequisites", [])
        for prereq_id in prereq_ids:
            # This is simplified - in a real implementation, you'd check if the prerequisite action
            # has been performed and is still active
            pass
        
        # Check resource requirements
        if resources:
            for resource_type, amount in action["requirements"].get("resources", {}).items():
                if resource_type not in resources or resources[resource_type] < amount:
                    return {"success": False, "message": f"Not enough {resource_type}. Need {amount}."}
        
        # Apply relation change
        self.value += action["effects"].get("relation_change", 0)
        
        # Limit relation value to valid range
        self.value = max(-100, min(100, self.value))
        
        # Handle war state changes
        if "war_state" in action["effects"]:
            if action["effects"]["war_state"]:
                # Start a war if not already at war
                if not self.war:
                    self.war = War(
                        aggressor_id=initiator_id,
                        defender_id=target_id,
                        start_date=datetime.utcnow(),
                        is_active=True
                    )
                    db.session.add(self.war)
            else:
                # End a war if at war
                if self.war:
                    self.war.is_active = False
                    self.war.end_date = datetime.utcnow()
                    self.war.aggressor_victory = action["effects"].get("aggressor_victory", None)
        
        # Handle alliance changes
        if action["id"] == 5:  # Form Alliance
            if not self.alliance:
                self.alliance = Alliance(
                    nation1_id=initiator_id,
                    nation2_id=target_id,
                    formed_date=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(self.alliance)
        
        # Add the action to active actions if it has a duration
        if action["duration"] > 0:
            end_date = datetime.utcnow() + timedelta(days=action["duration"])
            self.active_actions.append({
                "action_id": action_id,
                "start_date": datetime.utcnow(),
                "end_date": end_date,
                "initiator_id": initiator_id
            })
        
        # Add a relation modifier
        self.modifiers.append({
            "source": f"Diplomatic action: {action['name']}",
            "value": action["effects"].get("relation_change", 0),
            "expiry": datetime.utcnow() + timedelta(days=30)  # Most modifiers expire after 30 days
        })
        
        # Commit changes
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Diplomatic action '{action['name']}' performed successfully.",
            "new_relation_value": self.value,
            "new_relation_state": self.get_relation_state()["name"]
        }

def get_available_actions(nation, target_nation):
    """Get diplomatic actions available between two nations."""
    # Create a diplomatic relation object
    relation = DiplomaticRelation(nation.id, target_nation.id)
    
    # Get current relation state
    state = relation.get_relation_state()
    
    # Get actions available in this state
    available_actions = []
    for action_id in state["effects"].get("diplomatic_options", []):
        action = next((a for a in DIPLOMATIC_ACTIONS if a["id"] == action_id), None)
        if action:
            available_actions.append(action)
    
    # Filter by technology requirements
    # In a real implementation, you'd check if the nation has the required technologies
    
    return {
        "relation_value": relation.value,
        "relation_state": state["name"],
        "available_actions": available_actions
    }

def perform_diplomatic_action(nation, target_nation_id, action_id):
    """Perform a diplomatic action towards another nation."""
    # Validate target nation exists
    target_nation = Nation.query.get(target_nation_id)
    if not target_nation:
        return {"success": False, "message": "Target nation not found."}
    
    # Validate action exists
    action = next((a for a in DIPLOMATIC_ACTIONS if a["id"] == action_id), None)
    if not action:
        return {"success": False, "message": "Invalid diplomatic action."}
    
    # Create diplomatic relation
    relation = DiplomaticRelation(nation.id, target_nation_id)
    
    # Check if action is available in current state
    state = relation.get_relation_state()
    if action_id not in state["effects"].get("diplomatic_options", []):
        return {"success": False, "message": f"This action is not available in the current relation state ({state['name']})."}
    
    # Perform the action
    result = relation.apply_action(action_id, nation.id, target_nation_id)
    
    return result

def get_diplomatic_stance(nation_id, target_nation_id=None):
    """Get the diplomatic stance between two nations or overall diplomatic status."""
    if target_nation_id:
        # Get relation with specific nation
        relation = DiplomaticRelation(nation_id, target_nation_id)
        
        # Check if nations are neighbors (sharing a border)
        is_neighbor = are_nations_neighbors(nation_id, target_nation_id)
        
        # Check for transit rights in both directions
        has_transit_rights = check_transit_rights(target_nation_id, nation_id)
        has_granted_transit = check_transit_rights(nation_id, target_nation_id)
        
        # Calculate travel time between nations
        # Consider transit rights when calculating
        travel_time = calculate_travel_time(nation_id, target_nation_id, has_transit_rights)
        
        # Get active war (if any) for war start date
        war_start_date = None
        if relation.war:
            war_start_date = relation.war.start_date
        
        return {
            "relation_value": relation.value,
            "relation_state": relation.get_relation_state()["name"],
            "is_allied": relation.alliance is not None,
            "is_at_war": relation.war is not None,
            "is_neighbor": is_neighbor,
            "has_transit_rights": has_transit_rights or is_neighbor,  # Neighbors don't need transit rights
            "has_granted_transit": has_granted_transit or is_neighbor,
            "travel_time": travel_time,
            "war_start_date": war_start_date,
            "modifiers": relation.modifiers,
            "active_actions": relation.active_actions
        }
    else:
        # Get overall diplomatic status
        nation = Nation.query.get(nation_id)
        if not nation:
            return {"success": False, "message": "Nation not found."}
        
        # Get alliances
        alliances = Alliance.query.filter(
            ((Alliance.nation1_id == nation_id) | (Alliance.nation2_id == nation_id)),
            Alliance.is_active == True
        ).all()
        
        alliance_nations = []
        for alliance in alliances:
            ally_id = alliance.nation1_id if alliance.nation2_id == nation_id else alliance.nation2_id
            ally = Nation.query.get(ally_id)
            if ally:
                alliance_nations.append({
                    "id": ally.id,
                    "name": ally.name,
                    "formed_date": alliance.formed_date.strftime("%Y-%m-%d")
                })
        
        # Get wars
        wars = War.query.filter(
            ((War.aggressor_id == nation_id) | (War.defender_id == nation_id)),
            War.is_active == True
        ).all()
        
        war_nations = []
        for war in wars:
            enemy_id = war.defender_id if war.aggressor_id == nation_id else war.aggressor_id
            enemy = Nation.query.get(enemy_id)
            if enemy:
                war_nations.append({
                    "id": enemy.id,
                    "name": enemy.name,
                    "start_date": war.start_date.strftime("%Y-%m-%d"),
                    "is_aggressor": war.aggressor_id == nation_id
                })
        
        return {
            "alliances": alliance_nations,
            "wars": war_nations,
            "diplomatic_influence": calculate_diplomatic_influence(nation)
        }

def calculate_diplomatic_influence(nation):
    """Calculate a nation's diplomatic influence based on various factors."""
    # This would be a more complex calculation in a real implementation,
    # considering factors like economic power, military strength, technology level, etc.
    base_influence = 10
    
    # Economic factor
    economic_factor = nation.gdp / 1000000  # Scale appropriately
    
    # Military factor (simplified)
    military = nation.military
    military_factor = (military.offensive_power + military.defensive_power) / 100
    
    # Alliance factor
    alliances = Alliance.query.filter(
        ((Alliance.nation1_id == nation.id) | (Alliance.nation2_id == nation.id)),
        Alliance.is_active == True
    ).count()
    alliance_factor = alliances * 2
    
    # Total influence (capped at MAX_DIPLOMATIC_INFLUENCE)
    total_influence = base_influence + economic_factor + military_factor + alliance_factor
    
    return min(total_influence, MAX_DIPLOMATIC_INFLUENCE)

def update_diplomatic_relations():
    """Update diplomatic relations for all nations.
    This function is intended to be run periodically (e.g. daily)."""
    # Get all nations
    nations = Nation.query.all()
    
    # Process all bilateral relationships
    for i in range(len(nations)):
        for j in range(i+1, len(nations)):
            nation1 = nations[i]
            nation2 = nations[j]
            
            # Skip if same nation
            if nation1.id == nation2.id:
                continue
            
            # Create diplomatic relation
            relation = DiplomaticRelation(nation1.id, nation2.id)
            
            # Update relation value based on various factors
            # This would be more complex in a real implementation
            
            # Random small fluctuation (-2 to +2)
            random_change = random.randint(-2, 2)
            relation.value += random_change
            
            # Limit relation value to valid range
            relation.value = max(-100, min(100, relation.value))
            
            # Update expired modifiers
            now = datetime.utcnow()
            relation.modifiers = [mod for mod in relation.modifiers if mod["expiry"] > now]
            
            # Update expired actions
            relation.active_actions = [action for action in relation.active_actions if action["end_date"] > now]
    
    db.session.commit()
    
    return {"success": True, "message": "Diplomatic relations updated."}


def check_transit_rights(grantor_id, receiver_id):
    """Check if transit rights exist between two nations (grantor -> receiver)."""
    # Check if transit rights exist
    transit_rights = TransitRights.query.filter_by(
        grantor_id=grantor_id,
        receiver_id=receiver_id,
        is_active=True
    ).first()
    
    return transit_rights is not None

def get_transit_rights(nation_id, target_nation_id=None):
    """Get transit rights between nations."""
    if target_nation_id:
        # Check if nation has transit rights with target
        return check_transit_rights(target_nation_id, nation_id)
    else:
        # Get all nations that have granted transit rights to this nation
        granted_rights = TransitRights.query.filter_by(
            receiver_id=nation_id,
            is_active=True
        ).all()
        
        granted_nations = []
        for right in granted_rights:
            grantor = Nation.query.get(right.grantor_id)
            if grantor:
                granted_nations.append({
                    "id": grantor.id,
                    "name": grantor.name,
                    "granted_date": right.granted_date.strftime("%Y-%m-%d"),
                    "expiry_date": right.expiry_date.strftime("%Y-%m-%d") if right.expiry_date else "Never"
                })
        
        # Get all nations that this nation has granted transit rights to
        given_rights = TransitRights.query.filter_by(
            grantor_id=nation_id,
            is_active=True
        ).all()
        
        given_nations = []
        for right in given_rights:
            receiver = Nation.query.get(right.receiver_id)
            if receiver:
                given_nations.append({
                    "id": receiver.id,
                    "name": receiver.name,
                    "granted_date": right.granted_date.strftime("%Y-%m-%d"),
                    "expiry_date": right.expiry_date.strftime("%Y-%m-%d") if right.expiry_date else "Never"
                })
        
        return {
            "granted_rights": granted_nations,
            "given_rights": given_nations
        }


def are_nations_neighbors(nation1_id, nation2_id):
    """Check if two nations are neighbors (sharing a border).
    This is determined by checking if they are in the same continent
    and their map coordinates are close enough."""
    
    nation1 = Nation.query.get(nation1_id)
    nation2 = Nation.query.get(nation2_id)
    
    if not nation1 or not nation2:
        return False
    
    # First check if they're in the same continent
    if nation1.continent != nation2.continent:
        return False
    
    # Calculate the Euclidean distance between their map coordinates
    distance = ((nation1.map_x - nation2.map_x) ** 2 + (nation1.map_y - nation2.map_y) ** 2) ** 0.5
    
    # Define a threshold for considering nations as neighbors
    # This value should be calibrated based on your map scale
    NEIGHBOR_DISTANCE_THRESHOLD = 70.0
    
    return distance <= NEIGHBOR_DISTANCE_THRESHOLD

def calculate_travel_time(nation1_id, nation2_id, transit_rights=False):
    """Calculate the travel time between two nations in hours.
    If transit rights are available, travel time is reduced."""
    
    nation1 = Nation.query.get(nation1_id)
    nation2 = Nation.query.get(nation2_id)
    
    if not nation1 or not nation2:
        return None
    
    # Calculate the Euclidean distance between their map coordinates
    distance = ((nation1.map_x - nation2.map_x) ** 2 + (nation1.map_y - nation2.map_y) ** 2) ** 0.5
    
    # Applica un fattore di scala per ottenere tempi di viaggio più realistici
    # Questo fattore è calibrato per dare tempi tra 0.5 e 6 ore basati sulla distribuzione delle nazioni
    # Un valore più alto = viaggi più lunghi
    TRAVEL_TIME_FACTOR = 0.03
    
    # Different continents add a travel time penalty
    continent_multiplier = 1.5 if nation1.continent != nation2.continent else 1.0
    
    # Se sono vicini (neighbors) hanno uno sconto sul tempo di viaggio
    neighbor_discount = 0.8 if are_nations_neighbors(nation1_id, nation2_id) else 1.0
    
    # Se hanno diritti di transito, viaggiano più velocemente
    transit_discount = 0.7 if transit_rights else 1.0
    
    # Calcola il tempo di viaggio base
    travel_time = distance * TRAVEL_TIME_FACTOR * continent_multiplier * neighbor_discount * transit_discount
    
    # Assicurati che il tempo sia almeno 0.5 ore per le nazioni più vicine
    travel_time = max(0.5, travel_time)
    
    # Calcola un tempo più lungo per Canada e altre nazioni più lontane
    # Questo è basato sulla distanza effettiva che vediamo dai log
    if distance > 130:  # Canada è a distanza 142.1 da Australia
        travel_time = max(travel_time, 5.0)  # Garantisce almeno 5 ore per nazioni molto lontane
    elif distance > 90:  # Per nazioni a distanza media
        travel_time = max(travel_time, 2.0)  # Garantisce almeno 2 ore
    
    # Cap maximum travel time at 6 hours
    travel_time = min(6.0, travel_time)
    
    # Debug print
    travel_time_rounded = round(travel_time, 1)
    print(f"DEBUG: Travel time from {nation1.name} to {nation2.name}: {travel_time_rounded}h (distance: {round(distance, 1)})")
    
    return travel_time_rounded  # Round to 1 decimal place

def grant_transit_rights(grantor_id, receiver_id, duration_days=None):
    """Grant transit rights to another nation."""
    # Check if rights already exist
    existing_rights = TransitRights.query.filter_by(
        grantor_id=grantor_id,
        receiver_id=receiver_id,
        is_active=True
    ).first()
    
    if existing_rights:
        return {"success": False, "message": "Transit rights already granted to this nation."}
    
    # Check if nations are neighbors
    if are_nations_neighbors(grantor_id, receiver_id):
        return {"success": False, "message": "Transit rights are not needed for neighboring nations."}
    
    # Check if nations are allied
    alliance = Alliance.query.filter(
        ((Alliance.nation1_id == grantor_id) & (Alliance.nation2_id == receiver_id)) |
        ((Alliance.nation1_id == receiver_id) & (Alliance.nation2_id == grantor_id)),
        Alliance.is_active == True
    ).first()
    
    # Automatic transit rights for allies
    if alliance:
        duration_days = None  # Indefinite duration for allies
    
    # Calculate expiry date if duration provided
    expiry_date = None
    if duration_days:
        expiry_date = datetime.utcnow() + timedelta(days=duration_days)
    
    # Create new transit rights
    transit_rights = TransitRights(
        grantor_id=grantor_id,
        receiver_id=receiver_id,
        granted_date=datetime.utcnow(),
        expiry_date=expiry_date,
        is_active=True
    )
    
    db.session.add(transit_rights)
    db.session.commit()
    
    return {"success": True, "message": "Transit rights granted successfully."}


def revoke_transit_rights(grantor_id, receiver_id):
    """Revoke transit rights from another nation."""
    existing_rights = TransitRights.query.filter_by(
        grantor_id=grantor_id,
        receiver_id=receiver_id,
        is_active=True
    ).first()
    
    if not existing_rights:
        return {"success": False, "message": "No active transit rights found for this nation."}
    
    # Check if nations are allies
    alliance = Alliance.query.filter(
        ((Alliance.nation1_id == grantor_id) & (Alliance.nation2_id == receiver_id)) |
        ((Alliance.nation1_id == receiver_id) & (Alliance.nation2_id == grantor_id)),
        Alliance.is_active == True
    ).first()
    
    # Cannot revoke transit rights from allies
    if alliance:
        return {"success": False, "message": "Transit rights cannot be revoked from allies. Dissolve the alliance first."}
    
    existing_rights.is_active = False
    db.session.commit()
    
    return {"success": True, "message": "Transit rights revoked successfully."}