"""
Ambient news generator module for EcoWorld.
Creates immersive news articles that don't directly impact gameplay.
These articles are meant to create a sense of a living, breathing world.
"""

from datetime import datetime
import random
from app import db
from models import NewsArticle

# Lists of news themes and templates
GLOBAL_EVENTS = [
    {
        "title": "Global Climate Conference Addresses Resource Management",
        "content": """
        <p>Representatives from over 150 nations gathered today for the annual Global Climate and Resource Summit, 
        addressing critical issues of sustainable development and resource management in an increasingly interdependent world.</p>
        
        <p>"We stand at a crossroads," stated the conference chair. "The decisions we make today about how we manage our 
        collective resources will shape the future of our planet and our economies."</p>
        
        <p>Key topics of discussion included renewable energy transitions, sustainable agriculture practices, and international 
        cooperation on resource conservation. The summit is expected to conclude with a non-binding resolution outlining 
        best practices for nations seeking to balance economic growth with environmental sustainability.</p>
        """,
        "summary": "Global summit discusses sustainable resource management and climate action",
        "category": "event"
    },
    {
        "title": "International Arts Festival Celebrates Cultural Exchange",
        "content": """
        <p>The 32nd International Arts Festival opened today with spectacular displays of music, visual arts, and performances 
        from cultures around the world.</p>
        
        <p>This year's theme, "Bridges Between Nations," emphasizes the role of cultural exchange in fostering understanding 
        and cooperation across political boundaries.</p>
        
        <p>"Art transcends national interests and speaks to our shared humanity," said the festival director at the opening ceremony. 
        "In times of geopolitical tension, cultural diplomacy becomes even more essential."</p>
        
        <p>The two-week festival is expected to draw visitors from dozens of nations and will feature over 200 exhibits and performances.</p>
        """,
        "summary": "Global arts festival promotes cultural exchange and international cooperation",
        "category": "event"
    },
    {
        "title": "World Health Organization Warns of Emerging Pandemic Risks",
        "content": """
        <p>The World Health Organization (WHO) released a comprehensive report today highlighting significant gaps in global 
        pandemic preparedness despite lessons learned from recent health crises.</p>
        
        <p>"While nations have made progress in surveillance systems and medical infrastructure, our collective ability to 
        respond to a major outbreak remains insufficient," the report concluded.</p>
        
        <p>The WHO is calling for increased international cooperation on disease monitoring, vaccine development, and 
        the strategic stockpiling of medical supplies. Experts warn that increasing global trade and travel patterns continue 
        to elevate the risk of rapid disease transmission across borders.</p>
        
        <p>The report specifically notes that nations with more developed healthcare systems have a responsibility to assist 
        those with less robust infrastructure to ensure global health security.</p>
        """,
        "summary": "WHO report calls for improved global pandemic preparedness",
        "category": "event"
    }
]

