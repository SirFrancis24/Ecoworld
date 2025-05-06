"""
Economic system data for the game.
Contains:
- Economic policies and their effects
- Inflation mechanics
- Population happiness factors
- Economic events
- Trade mechanics
"""

# Economic policies that players can choose
ECONOMIC_POLICIES = [
    {
        "id": 1,
        "name": "Free Market",
        "description": "Minimal government intervention with focus on private enterprise.",
        "requirements": {
            "technologies": []  # No tech requirements
        },
        "effects": {
            "gdp_growth": 0.03,  # 3% higher base GDP growth
            "tax_income": 0.8,   # 20% less tax income
            "inflation_rate": 0.02,  # 2% base inflation
            "market_efficiency": 1.2,  # 20% more efficient markets
            "research_efficiency": 1.1,  # 10% better research
            "happiness_commerce": 1.1,  # 10% happiness from commercial sector
            "happiness_equality": 0.9,  # 10% less happiness from equality
            "public_satisfaction": 0.0  # Neutral effect on public satisfaction
        },
        "flavor_text": "The government that governs least, governs best. Let the invisible hand of the market work its magic."
    },
    {
        "id": 2,
        "name": "Mixed Economy",
        "description": "Balance between government regulation and market freedom.",
        "requirements": {
            "technologies": []  # No tech requirements
        },
        "effects": {
            "gdp_growth": 0.025,  # 2.5% GDP growth
            "tax_income": 1.0,    # Normal tax income
            "inflation_rate": 0.025,  # 2.5% base inflation
            "market_efficiency": 1.0,  # Normal market efficiency
            "research_efficiency": 1.0,  # Normal research efficiency
            "happiness_commerce": 1.0,  # Normal happiness from commerce
            "happiness_equality": 1.0,  # Normal happiness from equality
            "public_satisfaction": 0.05  # Slight positive effect on public satisfaction
        },
        "flavor_text": "Taking the best aspects of multiple economic systems creates a resilient economy that can weather various challenges."
    },
    {
        "id": 3,
        "name": "Command Economy",
        "description": "Central planning with government control of major industries.",
        "requirements": {
            "technologies": []  # No tech requirements
        },
        "effects": {
            "gdp_growth": 0.02,  # 2% GDP growth (lower)
            "tax_income": 1.3,   # 30% more tax income
            "inflation_rate": 0.04,  # 4% base inflation (higher)
            "market_efficiency": 0.8,  # 20% less efficient markets
            "research_efficiency": 0.9,  # 10% less research efficiency
            "happiness_commerce": 0.8,  # 20% less happiness from commerce
            "happiness_equality": 1.2,  # 20% more happiness from equality
            "public_satisfaction": -0.05  # Slight negative effect on public satisfaction
        },
        "flavor_text": "By controlling the economy directly, we ensure resources are distributed according to the nation's needs, not profit motives."
    },
    {
        "id": 4,
        "name": "Sustainable Economy",
        "description": "Focus on environmental protection and sustainable development.",
        "requirements": {
            "technologies": [14]  # Requires Green Energy
        },
        "effects": {
            "gdp_growth": 0.02,  # 2% GDP growth (lower)
            "tax_income": 0.9,   # 10% less tax income
            "inflation_rate": 0.02,  # 2% base inflation
            "market_efficiency": 0.9,  # 10% less efficient markets
            "research_efficiency": 1.1,  # 10% better research
            "environmental_impact": 0.7,  # 30% less environmental impact
            "happiness_environment": 1.3,  # 30% more happiness from environment
            "public_satisfaction": 0.1  # Positive effect on public satisfaction
        },
        "flavor_text": "Our economy must work within planetary boundaries. Future generations depend on the choices we make today."
    },
    {
        "id": 5,
        "name": "Innovation Economy",
        "description": "Focus on technological advancement and research.",
        "requirements": {
            "technologies": [17, 18]  # Requires Research Networks and Basic Computing
        },
        "effects": {
            "gdp_growth": 0.025,  # 2.5% GDP growth
            "tax_income": 0.9,    # 10% less tax income
            "inflation_rate": 0.02,  # 2% base inflation
            "market_efficiency": 1.1,  # 10% more efficient markets
            "research_efficiency": 1.3,  # 30% better research
            "technology_points": 1.2,  # 20% more technology points
            "happiness_commerce": 1.1,  # 10% more happiness from commerce
            "public_satisfaction": 0.05  # Slight positive effect on public satisfaction
        },
        "flavor_text": "The future belongs to those who innovate. Our economy is built on creating technologies that transform how we live and work."
    },
    {
        "id": 6,
        "name": "Wartime Economy",
        "description": "Economy focused on military production and security.",
        "requirements": {
            "technologies": [31]  # Requires Basic Military Technology
        },
        "effects": {
            "gdp_growth": 0.01,  # 1% GDP growth (much lower)
            "tax_income": 1.2,   # 20% more tax income
            "inflation_rate": 0.05,  # 5% base inflation (higher)
            "market_efficiency": 0.8,  # 20% less efficient markets
            "military_production": 1.5,  # 50% more military production
            "resource_consumption": 1.3,  # 30% more resource consumption
            "happiness_security": 1.2,  # 20% more happiness from security
            "happiness_commerce": 0.8,  # 20% less happiness from commerce
            "public_satisfaction": -0.1  # Negative effect on public satisfaction
        },
        "flavor_text": "In dangerous times, a nation must prioritize its security above all else. The economy must serve the military's needs."
    },
    {
        "id": 7,
        "name": "Autarkic Economy",
        "description": "Focus on self-sufficiency and isolation from global markets.",
        "requirements": {
            "technologies": []  # No tech requirements
        },
        "effects": {
            "gdp_growth": 0.015,  # 1.5% GDP growth (lower)
            "tax_income": 1.1,    # 10% more tax income
            "inflation_rate": 0.03,  # 3% base inflation
            "market_efficiency": 0.7,  # 30% less efficient markets
            "research_efficiency": 0.9,  # 10% less research efficiency
            "resource_production": 1.2,  # 20% more resource production
            "trade_dependency": 0.6,  # 40% less trade dependency
            "happiness_security": 1.1,  # 10% more happiness from security
            "public_satisfaction": -0.05  # Slight negative effect on public satisfaction
        },
        "flavor_text": "We must be independent of foreign influence. Our nation will stand alone, relying on its own resources and industry."
    },
    {
        "id": 8,
        "name": "Export-Oriented Economy",
        "description": "Focus on international trade and export industries.",
        "requirements": {
            "technologies": []  # No tech requirements
        },
        "effects": {
            "gdp_growth": 0.035,  # 3.5% GDP growth (higher)
            "tax_income": 0.9,    # 10% less tax income
            "inflation_rate": 0.02,  # 2% base inflation
            "market_efficiency": 1.2,  # 20% more efficient markets
            "trade_income": 1.4,  # 40% more income from trade
            "trade_dependency": 1.4,  # 40% more trade dependency
            "diplomatic_influence": 1.1,  # 10% more diplomatic influence
            "public_satisfaction": 0.0  # Neutral effect on public satisfaction
        },
        "flavor_text": "Our future lies in global markets. By specializing in what we do best and trading with others, we all prosper."
    },
    {
        "id": 9,
        "name": "Knowledge Economy",
        "description": "Focus on services, information, and intellectual property.",
        "requirements": {
            "technologies": [19]  # Requires Advanced Computing
        },
        "effects": {
            "gdp_growth": 0.03,  # 3% GDP growth
            "tax_income": 1.0,   # Normal tax income
            "inflation_rate": 0.015,  # 1.5% base inflation (lower)
            "market_efficiency": 1.1,  # 10% more efficient markets
            "research_efficiency": 1.2,  # 20% better research
            "resource_consumption": 0.8,  # 20% less resource consumption
            "technology_points": 1.3,  # 30% more technology points
            "happiness_education": 1.2,  # 20% more happiness from education
            "public_satisfaction": 0.05  # Slight positive effect on public satisfaction
        },
        "flavor_text": "Information is the currency of the future. Our economy is built on ideas, services, and intellectual property."
    },
    {
        "id": 10,
        "name": "Resource Extraction Economy",
        "description": "Focus on extracting and processing natural resources.",
        "requirements": {
            "technologies": [6]  # Requires Basic Industry
        },
        "effects": {
            "gdp_growth": 0.025,  # 2.5% GDP growth
            "tax_income": 1.1,    # 10% more tax income
            "inflation_rate": 0.03,  # 3% base inflation
            "market_efficiency": 0.9,  # 10% less efficient markets
            "raw_materials_production": 1.5,  # 50% more raw materials
            "energy_production": 1.3,  # 30% more energy production
            "environmental_impact": 1.5,  # 50% more environmental impact
            "happiness_environment": 0.7,  # 30% less happiness from environment
            "public_satisfaction": -0.05  # Slight negative effect on public satisfaction
        },
        "flavor_text": "Our nation is blessed with abundant natural resources. By extracting and processing these riches, we secure our prosperity."
    }
]

