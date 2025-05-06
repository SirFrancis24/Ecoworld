"""
Espionage mission data for the game.
Each mission has:
- name: The name of the mission
- description: A description of what the mission does
- success_rate_base: Base success rate (0.0-1.0) before modifiers
- risk_level: How dangerous the mission is (1-5)
- rewards: What you get on success
- penalties: What happens on failure
- requirements: Technologies and resources required
- flavor_text: Story elements for immersion
"""

ESPIONAGE_MISSIONS = [
    {
        "id": 1,
        "name": "Intelligence Gathering",
        "description": "Collect basic information about a target nation.",
        "success_rate_base": 0.8,  # 80% base success rate
        "risk_level": 1,  # Low risk
        "rewards": {
            "intel_points": 10,
            "revealed_info": "basic"  # Reveals basic statistics about the target
        },
        "penalties": {
            "spy_capture_risk": 0.1,  # 10% chance of spy capture
            "diplomatic_penalty": 5  # Minor diplomatic penalty if caught
        },
        "requirements": {
            "spies": 1,  # Requires 1 spy
            "resources": {
                "currency": 500
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "Our agent will blend in with the local population to gather publicly available information and make basic observations about the target nation's capabilities."
    },
    {
        "id": 2,
        "name": "Economic Espionage",
        "description": "Steal economic secrets and trade information.",
        "success_rate_base": 0.7,  # 70% base success rate
        "risk_level": 2,  # Moderate risk
        "rewards": {
            "intel_points": 20,
            "currency": 2000,  # Financial gain
            "revealed_info": "economic",  # Reveals economic data
            "technology_boost": 0.05  # Small boost to technology research
        },
        "penalties": {
            "spy_capture_risk": 0.2,  # 20% chance of spy capture
            "diplomatic_penalty": 10  # Moderate diplomatic penalty if caught
        },
        "requirements": {
            "spies": 2,  # Requires 2 spies
            "resources": {
                "currency": 1000
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "Our operatives will infiltrate financial institutions and trade networks to gather valuable economic intelligence that can be used to our advantage."
    },
    {
        "id": 3,
        "name": "Military Intelligence",
        "description": "Gather information about military capabilities and deployments.",
        "success_rate_base": 0.6,  # 60% base success rate
        "risk_level": 3,  # Significant risk
        "rewards": {
            "intel_points": 30,
            "revealed_info": "military",  # Reveals military data
            "military_advantage": 0.1  # 10% advantage in potential conflicts
        },
        "penalties": {
            "spy_capture_risk": 0.3,  # 30% chance of spy capture
            "diplomatic_penalty": 15,  # Significant diplomatic penalty if caught
            "counter_espionage_alert": True  # Target becomes more vigilant
        },
        "requirements": {
            "spies": 3,  # Requires 3 spies
            "resources": {
                "currency": 2000
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "Our agents will covertly observe military installations, troop movements, and weapons systems to assess the target's true military capabilities."
    },
    {
        "id": 4,
        "name": "Technology Theft",
        "description": "Steal research and technological secrets.",
        "success_rate_base": 0.5,  # 50% base success rate
        "risk_level": 4,  # High risk
        "rewards": {
            "intel_points": 40,
            "technology_points": 200,  # Significant tech points
            "specific_technology_boost": 0.2,  # 20% boost to a specific technology
            "revealed_info": "research"  # Reveals research data
        },
        "penalties": {
            "spy_capture_risk": 0.4,  # 40% chance of spy capture
            "diplomatic_penalty": 20,  # Major diplomatic penalty if caught
            "counter_espionage_alert": True  # Target becomes more vigilant
        },
        "requirements": {
            "spies": 3,  # Requires 3 spies
            "resources": {
                "currency": 3000
            },
            "technologies": [18]  # Requires Basic Computing
        },
        "flavor_text": "Our team of highly skilled operatives will infiltrate research facilities to acquire advanced technological secrets that could save us years of research and development."
    },
    {
        "id": 5,
        "name": "Sabotage Resources",
        "description": "Damage or destroy enemy resource production facilities.",
        "success_rate_base": 0.4,  # 40% base success rate
        "risk_level": 5,  # Very high risk
        "rewards": {
            "intel_points": 50,
            "target_resource_reduction": 0.15  # 15% reduction in target resources
        },
        "penalties": {
            "spy_capture_risk": 0.5,  # 50% chance of spy capture
            "diplomatic_penalty": 30,  # Severe diplomatic penalty if caught
            "war_risk": 0.2  # 20% chance of triggering war if caught
        },
        "requirements": {
            "spies": 4,  # Requires 4 spies
            "resources": {
                "currency": 5000
            },
            "technologies": [31]  # Requires Basic Military Technology
        },
        "flavor_text": "This covert operation aims to disable key infrastructure and production facilities, severely hampering the target nation's economic output."
    },
    {
        "id": 6,
        "name": "Diplomatic Secrets",
        "description": "Uncover diplomatic strategies and international agreements.",
        "success_rate_base": 0.6,  # 60% base success rate
        "risk_level": 3,  # Significant risk
        "rewards": {
            "intel_points": 35,
            "revealed_info": "diplomatic",  # Reveals diplomatic data
            "diplomatic_advantage": 0.15  # 15% advantage in diplomatic negotiations
        },
        "penalties": {
            "spy_capture_risk": 0.3,  # 30% chance of spy capture
            "diplomatic_penalty": 15  # Significant diplomatic penalty if caught
        },
        "requirements": {
            "spies": 2,  # Requires 2 spies
            "resources": {
                "currency": 2500
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "By infiltrating diplomatic channels and communications, our agents can reveal the true intentions and secret agreements of the target nation."
    },
    {
        "id": 7,
        "name": "Political Destabilization",
        "description": "Create internal political unrest in the target nation.",
        "success_rate_base": 0.3,  # 30% base success rate
        "risk_level": 5,  # Very high risk
        "rewards": {
            "intel_points": 60,
            "target_stability_reduction": 0.2,  # 20% reduction in political stability
            "target_productivity_reduction": 0.1  # 10% reduction in productivity
        },
        "penalties": {
            "spy_capture_risk": 0.5,  # 50% chance of spy capture
            "diplomatic_penalty": 40,  # Extreme diplomatic penalty if caught
            "war_risk": 0.3  # 30% chance of triggering war if caught
        },
        "requirements": {
            "spies": 5,  # Requires 5 spies
            "resources": {
                "currency": 8000
            },
            "counter_intelligence": 3,  # Requires counter-intelligence level
            "technologies": [34]  # Requires Electronic Warfare
        },
        "flavor_text": "This highly sensitive operation aims to exploit internal tensions to create political instability, weakening the target government's ability to function effectively."
    },
    {
        "id": 8,
        "name": "Infiltrate Research Network",
        "description": "Place a long-term agent within research institutions.",
        "success_rate_base": 0.4,  # 40% base success rate
        "risk_level": 4,  # High risk
        "rewards": {
            "intel_points": 30,
            "ongoing_technology_points": 10,  # Per turn
            "research_visibility": "Complete",  # Full visibility into research
            "technology_boost": 0.1  # 10% overall research boost
        },
        "penalties": {
            "spy_capture_risk": 0.4,  # 40% chance of spy capture
            "diplomatic_penalty": 25,  # Major diplomatic penalty if caught
            "counter_espionage_alert": True  # Target becomes more vigilant
        },
        "requirements": {
            "spies": 3,  # Requires 3 spies
            "resources": {
                "currency": 4000
            },
            "technologies": [17, 19]  # Requires Research Networks and Advanced Computing
        },
        "flavor_text": "This operation places a deep-cover agent within the target's research institutions, providing ongoing access to their latest scientific developments."
    },
    {
        "id": 9,
        "name": "Counter-Intelligence Operation",
        "description": "Identify and neutralize enemy spies in your nation.",
        "success_rate_base": 0.6,  # 60% base success rate
        "risk_level": 2,  # Moderate risk
        "rewards": {
            "intel_points": 25,
            "counter_intelligence_boost": 0.2,  # 20% boost to counter-intelligence
            "enemy_spy_capture": 0.7  # 70% chance to capture enemy spy
        },
        "penalties": {
            "spy_capture_risk": 0.1,  # 10% chance of spy capture
            "false_positives": 0.2  # 20% chance of mistakenly identifying innocent
        },
        "requirements": {
            "spies": 2,  # Requires 2 spies
            "counter_intelligence": 2,  # Requires counter-intelligence level
            "resources": {
                "currency": 2000
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "This defensive operation aims to identify, track, and neutralize foreign intelligence assets operating within our borders."
    },
    {
        "id": 10,
        "name": "Deep Cover Infiltration",
        "description": "Place an agent in a high-level government position.",
        "success_rate_base": 0.2,  # 20% base success rate
        "risk_level": 5,  # Very high risk
        "rewards": {
            "intel_points": 100,
            "government_visibility": "Complete",  # Full visibility into government
            "diplomatic_visibility": "Complete",  # Full visibility into diplomacy
            "military_visibility": "Complete",  # Full visibility into military
            "decision_influence": 0.1  # 10% chance to influence decisions
        },
        "penalties": {
            "spy_capture_risk": 0.6,  # 60% chance of spy capture
            "diplomatic_penalty": 50,  # Extreme diplomatic penalty if caught
            "war_risk": 0.4  # 40% chance of triggering war if caught
        },
        "requirements": {
            "spies": 5,  # Requires 5 spies
            "counter_intelligence": 4,  # Requires high counter-intelligence level
            "resources": {
                "currency": 10000
            },
            "technologies": [34]  # Requires Electronic Warfare
        },
        "flavor_text": "Our most ambitious and dangerous operation, this mission places a highly trained operative in a position of trust within the target government's inner circle."
    },
    {
        "id": 11,
        "name": "Disinformation Campaign",
        "description": "Spread false information to mislead enemy intelligence.",
        "success_rate_base": 0.7,  # 70% base success rate
        "risk_level": 2,  # Moderate risk
        "rewards": {
            "intel_points": 20,
            "enemy_intel_corruption": 0.3,  # 30% chance of enemy making wrong decisions
            "misdirection": "Active"  # Enemy intelligence is compromised
        },
        "penalties": {
            "spy_capture_risk": 0.2,  # 20% chance of spy capture
            "diplomatic_penalty": 10,  # Moderate diplomatic penalty if caught
            "backfire": 0.1  # 10% chance of causing self-damage
        },
        "requirements": {
            "spies": 2,  # Requires 2 spies
            "resources": {
                "currency": 3000
            },
            "technologies": [17]  # Requires Research Networks
        },
        "flavor_text": "This sophisticated operation plants carefully crafted false information that will be picked up by enemy intelligence, leading them to incorrect conclusions."
    },
    {
        "id": 12,
        "name": "Hack Financial Systems",
        "description": "Electronically infiltrate financial institutions for gain.",
        "success_rate_base": 0.4,  # 40% base success rate
        "risk_level": 4,  # High risk
        "rewards": {
            "intel_points": 30,
            "currency": 5000,  # Significant financial gain
            "financial_visibility": "Complete",  # Full visibility into finances
            "market_manipulation": 0.1  # 10% market advantage
        },
        "penalties": {
            "spy_capture_risk": 0.3,  # 30% chance of spy capture
            "diplomatic_penalty": 20,  # Major diplomatic penalty if caught
            "counter_attack": 0.2  # 20% chance of cyber counter-attack
        },
        "requirements": {
            "spies": 3,  # Requires 3 spies
            "resources": {
                "currency": 4000
            },
            "technologies": [19, 29]  # Requires Advanced Computing and Artificial Intelligence
        },
        "flavor_text": "Our cyber specialists will breach the target's financial systems, extracting funds and market intelligence while covering their tracks."
    },
    {
        "id": 13,
        "name": "Military Sabotage",
        "description": "Disable or destroy key military installations.",
        "success_rate_base": 0.3,  # 30% base success rate
        "risk_level": 5,  # Very high risk
        "rewards": {
            "intel_points": 70,
            "target_military_reduction": 0.15,  # 15% reduction in military effectiveness
            "offensive_advantage": 0.2  # 20% advantage in offensive operations
        },
        "penalties": {
            "spy_capture_risk": 0.5,  # 50% chance of spy capture
            "diplomatic_penalty": 40,  # Extreme diplomatic penalty if caught
            "war_declaration": 0.5  # 50% chance of immediate war declaration
        },
        "requirements": {
            "spies": 4,  # Requires 4 spies
            "resources": {
                "currency": 8000
            },
            "technologies": [32]  # Requires Advanced Weaponry
        },
        "flavor_text": "This high-risk operation targets critical military infrastructure, significantly reducing the enemy's capability to wage war effectively."
    },
    {
        "id": 14,
        "name": "Establish Spy Network",
        "description": "Create a long-term intelligence gathering infrastructure.",
        "success_rate_base": 0.5,  # 50% base success rate
        "risk_level": 3,  # Significant risk
        "rewards": {
            "intel_points": 40,
            "ongoing_intel": 5,  # Per turn
            "espionage_success_boost": 0.1,  # 10% better success rate for future missions
            "territorial_coverage": "Wide"  # Coverage across territory
        },
        "penalties": {
            "spy_capture_risk": 0.3,  # 30% chance of spy capture
            "diplomatic_penalty": 15,  # Significant diplomatic penalty if caught
            "network_compromise": 0.2  # 20% chance of entire network exposure
        },
        "requirements": {
            "spies": 5,  # Requires 5 spies
            "resources": {
                "currency": 5000
            },
            "technologies": []  # No tech requirements
        },
        "flavor_text": "This operation establishes a robust network of informants, safe houses, and communication channels, creating persistent intelligence gathering capabilities."
    },
    {
        "id": 15,
        "name": "Agricultural Sabotage",
        "description": "Contaminate crops or disrupt food production.",
        "success_rate_base": 0.5,  # 50% base success rate
        "risk_level": 4,  # High risk
        "rewards": {
            "intel_points": 40,
            "target_food_reduction": 0.2,  # 20% reduction in food production
            "public_unrest": 0.15  # 15% increase in public unrest
        },
        "penalties": {
            "spy_capture_risk": 0.4,  # 40% chance of spy capture
            "diplomatic_penalty": 30,  # Severe diplomatic penalty if caught
            "humanitarian_crisis": 0.3,  # 30% chance of creating humanitarian crisis
            "global_condemnation": 0.5  # 50% chance of global condemnation
        },
        "requirements": {
            "spies": 3,  # Requires 3 spies
            "resources": {
                "currency": 4000
            },
            "technologies": [24]  # Requires Basic Biotechnology
        },
        "flavor_text": "This controversial operation targets food production systems, creating scarcity that strains the target nation's stability and resources."
    }
]