TECHNOLOGICAL_ADVANCEMENTS = [
    {
        "title": "Breakthrough in Fusion Energy Research Promises Abundant Power",
        "content": """
        <p>Scientists at the International Fusion Research Center have announced a significant breakthrough in plasma containment 
        technology, potentially bringing commercially viable fusion power closer to reality.</p>
        
        <p>"For the first time, we've maintained a stable fusion reaction for over 30 minutes while generating more energy than 
        required to sustain the reaction," said the lead researcher. "This represents a crucial milestone in our quest for 
        clean, virtually limitless energy."</p>
        
        <p>While experts caution that commercial fusion power plants remain at least a decade away, this advancement has been 
        hailed as one of the most significant steps forward in the field in the past 50 years.</p>
        
        <p>Nations investing heavily in fusion research may gain significant economic and strategic advantages as this 
        technology approaches practical implementation.</p>
        """,
        "summary": "Major advancement in fusion energy brings clean, abundant power closer to reality",
        "category": "technology"
    },
    {
        "title": "Quantum Computing Reaches New Milestone with 1,000-Qubit Processor",
        "content": """
        <p>QuantumTech Industries unveiled today the world's first 1,000-qubit quantum processor, significantly expanding 
        the complexity of problems quantum computers can potentially solve.</p>
        
        <p>"This processor represents an order of magnitude improvement over previous systems," said the company's chief 
        technology officer. "It opens new possibilities for cryptography, material science, and complex system modeling."</p>
        
        <p>The breakthrough could have far-reaching implications for national security, as quantum computers of this scale 
        begin to approach the theoretical threshold needed to break currently used encryption standards.</p>
        
        <p>Nations and corporations are racing to develop post-quantum cryptography to protect sensitive information in 
        anticipation of these advances.</p>
        """,
        "summary": "New quantum processor breakthrough may revolutionize computing and encryption",
        "category": "technology"
    },
    {
        "title": "Autonomous Farming Systems Show Promise for Global Food Security",
        "content": """
        <p>The Global Agricultural Technology Institute released promising data today from its five-year study on fully 
        autonomous farming systems, showing yield increases of up to 35% with 40% less water usage compared to 
        traditional methods.</p>
        
        <p>"These systems combine AI-driven decision making, precision robotics, and advanced soil monitoring to optimize 
        every aspect of crop production," explained the institute's director. "The implications for global food security 
        are substantial."</p>
        
        <p>Nations facing agricultural challenges due to climate change, labor shortages, or limited arable land are 
        showing particular interest in the technology. However, the high initial investment costs remain a barrier to 
        widespread adoption.</p>
        
        <p>Experts suggest that countries developing expertise in these systems may gain significant advantages in 
        agricultural exports and food sovereignty in coming decades.</p>
        """,
        "summary": "Autonomous farming technology shows potential to revolutionize global agriculture",
        "category": "technology"
    }
]

ECONOMIC_TRENDS = [
    {
        "title": "Global Economic Forum Predicts Shift in Trade Patterns",
        "content": """
        <p>The annual Global Economic Outlook report released today forecasts significant shifts in international trade 
        patterns over the next decade, driven by changing resource availability, technological innovations, and evolving 
        geopolitical alignments.</p>
        
        <p>"We're seeing the emergence of new economic corridors and partnerships that don't necessarily follow historical 
        trading relationships," said the chief economist of the Global Economic Forum. "Nations that can adapt quickly to 
        these changes will find themselves with competitive advantages."</p>
        
        <p>The report particularly highlights the growing importance of rare earth minerals, renewable energy infrastructure, 
        and advanced manufacturing capabilities as determinants of economic influence in the coming years.</p>
        
        <p>Analysts recommend that forward-thinking nations diversify their trading partnerships and invest in emerging 
        sectors to maintain economic resilience amid these transitions.</p>
        """,
        "summary": "Economic forecast predicts major shifts in global trade relationships",
        "category": "market"
    },
    {
        "title": "Central Banks Coordinate on Digital Currency Frameworks",
        "content": """
        <p>Representatives from twelve of the world's largest central banks announced today a coordinated framework for 
        the potential implementation of central bank digital currencies (CBDCs), addressing growing concern about the 
        fragmentation of the global monetary system.</p>
        
        <p>"As digital currencies become increasingly important in the global economy, it's essential that we maintain 
        interoperability and shared standards," stated the joint communiqué.</p>
        
        <p>The framework establishes common protocols for cross-border CBDC transactions, privacy standards, and monitoring 
        systems to prevent illicit usage, while still allowing individual nations to customize implementation to their specific 
        economic conditions and policy goals.</p>
        
        <p>Economic analysts suggest this coordination could accelerate the adoption of official digital currencies and potentially 
        reshape international finance in the coming decade.</p>
        """,
        "summary": "Major central banks develop framework for digital currency implementation",
        "category": "market"
    },
    {
        "title": "Resource Economists Warn of Strategic Mineral Constraints",
        "content": """
        <p>A consortium of resource economists from major research institutions published findings today indicating that several 
        critical minerals essential for advanced technology manufacturing may face supply constraints within the next 15 years.</p>
        
        <p>"The combination of increasing demand from emerging technologies and the geographic concentration of known reserves 
        creates potential bottlenecks that could impact global industrial production," the report states.</p>
        
        <p>The study particularly highlights concerns around rare earth elements, cobalt, lithium, and certain specialized 
        industrial metals that are critical components in everything from renewable energy systems to advanced military equipment.</p>
        
        <p>Nations with domestic sources of these resources or those developing effective recycling and material science 
        capabilities may gain significant economic leverage as these constraints intensify.</p>
        """,
        "summary": "Economists predict supply constraints for critical industrial minerals",
        "category": "market"
    }
]

