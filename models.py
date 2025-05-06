from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for alliances between nations
alliances = Table(
    'alliances',
    db.metadata,
    Column('nation_id', Integer, ForeignKey('nation.id'), primary_key=True),
    Column('ally_id', Integer, ForeignKey('nation.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    nation = db.relationship('Nation', uselist=False, backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        # Protezione contro password_hash vuoti o malformati
        if not self.password_hash or len(self.password_hash) < 8:
            return False
        
        # Gestisci diversi formati di hash
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError as e:
            # Vecchio formato di hash bcrypt ($2b$...)
            if self.password_hash.startswith('$2b$'):
                import bcrypt
                try:
                    return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
                except Exception as e:
                    print(f"Errore bcrypt: {e}")
                    return False
            else:
                print(f"Formato hash non supportato: {self.password_hash[:10]}...")
                return False

class Nation(db.Model):
    """Nation model representing a player's country"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    founded_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    total_population = db.Column(db.Integer, default=1000000)
    
    # Location on world map (for strategic map)
    continent = db.Column(db.String(50), default="Europe")
    map_x = db.Column(db.Float, default=50.0)  # X coordinate on world map (%)
    map_y = db.Column(db.Float, default=30.0)  # Y coordinate on world map (%)
    svg_id = db.Column(db.String(50))  # ID of the SVG element on the map (e.g., "usa", "china")
    
    # Population distribution in different sectors (percentages)
    agriculture_population = db.Column(db.Float, default=30.0)  # %
    industry_population = db.Column(db.Float, default=30.0)     # %
    energy_population = db.Column(db.Float, default=15.0)       # %
    research_population = db.Column(db.Float, default=10.0)     # %
    military_population = db.Column(db.Float, default=15.0)     # %
    
    # Economic indicators
    gdp = db.Column(db.Float, default=1000000.0)
    inflation_rate = db.Column(db.Float, default=2.0)  # %
    tax_rate = db.Column(db.Float, default=20.0)       # %
    
    # Rankings (calculated based on various factors)
    economic_rank = db.Column(db.Integer, default=0)
    military_rank = db.Column(db.Integer, default=0)
    technology_rank = db.Column(db.Integer, default=0)
    overall_rank = db.Column(db.Integer, default=0)
    
    # Relationships
    resources = db.relationship('Resource', backref='nation', lazy=True)
    technologies = db.relationship('Technology', backref='nation', lazy=True)
    military = db.relationship('Military', uselist=False, backref='nation', lazy=True)
    market_items = db.relationship('MarketItem', backref='seller', lazy=True, foreign_keys='MarketItem.seller_id')
    
    # Many-to-many relationship for alliances
    allies = db.relationship(
        'Nation', 
        secondary=alliances,
        primaryjoin=(alliances.c.nation_id == id),
        secondaryjoin=(alliances.c.ally_id == id),
        backref=db.backref('allied_by', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def calculate_resource_production(self):
        """Calculate resource production based on population distribution and technology"""
        from utils.game_logic import get_production_rate, get_consumption_rate
        
        resources = Resource.query.filter_by(nation_id=self.id).first()
        if not resources:
            return
            
        # Calculate production rates
        resources.raw_materials_production = get_production_rate(self, 'raw_materials')
        resources.food_production = get_production_rate(self, 'food')
        resources.energy_production = get_production_rate(self, 'energy')
        resources.technology_production = get_production_rate(self, 'technology')
        resources.currency_production = get_production_rate(self, 'currency')
        
        # Calculate consumption rates
        resources.raw_materials_consumption = get_consumption_rate(self, 'raw_materials')
        resources.food_consumption = get_consumption_rate(self, 'food')
        resources.energy_consumption = get_consumption_rate(self, 'energy')
        
        # Save changes
        db.session.commit()
    
    def update_rankings(self):
        """Update the nation's rankings based on various metrics"""
        # This will be implemented in game_logic.py
        pass

class Resource(db.Model):
    """Resource model for tracking nation's resources"""
    id = db.Column(db.Integer, primary_key=True)
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    
    # Basic resources
    raw_materials = db.Column(db.Float, default=1000.0)
    food = db.Column(db.Float, default=1000.0)
    energy = db.Column(db.Float, default=1000.0)
    technology_points = db.Column(db.Float, default=100.0)
    currency = db.Column(db.Float, default=10000.0)
    
    # Production rates (per day)
    raw_materials_production = db.Column(db.Float, default=100.0)
    food_production = db.Column(db.Float, default=100.0)
    energy_production = db.Column(db.Float, default=100.0)
    technology_production = db.Column(db.Float, default=10.0)
    currency_production = db.Column(db.Float, default=1000.0)
    
    # Consumption rates (per day)
    raw_materials_consumption = db.Column(db.Float, default=50.0)
    food_consumption = db.Column(db.Float, default=50.0)
    energy_consumption = db.Column(db.Float, default=50.0)
    
    # Last update timestamp
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Technology(db.Model):
    """Technology model for research and development"""
    id = db.Column(db.Integer, primary_key=True)
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Military', 'Production', 'Research', 'Espionage'
    level = db.Column(db.Integer, default=0)
    max_level = db.Column(db.Integer, default=10)
    
    # Technology effects on production/consumption
    production_multiplier = db.Column(db.Float, default=1.0)
    consumption_efficiency = db.Column(db.Float, default=1.0)
    military_bonus = db.Column(db.Float, default=0.0)
    research_bonus = db.Column(db.Float, default=0.0)
    espionage_bonus = db.Column(db.Float, default=0.0)
    
    # Research progress
    research_points_required = db.Column(db.Float, nullable=False)
    research_points_current = db.Column(db.Float, default=0.0)
    researching = db.Column(db.Boolean, default=False)
    research_started = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    
    # Prereq technologies
    prerequisites = db.Column(db.String(500))  # Comma-separated list of tech IDs

class Military(db.Model):
    """Military model for defense and offense"""
    id = db.Column(db.Integer, primary_key=True)
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    
    # Military units
    infantry = db.Column(db.Integer, default=1000)
    tanks = db.Column(db.Integer, default=50)
    aircraft = db.Column(db.Integer, default=10)
    navy = db.Column(db.Integer, default=5)
    missiles = db.Column(db.Integer, default=0)
    
    # Defensive structures
    bunkers = db.Column(db.Integer, default=5)
    anti_air = db.Column(db.Integer, default=5)
    coastal_defenses = db.Column(db.Integer, default=3)
    
    # Espionage capabilities
    spies = db.Column(db.Integer, default=2)
    counter_intelligence = db.Column(db.Integer, default=1)
    max_spies = db.Column(db.Integer, default=6)  # Maximum number of spies a nation can have
    
    # Military metrics
    offensive_power = db.Column(db.Float, default=0.0)
    defensive_power = db.Column(db.Float, default=0.0)
    espionage_power = db.Column(db.Float, default=0.0)
    intel_points = db.Column(db.Integer, default=0)
    
    # Military status
    at_war = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class MarketItem(db.Model):
    """Market item for trading resources"""
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # 'raw_materials', 'food', 'energy'
    quantity = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    is_active = db.Column(db.Boolean, default=True)

class Trade(db.Model):
    """Trade record between nations"""
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    market_item_id = db.Column(db.Integer, db.ForeignKey('market_item.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    trade_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    seller = db.relationship('Nation', foreign_keys=[seller_id])
    buyer = db.relationship('Nation', foreign_keys=[buyer_id])
    market_item = db.relationship('MarketItem')

class War(db.Model):
    """War record between nations"""
    id = db.Column(db.Integer, primary_key=True)
    aggressor_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    defender_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    aggressor_victory = db.Column(db.Boolean)
    
    # War statistics
    aggressor_casualties = db.Column(db.Integer, default=0)
    defender_casualties = db.Column(db.Integer, default=0)
    resources_plundered = db.Column(db.Float, default=0.0)
    
    # Population losses
    aggressor_population_lost = db.Column(db.Integer, default=0)
    defender_population_lost = db.Column(db.Integer, default=0)
    
    # Territory changes (future implementation)
    territory_captured = db.Column(db.Float, default=0.0)  # Percentage of land taken
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    peace_proposed = db.Column(db.Boolean, default=False)
    
    # Relationships
    aggressor = db.relationship('Nation', foreign_keys=[aggressor_id])
    defender = db.relationship('Nation', foreign_keys=[defender_id])
    battle_reports = db.relationship('BattleReport', backref='war', lazy=True)
    
    def get_summary(self):
        """Return a summary of the war's outcome"""
        result = {
            'aggressor_name': self.aggressor.name,
            'defender_name': self.defender.name,
            'duration': (self.end_date - self.start_date).days if self.end_date else (datetime.utcnow() - self.start_date).days,
            'aggressor_casualties': self.aggressor_casualties,
            'defender_casualties': self.defender_casualties,
            'resources_plundered': int(self.resources_plundered),
            'aggressor_population_lost': self.aggressor_population_lost,
            'defender_population_lost': self.defender_population_lost,
            'status': 'Active' if self.is_active else 'Ended',
            'victory': 'Aggressor Victory' if self.aggressor_victory else 'Defender Victory' if self.aggressor_victory is not None else 'Ongoing'
        }
        return result

class Alliance(db.Model):
    """Alliance record for tracking alliance history"""
    id = db.Column(db.Integer, primary_key=True)
    nation1_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    nation2_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    formed_date = db.Column(db.DateTime, default=datetime.utcnow)
    dissolved_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    nation1 = db.relationship('Nation', foreign_keys=[nation1_id])
    nation2 = db.relationship('Nation', foreign_keys=[nation2_id])


class TransitRights(db.Model):
    """Transit rights between nations for military movement"""
    id = db.Column(db.Integer, primary_key=True)
    grantor_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    granted_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    grantor = db.relationship('Nation', foreign_keys=[grantor_id])
    receiver = db.relationship('Nation', foreign_keys=[receiver_id])


class DeployedSpy(db.Model):
    """Deployed spy in a foreign nation"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Owner nation and target nation
    owner_nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    target_nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    
    # Spy status
    deployment_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_strength = db.Column(db.Float, default=100.0)  # 0-100 scale, decreases over time or with risky operations
    intel_level = db.Column(db.Integer, default=0)  # Increases over time, determines intel quality
    is_active = db.Column(db.Boolean, default=True)
    is_discovered = db.Column(db.Boolean, default=False)
    
    # Spy capabilities
    specialization = db.Column(db.String(50), default='general')  # 'general', 'military', 'economic', 'technological', 'diplomatic'
    skill_level = db.Column(db.Integer, default=1)  # 1-5 scale
    
    # Relationships
    owner_nation = db.relationship('Nation', foreign_keys=[owner_nation_id], backref=db.backref('deployed_spies', lazy='dynamic'))
    target_nation = db.relationship('Nation', foreign_keys=[target_nation_id], backref=db.backref('foreign_spies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Spy {self.id} from {self.owner_nation_id} in {self.target_nation_id}>'


class SpyMission(db.Model):
    """Mission conducted by a deployed spy"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Spy executing the mission
    spy_id = db.Column(db.Integer, db.ForeignKey('deployed_spy.id'), nullable=False)
    
    # Mission details
    mission_type = db.Column(db.String(50), nullable=False)  # 'gather_intel', 'sabotage', 'steal_tech', etc.
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    success_chance = db.Column(db.Float, default=50.0)  # Percentage
    is_completed = db.Column(db.Boolean, default=False)
    is_successful = db.Column(db.Boolean)
    
    # Mission outcome
    outcome_description = db.Column(db.Text)
    intel_gained = db.Column(db.Integer, default=0)
    diplomatic_incident = db.Column(db.Boolean, default=False)
    
    # Relationship
    spy = db.relationship('DeployedSpy', backref=db.backref('missions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SpyMission {self.id} by spy {self.spy_id}>'


class SpyReport(db.Model):
    """Intelligence report generated by spies"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Report ownership
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    spy_id = db.Column(db.Integer, db.ForeignKey('deployed_spy.id'))
    mission_id = db.Column(db.Integer, db.ForeignKey('spy_mission.id'))
    
    # Report details
    target_nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    report_type = db.Column(db.String(50), nullable=False)  # 'military', 'economic', 'technological', 'diplomatic'
    intel_quality = db.Column(db.Integer, default=1)  # 1-5 scale, determines accuracy
    
    # Report content (JSON serialized)
    report_content = db.Column(db.Text)
    
    # Relationships
    nation = db.relationship('Nation', foreign_keys=[nation_id], backref=db.backref('intel_reports', lazy='dynamic'))
    target_nation = db.relationship('Nation', foreign_keys=[target_nation_id])
    spy = db.relationship('DeployedSpy', backref=db.backref('reports', lazy='dynamic'))
    mission = db.relationship('SpyMission', backref=db.backref('reports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SpyReport {self.id} for nation {self.nation_id}>'


class BattleReport(db.Model):
    """Detailed report for individual battles in a war"""
    id = db.Column(db.Integer, primary_key=True)
    war_id = db.Column(db.Integer, db.ForeignKey('war.id'), nullable=False)
    
    # Battle metadata
    battle_date = db.Column(db.DateTime, default=datetime.utcnow)
    attack_type = db.Column(db.String(50), nullable=False)  # 'infantry', 'tanks', 'aircraft', 'navy', 'missiles'
    is_attacker_victory = db.Column(db.Boolean, nullable=False)
    
    # Casualties
    attacker_casualties = db.Column(db.Integer, default=0)
    defender_casualties = db.Column(db.Integer, default=0)
    
    # Population losses
    attacker_population_lost = db.Column(db.Integer, default=0)
    defender_population_lost = db.Column(db.Integer, default=0)
    
    # Resources
    resources_plundered = db.Column(db.Float, default=0.0)
    raw_materials_plundered = db.Column(db.Float, default=0.0)
    food_plundered = db.Column(db.Float, default=0.0)
    energy_plundered = db.Column(db.Float, default=0.0)
    
    # Stats before battle
    attacker_strength = db.Column(db.Float, default=0.0)
    defender_strength = db.Column(db.Float, default=0.0)
    
    # Additional details
    battle_description = db.Column(db.Text)
    
    def get_summary(self):
        """Return a summary of the battle"""
        war = War.query.get(self.war_id)
        if not war:
            return {"error": "War not found"}
            
        return {
            'date': self.battle_date.strftime("%Y-%m-%d %H:%M"),
            'attack_type': self.attack_type.capitalize(),
            'result': 'Victory for attacker' if self.is_attacker_victory else 'Victory for defender',
            'attacker': war.aggressor.name,
            'defender': war.defender.name,
            'attacker_casualties': self.attacker_casualties,
            'defender_casualties': self.defender_casualties,
            'attacker_population_lost': self.attacker_population_lost,
            'defender_population_lost': self.defender_population_lost,
            'resources_plundered': int(self.resources_plundered),
            'description': self.battle_description
        }


class NewsArticle(db.Model):
    """News article for the global newspaper"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Article details
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))  # Short summary for previews
    
    # Categorization
    category = db.Column(db.String(50), nullable=False)  # 'market', 'war', 'diplomacy', 'technology', 'espionage', 'event'
    importance = db.Column(db.Integer, default=1)  # 1-5 scale, determines display priority
    
    # Related entities (optional)
    nation1_id = db.Column(db.Integer, db.ForeignKey('nation.id'))  # Primary nation in the article
    nation2_id = db.Column(db.Integer, db.ForeignKey('nation.id'))  # Secondary nation (if applicable)
    related_war_id = db.Column(db.Integer, db.ForeignKey('war.id'))
    related_alliance_id = db.Column(db.Integer, db.ForeignKey('alliance.id'))
    related_trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    related_technology_id = db.Column(db.Integer, db.ForeignKey('technology.id'))
    
    # Publication info
    publication_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)  # Some articles might be nation-specific
    is_featured = db.Column(db.Boolean, default=False)  # Featured articles appear on top
    
    # Relationships
    nation1 = db.relationship('Nation', foreign_keys=[nation1_id], backref=db.backref('primary_news', lazy='dynamic'))
    nation2 = db.relationship('Nation', foreign_keys=[nation2_id], backref=db.backref('secondary_news', lazy='dynamic'))
    related_war = db.relationship('War', backref=db.backref('news_articles', lazy='dynamic'))
    related_alliance = db.relationship('Alliance', backref=db.backref('news_articles', lazy='dynamic'))
    related_trade = db.relationship('Trade', backref=db.backref('news_articles', lazy='dynamic'))
    related_technology = db.relationship('Technology', backref=db.backref('news_articles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<NewsArticle {self.id}: {self.title}>'