# Factors affecting inflation and their relative importance
INFLATION_FACTORS = {
    "money_supply_growth": {
        "base_effect": 0.5,  # How strongly this affects inflation
        "optimal_range": [0.02, 0.04],  # 2-4% annual growth is ideal
        "danger_threshold": 0.10,  # Above 10% is dangerous
        "description": "The rate at which currency is added to the economy."
    },
    "resource_scarcity": {
        "base_effect": 0.3,
        "affected_by": ["raw_materials", "food", "energy"],
        "description": "Scarcity of essential resources drives up prices."
    },
    "production_capacity": {
        "base_effect": 0.2,
        "description": "The economy's ability to produce goods to meet demand."
    },
    "external_trade": {
        "base_effect": 0.1,
        "description": "Exposure to international markets can import inflation or deflation."
    },
    "policy_stability": {
        "base_effect": 0.1,
        "description": "Frequent policy changes create uncertainty that affects prices."
    }
}

# Effects of different inflation rates
INFLATION_EFFECTS = {
    "deflation": {
        "range": [-0.05, -0.01],
        "description": "Falling prices encourage holding money rather than spending or investing.",
        "effects": {
            "economic_growth": 0.8,  # 20% reduction in growth
            "debt_burden": 1.1,  # 10% increase in debt burden
            "consumption": 0.9,  # 10% decrease in consumption
            "unemployment": 1.2  # 20% increase in unemployment
        },
        "flavor_text": "As prices fall across the economy, consumers delay purchases, businesses cut production, and a dangerous cycle begins."
    },
    "low": {
        "range": [-0.01, 0.02],
        "description": "Slight price growth encourages spending while maintaining purchasing power.",
        "effects": {
            "economic_growth": 1.05,  # 5% boost to growth
            "debt_burden": 0.95,  # 5% decrease in debt burden
            "consumption": 1.05,  # 5% increase in consumption
            "interest_rates": 0.9  # 10% lower interest rates
        },
        "flavor_text": "A gentle rise in prices creates a healthy economic incentive to spend and invest, without eroding savings."
    },
    "moderate": {
        "range": [0.02, 0.05],
        "description": "Noticeable price increases begin to affect planning and fixed incomes.",
        "effects": {
            "economic_growth": 1.0,  # No effect on growth
            "debt_burden": 0.9,  # 10% decrease in debt burden
            "consumption": 1.0,  # No effect on consumption
            "interest_rates": 1.0  # No effect on interest rates
        },
        "flavor_text": "Citizens notice rising prices, but the economy continues to function normally as the increases remain manageable."
    },
    "high": {
        "range": [0.05, 0.1],
        "description": "Rapid price increases disrupt economic planning and erode savings.",
        "effects": {
            "economic_growth": 0.9,  # 10% reduction in growth
            "debt_burden": 0.8,  # 20% decrease in debt burden
            "consumption": 0.9,  # 10% decrease in consumption
            "interest_rates": 1.2,  # 20% higher interest rates
            "public_satisfaction": -0.1  # Negative effect on satisfaction
        },
        "flavor_text": "As inflation climbs, citizens rush to spend money before its value falls further, while businesses struggle with planning."
    },
    "very_high": {
        "range": [0.1, 0.2],
        "description": "Serious inflation forces frequent price adjustments and economic instability.",
        "effects": {
            "economic_growth": 0.7,  # 30% reduction in growth
            "debt_burden": 0.6,  # 40% decrease in debt burden
            "consumption": 0.8,  # 20% decrease in consumption
            "interest_rates": 1.5,  # 50% higher interest rates
            "public_satisfaction": -0.2  # Significant negative effect
        },
        "flavor_text": "Prices are adjusted weekly or even daily, as citizens lose confidence in the currency and the economic system."
    },
    "hyperinflation": {
        "range": [0.2, 1.0],
        "description": "Catastrophic inflation destroys the currency's value and economic function.",
        "effects": {
            "economic_growth": 0.4,  # 60% reduction in growth
            "debt_burden": 0.2,  # 80% decrease in debt burden
            "consumption": 0.5,  # 50% decrease in consumption
            "interest_rates": 2.0,  # 100% higher interest rates
            "public_satisfaction": -0.5,  # Severe negative effect
            "political_stability": 0.5  # 50% decrease in stability
        },
        "flavor_text": "Money loses value by the hour. Citizens carry cash in wheelbarrows for basic purchases, if they use the currency at all."
    }
}