GEOPOLITICAL_DEVELOPMENTS = [
    {
        "title": "International Space Station Extension Agreement Signed",
        "content": """
        <p>Following months of diplomatic negotiations, seven nations today signed an agreement extending the operational 
        lifetime of the International Space Station (ISS) through 2035, ensuring continued collaboration in orbit despite 
        terrestrial geopolitical tensions.</p>
        
        <p>"Space remains one of the few domains where international cooperation transcends other disagreements," said the 
        chair of the International Space Coordination Committee. "This agreement demonstrates our collective commitment to 
        scientific advancement."</p>
        
        <p>The extension includes provisions for upgrading key systems and expanding the station's research capabilities, as 
        well as guidelines for incorporating additional participating nations in the future.</p>
        
        <p>Analysts note that nations maintaining a presence in orbit gain not only scientific benefits but also strategic 
        advantages in satellite monitoring, communications, and potential resource development beyond Earth.</p>
        """,
        "summary": "Major powers agree to extend International Space Station operations",
        "category": "diplomacy"
    },
    {
        "title": "Regional Security Pact Formed Between Coastal Nations",
        "content": """
        <p>Five coastal nations formalized a new regional security agreement today, establishing coordinated maritime patrols, 
        intelligence sharing, and disaster response protocols across a strategically significant waterway.</p>
        
        <p>"In an era of increasing competition for marine resources and shipping lanes, this agreement provides a framework 
        for maintaining regional stability and protecting our shared interests," said one participating defense minister.</p>
        
        <p>The pact notably focuses on combating illegal fishing, securing maritime commerce, and coordinating responses to 
        natural disasters, while specifically avoiding language that might be interpreted as targeting any non-member nation.</p>
        
        <p>However, geopolitical analysts suggest the agreement represents a significant realignment of regional power dynamics 
        and may influence future diplomatic and economic relationships throughout the area.</p>
        """,
        "summary": "New maritime security agreement changes regional power dynamics",
        "category": "diplomacy"
    },
    {
        "title": "International Court Rules on Transboundary Water Dispute",
        "content": """
        <p>The International Court of Justice issued a landmark ruling today in a long-running dispute between three nations 
        over rights to a shared river system, establishing new precedents for transboundary water management.</p>
        
        <p>"This decision balances national sovereignty with the obligation of upstream nations to consider impacts on downstream 
        neighbors," said the court's president in announcing the ruling. "It provides a framework for equitable resource sharing."</p>
        
        <p>The ruling establishes minimum water flow requirements, pollution monitoring standards, and a joint commission structure 
        for ongoing management of the shared resource. All parties have pledged to abide by the decision.</p>
        
        <p>With over 260 transboundary river basins worldwide, legal experts suggest this ruling could influence how nations 
        approach similar disputes in an era of increasing water scarcity and climate change impacts.</p>
        """,
        "summary": "International court establishes precedent for resolving transboundary water disputes",
        "category": "diplomacy"
    }
]

