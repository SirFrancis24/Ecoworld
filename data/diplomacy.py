"""
Diplomacy actions and relations data for the game.
Each diplomatic action has:
- name: The name of the action
- description: A description of what the action does
- requirements: What's needed to perform this action
- effects: How it affects relations and game mechanics
- duration: How long the effects last (turns)
- cooldown: How long before action can be used again
- flavor_text: Story elements for immersion
"""

# Define the diplomatic actions available
DIPLOMATIC_ACTIONS = [
    {
        "id": 1,
        "name": "Propose Alliance",
        "description": "Propose a formal alliance with another nation.",
        "requirements": {
            "minimum_relation": 30,  # Can be done with Friendly relations or better
            "resources": {"currency": 1000},
            "technologies": []  # No tech requirements
        },
        "effects": {
            "relation_change": 40,
            "diplomatic_options": [2, 3, 6]  # Allows these additional actions
        },
        "duration": 0,  # Permanent until canceled
        "cooldown": 10,  # Turns before can be used again if broken
        "flavor_text": "An alliance forms a strong bond between nations, promising mutual aid and protection."
    },
    {
        "id": 2,
        "name": "Request Transit Rights",
        "description": "Request permission to move military units through another nation's territory.",
        "requirements": {
            "minimum_relation": 10,  # Can be done with Cordial relations or better
            "resources": {"currency": 500},
            "technologies": []
        },
        "effects": {
            "relation_change": 10,
            "transit_rights": True
        },
        "duration": 20,  # Lasts 20 turns
        "cooldown": 5,
        "flavor_text": "Transit rights allow military units to pass through foreign territory without incident."
    },
    {
        "id": 3,
        "name": "Sign Non-aggression Pact",
        "description": "A formal agreement not to attack each other.",
        "requirements": {
            "minimum_relation": -20,  # Can be done with Tense relations or better
            "resources": {"currency": 300},
            "technologies": []
        },
        "effects": {
            "relation_change": 15,
            "non_aggression": True
        },
        "duration": 30,  # Lasts 30 turns
        "cooldown": 10,
        "flavor_text": "A non-aggression pact is a promise of peace, though perhaps a tenuous one."
    },
    {
        "id": 4,
        "name": "Declare War",
        "description": "Formally declare war on another nation.",
        "requirements": {
            "maximum_relation": 100,  # Can be done regardless of relations
            "resources": {"currency": 1000, "energy": 100},
            "technologies": []
        },
        "effects": {
            "relation_change": -80,
            "war_state": True,
            "diplomatic_options": [5]  # Allows only peace proposals
        },
        "duration": 0,  # Permanent until peace
        "cooldown": 0,  # No cooldown
        "flavor_text": "War is the ultimate breakdown of diplomacy, leading to armed conflict."
    },
    {
        "id": 5,
        "name": "Propose Peace",
        "description": "Propose an end to hostilities.",
        "requirements": {
            "war_state": True,  # Can only be done during war
            "resources": {"currency": 500},
            "technologies": []
        },
        "effects": {
            "relation_change": 30,
            "war_state": False,
            "diplomatic_options": [1, 2, 3]  # Allows these actions after peace
        },
        "duration": 0,  # Peace is permanent until broken
        "cooldown": 0,
        "flavor_text": "Peace offers a chance for nations to rebuild and relations to heal."
    },
    {
        "id": 6,
        "name": "Cancel Alliance",
        "description": "Formally end an alliance with another nation.",
        "requirements": {
            "alliance_state": True,  # Can only be done if alliance exists
            "resources": {},  # No resource cost
            "technologies": []
        },
        "effects": {
            "relation_change": -50,
            "alliance_state": False,
            "diplomatic_options": [1, 2, 3, 4]  # Allows these actions after alliance ends
        },
        "duration": 0,
        "cooldown": 10,
        "flavor_text": "The dissolution of an alliance marks a significant shift in international relations."
    },
    {
        "id": 7,
        "name": "Revoke Transit Rights",
        "description": "Revoke permission for another nation to move through your territory.",
        "requirements": {
            "transit_rights_granted": True,  # Can only be done if you granted transit rights
            "resources": {},  # No resource cost
            "technologies": []
        },
        "effects": {
            "relation_change": -20,
            "transit_rights": False
        },
        "duration": 0,
        "cooldown": 5,
        "flavor_text": "Revoking transit rights shows a decline in trust between nations."
    }
]

# Define the relation states based on values
RELATION_STATES = [
    {
        "name": "Hostile",
        "range": [-100, -51],
        "description": "Open hostility exists between nations.",
        "effects": {
            "trade_modifier": 0.5,  # Reduced trade
            "diplomatic_options": [5]  # Can only propose peace
        }
    },
    {
        "name": "Unfriendly",
        "range": [-50, -21],
        "description": "Relations are poor, but not openly hostile.",
        "effects": {
            "trade_modifier": 0.7,
            "diplomatic_options": [3, 4, 5]  # Can sign non-aggression pact, declare war, or propose peace
        }
    },
    {
        "name": "Tense",
        "range": [-20, -1],
        "description": "Relations are strained but manageable.",
        "effects": {
            "trade_modifier": 0.9,
            "diplomatic_options": [2, 3, 4]  # Can request transit rights, sign non-aggression pact, or declare war
        }
    },
    {
        "name": "Neutral",
        "range": [0, 19],
        "description": "Normal diplomatic relations without special ties.",
        "effects": {
            "trade_modifier": 1.0,
            "diplomatic_options": [1, 2, 3, 4]  # All basic diplomatic options
        }
    },
    {
        "name": "Cordial",
        "range": [20, 49],
        "description": "Positive relations with some cooperation.",
        "effects": {
            "trade_modifier": 1.1,
            "diplomatic_options": [1, 2, 3]  # Alliance, transit rights, non-aggression
        }
    },
    {
        "name": "Friendly",
        "range": [50, 79],
        "description": "Strong friendly relations with close cooperation.",
        "effects": {
            "trade_modifier": 1.2,
            "diplomatic_options": [1, 2]  # Alliance, transit rights
        }
    },
    {
        "name": "Allied",
        "range": [80, 100],
        "description": "The strongest possible diplomatic ties.",
        "effects": {
            "trade_modifier": 1.3,
            "diplomatic_options": [6]  # Can only cancel alliance
        }
    }
]

# Transit treaty settings
TRANSIT_TREATY_SETTINGS = {
    "default_duration_days": 30,
    "movement_penalty_without_treaty": 2.0,  # Movement costs twice as much without treaty
    "cross_border_penalty": 10.0,  # Crossing hostile borders costs 10x movement
    "violation_relation_penalty": -30,  # Violating borders decreases relations
    "neutral_airspace_violation_penalty": -20  # Penalty for violating neutral airspace
}

# Geographical proximity settings
GEOGRAPHICAL_SETTINGS = {
    "border_nations": {
        "North America": ["Europe", "Asia"],
        "South America": ["North America", "Africa"],
        "Europe": ["North America", "Asia", "Africa"],
        "Africa": ["Europe", "Asia", "South America"],
        "Asia": ["Europe", "North America", "Africa", "Australia"],
        "Australia": ["Asia"]
    },
    "continent_positions": {
        "North America": {"x": 20, "y": 20},
        "South America": {"x": 25, "y": 60},
        "Europe": {"x": 50, "y": 20},
        "Africa": {"x": 50, "y": 55},
        "Asia": {"x": 70, "y": 25},
        "Australia": {"x": 80, "y": 65}
    }
}