"""
World lore and background for the game.
Contains the fictional history, geopolitics, and context that frames the game world.
"""

WORLD_HISTORY = """
# The World of EcoWorld

## The Great Divergence (2030-2040)

The 2030s marked a period of unprecedented global change. What historians now call "The Great Divergence" began with a series of cascading crises: climate disasters, resource wars, and technological disruptions that collectively shattered the old international order.

As traditional power structures collapsed, nation-states fragmented along cultural, economic, and ideological lines. The era of superpowers gave way to a more diverse global landscape with hundreds of independent nations, each seeking to carve out their path in a chaotic world.

## The New Foundations (2040-2050)

From the ashes of the old order, new political entities emerged. Some were built around resource-rich territories, others around technological centers, and still others around cultural or religious identities. What they shared was a fierce commitment to independence in a world without overarching authorities.

During this period, the Consortium of Sovereign Nations (CSN) was established – not as a global government but as a minimal forum for resolving disputes and establishing basic rules for international engagement. Unlike its predecessors, the CSN was designed with limited powers, respecting the hard-won sovereignty of its member states.

## The Current Era (2050-Present)

Today's world is characterized by dynamic competition and cooperation between nations of vastly different sizes, resources, and ideologies. Without dominant superpowers to impose order, international relations have become more fluid, with shifting alliances and rivalries creating a complex geopolitical landscape.

Technology has advanced in unexpected ways, diverging along different paths as nations prioritized solutions to their particular challenges. Some focused on biotechnology to address food security, others on energy independence, and still others on military technology for defense in an uncertain world.

The global economy has become more regionalized, with trading blocs forming around geographical proximity and resource complementarity. While global trade continues, nations place greater emphasis on self-sufficiency in critical sectors, a lesson learned from the supply chain collapses of the Great Divergence.

The past decade has been relatively peaceful compared to the chaos of the Great Divergence, but tensions are rising as nations compete for dwindling resources and strategic advantage. Many observers fear that the world stands at another inflection point, where today's rivalries could transform into tomorrow's conflicts.

As a leader of a newly-established nation, you enter this world of opportunity and peril. Your decisions will not only shape the destiny of your people but could influence the trajectory of this new global era.
"""