# Factors affecting population happiness
POPULATION_HAPPINESS_FACTORS = {
    "economic_prosperity": {
        "weight": 0.25,
        "description": "Overall economic well-being of the population.",
        "affected_by": ["gdp_per_capita", "unemployment", "inflation"]
    },
    "public_services": {
        "weight": 0.2,
        "description": "Quality and accessibility of government services.",
        "affected_by": ["tax_rate", "infrastructure", "healthcare", "education"]
    },
    "security_situation": {
        "weight": 0.15,
        "description": "Safety from crime, war, and other threats.",
        "affected_by": ["at_war", "defensive_power", "crime_rate"]
    },
    "freedom_and_rights": {
        "weight": 0.15,
        "description": "Civil liberties and political freedoms.",
        "affected_by": ["economic_policy", "political_freedoms"]
    },
    "environmental_quality": {
        "weight": 0.1,
        "description": "State of the natural environment.",
        "affected_by": ["environmental_impact", "pollution_level", "green_spaces"]
    },
    "social_cohesion": {
        "weight": 0.1,
        "description": "Sense of community and social trust.",
        "affected_by": ["inequality", "cultural_diversity", "social_programs"]
    },
    "cultural_vibrancy": {
        "weight": 0.05,
        "description": "Arts, entertainment, and cultural expression.",
        "affected_by": ["cultural_investment", "freedom_of_expression"]
    }
}

