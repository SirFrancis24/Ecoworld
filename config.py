import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'ecoworld-default-secret')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ecoworld.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Game configuration
    RESOURCE_UPDATE_INTERVAL = 3600  # seconds (1 hour)
    MARKET_LISTING_DURATION = 86400  # seconds (24 hours)
    
    # Default resource production rates
    DEFAULT_RAW_MATERIALS_RATE = 100
    DEFAULT_FOOD_RATE = 100
    DEFAULT_ENERGY_RATE = 100
    DEFAULT_TECHNOLOGY_RATE = 10
    DEFAULT_CURRENCY_RATE = 1000
    
    # Game parameters
    INITIAL_POPULATION = 1000000
    INITIAL_RESOURCES = 1000
    INITIAL_CURRENCY = 10000
    
    # Military unit costs
    INFANTRY_COST = {'raw_materials': 10, 'energy': 5, 'currency': 100}
    TANK_COST = {'raw_materials': 100, 'energy': 50, 'currency': 1000}
    AIRCRAFT_COST = {'raw_materials': 200, 'energy': 150, 'currency': 5000}
    NAVY_COST = {'raw_materials': 500, 'energy': 300, 'currency': 10000}
    MISSILE_COST = {'raw_materials': 300, 'energy': 200, 'currency': 7500}

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_ecoworld.db'
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

# Set the configuration based on environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