REGIONAL_DESCRIPTIONS = {
    "Northern Hemisphere Alliance": {
        "description": """
        The Northern Hemisphere Alliance (NHA) comprises nations in the former territories of North America, Europe, and parts of Asia. These countries generally share commitment to technological innovation and free markets, though with varying degrees of social welfare systems.
        
        NHA nations typically have advanced industrial bases, strong research capabilities, and well-developed infrastructure, but face challenges from aging populations and resource limitations. Their economies are increasingly service-oriented and digital, with manufacturing shifting to automated processes.
        
        Relations within the alliance are generally cooperative, with free trade agreements and joint research initiatives, though competition for leadership positions creates occasional tensions.
        """,
        "dominant_resources": ["technology_points", "energy"],
        "scarce_resources": ["raw_materials", "food"],
        "common_technologies": [5, 9, 14, 18, 21, 25],  # IDs from technologies.py
        "common_economic_policies": [1, 2, 5, 9],  # IDs from economy.py
        "regional_tensions": 0.4  # 0.0-1.0 scale, with 1.0 being highest
    },
    "Pan-Pacific Cooperation": {
        "description": """
        The Pan-Pacific Cooperation (PPC) consists of coastal nations around the Pacific Rim, including parts of East Asia, Oceania, and the Americas' western coasts. These nations built their prosperity on trade networks and maritime resources.
        
        PPC countries excel in logistics, shipbuilding, and aquatic technologies. They've developed some of the world's most efficient port systems and innovative aquaculture methods. Their economies typically blend state coordination with entrepreneurial activity.
        
        While unified by shared maritime interests, historical rivalries and territorial disputes over resource-rich seas create ongoing tensions within the Cooperation.
        """,
        "dominant_resources": ["food", "raw_materials"],
        "scarce_resources": ["energy"],
        "common_technologies": [3, 10, 13, 20, 28, 34],
        "common_economic_policies": [2, 4, 5, 9],
        "regional_tensions": 0.6
    },
    "Continental Federation": {
        "description": """
        The Continental Federation unites the heartland nations of major continents, focused on agricultural production and resource extraction. These regions transformed former rural territories into modernized production centers with advanced agro-industrial complexes.
        
        Federation nations control vast land areas with rich mineral deposits and fertile farming regions. They've developed sophisticated techniques for maximizing agricultural yields and efficient resource extraction, though often at environmental cost.
        
        Relations within the Federation are pragmatic, based on mutual security concerns and transportation infrastructure, but disagreements over water rights and border definitions remain contentious.
        """,
        "dominant_resources": ["food", "raw_materials"],
        "scarce_resources": ["technology_points"],
        "common_technologies": [1, 2, 4, 8, 12, 26],
        "common_economic_policies": [2, 3, 4, 7],
        "regional_tensions": 0.5
    },
    "Equatorial Alliance": {
        "description": """
        The Equatorial Alliance spans nations near the Earth's equator across Africa, South America, and Southeast Asia. Once marginalized in the old order, these nations leveraged their biological diversity and solar potential to become green technology leaders.
        
        Alliance territories contain the world's richest biodiversity and receive the most consistent solar radiation. They've pioneered sustainable technologies in energy production, pharmaceuticals, and agricultural sciences. Their economies emphasize environmental sustainability alongside development.
        
        While united by shared climatic challenges and development models, competition for eco-technology markets and disagreements over conservation priorities create ongoing friction.
        """,
        "dominant_resources": ["energy", "food"],
        "scarce_resources": ["technology_points", "currency"],
        "common_technologies": [2, 5, 10, 15, 22, 33],
        "common_economic_policies": [2, 4, 8, 9],
        "regional_tensions": 0.3
    },
    "Arctic Council": {
        "description": """
        The Arctic Council consists of northern nations controlling newly-accessible territories revealed by receding ice. These countries have developed specialized technologies for extreme cold-weather resource extraction and habitation.
        
        Council territories contain vast untapped mineral and energy reserves, along with newly-viable shipping routes. They've created remarkable engineering solutions for arctic construction and resource development, alongside governance models for sparse populations over vast areas.
        
        Relations are characterized by careful cooperation over environmental monitoring and emergency response, coupled with intense competition for territorial claims and resource rights.
        """,
        "dominant_resources": ["raw_materials", "energy"],
        "scarce_resources": ["food"],
        "common_technologies": [7, 8, 15, 19, 24, 31],
        "common_economic_policies": [3, 4, 7, 10],
        "regional_tensions": 0.7
    },
    "Maritime Confederacy": {
        "description": """
        The Maritime Confederacy brings together island nations and coastal states with economies built around ocean resources and trade. These nations have turned their geographical limitations into strengths through innovative marine technologies and trading networks.
        
        Confederacy territories control critical shipping lanes and vast exclusive economic zones rich in marine resources. They've pioneered floating infrastructure, seawater mining, and advanced aquaculture. Their economies typically emphasize trade services, tourism, and sustainable marine resource harvesting.
        
        While sharing interests in ocean management and climate adaptation, competition for fishing rights and shipping dominance creates persistent tensions.
        """,
        "dominant_resources": ["food", "raw_materials"],
        "scarce_resources": ["energy", "technology_points"],
        "common_technologies": [2, 7, 10, 16, 28, 33],
        "common_economic_policies": [4, 8, 9, 1],
        "regional_tensions": 0.4
    },
    "Independent Technological Enclaves": {
        "description": """
        The Independent Technological Enclaves are a loose association of small, technology-focused city-states and special economic zones that broke away from larger nations. These territories leveraged specialized knowledge and strategic locations to establish independence.
        
        Enclave territories are typically small but densely developed, with cutting-edge infrastructure and research facilities. They've excelled in creating innovation ecosystems and specialized technologies. Their economies emphasize intellectual property, financial services, and high-value manufacturing.
        
        Relations between Enclaves are opportunistic rather than strategic, with rapid shifts between cooperation and competition based on immediate advantage rather than long-term alignment.
        """,
        "dominant_resources": ["technology_points", "currency"],
        "scarce_resources": ["raw_materials", "food"],
        "common_technologies": [14, 16, 18, 21, 23, 30],
        "common_economic_policies": [1, 5, 9, 4],
        "regional_tensions": 0.2
    }
}