# Effects of different happiness levels
HAPPINESS_EFFECTS = {
    "revolutionary": {
        "range": [0.0, 0.2],
        "effects": {
            "productivity": -0.3,  # 30% reduction
            "population_growth": -0.02,  # 2% population decline
            "political_stability": -0.5,  # 50% reduction in stability
            "emigration_rate": 0.05,  # 5% emigration
            "revolt_risk": 0.3  # 30% chance of revolt
        },
        "flavor_text": "The population is seething with discontent. Revolutionary groups gain widespread support as the government's legitimacy collapses."
    },
    "very_unhappy": {
        "range": [0.2, 0.4],
        "effects": {
            "productivity": -0.15,  # 15% reduction
            "population_growth": -0.01,  # 1% population decline
            "political_stability": -0.3,  # 30% reduction
            "emigration_rate": 0.03,  # 3% emigration
            "protest_frequency": "High"
        },
        "flavor_text": "Public dissatisfaction is widespread and vocal. Protests are common, and government announcements are met with skepticism or hostility."
    },
    "unhappy": {
        "range": [0.4, 0.5],
        "effects": {
            "productivity": -0.05,  # 5% reduction
            "population_growth": -0.005,  # 0.5% population decline
            "political_stability": -0.1,  # 10% reduction
            "emigration_rate": 0.01,  # 1% emigration
            "protest_frequency": "Occasional"
        },
        "flavor_text": "A sense of malaise pervades society. While most go about their business, there's underlying resentment toward the government."
    },
    "neutral": {
        "range": [0.5, 0.6],
        "effects": {
            "productivity": 0.0,  # No effect
            "population_growth": 0.0,  # No effect
            "political_stability": 0.0,  # No effect
            "emigration_rate": 0.005  # 0.5% background emigration
        },
        "flavor_text": "Most citizens neither particularly happy nor unhappy with their lives and government. They focus on their personal concerns."
    },
    "content": {
        "range": [0.6, 0.7],
        "effects": {
            "productivity": 0.05,  # 5% boost
            "population_growth": 0.005,  # 0.5% growth
            "political_stability": 0.1,  # 10% increased stability
            "emigration_rate": 0.002  # 0.2% background emigration
        },
        "flavor_text": "There's a general sense of satisfaction in society. While not everything is perfect, most feel the nation is on the right track."
    },
    "happy": {
        "range": [0.7, 0.85],
        "effects": {
            "productivity": 0.1,  # 10% boost
            "population_growth": 0.01,  # 1% growth
            "political_stability": 0.2,  # 20% increased stability
            "immigration_rate": 0.01,  # 1% immigration from outside
            "innovation_rate": 1.1  # 10% more innovation
        },
        "flavor_text": "A positive atmosphere pervades society. Citizens are optimistic about the future and generally supportive of their government."
    },
    "very_happy": {
        "range": [0.85, 1.0],
        "effects": {
            "productivity": 0.2,  # 20% boost
            "population_growth": 0.015,  # 1.5% growth
            "political_stability": 0.4,  # 40% increased stability
            "immigration_rate": 0.02,  # 2% immigration
            "innovation_rate": 1.2,  # 20% more innovation
            "national_prestige": 1.1  # 10% more prestige
        },
        "flavor_text": "The nation experiences a golden age of satisfaction and optimism. Citizens take pride in their country and its achievements."
    }
}

