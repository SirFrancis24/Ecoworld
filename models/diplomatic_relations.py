from datetime import datetime
from app import db
from models import Nation

# Association tables
transit_rights = db.Table('transit_rights',
    db.Column('grantor_id', db.Integer, db.ForeignKey('nation.id'), primary_key=True),
    db.Column('receiver_id', db.Integer, db.ForeignKey('nation.id'), primary_key=True),
    db.Column('formed_date', db.DateTime, default=datetime.utcnow),
    db.Column('expires_at', db.DateTime, nullable=True),
    db.Column('is_active', db.Boolean, default=True)
)

non_aggression_pacts = db.Table('non_aggression_pacts',
    db.Column('nation1_id', db.Integer, db.ForeignKey('nation.id'), primary_key=True),
    db.Column('nation2_id', db.Integer, db.ForeignKey('nation.id'), primary_key=True),
    db.Column('formed_date', db.DateTime, default=datetime.utcnow),
    db.Column('expires_at', db.DateTime, nullable=True),
    db.Column('is_active', db.Boolean, default=True)
)

class DiplomaticRelation:
    """Class to handle relations between nations (not a database model)"""
    
    def __init__(self, nation_id, target_nation_id):
        self.nation_id = nation_id
        self.target_nation_id = target_nation_id
        self.value = 0  # Default neutral
        
        # Check for alliance
        self.alliance = Alliance.query.filter(
            ((Alliance.nation1_id == nation_id) & (Alliance.nation2_id == target_nation_id)) |
            ((Alliance.nation1_id == target_nation_id) & (Alliance.nation2_id == nation_id)),
            Alliance.is_active == True
        ).first()
        
        # Check for war
        self.war = War.query.filter(
            ((War.aggressor_id == nation_id) & (War.defender_id == target_nation_id)) |
            ((War.aggressor_id == target_nation_id) & (War.defender_id == nation_id)),
            War.is_active == True
        ).first()
        
        # Check for transit rights
        self.transit_rights = db.session.query(transit_rights).filter(
            ((transit_rights.c.grantor_id == nation_id) & (transit_rights.c.receiver_id == target_nation_id)) |
            ((transit_rights.c.grantor_id == target_nation_id) & (transit_rights.c.receiver_id == nation_id)),
            transit_rights.c.is_active == True
        ).first()
        
        # Check for non-aggression pact
        self.non_aggression = db.session.query(non_aggression_pacts).filter(
            ((non_aggression_pacts.c.nation1_id == nation_id) & (non_aggression_pacts.c.nation2_id == target_nation_id)) |
            ((non_aggression_pacts.c.nation1_id == target_nation_id) & (non_aggression_pacts.c.nation2_id == nation_id)),
            non_aggression_pacts.c.is_active == True
        ).first()
        
        # Calculate base relation value
        if self.alliance:
            self.value = 75
        elif self.war:
            self.value = -75
        elif self.non_aggression:
            self.value = 25
        elif self.transit_rights:
            self.value = 40
        else:
            # Default starting relations (neutral)
            self.value = 0
        
        # Apply modifiers
        self.modifiers = self._calculate_modifiers()
        for modifier, value in self.modifiers.items():
            self.value += value
            
        # Limit relation value between -100 and 100
        self.value = max(-100, min(100, self.value))
        
        # Store active diplomatic actions
        self.active_actions = self._get_active_actions()
    
    def _calculate_modifiers(self):
        """Calculate relation modifiers based on various factors"""
        modifiers = {}
        
        nation = Nation.query.get(self.nation_id)
        target_nation = Nation.query.get(self.target_nation_id)
        
        if not nation or not target_nation:
            return modifiers
        
        # Economic relations (trade volume would affect this)
        modifiers['economic'] = 0
        
        # Military power difference
        if hasattr(nation, 'military') and hasattr(target_nation, 'military'):
            if nation.military and target_nation.military:
                nation_power = nation.military.offensive_power + nation.military.defensive_power
                target_power = target_nation.military.offensive_power + target_nation.military.defensive_power
                
                # Very powerful nations intimidate weaker ones
                if target_power > nation_power * 2:
                    modifiers['military_fear'] = -10
                
                # Similar military powers tend to respect each other
                elif 0.8 <= (nation_power / target_power) <= 1.2:
                    modifiers['military_respect'] = 5
        
        # Shared allies bonus
        # This would require checking if both nations have alliances with the same third parties
        
        return modifiers
    
    def _get_active_actions(self):
        """Get currently active diplomatic actions between the nations"""
        actions = []
        
        # Add active status
        if self.alliance:
            actions.append({
                'type': 'alliance',
                'formed_date': self.alliance.formed_date,
                'status': 'active'
            })
        
        if self.war:
            actions.append({
                'type': 'war',
                'started_date': self.war.start_date,
                'status': 'active',
                'aggressor_id': self.war.aggressor_id,
                'peace_proposed': self.war.peace_proposed
            })
        
        if self.transit_rights:
            actions.append({
                'type': 'transit_rights',
                'formed_date': self.transit_rights.formed_date,
                'expires_at': self.transit_rights.expires_at,
                'grantor_id': self.transit_rights.grantor_id
            })
            
        if self.non_aggression:
            actions.append({
                'type': 'non_aggression',
                'formed_date': self.non_aggression.formed_date,
                'expires_at': self.non_aggression.expires_at
            })
            
        return actions
    
    def get_relation_state(self):
        """Get the current relation state based on value"""
        for state in RELATION_STATES:
            if state["min_value"] <= self.value <= state["max_value"]:
                return state
        
        # Default fallback
        return RELATION_STATES[3]  # Neutral
    
    def apply_action(self, action_id, initiator_id, target_id):
        """Apply a diplomatic action and update relations accordingly"""
        # Get the action details
        action = next((a for a in DIPLOMATIC_ACTIONS if a["id"] == action_id), None)
        if not action:
            return {"success": False, "message": "Invalid diplomatic action."}
        
        # Check if this action can be applied in current state
        # Implement the logic here based on the action
        
        # Example: Alliance creation
        if action_id == 1:  # Assume 1 is "Propose Alliance"
            if self.alliance:
                return {"success": False, "message": "Already in an alliance with this nation."}
            
            if self.war:
                return {"success": False, "message": "Cannot form an alliance while at war."}
            
            # Create new alliance
            alliance = Alliance(
                nation1_id=initiator_id,
                nation2_id=target_id,
                formed_date=datetime.utcnow(),
                is_active=True
            )
            
            db.session.add(alliance)
            db.session.commit()
            
            return {
                "success": True, 
                "message": "Alliance proposed and accepted.",
                "relation_change": 75
            }
        
        # Example: Request Transit Rights
        elif action_id == 2:
            if self.transit_rights:
                return {"success": False, "message": "Transit rights agreement already exists."}
            
            if self.war:
                return {"success": False, "message": "Cannot establish transit rights while at war."}
            
            # Create transit rights entry in association table
            stmt = transit_rights.insert().values(
                grantor_id=target_id,
                receiver_id=initiator_id,
                formed_date=datetime.utcnow(),
                is_active=True
            )
            
            db.session.execute(stmt)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Transit rights granted by the other nation.",
                "relation_change": 40
            }
        
        # Example: Sign Non-aggression Pact
        elif action_id == 3:
            if self.non_aggression:
                return {"success": False, "message": "Non-aggression pact already exists."}
            
            if self.war:
                return {"success": False, "message": "Cannot sign non-aggression pact while at war."}
            
            # Create non-aggression pact entry
            stmt = non_aggression_pacts.insert().values(
                nation1_id=initiator_id,
                nation2_id=target_id,
                formed_date=datetime.utcnow(),
                is_active=True
            )
            
            db.session.execute(stmt)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Non-aggression pact signed.",
                "relation_change": 25
            }
        
        # Example: Declare War
        elif action_id == 4:
            if self.war:
                return {"success": False, "message": "Already at war with this nation."}
            
            if self.alliance:
                # First break alliance
                self.alliance.is_active = False
                self.alliance.dissolved_date = datetime.utcnow()
                db.session.commit()
            
            if self.non_aggression:
                # Break non-aggression pact
                stmt = non_aggression_pacts.update().\
                    where(
                        ((non_aggression_pacts.c.nation1_id == initiator_id) & (non_aggression_pacts.c.nation2_id == target_id)) |
                        ((non_aggression_pacts.c.nation1_id == target_id) & (non_aggression_pacts.c.nation2_id == initiator_id))
                    ).\
                    values(is_active=False)
                
                db.session.execute(stmt)
            
            # Create war
            war = War(
                aggressor_id=initiator_id,
                defender_id=target_id,
                start_date=datetime.utcnow(),
                is_active=True
            )
            
            db.session.add(war)
            db.session.commit()
            
            return {
                "success": True,
                "message": "War declared on the nation.",
                "relation_change": -75
            }
        
        # Example: Propose Peace
        elif action_id == 5:
            if not self.war:
                return {"success": False, "message": "Not at war with this nation."}
            
            if self.war.peace_proposed:
                return {"success": False, "message": "Peace already proposed."}
            
            # Update war with peace proposal
            self.war.peace_proposed = True
            db.session.commit()
            
            return {
                "success": True,
                "message": "Peace proposal sent.",
                "relation_change": 10
            }
        
        # Example: Cancel Alliance
        elif action_id == 6:
            if not self.alliance:
                return {"success": False, "message": "No alliance exists to cancel."}
            
            # End alliance
            self.alliance.is_active = False
            self.alliance.dissolved_date = datetime.utcnow()
            db.session.commit()
            
            return {
                "success": True,
                "message": "Alliance has been cancelled.",
                "relation_change": -50
            }
        
        # Example: Revoke Transit Rights
        elif action_id == 7:
            if not self.transit_rights:
                return {"success": False, "message": "No transit rights to revoke."}
            
            # Check if the initiator is the grantor
            if self.transit_rights.grantor_id != initiator_id:
                return {"success": False, "message": "Only the nation that granted transit rights can revoke them."}
            
            # Revoke transit rights
            stmt = transit_rights.update().\
                where(
                    (transit_rights.c.grantor_id == initiator_id) & 
                    (transit_rights.c.receiver_id == target_id)
                ).\
                values(is_active=False)
            
            db.session.execute(stmt)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Transit rights revoked.",
                "relation_change": -30
            }
        
        # Default case if action not handled
        return {"success": False, "message": "Action not implemented."}

# Import at the end to avoid circular imports
from models import Alliance, War
from data.diplomacy import DIPLOMATIC_ACTIONS, RELATION_STATES