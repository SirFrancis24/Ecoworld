"""
Technology tree data for the game.
Each technology has:
- name: The name of the technology
- description: A description of what the technology does
- category: The category of technology (Production, Military, Energy, Research, etc.)
- level: The initial level (usually 0 until researched)
- max_level: The maximum level that can be researched
- prerequisites: List of technology IDs that must be researched first
- research_points_required: Base points required for research
- effects: Dictionary of effects this technology provides
- flavor_text: Historical/fictional background for immersion
"""

TECHNOLOGIES = [
    # Agriculture Technologies
    {
        "id": 1,
        "name": "Basic Agriculture",
        "description": "Fundamental farming techniques that increase food production.",
        "category": "Agriculture",
        "level": 0,
        "max_level": 5,
        "prerequisites": [],
        "research_points_required": 100,
        "effects": {
            "food_production": 1.1,  # 10% increase
        },
        "flavor_text": "The development of agriculture was one of humanity's first great innovations, allowing settlements to grow and civilizations to flourish."
    },
    {
        "id": 2,
        "name": "Irrigation Systems",
        "description": "Water management systems that enhance crop growth.",
        "category": "Agriculture",
        "level": 0,
        "max_level": 5,
        "prerequisites": [1],  # Requires Basic Agriculture
        "research_points_required": 200,
        "effects": {
            "food_production": 1.15,
            "water_consumption": 1.1
        },
        "flavor_text": "The control of water through irrigation transformed arid regions into fertile farmland, expanding the reach of agriculture."
    },
    {
        "id": 3,
        "name": "Advanced Crop Rotation",
        "description": "Scientific crop rotation techniques that maximize soil fertility.",
        "category": "Agriculture",
        "level": 0,
        "max_level": 3,
        "prerequisites": [2],  # Requires Irrigation Systems
        "research_points_required": 300,
        "effects": {
            "food_production": 1.2,
            "land_use_efficiency": 1.1
        },
        "flavor_text": "By carefully planning the sequence of crops, farmers discovered they could maintain soil health while increasing overall yields."
    },
    {
        "id": 4,
        "name": "Vertical Farming",
        "description": "Multi-level agricultural techniques that maximize land usage.",
        "category": "Agriculture",
        "level": 0,
        "max_level": 5,
        "prerequisites": [3, 14],  # Requires Advanced Crop Rotation and Green Energy
        "research_points_required": 800,
        "effects": {
            "food_production": 1.25,
            "land_use_efficiency": 1.5,
            "energy_consumption": 1.2
        },
        "flavor_text": "As urban areas expanded, the need to produce food in limited spaces led to the development of vertical farming, which stacked growing areas on top of each other."
    },
    {
        "id": 5,
        "name": "Genetically Optimized Crops",
        "description": "Bioengineered crops with enhanced yield and resistance.",
        "category": "Agriculture",
        "level": 0,
        "max_level": 4,
        "prerequisites": [3, 24],  # Requires Advanced Crop Rotation and Basic Biotechnology
        "research_points_required": 1000,
        "effects": {
            "food_production": 1.5,
            "resource_consumption": 0.9
        },
        "flavor_text": "The application of genetic engineering to agriculture created crops with unprecedented efficiency, resilience, and nutritional value."
    },

    # Industry Technologies
    {
        "id": 6,
        "name": "Basic Industry",
        "description": "Fundamental industrial techniques for manufacturing.",
        "category": "Industry",
        "level": 0,
        "max_level": 5,
        "prerequisites": [],
        "research_points_required": 100,
        "effects": {
            "raw_materials_production": 1.1
        },
        "flavor_text": "The organization of labor into specialized factories enabled the mass production of goods, transforming society."
    },
    {
        "id": 7,
        "name": "Advanced Materials",
        "description": "Improved materials science for better manufacturing.",
        "category": "Industry",
        "level": 0,
        "max_level": 4,
        "prerequisites": [6],  # Requires Basic Industry
        "research_points_required": 250,
        "effects": {
            "raw_materials_production": 1.15,
            "resource_consumption": 0.95
        },
        "flavor_text": "The development of new materials with specific properties opened possibilities previously thought impossible in construction, manufacturing, and technology."
    },
    {
        "id": 8,
        "name": "Automated Assembly",
        "description": "Robotics and automation in manufacturing processes.",
        "category": "Industry",
        "level": 0,
        "max_level": 5,
        "prerequisites": [7, 18],  # Requires Advanced Materials and Basic Computing
        "research_points_required": 600,
        "effects": {
            "raw_materials_production": 1.3,
            "energy_consumption": 1.1,
            "productivity": 1.2
        },
        "flavor_text": "When machines began assembling other machines, a new era of productivity was born, though not without societal implications."
    },
    {
        "id": 9,
        "name": "Nanotechnology",
        "description": "Molecular-level manufacturing capabilities.",
        "category": "Industry",
        "level": 0,
        "max_level": 5,
        "prerequisites": [8, 19],  # Requires Automated Assembly and Advanced Computing
        "research_points_required": 1200,
        "effects": {
            "raw_materials_production": 1.5,
            "resource_consumption": 0.8,
            "technology_points": 1.2
        },
        "flavor_text": "The ability to manipulate matter at the atomic scale revolutionized manufacturing, medicine, and materials science."
    },
    {
        "id": 10,
        "name": "Self-Replicating Systems",
        "description": "Manufacturing systems that can build copies of themselves.",
        "category": "Industry",
        "level": 0,
        "max_level": 3,
        "prerequisites": [9, 29],  # Requires Nanotechnology and Artificial Intelligence
        "research_points_required": 2000,
        "effects": {
            "raw_materials_production": 2.0,
            "productivity": 1.5,
            "technology_points": 1.3
        },
        "flavor_text": "When machines gained the ability to reproduce themselves, humanity crossed a threshold into a new economic paradigm."
    },

    # Energy Technologies
    {
        "id": 11,
        "name": "Basic Energy Production",
        "description": "Fundamental power generation techniques.",
        "category": "Energy",
        "level": 0,
        "max_level": 5,
        "prerequisites": [],
        "research_points_required": 100,
        "effects": {
            "energy_production": 1.1
        },
        "flavor_text": "The harnessing of energy—first from animals, then from combustion—drove humanity's advancement from its earliest days."
    },
    {
        "id": 12,
        "name": "Fossil Fuel Optimization",
        "description": "Enhanced extraction and usage of fossil fuels.",
        "category": "Energy",
        "level": 0,
        "max_level": 3,
        "prerequisites": [11],  # Requires Basic Energy Production
        "research_points_required": 200,
        "effects": {
            "energy_production": 1.2,
            "environmental_impact": 1.2  # Negative effect
        },
        "flavor_text": "Though ultimately unsustainable, fossil fuels provided the energy that powered industrial civilization for centuries."
    },
    {
        "id": 13,
        "name": "Nuclear Fission",
        "description": "Power generation through nuclear fission reactions.",
        "category": "Energy",
        "level": 0,
        "max_level": 5,
        "prerequisites": [11, 12],  # Requires Basic Energy Production AND Fossil Fuel Optimization
        "research_points_required": 500,
        "effects": {
            "energy_production": 1.4,
            "environmental_impact": 1.1,  # Slight negative effect
            "risk_factor": 1.2  # Increased risk
        },
        "flavor_text": "The splitting of atoms released unprecedented amounts of energy, though with significant challenges in safety and waste management."
    },
    {
        "id": 14,
        "name": "Green Energy",
        "description": "Renewable energy sources like solar and wind.",
        "category": "Energy",
        "level": 0,
        "max_level": 5,
        "prerequisites": [11],  # Requires Basic Energy Production
        "research_points_required": 400,
        "effects": {
            "energy_production": 1.3,
            "environmental_impact": 0.9,  # Positive effect
            "happiness": 1.05  # Increased happiness
        },
        "flavor_text": "The transition to energy sources that could be sustained indefinitely marked a crucial step in humanity's relationship with its planetary home."
    },
    {
        "id": 15,
        "name": "Fusion Power",
        "description": "Energy generation through nuclear fusion.",
        "category": "Energy",
        "level": 0,
        "max_level": 5,
        "prerequisites": [13, 14, 28],  # Requires Nuclear Fission, Green Energy, and Advanced Physics
        "research_points_required": 2000,
        "effects": {
            "energy_production": 2.0,
            "environmental_impact": 0.8,
            "research_efficiency": 1.1
        },
        "flavor_text": "The achievement of sustained fusion power fulfilled a dream dating back to the 20th century, providing nearly limitless clean energy."
    },

    # Research Technologies
    {
        "id": 16,
        "name": "Scientific Method",
        "description": "Systematic approach to scientific research and discovery.",
        "category": "Research",
        "level": 0,
        "max_level": 3,
        "prerequisites": [],
        "research_points_required": 150,
        "effects": {
            "research_efficiency": 1.1,
            "technology_points": 1.1
        },
        "flavor_text": "The formalization of observation, hypothesis, experimentation, and analysis accelerated humanity's acquisition of knowledge."
    },
    {
        "id": 17,
        "name": "Research Networks",
        "description": "Collaborative research infrastructure for knowledge sharing.",
        "category": "Research",
        "level": 0,
        "max_level": 4,
        "prerequisites": [16],  # Requires Scientific Method
        "research_points_required": 300,
        "effects": {
            "research_efficiency": 1.15,
            "technology_points": 1.15,
            "diplomatic_influence": 1.05
        },
        "flavor_text": "The recognition that science advances faster when researchers collaborate led to the creation of global networks for sharing knowledge."
    },
    {
        "id": 18,
        "name": "Basic Computing",
        "description": "Early computational systems for data processing.",
        "category": "Research",
        "level": 0,
        "max_level": 3,
        "prerequisites": [16],  # Requires Scientific Method
        "research_points_required": 400,
        "effects": {
            "research_efficiency": 1.2,
            "technology_points": 1.1,
            "productivity": 1.1
        },
        "flavor_text": "The automation of calculation transformed research, business, and eventually nearly every aspect of society."
    },
    {
        "id": 19,
        "name": "Advanced Computing",
        "description": "Sophisticated computational systems with enhanced capabilities.",
        "category": "Research",
        "level": 0,
        "max_level": 5,
        "prerequisites": [18],  # Requires Basic Computing
        "research_points_required": 800,
        "effects": {
            "research_efficiency": 1.3,
            "technology_points": 1.2,
            "productivity": 1.2,
            "espionage_power": 1.1
        },
        "flavor_text": "As computing power increased exponentially, the range of problems that could be solved through simulation and analysis grew accordingly."
    },
    {
        "id": 20,
        "name": "Quantum Computing",
        "description": "Computing based on quantum mechanical phenomena.",
        "category": "Research",
        "level": 0,
        "max_level": 5,
        "prerequisites": [19, 28],  # Requires Advanced Computing and Advanced Physics
        "research_points_required": 1500,
        "effects": {
            "research_efficiency": 1.5,
            "technology_points": 1.3,
            "espionage_power": 1.2,
            "counter_intelligence": 1.2
        },
        "flavor_text": "When computation harnessed the strange properties of quantum mechanics, problems previously considered intractable became solvable."
    },

    # Biology Technologies
    {
        "id": 21,
        "name": "Advanced Medicine",
        "description": "Improved medical treatments and healthcare systems.",
        "category": "Biology",
        "level": 0,
        "max_level": 5,
        "prerequisites": [16],  # Requires Scientific Method
        "research_points_required": 300,
        "effects": {
            "population_growth": 1.1,
            "happiness": 1.05
        },
        "flavor_text": "The application of scientific principles to medicine transformed healthcare from superstition to science, dramatically extending human lifespans."
    },
    {
        "id": 22,
        "name": "Synthetic Biology",
        "description": "Engineering of biological systems for specific purposes.",
        "category": "Biology",
        "level": 0,
        "max_level": 4,
        "prerequisites": [21, 17],  # Requires Advanced Medicine and Research Networks
        "research_points_required": 600,
        "effects": {
            "food_production": 1.1,
            "raw_materials_production": 1.1,
            "population_growth": 1.05
        },
        "flavor_text": "The ability to design and construct biological systems with novel functions opened new frontiers in medicine, agriculture, and manufacturing."
    },
    {
        "id": 23,
        "name": "Genetic Engineering",
        "description": "Manipulation of genetic material to modify organisms.",
        "category": "Biology",
        "level": 0,
        "max_level": 5,
        "prerequisites": [22],  # Requires Synthetic Biology
        "research_points_required": 800,
        "effects": {
            "food_production": 1.15,
            "population_growth": 1.1,
            "research_efficiency": 1.05
        },
        "flavor_text": "Once humanity gained the ability to edit the code of life itself, profound ethical questions arose alongside unprecedented opportunities."
    },
    {
        "id": 24,
        "name": "Basic Biotechnology",
        "description": "Applied biology for industrial and agricultural applications.",
        "category": "Biology",
        "level": 0,
        "max_level": 3,
        "prerequisites": [22],  # Requires Synthetic Biology
        "research_points_required": 700,
        "effects": {
            "food_production": 1.2,
            "raw_materials_production": 1.1,
            "resource_consumption": 0.95
        },
        "flavor_text": "The use of living systems for industrial processes created more efficient, sustainable approaches to manufacturing and agriculture."
    },
    {
        "id": 25,
        "name": "Longevity Treatments",
        "description": "Medical techniques to extend healthy human lifespan.",
        "category": "Biology",
        "level": 0,
        "max_level": 5,
        "prerequisites": [23, 24],  # Requires Genetic Engineering and Basic Biotechnology
        "research_points_required": 1200,
        "effects": {
            "population_growth": 1.2,
            "happiness": 1.1,
            "productivity": 1.1
        },
        "flavor_text": "As the mysteries of aging began to be unraveled, the dream of significantly extending healthy human lifespan became reality."
    },

    # Physics Technologies
    {
        "id": 26,
        "name": "Basic Physics",
        "description": "Fundamental understanding of physical laws.",
        "category": "Physics",
        "level": 0,
        "max_level": 3,
        "prerequisites": [16],  # Requires Scientific Method
        "research_points_required": 200,
        "effects": {
            "research_efficiency": 1.1,
            "energy_production": 1.05
        },
        "flavor_text": "The systematic study of nature's fundamental forces and particles provided the foundation for countless technological innovations."
    },
    {
        "id": 27,
        "name": "Material Science",
        "description": "Study and development of new materials with specific properties.",
        "category": "Physics",
        "level": 0,
        "max_level": 5,
        "prerequisites": [26],  # Requires Basic Physics
        "research_points_required": 400,
        "effects": {
            "raw_materials_production": 1.15,
            "resource_consumption": 0.95,
            "military_strength": 1.05
        },
        "flavor_text": "The creation of materials with properties not found in nature—from superconductors to metamaterials—continually expanded technological possibilities."
    },
    {
        "id": 28,
        "name": "Advanced Physics",
        "description": "Deep understanding of quantum mechanics and relativity.",
        "category": "Physics",
        "level": 0,
        "max_level": 5,
        "prerequisites": [26, 19],  # Requires Basic Physics and Advanced Computing
        "research_points_required": 800,
        "effects": {
            "research_efficiency": 1.2,
            "energy_production": 1.1,
            "technology_points": 1.1
        },
        "flavor_text": "The exploration of reality at its most fundamental levels revealed a universe stranger and more wonderful than anyone had imagined."
    },
    {
        "id": 29,
        "name": "Artificial Intelligence",
        "description": "Systems with human-like cognitive abilities.",
        "category": "Physics",
        "level": 0,
        "max_level": 5,
        "prerequisites": [19, 28],  # Requires Advanced Computing and Advanced Physics
        "research_points_required": 1000,
        "effects": {
            "research_efficiency": 1.4,
            "productivity": 1.3,
            "espionage_power": 1.2,
            "counter_intelligence": 1.1
        },
        "flavor_text": "The creation of machines that could think—in ways both similar to and different from humans—was perhaps the most transformative technological achievement in history."
    },
    {
        "id": 30,
        "name": "Space-Time Manipulation",
        "description": "Technologies to manipulate spacetime for practical applications.",
        "category": "Physics",
        "level": 0,
        "max_level": 3,
        "prerequisites": [28, 29],  # Requires Advanced Physics and Artificial Intelligence
        "research_points_required": 2500,
        "effects": {
            "research_efficiency": 1.5,
            "energy_production": 1.3,
            "military_strength": 1.2,
            "defensive_power": 1.2
        },
        "flavor_text": "The ability to manipulate the fabric of spacetime itself—once considered purely theoretical—opened possibilities previously relegated to science fiction."
    },

    # Military Technologies
    {
        "id": 31,
        "name": "Basic Military Technology",
        "description": "Fundamental military equipment and tactics.",
        "category": "Military",
        "level": 0,
        "max_level": 5,
        "prerequisites": [],
        "research_points_required": 150,
        "effects": {
            "military_strength": 1.1,
            "defensive_power": 1.1
        },
        "flavor_text": "The development of specialized tools for warfare has been a constant throughout human history, driving technological innovation along with tragic destruction."
    },
    {
        "id": 32,
        "name": "Advanced Weaponry",
        "description": "Improved weapons with greater firepower and precision.",
        "category": "Military",
        "level": 0,
        "max_level": 5,
        "prerequisites": [31],  # Requires Basic Military Technology
        "research_points_required": 300,
        "effects": {
            "military_strength": 1.2,
            "offensive_power": 1.15
        },
        "flavor_text": "The ongoing race to develop more effective weapons has been one of the primary drivers of technological research and development."
    },
    {
        "id": 33,
        "name": "Defensive Systems",
        "description": "Advanced defensive technologies to protect territory.",
        "category": "Military",
        "level": 0,
        "max_level": 5,
        "prerequisites": [31],  # Requires Basic Military Technology
        "research_points_required": 300,
        "effects": {
            "defensive_power": 1.2,
            "counter_intelligence": 1.1
        },
        "flavor_text": "Throughout history, every advance in offensive capability has sparked corresponding innovation in defense, from castle walls to missile shields."
    },
    {
        "id": 34,
        "name": "Electronic Warfare",
        "description": "Technology for disrupting enemy communications and systems.",
        "category": "Military",
        "level": 0,
        "max_level": 4,
        "prerequisites": [31, 18],  # Requires Basic Military Technology and Basic Computing
        "research_points_required": 500,
        "effects": {
            "espionage_power": 1.2,
            "counter_intelligence": 1.15,
            "offensive_power": 1.1
        },
        "flavor_text": "As societies became increasingly dependent on electronic systems, the ability to disrupt those systems became a powerful military capability."
    },
    {
        "id": 35,
        "name": "Advanced Military AI",
        "description": "AI systems designed for military applications.",
        "category": "Military",
        "level": 0,
        "max_level": 5,
        "prerequisites": [32, 33, 29],  # Requires Advanced Weaponry, Defensive Systems, and Artificial Intelligence
        "research_points_required": 1200,
        "effects": {
            "military_strength": 1.3,
            "offensive_power": 1.2,
            "defensive_power": 1.2,
            "espionage_power": 1.1
        },
        "flavor_text": "The integration of artificial intelligence into military operations raised profound questions about the future of warfare and human control over lethal force."
    }
]