# Economic events that can occur
ECONOMIC_EVENTS = [
    {
        "id": 1,
        "name": "Market Boom",
        "description": "A period of rapid economic growth and market optimism.",
        "probability": 0.05,  # 5% chance each check
        "prerequisites": {
            "economic_policy": [1, 5, 8, 9],  # More likely with these policies
            "min_economic_stability": 0.6  # Requires relatively stable economy
        },
        "effects": {
            "gdp_growth": 0.03,  # 3% additional growth
            "market_efficiency": 1.2,  # 20% more efficient markets
            "public_satisfaction": 0.1  # Positive effect on satisfaction
        },
        "duration": [4, 8],  # Lasts 4-8 turns
        "flavor_text": "Optimism surges through markets as investments yield unprecedented returns. Economic indicators reach new heights across sectors."
    },
    {
        "id": 2,
        "name": "Market Recession",
        "description": "Economic contraction with rising unemployment and falling output.",
        "probability": 0.05,
        "prerequisites": {},  # Can happen to any economy
        "effects": {
            "gdp_growth": -0.03,  # 3% contraction
            "market_efficiency": 0.8,  # 20% less efficient markets
            "unemployment": 1.5,  # 50% more unemployment
            "public_satisfaction": -0.15  # Negative effect on satisfaction
        },
        "duration": [6, 12],  # Lasts 6-12 turns
        "flavor_text": "Economic activity contracts sharply as businesses fail and unemployment rises. Consumer confidence plummets in a vicious cycle."
    },
    {
        "id": 3,
        "name": "Resource Discovery",
        "description": "Discovery of valuable natural resources within national territory.",
        "probability": 0.02,
        "prerequisites": {},
        "effects": {
            "raw_materials": 5000,  # One-time bonus
            "raw_materials_production": 1.2,  # 20% more production
            "foreign_investment": 1.3,  # 30% more investment
            "public_satisfaction": 0.1  # Positive effect
        },
        "duration": 0,  # Permanent effect
        "flavor_text": "Geological surveys confirm major deposits of valuable resources, prompting celebration and a rush of investment activity."
    },
    {
        "id": 4,
        "name": "Trade Disruption",
        "description": "International incident disrupts normal trade patterns.",
        "probability": 0.04,
        "prerequisites": {},
        "effects": {
            "trade_income": 0.7,  # 30% less trade income
            "market_efficiency": 0.9,  # 10% less efficient markets
            "inflation_rate": 0.01  # 1% additional inflation
        },
        "duration": [3, 6],  # Lasts 3-6 turns
        "flavor_text": "Global shipping lanes are disrupted by conflict, natural disaster, or political crisis, causing shortages and delivery delays."
    },
    {
        "id": 5,
        "name": "Foreign Investment",
        "description": "Influx of foreign capital into domestic industries.",
        "probability": 0.04,
        "prerequisites": {
            "economic_policy": [1, 5, 8, 9],
            "min_economic_stability": 0.5
        },
        "effects": {
            "gdp_growth": 0.02,  # 2% additional growth
            "raw_materials_production": 1.1,  # 10% more production
            "technology_points": 1.1,  # 10% more tech points
            "currency": 2000  # One-time cash influx
        },
        "duration": [8, 12],
        "flavor_text": "Foreign investors recognize the potential in your nation's economy, injecting capital that creates jobs and transfers technology."
    },
    {
        "id": 6,
        "name": "Supply Chain Crisis",
        "description": "Breakdown in logistics networks disrupts production.",
        "probability": 0.03,
        "prerequisites": {},
        "effects": {
            "raw_materials_production": 0.8,  # 20% less production
            "food_production": 0.9,  # 10% less food
            "inflation_rate": 0.02,  # 2% additional inflation
            "public_satisfaction": -0.05  # Negative effect
        },
        "duration": [3, 8],
        "flavor_text": "Critical components fail to reach factories, while food and goods sit in warehouses unable to reach consumers."
    },
    {
        "id": 7,
        "name": "Technological Breakthrough",
        "description": "Major technological innovation with wide economic impact.",
        "probability": 0.03,
        "prerequisites": {
            "economic_policy": [5, 9],
            "min_technology_level": 15
        },
        "effects": {
            "productivity": 1.15,  # 15% more productivity
            "research_efficiency": 1.2,  # 20% better research
            "technology_points": 500,  # One-time bonus
            "public_satisfaction": 0.1  # Positive effect
        },
        "duration": [8, 12],
        "flavor_text": "A breakthrough innovation transforms multiple industries, creating new opportunities and efficiencies across the economy."
    },
    {
        "id": 8,
        "name": "Currency Crisis",
        "description": "Rapid devaluation of the national currency.",
        "probability": 0.02,
        "prerequisites": {
            "max_economic_stability": 0.4,  # Only happens in unstable economies
            "inflation_threshold": 0.06  # Requires high inflation
        },
        "effects": {
            "inflation_rate": 0.1,  # 10% additional inflation
            "foreign_debt_burden": 1.5,  # 50% more debt burden
            "market_efficiency": 0.7,  # 30% less efficient markets
            "public_satisfaction": -0.2  # Significant negative effect
        },
        "duration": [6, 10],
        "flavor_text": "Confidence in the national currency collapses as investors flee, causing rapid devaluation and financial panic."
    },
    {
        "id": 9,
        "name": "Agricultural Boom",
        "description": "Exceptional harvests and agricultural productivity.",
        "probability": 0.04,
        "prerequisites": {},
        "effects": {
            "food_production": 1.3,  # 30% more food
            "food": 2000,  # One-time bonus
            "public_satisfaction": 0.05  # Positive effect
        },
        "duration": [2, 4],  # Relatively short-lived
        "flavor_text": "Ideal weather conditions and improved farming techniques combine to create record harvests across agricultural regions."
    },
    {
        "id": 10,
        "name": "Agricultural Failure",
        "description": "Crop failures and food shortages.",
        "probability": 0.03,
        "prerequisites": {},
        "effects": {
            "food_production": 0.7,  # 30% less food
            "inflation_rate": 0.01,  # 1% additional inflation (food prices)
            "public_satisfaction": -0.1  # Negative effect
        },
        "duration": [2, 4],
        "flavor_text": "Drought, disease, or other calamities devastate crops, leading to food shortages and price spikes for basic necessities."
    },
    {
        "id": 11,
        "name": "Energy Crisis",
        "description": "Severe shortage of energy resources.",
        "probability": 0.03,
        "prerequisites": {},
        "effects": {
            "energy_production": 0.7,  # 30% less energy
            "productivity": 0.9,  # 10% less productivity
            "inflation_rate": 0.02,  # 2% additional inflation
            "public_satisfaction": -0.1  # Negative effect
        },
        "duration": [4, 8],
        "flavor_text": "Energy shortages force rolling blackouts, while transportation and industry struggle with limited fuel supplies."
    },
    {
        "id": 12,
        "name": "Consumer Boom",
        "description": "Surge in consumer spending and confidence.",
        "probability": 0.04,
        "prerequisites": {
            "min_economic_stability": 0.6,
            "min_happiness": 0.6
        },
        "effects": {
            "gdp_growth": 0.02,  # 2% additional growth
            "tax_income": 1.1,  # 10% more tax income
            "currency_circulation": 1.2  # 20% more currency circulation
        },
        "duration": [3, 6],
        "flavor_text": "Consumer confidence surges as citizens open their wallets, creating a virtuous cycle of spending and economic activity."
    },
    {
        "id": 13,
        "name": "Infrastructure Breakthrough",
        "description": "Major improvements to national infrastructure.",
        "probability": 0.02,
        "prerequisites": {
            "min_economic_stability": 0.5,
            "infrastructure_investment": True
        },
        "effects": {
            "productivity": 1.1,  # 10% more productivity
            "market_efficiency": 1.1,  # 10% more efficient markets
            "public_satisfaction": 0.1  # Positive effect
        },
        "duration": 0,  # Permanent effect
        "flavor_text": "The completion of major infrastructure projects connects regions and reduces costs, creating lasting economic benefits."
    },
    {
        "id": 14,
        "name": "Brain Drain",
        "description": "Exodus of highly skilled workers to other nations.",
        "probability": 0.02,
        "prerequisites": {
            "max_happiness": 0.5,
            "max_economic_stability": 0.5
        },
        "effects": {
            "research_efficiency": 0.9,  # 10% worse research
            "productivity": 0.95,  # 5% less productivity
            "innovation_rate": 0.9,  # 10% less innovation
            "public_satisfaction": -0.05  # Negative effect
        },
        "duration": [8, 16],  # Long-lasting problem
        "flavor_text": "The nation's brightest minds seek opportunities elsewhere, depriving the economy of talent and innovation."
    },
    {
        "id": 15,
        "name": "Environmental Disaster",
        "description": "Major environmental catastrophe affecting economic activity.",
        "probability": 0.02,
        "prerequisites": {
            "environmental_degradation": True  # More likely with poor environmental policy
        },
        "effects": {
            "raw_materials_production": 0.8,  # 20% less production
            "food_production": 0.8,  # 20% less food
            "public_satisfaction": -0.15,  # Significant negative effect
            "cleanup_cost": 5000  # One-time cost
        },
        "duration": [5, 10],
        "flavor_text": "A major environmental disaster contaminates resources, displaces populations, and requires costly cleanup and reconstruction."
    },
    {
        "id": 16,
        "name": "Foreign Aid",
        "description": "Receipt of significant foreign assistance.",
        "probability": 0.02,
        "prerequisites": {
            "diplomatic_relations": "Positive",
            "max_economic_stability": 0.4  # More likely for struggling economies
        },
        "effects": {
            "currency": 3000,  # One-time bonus
            "diplomatic_relations": 1.1,  # 10% better relations
            "public_satisfaction": 0.05  # Positive effect
        },
        "duration": [4, 8],
        "flavor_text": "International partners provide substantial assistance, demonstrating solidarity and helping stabilize the economy."
    },
    {
        "id": 17,
        "name": "Industrial Accident",
        "description": "Major industrial disaster disrupting production.",
        "probability": 0.03,
        "prerequisites": {
            "economic_policy": [1, 3, 6, 10],  # More likely with these policies
            "safety_regulations": "Low"
        },
        "effects": {
            "raw_materials_production": 0.9,  # 10% less production
            "public_satisfaction": -0.1,  # Negative effect
            "cleanup_cost": 2000  # One-time cost
        },
        "duration": [2, 5],
        "flavor_text": "A catastrophic failure at a major industrial facility causes loss of life, environmental damage, and production disruptions."
    },
    {
        "id": 18,
        "name": "Economic Sanctions",
        "description": "International economic penalties imposed on your nation.",
        "probability": 0.02,
        "prerequisites": {
            "diplomatic_relations": "Negative",
            "international_pariah": True
        },
        "effects": {
            "trade_income": 0.7,  # 30% less trade income
            "foreign_investment": 0.6,  # 40% less investment
            "market_efficiency": 0.9,  # 10% less efficient markets
            "public_satisfaction": -0.1  # Negative effect
        },
        "duration": [10, 20],  # Long-lasting problem
        "flavor_text": "International condemnation translates into concrete economic penalties, isolating your nation from global markets."
    },
    {
        "id": 19,
        "name": "Black Market Surge",
        "description": "Growth of unofficial economic activity outside government control.",
        "probability": 0.03,
        "prerequisites": {
            "max_economic_stability": 0.4,
            "max_government_effectiveness": 0.5
        },
        "effects": {
            "tax_income": 0.9,  # 10% less tax income
            "market_efficiency": 0.95,  # 5% less efficient markets
            "crime_rate": 1.2,  # 20% more crime
            "resource_leakage": 0.05  # 5% of resources diverted
        },
        "duration": [6, 12],
        "flavor_text": "As trust in official institutions falters, parallel markets emerge where goods, services, and currency change hands unofficially."
    },
    {
        "id": 20,
        "name": "Economic Golden Age",
        "description": "Period of exceptional prosperity and opportunity.",
        "probability": 0.01,  # Very rare
        "prerequisites": {
            "min_economic_stability": 0.8,
            "min_happiness": 0.8,
            "min_diplomatic_standing": 0.7
        },
        "effects": {
            "gdp_growth": 0.04,  # 4% additional growth
            "productivity": 1.2,  # 20% more productivity
            "innovation_rate": 1.3,  # 30% more innovation
            "public_satisfaction": 0.2,  # Significant positive effect
            "national_prestige": 1.2  # 20% more prestige
        },
        "duration": [8, 16],
        "flavor_text": "A remarkable convergence of factors creates a period of historic prosperity, technological advancement, and cultural flourishing."
    }
]