SOCIETY_AND_CULTURE = [
    {
        "title": "Global Demographics Report Shows Shifting Population Patterns",
        "content": """
        <p>The United Nations Population Division released its decennial demographic report today, highlighting significant 
        shifts in global population distribution, urbanization trends, and age structures that will reshape societies over 
        the coming decades.</p>
        
        <p>"We're witnessing unprecedented demographic transitions across multiple regions simultaneously," said the report's 
        lead author. "Nations that adapt their economic and social policies to these changes will be better positioned for 
        sustainable development."</p>
        
        <p>Key findings include accelerating urbanization in developing regions, rapid aging in most advanced economies, and 
        changing migration patterns influenced by climate impacts and economic opportunities.</p>
        
        <p>The report suggests that nations investing in education, healthcare infrastructure, and flexible labor policies will 
        be best equipped to navigate these demographic shifts successfully.</p>
        """,
        "summary": "UN report outlines major demographic changes reshaping global societies",
        "category": "event"
    },
    {
        "title": "International Youth Leadership Summit Addresses Global Challenges",
        "content": """
        <p>Over 500 young leaders from 120 nations convened today for the start of the International Youth Leadership Summit, 
        focusing on developing collaborative approaches to global challenges including climate change, resource management, 
        and technological disruption.</p>
        
        <p>"This generation will inherit a world of unprecedented complexity and interconnectedness," noted the summit's organizer. 
        "Building transnational networks of cooperation now will be essential for addressing future challenges."</p>
        
        <p>The two-week program includes workshops on sustainable development, conflict resolution, and economic innovation, 
        with participants developing action plans to implement in their home countries.</p>
        
        <p>Nations that invest in developing young leadership talent may gain long-term advantages in diplomatic influence and 
        international cooperation as this generation assumes positions of authority in coming decades.</p>
        """,
        "summary": "Young leaders from 120 nations collaborate on solutions to global challenges",
        "category": "event"
    },
    {
        "title": "International Commission Releases Global Education Standards",
        "content": """
        <p>After three years of research and consultation, the International Education Standards Commission today published 
        its comprehensive framework for education systems suited to 21st century economic and social needs.</p>
        
        <p>"The nature of work, citizenship, and daily life is being transformed by technological and social changes," stated 
        the commission's report. "Education systems must evolve accordingly to prepare young people for this new reality."</p>
        
        <p>The framework emphasizes adaptable skill development, critical thinking, digital literacy, and cross-cultural 
        competence as essential components of modern education, while providing flexible implementation guidelines adaptable 
        to different cultural and economic contexts.</p>
        
        <p>Nations that successfully modernize their education systems in line with these recommendations may gain significant 
        competitive advantages in human capital development and economic innovation capacity.</p>
        """,
        "summary": "New international education framework emphasizes adaptable skills for changing world",
        "category": "event"
    }
]