MAJOR_HISTORICAL_EVENTS = [
    {
        "year": 2031,
        "name": "The Singapore Collapse",
        "description": """
        The catastrophic failure of sea walls protecting Singapore during a category 6 typhoon led to the flooding of 60% of the city-state, causing unprecedented loss of life and triggering cascading failures in global financial markets. The Singapore Collapse marked the beginning of the Great Divergence, as the world realized existing infrastructure and institutions were inadequate for emerging challenges.
        """,
        "effects": ["Financial system destabilization", "Mass migration crisis", "Loss of faith in traditional governance"]
    },
    {
        "year": 2034,
        "name": "The Three Breadbasket Failure",
        "description": """
        Simultaneous crop failures in North America, Ukraine, and Australia due to extreme weather events created a global food crisis unprecedented in modern history. Food riots erupted in dozens of countries, toppling multiple governments and ending the era of cheap food that had characterized the early 21st century.
        """,
        "effects": ["Global food price spike", "Political instability", "Agricultural technology investment boom"]
    },
    {
        "year": 2036,
        "name": "The Digital Cascading Failure",
        "description": """
        A coordinated cyberattack of unknown origin compromised critical infrastructure across multiple continents, causing power outages, communication blackouts, and industrial accidents. The attack revealed the extreme vulnerability of interconnected systems and accelerated the trend toward more regionalized and resilient infrastructure.
        """,
        "effects": ["Internet fragmentation", "Critical infrastructure redesign", "Cyber-sovereignty movement"]
    },
    {
        "year": 2039,
        "name": "The Microbial Resource War",
        "description": """
        The discovery of extremophile bacteria with applications in pharmaceuticals, energy production, and materials science in deep sea vents triggered the first resource war focused on microbial resources. The conflict primarily involved naval forces from multiple nations and marked a new type of resource competition beyond traditional minerals and fuels.
        """,
        "effects": ["Biotechnology arms race", "Marine territory disputes", "Emergence of bioprospecting regulations"]
    },
    {
        "year": 2041,
        "name": "Formation of the Consortium of Sovereign Nations",
        "description": """
        Following years of increasing international disorder, representatives from 193 nations gathered in Addis Ababa to establish the Consortium of Sovereign Nations (CSN). Unlike its predecessors, the CSN was designed with limited powers, focusing on conflict resolution, minimum standards for international conduct, and voluntary cooperation mechanisms.
        """,
        "effects": ["New international legal framework", "Formal recognition of new nations", "Establishment of conflict resolution mechanisms"]
    },
    {
        "year": 2043,
        "name": "The Great Northern Opening",
        "description": """
        The complete summer ice melt in the Arctic Ocean opened new shipping routes and access to vast resource deposits. The rapid establishment of extraction operations and military bases in the region created new tensions between Arctic powers and redrew global trade networks as shipping times between major markets decreased dramatically.
        """,
        "effects": ["New trade routes", "Resource rush", "Territorial disputes in Arctic regions"]
    },
    {
        "year": 2046,
        "name": "The African Renaissance Conference",
        "description": """
        Leaders from 52 African nations met in Kigali to establish the African Economic Zone, creating the world's largest free trade area. The conference marked the continent's emergence as a unified economic power, leveraging its young population, natural resources, and strategic position to demand a central role in the new global order.
        """,
        "effects": ["African economic integration", "Shift in global economic balance", "New development model emergence"]
    },
    {
        "year": 2049,
        "name": "The Autonomous Intelligence Treaty",
        "description": """
        Following several incidents involving autonomous weapons systems and uncontrolled AI applications, the CSN brokered the Autonomous Intelligence Treaty, establishing international standards for AI development, deployment, and control. The treaty created a framework for managing the rapidly advancing technology while preventing an uncontrolled AI arms race.
        """,
        "effects": ["AI development regulations", "International monitoring systems", "Shared safety protocols"]
    },
    {
        "year": 2052,
        "name": "The New Silk Road Completion",
        "description": """
        The completion of the integrated rail, energy, and data corridor connecting East Asia, Central Asia, and Europe created a revolutionary transportation and communication backbone across the Eurasian continent. The project, funded by a consortium of nations and corporations, dramatically reduced transit times and costs, reshaping trade patterns and power relations across the supercontinent.
        """,
        "effects": ["Eurasian economic integration", "Reduced maritime dependency", "New economic centers in Central Asia"]
    },
    {
        "year": 2055,
        "name": "The Fusion Breakthrough",
        "description": """
        Scientists at the International Fusion Research Center announced the first commercially viable fusion reactor design, promising abundant clean energy. The breakthrough triggered massive investment in fusion infrastructure and a restructuring of global energy markets in anticipation of a post-scarcity energy future.
        """,
        "effects": ["Energy market transformation", "Climate stabilization efforts", "Geopolitical shift away from fossil fuel regions"]
    }
]

WORLD_FACTIONS = [
    {
        "name": "The Consortium Loyalists",
        "description": """
        Nations and organizations that strongly support the Consortium of Sovereign Nations (CSN) as the framework for international cooperation. They advocate for strengthening CSN institutions and expanding their mandate while respecting national sovereignty.
        
        Loyalists believe that only through multilateral cooperation can humanity address existential challenges like climate change, resource depletion, and technological risks. They promote international standards, peaceful dispute resolution, and shared management of global commons.
        
        While idealistic in their vision of cooperation, Loyalists are pragmatic in recognizing the limits of international governance and the importance of maintaining legitimacy through respect for sovereignty.
        """,
        "key_members": ["United European Republics", "East African Federation", "Andean Community"],
        "influence": 0.7,  # Scale 0-1
        "resources": "Diplomatic leverage, legitimacy, institutional infrastructure",
        "goals": ["Strengthen CSN institutions", "Expand international law", "Promote resource sharing agreements"]
    },
    {
        "name": "The Sovereignty Alliance",
        "description": """
        A coalition of nations that prioritize maximum independence in decision-making and minimal external constraints on national action. They resist expansion of international authority and emphasize bilateral rather than multilateral agreements.
        
        Alliance members view national sovereignty as the fundamental principle of international relations and are skeptical of institutions that could constrain their freedom of action. They tend to pursue self-sufficiency in critical resources and maintain strong defensive capabilities.
        
        While often portrayed as isolationist, Alliance members engage actively in international affairs but strictly on terms that preserve their decision-making autonomy and advance their specific interests.
        """,
        "key_members": ["North American Confederation", "Russian Federation", "Central Asian Economic Zone"],
        "influence": 0.65,
        "resources": "Military power, resource wealth, territorial control",
        "goals": ["Limit CSN authority", "Maintain freedom of action", "Secure critical resource access"]
    },
    {
        "name": "The Corporate League",
        "description": """
        An association of powerful multinational corporations and corporate-governed territories that advocate for free markets, minimal regulation, and the primacy of commercial interests in international affairs.
        
        League members have gained unprecedented influence following the Great Divergence, with some corporations directly governing special economic zones and former city-states. They promote seamless global markets, strong intellectual property protections, and corporate self-regulation.
        
        The League operates through economic leverage, technological innovation, and strategic partnerships with nations that share their vision of a market-driven global order.
        """,
        "key_members": ["Singapore Business Authority", "Neo Tokyo Economic Zone", "Orbital Industries Consortium"],
        "influence": 0.6,
        "resources": "Financial capital, intellectual property, technological infrastructure",
        "goals": ["Reduce trade barriers", "Establish corporate governance zones", "Limit state regulation of commerce"]
    },
    {
        "name": "The Ecological Front",
        "description": """
        A diverse coalition of nations, organizations, and movements dedicated to addressing the environmental crisis through radical transformation of economic and social systems.
        
        Front members range from nations whose survival is threatened by climate change to indigenous communities protecting biodiversity to green political movements within larger nations. They advocate for strict emission controls, restoration of natural systems, and rights for non-human species.
        
        The Front has gained influence as environmental disasters have demonstrated the accuracy of their warnings and as sustainable technologies have become economically competitive with traditional alternatives.
        """,
        "key_members": ["Pacific Island Confederation", "Amazon Basin Alliance", "Northern European Green States"],
        "influence": 0.55,
        "resources": "Moral authority, critical ecosystems control, sustainable technologies",
        "goals": ["Enforce emissions reductions", "Protect biodiversity reserves", "Transition to circular economies"]
    },
    {
        "name": "The Technological Vanguard",
        "description": """
        An informal network of nations, research institutions, and technology developers pursuing rapid technological advancement with minimal constraints on innovation.
        
        Vanguard members believe humanity's survival depends on accelerating technological development to overcome resource limitations, environmental degradation, and biological constraints. They promote ambitious research programs, minimal regulation of emerging technologies, and transhumanist values.
        
        While lacking formal structure, the Vanguard exerts influence through technological breakthroughs that create new possibilities and render existing regulations or limitations obsolete.
        """,
        "key_members": ["Greater Korean Technology Republic", "Israeli Innovation Authority", "Autonomous Academic Alliance"],
        "influence": 0.5,
        "resources": "Cutting-edge research, high-skilled talent, advanced infrastructure",
        "goals": ["Accelerate technological development", "Reduce innovation constraints", "Pioneer space-based resources"]
    },
    {
        "name": "The People's Liberation Movement",
        "description": """
        A coalition of populist governments, labor organizations, and social movements advocating for economic justice, democratic control, and resistance to corporate or elite domination.
        
        Movement members emerged from popular rebellions against governments that failed to protect their populations during the Great Divergence. They promote economic models that prioritize human wellbeing over profit, democratic control of critical infrastructure, and strong social safety nets.
        
        The Movement draws strength from mass support among those who felt abandoned by traditional institutions during the crises of the past decades and who demand a more equitable distribution of resources and power.
        """,
        "key_members": ["South American Union", "Mediterranean Workers' Republic", "Southeast Asian People's Alliance"],
        "influence": 0.45,
        "resources": "Mass mobilization capabilities, control of critical labor, democratic legitimacy",
        "goals": ["Democratize economic decisions", "Redistribute wealth", "Establish universal basic services"]
    },
    {
        "name": "The Heritage Confederacy",
        "description": """
        An association of nations and movements committed to preserving distinct cultural, religious, and traditional identities against homogenizing global influences.
        
        Confederacy members view cultural diversity and traditional values as essential components of human flourishing that must be protected from both corporate standardization and enforced international norms. They promote cultural sovereignty, religious freedom, and right of communities to maintain traditional practices.
        
        The Confederacy has gained strength as a reaction to rapid social changes and perceived threats to established ways of life, offering stability and meaning in a world of accelerating transformation.
        """,
        "key_members": ["Pan-Arab Cooperative", "Subcontinental Cultural Alliance", "African Traditional Council"],
        "influence": 0.4,
        "resources": "Cultural heritage, religious authority, community cohesion",
        "goals": ["Protect cultural autonomy", "Limit homogenizing influences", "Maintain traditional social structures"]
    }
]

GAME_WORLD_LORE = {
    "title": "EcoWorld: Dawn of a New Era",
    "setting": "Earth, 2060",
    "background": WORLD_HISTORY,
    "regions": REGIONAL_DESCRIPTIONS,
    "historical_events": MAJOR_HISTORICAL_EVENTS,
    "factions": WORLD_FACTIONS,
    "player_context": """
    As the leader of a newly-established nation in this complex world, you face both unprecedented challenges and opportunities. Your decisions will shape not only your country's development but potentially the trajectory of this critical period in human history.
    
    Will you prioritize rapid economic growth, environmental sustainability, technological advancement, or military security? Will you align with established power blocs or chart an independent course? Will you build a society focused on individual freedom, collective welfare, traditional values, or technological transcendence?
    
    The choices are yours, but remember that in this interconnected world, no nation exists in isolation. Your decisions will ripple through the global system, creating allies and adversaries, opportunities and threats. Navigate wisely through the currents of history as you build your nation's future.
    """
}