SPORTS_AND_ENTERTAINMENT = [
    {
        "title": "Preparations Underway for Global Games 2026",
        "content": """
        <p>The host city for the 2026 Global Games unveiled its ambitious infrastructure plans today, showcasing the 
        newly designed Olympic Village, stadium renovations, and transportation improvements ahead of the quadrennial 
        sporting event.</p>
        
        <p>"These Games will set new standards for sustainability and technological integration," said the organizing 
        committee chair. "Every facility is designed for maximum efficiency and minimum environmental impact."</p>
        
        <p>Nations participating in the Games typically see not only sporting benefits but also diplomatic opportunities 
        and international prestige. Host countries historically experience economic boosts from infrastructure development 
        and tourism.</p>
        
        <p>Qualification tournaments will begin next year, with an expected 12,000 athletes from over 200 nations competing 
        in 32 different sports during the three-week competition.</p>
        """,
        "summary": "Host city reveals infrastructure plans for upcoming Global Games",
        "category": "event"
    },
    {
        "title": "International Film Festival Highlights Cross-Cultural Stories",
        "content": """
        <p>The prestigious International Film Festival opened yesterday with a record 87 countries represented among its 
        selections, reflecting growing global interest in diverse storytelling perspectives.</p>
        
        <p>"Cinema has become an increasingly important medium for cultural diplomacy and international understanding," 
        noted the festival director. "The films selected this year particularly emphasize themes of cooperation across 
        boundaries and shared human experiences."</p>
        
        <p>Several entries directly address contemporary geopolitical issues, including resource management, technological 
        disruption, and changing power dynamics between nations.</p>
        
        <p>Nations with strong cultural export industries often enjoy enhanced international influence and "soft power" 
        that can translate into diplomatic and economic advantages on the world stage.</p>
        """,
        "summary": "Global film festival showcases diverse perspectives and cultural exchange",
        "category": "event"
    },
    {
        "title": "International Esports Championship Draws Record Viewership",
        "content": """
        <p>The World Esports Federation Championship concluded yesterday with unprecedented global viewership, cementing 
        competitive gaming's status as a major international sport and cultural phenomenon.</p>
        
        <p>"With over 85 million concurrent viewers at peak moments, this year's championship surpassed many traditional 
        sporting events in global audience," said the federation president. "Esports has become a truly global language."</p>
        
        <p>Teams from 24 nations competed in multiple game categories, with the overall championship going to a multinational 
        squad representing three different countries.</p>
        
        <p>Nations developing strong esports programs are finding benefits beyond entertainment, including technological 
        innovation, digital infrastructure development, and youth engagement. Several countries now include esports in 
        their national sports development strategies.</p>
        """,
        "summary": "Global esports championship becomes one of world's most-watched sporting events",
        "category": "event"
    }
]

# List of all content collections for easier random selection
ALL_CONTENT_COLLECTIONS = [
    GLOBAL_EVENTS,
    TECHNOLOGICAL_ADVANCEMENTS,
    ECONOMIC_TRENDS,
    GEOPOLITICAL_DEVELOPMENTS,
    SOCIETY_AND_CULTURE,
    SPORTS_AND_ENTERTAINMENT
]

def generate_ambient_news(count=3):
    """
    Generate ambient news articles that create immersion without impacting gameplay
    
    Args:
        count (int): Number of ambient news articles to generate
        
    Returns:
        int: Number of articles created
    """
    articles_created = 0
    
    # Get all existing news articles to avoid duplicates
    existing_titles = [article.title for article in NewsArticle.query.all()]
    
    # Select random events from different categories
    chosen_articles = []
    
    # Try to pick from various categories
    for _ in range(min(count, len(ALL_CONTENT_COLLECTIONS))):
        # Pick a random category
        category_index = random.randint(0, len(ALL_CONTENT_COLLECTIONS) - 1)
        collection = ALL_CONTENT_COLLECTIONS[category_index]
        
        # Try to find a non-duplicate article
        for _ in range(5):  # Try up to 5 times to find a non-duplicate
            if collection:
                article_index = random.randint(0, len(collection) - 1)
                article = collection[article_index]
                
                if article["title"] not in existing_titles and article not in chosen_articles:
                    chosen_articles.append(article)
                    break
    
    # If we need more articles, pick randomly from any category
    while len(chosen_articles) < count:
        collection = random.choice(ALL_CONTENT_COLLECTIONS)
        if collection:
            article = random.choice(collection)
            if article["title"] not in existing_titles and article not in chosen_articles:
                chosen_articles.append(article)
    
    # Create the chosen news articles
    for article_data in chosen_articles:
        article = NewsArticle(
            title=article_data["title"],
            content=article_data["content"],
            summary=article_data["summary"],
            category=article_data["category"],
            importance=random.randint(1, 3),  # Ambient news is lower priority
            is_featured=random.random() < 0.2,  # 20% chance of being featured
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    if articles_created > 0:
        db.session.commit()
    
    return articles_created