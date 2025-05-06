"""
News generator module for EcoWorld.
Handles the generation of news articles based on game events.
"""

from datetime import datetime, timedelta
import random
from sqlalchemy import desc, func, or_, and_
from app import db
from models import (
    NewsArticle, Nation, War, Alliance, Trade, Technology, 
    MarketItem, Resource, Military, DeployedSpy, SpyMission
)

def get_latest_news(limit=10, category=None, nation_id=None, featured_only=False):
    """
    Get the latest news articles with optional filtering
    
    Args:
        limit (int): Maximum number of articles to return
        category (str): Filter by category if provided
        nation_id (int): Filter by articles related to this nation if provided
        featured_only (bool): Return only featured articles if True
        
    Returns:
        list: List of NewsArticle objects
    """
    query = NewsArticle.query
    
    # Apply filters
    if category:
        query = query.filter(NewsArticle.category == category)
    
    if nation_id:
        query = query.filter(
            or_(
                NewsArticle.nation1_id == nation_id,
                NewsArticle.nation2_id == nation_id
            )
        )
    
    if featured_only:
        query = query.filter(NewsArticle.is_featured == True)
    
    # Get latest articles, ordered by importance and date
    return query.order_by(
        desc(NewsArticle.is_featured),
        desc(NewsArticle.importance), 
        desc(NewsArticle.publication_date)
    ).limit(limit).all()

def generate_daily_news():
    """
    Generate daily news articles based on game events
    
    This function should be called once per game day to create
    news articles that reflect recent events in the game world.
    """
    # Clear out very old news to avoid DB bloat
    cleanup_old_news()
    
    # Generate different types of news
    generated_count = 0
    generated_count += generate_market_news()
    generated_count += generate_war_news()
    generated_count += generate_alliance_news()
    generated_count += generate_technology_news()
    generated_count += generate_espionage_news()
    generated_count += generate_ranking_news()
    
    # Add ambient immersive news articles that don't affect gameplay
    try:
        from utils.ambient_news_generator import generate_ambient_news
        generated_count += generate_ambient_news(count=3)  # Add 3 ambient news articles each day
    except Exception as e:
        print(f"Error generating ambient news: {e}")
    
    return generated_count

def cleanup_old_news(days_to_keep=30):
    """Remove news articles older than the specified number of days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    old_news = NewsArticle.query.filter(NewsArticle.publication_date < cutoff_date).all()
    
    for article in old_news:
        db.session.delete(article)
    
    db.session.commit()
    return len(old_news)

def generate_market_news():
    """Generate news about market trends and significant trades"""
    articles_created = 0
    
    # Find notable market trends
    resource_types = ['raw_materials', 'food', 'energy']
    for resource_type in resource_types:
        # Get average price for this resource type
        active_listings = MarketItem.query.filter_by(
            resource_type=resource_type,
            is_active=True
        ).all()
        
        if not active_listings or len(active_listings) < 3:
            continue
            
        # Calculate average price
        avg_price = sum(item.price_per_unit for item in active_listings) / len(active_listings)
        
        # Get recent completed trades for this resource
        recent_trades = Trade.query.filter_by(
            resource_type=resource_type
        ).order_by(desc(Trade.trade_date)).limit(20).all()
        
        if not recent_trades or len(recent_trades) < 3:
            continue
            
        # Calculate previous average price
        prev_avg_price = sum(trade.price_per_unit for trade in recent_trades) / len(recent_trades)
        
        # Check if there's a significant price change
        if abs(avg_price - prev_avg_price) / prev_avg_price > 0.15:  # 15% change
            # Create market trend article
            price_change = (avg_price - prev_avg_price) / prev_avg_price * 100
            direction = "increase" if price_change > 0 else "decrease"
            
            resource_names = {
                'raw_materials': 'Raw Materials',
                'food': 'Food',
                'energy': 'Energy'
            }
            
            title = f"{resource_names[resource_type]} Prices {direction.capitalize()} by {abs(price_change):.1f}%"
            
            content = f"""
            <p>Global market analysts report a significant {direction} in {resource_names[resource_type].lower()} 
            prices of approximately {abs(price_change):.1f}% compared to recent trading periods.</p>
            
            <p>The current average price stands at {avg_price:.2f} currency units per unit, while recent trades 
            averaged {prev_avg_price:.2f}.</p>
            
            <p>Experts attribute this change to {"increased demand and limited supply" if price_change > 0 
            else "oversupply and decreased global demand"}. Nations heavily dependent on {resource_names[resource_type].lower()} 
            imports may want to adjust their economic strategies accordingly.</p>
            """
            
            # Create the news article
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Global {resource_names[resource_type].lower()} prices {direction} by {abs(price_change):.1f}%",
                category='market',
                importance=min(5, int(abs(price_change) / 10) + 1),  # 1-5 based on change magnitude
                is_featured=abs(price_change) > 25,  # Feature very large changes
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    # Find significant trades
    significant_trades = Trade.query.filter(
        Trade.trade_date > datetime.utcnow() - timedelta(hours=24)
    ).order_by(desc(Trade.total_price)).limit(3).all()
    
    for trade in significant_trades:
        if trade.total_price > 5000:  # Only report large trades
            seller_name = trade.seller.name if trade.seller else "Unknown Nation"
            buyer_name = trade.buyer.name if trade.buyer else "Unknown Nation"
            
            resource_names = {
                'raw_materials': 'Raw Materials',
                'food': 'Food',
                'energy': 'Energy'
            }
            
            title = f"Major {resource_names[trade.resource_type]} Deal Between {seller_name} and {buyer_name}"
            
            content = f"""
            <p>A significant trade deal has been finalized between {seller_name} and {buyer_name}.</p>
            
            <p>The agreement involves the transfer of {trade.quantity:,} units of {resource_names[trade.resource_type].lower()} 
            at a price of {trade.price_per_unit:.2f} per unit, totaling {trade.total_price:,.2f} in currency.</p>
            
            <p>This transaction represents one of the largest {resource_names[trade.resource_type].lower()} trades in recent 
            days and may indicate a strategic shift in resource allocation for both nations.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"{seller_name} sells {trade.quantity:,} {trade.resource_type} to {buyer_name}",
                category='market',
                importance=min(4, int(trade.total_price / 2500)),  # 1-4 based on price
                nation1_id=trade.seller_id,
                nation2_id=trade.buyer_id,
                related_trade_id=trade.id,
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    db.session.commit()
    return articles_created

def generate_war_news():
    """Generate news about ongoing wars and battles"""
    articles_created = 0
    
    # Report new wars
    new_wars = War.query.filter(
        War.start_date > datetime.utcnow() - timedelta(hours=24),
        War.is_active == True
    ).all()
    
    for war in new_wars:
        aggressor_name = war.aggressor.name if war.aggressor else "Unknown Nation"
        defender_name = war.defender.name if war.defender else "Unknown Nation"
        
        title = f"War Declared: {aggressor_name} Attacks {defender_name}"
        
        content = f"""
        <p>Tensions have escalated into open conflict as {aggressor_name} has formally declared war against {defender_name}.</p>
        
        <p>Military movements have been observed along the borders, and initial skirmishes have been reported. 
        The international community watches closely as this conflict unfolds.</p>
        
        <p>Analysts speculate that control over resources and strategic territories may be the primary motivation 
        behind this aggression. Both nations have begun mobilizing their forces.</p>
        """
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=f"{aggressor_name} declares war on {defender_name}",
            category='war',
            importance=4,  # Wars are important news
            nation1_id=war.aggressor_id,
            nation2_id=war.defender_id,
            related_war_id=war.id,
            is_featured=True,  # Wars are always featured
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    # Report wars that ended
    ended_wars = War.query.filter(
        War.end_date > datetime.utcnow() - timedelta(hours=24),
        War.is_active == False
    ).all()
    
    for war in ended_wars:
        aggressor_name = war.aggressor.name if war.aggressor else "Unknown Nation"
        defender_name = war.defender.name if war.defender else "Unknown Nation"
        
        winner = aggressor_name if war.aggressor_victory else defender_name
        loser = defender_name if war.aggressor_victory else aggressor_name
        
        title = f"Peace Declared: War Between {aggressor_name} and {defender_name} Ends"
        
        content = f"""
        <p>The war between {aggressor_name} and {defender_name} has officially ended, with {winner} emerging victorious.</p>
        
        <p>The conflict resulted in significant casualties, with reports indicating approximately {war.aggressor_casualties + war.defender_casualties:,} 
        military personnel lost in the fighting.</p>
        
        <p>As part of the peace terms, {loser} has ceded resources valued at approximately {war.resources_plundered:,.2f} 
        to {winner}. The long process of rebuilding will now begin for both nations.</p>
        """
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=f"War between {aggressor_name} and {defender_name} ends with {winner} victorious",
            category='war',
            importance=4,  # End of wars are important news
            nation1_id=war.aggressor_id,
            nation2_id=war.defender_id,
            related_war_id=war.id,
            is_featured=True,  # War endings are always featured
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    # Report on major ongoing wars
    ongoing_wars = War.query.filter(
        War.is_active == True,
        War.start_date < datetime.utcnow() - timedelta(days=3)  # Wars lasting more than 3 days
    ).all()
    
    for war in ongoing_wars:
        # Only create a "war update" article with 20% probability to avoid spam
        if random.random() < 0.2:
            aggressor_name = war.aggressor.name if war.aggressor else "Unknown Nation"
            defender_name = war.defender.name if war.defender else "Unknown Nation"
            
            days_of_conflict = (datetime.utcnow() - war.start_date).days
            
            # Get military strengths
            aggressor_military = Military.query.filter_by(nation_id=war.aggressor_id).first()
            defender_military = Military.query.filter_by(nation_id=war.defender_id).first()
            
            if aggressor_military and defender_military:
                # Simplistic comparison of military power
                aggressor_power = aggressor_military.offensive_power
                defender_power = defender_military.defensive_power
                
                advantage = "neutral"
                if aggressor_power > defender_power * 1.5:
                    advantage = "heavily favoring the aggressor"
                elif aggressor_power > defender_power * 1.1:
                    advantage = "slightly favoring the aggressor"
                elif defender_power > aggressor_power * 1.5:
                    advantage = "heavily favoring the defender"
                elif defender_power > aggressor_power * 1.1:
                    advantage = "slightly favoring the defender"
                else:
                    advantage = "evenly matched"
                
                title = f"War Update: Conflict Between {aggressor_name} and {defender_name} Continues"
                
                content = f"""
                <p>The war between {aggressor_name} and {defender_name} has now entered its {days_of_conflict}th day, 
                with fighting continuing across multiple fronts.</p>
                
                <p>Military analysts assess the current situation as {advantage}, though the tide of war can change rapidly.</p>
                
                <p>Casualties continue to mount on both sides, with estimates now reaching approximately 
                {war.aggressor_casualties + war.defender_casualties:,} personnel lost in the conflict.</p>
                
                <p>The international community has called for peace talks, but both sides appear committed to 
                pursuing their military objectives at this time.</p>
                """
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    summary=f"Day {days_of_conflict} of war between {aggressor_name} and {defender_name}",
                    category='war',
                    importance=3,  # Updates are moderately important
                    nation1_id=war.aggressor_id,
                    nation2_id=war.defender_id,
                    related_war_id=war.id,
                    publication_date=datetime.utcnow()
                )
                
                db.session.add(article)
                articles_created += 1
    
    db.session.commit()
    return articles_created

def generate_alliance_news():
    """Generate news about new alliances and diplomatic relations"""
    articles_created = 0
    
    # Report new alliances
    new_alliances = Alliance.query.filter(
        Alliance.formed_date > datetime.utcnow() - timedelta(hours=24),
        Alliance.is_active == True
    ).all()
    
    for alliance in new_alliances:
        nation1_name = alliance.nation1.name if alliance.nation1 else "Unknown Nation"
        nation2_name = alliance.nation2.name if alliance.nation2 else "Unknown Nation"
        
        title = f"New Alliance Formed Between {nation1_name} and {nation2_name}"
        
        content = f"""
        <p>In a significant diplomatic development, {nation1_name} and {nation2_name} have announced the formation 
        of a formal alliance.</p>
        
        <p>The agreement, signed by representatives of both nations, establishes closer military coordination, 
        mutual defense commitments, and enhanced trade relations.</p>
        
        <p>International observers note that this alliance could significantly alter the balance of power in the region, 
        as both nations combine their military and economic resources. Neighboring countries are closely monitoring 
        the situation and assessing the potential impact on their own strategic positions.</p>
        """
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=f"{nation1_name} and {nation2_name} form a new alliance",
            category='diplomacy',
            importance=3,  # Alliances are moderately important
            nation1_id=alliance.nation1_id,
            nation2_id=alliance.nation2_id,
            related_alliance_id=alliance.id,
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    # Report dissolved alliances
    dissolved_alliances = Alliance.query.filter(
        Alliance.dissolved_date > datetime.utcnow() - timedelta(hours=24),
        Alliance.is_active == False
    ).all()
    
    for alliance in dissolved_alliances:
        nation1_name = alliance.nation1.name if alliance.nation1 else "Unknown Nation"
        nation2_name = alliance.nation2.name if alliance.nation2 else "Unknown Nation"
        
        title = f"Alliance Between {nation1_name} and {nation2_name} Dissolved"
        
        content = f"""
        <p>The alliance between {nation1_name} and {nation2_name}, which has lasted since {alliance.formed_date.strftime('%B %d, %Y')}, 
        has been officially dissolved.</p>
        
        <p>The decision to end the diplomatic and military partnership comes after {(alliance.dissolved_date - alliance.formed_date).days} days 
        of cooperation. Neither nation has provided detailed explanations for the split, though diplomatic sources cite 
        "diverging strategic objectives" as the primary cause.</p>
        
        <p>This development could create a power vacuum in the region, potentially opening the door for new alliances 
        or increasing vulnerability for both nations. Neighboring countries are already reassessing their diplomatic 
        and military postures in light of this change.</p>
        """
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=f"Alliance between {nation1_name} and {nation2_name} has ended",
            category='diplomacy',
            importance=3,  # Alliance dissolution is moderately important
            nation1_id=alliance.nation1_id,
            nation2_id=alliance.nation2_id,
            related_alliance_id=alliance.id,
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    db.session.commit()
    return articles_created

def generate_technology_news():
    """Generate news about significant technological advancements"""
    articles_created = 0
    
    # Find technologies that were recently completed
    recently_completed = Technology.query.filter(
        Technology.level > 0,
        Technology.research_points_current >= Technology.research_points_required,
        Technology.researching == False,
        Technology.research_started > datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    for tech in recently_completed:
        nation_name = tech.nation.name if tech.nation else "Unknown Nation"
        
        # Only report major technological breakthroughs
        if tech.level > 3:  # Advanced technologies only
            title = f"{nation_name} Achieves Breakthrough in {tech.name} Technology"
            
            content = f"""
            <p>{nation_name} has announced a major technological breakthrough, achieving level {tech.level} in {tech.name} technology.</p>
            
            <p>This advancement in the field of {tech.category} is expected to provide significant benefits to {nation_name}'s 
            {"production capabilities" if tech.production_multiplier > 1 else 
            "resource efficiency" if tech.consumption_efficiency < 1 else 
            "military strength" if tech.military_bonus > 0 else 
            "research capabilities" if tech.research_bonus > 0 else 
            "intelligence operations" if tech.espionage_bonus > 0 else "national capabilities"}.</p>
            
            <p>Experts estimate that this development could increase {nation_name}'s 
            {"production output by approximately" if tech.production_multiplier > 1 else
            "resource efficiency by approximately" if tech.consumption_efficiency < 1 else
            "military effectiveness by approximately" if tech.military_bonus > 0 else
            "research speed by approximately" if tech.research_bonus > 0 else
            "intelligence gathering by approximately" if tech.espionage_bonus > 0 else "capabilities by approximately"} 
            {(tech.production_multiplier - 1) * 100 if tech.production_multiplier > 1 else
            (1 - tech.consumption_efficiency) * 100 if tech.consumption_efficiency < 1 else
            tech.military_bonus * 100 if tech.military_bonus > 0 else
            tech.research_bonus * 100 if tech.research_bonus > 0 else
            tech.espionage_bonus * 100 if tech.espionage_bonus > 0 else 10:.1f}%.</p>
            
            <p>Other nations are likely to take notice of this development and may accelerate their own research programs in response.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"{nation_name} reaches level {tech.level} in {tech.name} technology",
                category='technology',
                importance=min(5, tech.level),  # Importance based on tech level
                nation1_id=tech.nation_id,
                related_technology_id=tech.id,
                is_featured=tech.level >= 5,  # Feature max-level technologies
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    # Occasionally feature "technology race" articles
    if random.random() < 0.3:  # 30% chance each day
        # Find technology categories where nations are competing
        top_tech_nations = db.session.query(
            Nation.id, Nation.name, func.sum(Technology.level).label('tech_sum')
        ).join(Technology).group_by(Nation.id).order_by(desc('tech_sum')).limit(3).all()
        
        if len(top_tech_nations) >= 2:
            leader_name = top_tech_nations[0][1]
            runner_up_name = top_tech_nations[1][1]
            
            title = f"Technology Race: {leader_name} Leads {runner_up_name} in Development"
            
            content = f"""
            <p>Analysis of global technology development shows that {leader_name} currently leads the world in technological advancement, 
            with {runner_up_name} close behind.</p>
            
            <p>The technology gap between these two powers has significant implications for military, economic, and diplomatic power projections.
            {"Third-placed " + top_tech_nations[2][1] + " is also making notable progress, though still trails the top two nations." if len(top_tech_nations) >= 3 else ""}</p>
            
            <p>Experts suggest that maintaining technological superiority requires nations to invest substantially in research facilities and 
            assign skilled population to research activities. The coming months will reveal whether {leader_name} can maintain its lead or if 
            competitors will close the gap.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"{leader_name} leads global technology race, with {runner_up_name} in second position",
                category='technology',
                importance=2,  # General tech news is moderately important
                nation1_id=top_tech_nations[0][0],
                nation2_id=top_tech_nations[1][0],
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    db.session.commit()
    return articles_created

def generate_espionage_news():
    """Generate news about espionage activities"""
    articles_created = 0
    
    # Report on captured spies
    recently_captured = DeployedSpy.query.filter(
        DeployedSpy.is_discovered == True,
        DeployedSpy.is_active == False,
        # Captured within last 24 hours (using deployment_date as proxy since we don't have a 'captured_date')
        DeployedSpy.deployment_date > datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    for spy in recently_captured:
        # Get nation names
        owner_name = "Unknown Nation"
        target_name = "Unknown Nation"
        
        if spy.owner_nation:
            owner_name = spy.owner_nation.name
        if spy.target_nation:
            target_name = spy.target_nation.name
        
        title = f"Espionage Scandal: {target_name} Captures {owner_name} Spy"
        
        content = f"""
        <p>Diplomatic tensions are rising after authorities in {target_name} announced the capture of a spy from {owner_name}.</p>
        
        <p>According to official statements, the agent was apprehended while attempting to gather 
        {"military intelligence" if spy.specialization == 'military' else 
        "economic information" if spy.specialization == 'economic' else 
        "technological secrets" if spy.specialization == 'technological' else 
        "diplomatic communications" if spy.specialization == 'diplomatic' else "classified information"}.</p>
        
        <p>The government of {target_name} has filed a formal protest with {owner_name} over this breach of sovereignty. 
        {owner_name} has not yet issued an official response to the allegations.</p>
        
        <p>Security experts note that this incident could lead to deteriorating relations between the two nations and 
        potentially disrupt any ongoing diplomatic or trade negotiations.</p>
        """
        
        article = NewsArticle(
            title=title,
            content=content,
            summary=f"{target_name} captures {owner_name} spy",
            category='espionage',
            importance=3,  # Spy captures are moderately important
            nation1_id=spy.target_nation_id,  # The capturing nation is primary
            nation2_id=spy.owner_nation_id,   # The spy's nation is secondary
            publication_date=datetime.utcnow()
        )
        
        db.session.add(article)
        articles_created += 1
    
    # Report on major espionage missions
    significant_missions = SpyMission.query.filter(
        SpyMission.is_completed == True,
        SpyMission.is_successful == True,
        SpyMission.completion_date > datetime.utcnow() - timedelta(hours=24),
        SpyMission.diplomatic_incident == True  # Only missions that caused incidents
    ).all()
    
    for mission in significant_missions:
        # We only report on missions that the target nation discovers
        if mission.spy and mission.spy.target_nation and mission.spy.owner_nation:
            target_name = mission.spy.target_nation.name
            owner_name = mission.spy.owner_nation.name
            
            # Different titles and content based on mission type
            if mission.mission_type == 'sabotage':
                title = f"Sabotage Suspected in {target_name}: {owner_name} Denies Involvement"
                
                content = f"""
                <p>Officials in {target_name} are investigating a suspected act of sabotage that has damaged key infrastructure facilities.</p>
                
                <p>While no direct evidence has been presented publicly, diplomatic sources indicate that {target_name} believes agents from 
                {owner_name} are responsible for the incident.</p>
                
                <p>The government of {owner_name} has categorically denied any involvement, calling the accusations "unfounded and provocative."</p>
                
                <p>The incident has resulted in temporary disruptions to {target_name}'s 
                {"military readiness" if random.random() < 0.3 else 
                "resource production" if random.random() < 0.5 else 
                "technological research" if random.random() < 0.7 else 
                "economic operations"}. Security measures across critical facilities have been heightened.</p>
                """
            
            elif mission.mission_type == 'steal_tech':
                title = f"{target_name} Accuses {owner_name} of Technology Theft"
                
                content = f"""
                <p>A serious diplomatic incident has erupted after {target_name} accused {owner_name} of orchestrating the theft of classified technology.</p>
                
                <p>According to sources within {target_name}'s security apparatus, the breach targeted research facilities developing advanced 
                {"military" if random.random() < 0.3 else 
                "production" if random.random() < 0.5 else 
                "research" if random.random() < 0.7 else 
                "energy"} technologies.</p>
                
                <p>The government of {owner_name} has dismissed the allegations as "baseless" and suggested they are intended to "distract from 
                internal problems" within {target_name}.</p>
                
                <p>International observers note that technology theft accusations are difficult to prove definitively, but the incident has 
                nevertheless created significant diplomatic tension between the two nations.</p>
                """
            
            else:  # Default for other mission types
                title = f"Covert Operation Allegations Strain Relations Between {target_name} and {owner_name}"
                
                content = f"""
                <p>Diplomatic relations between {target_name} and {owner_name} have deteriorated following allegations of covert operations.</p>
                
                <p>{target_name} claims to have uncovered evidence of {owner_name}'s involvement in unauthorized intelligence gathering activities 
                within its sovereign territory.</p>
                
                <p>The specific nature of the alleged operation has not been disclosed, but government officials describe it as "a serious violation 
                of international norms and an affront to peaceful relations."</p>
                
                <p>{owner_name} has neither confirmed nor denied the accusations, stating only that it "reserves all rights to protect its national 
                interests through legal means."</p>
                """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Espionage incident between {target_name} and {owner_name}",
                category='espionage',
                importance=3,  # Espionage incidents are moderately important
                nation1_id=mission.spy.target_nation_id,
                nation2_id=mission.spy.owner_nation_id,
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    db.session.commit()
    return articles_created

def generate_ranking_news():
    """Generate news about nation rankings and statistics"""
    articles_created = 0
    
    # We only want to generate ranking news occasionally
    if random.random() < 0.3:  # 30% chance each day
        # Gather top nations by different metrics
        top_economic = Nation.query.order_by(desc(Nation.economic_rank)).limit(3).all()
        top_military = Nation.query.order_by(desc(Nation.military_rank)).limit(3).all()
        top_technology = Nation.query.order_by(desc(Nation.technology_rank)).limit(3).all()
        top_overall = Nation.query.order_by(desc(Nation.overall_rank)).limit(5).all()
        
        # Choose one ranking type to report on
        ranking_type = random.choice(['economic', 'military', 'technology', 'overall'])
        
        if ranking_type == 'economic' and len(top_economic) >= 3:
            title = f"Economic Powers: {top_economic[0].name} Leads Global Economy"
            
            content = f"""
            <p>Economic analysts have released their latest assessment of global economic power, with {top_economic[0].name} retaining 
            its position as the world's leading economic power.</p>
            
            <p>The rankings, based on GDP, inflation rates, and resource production efficiency, show a clear advantage for 
            {top_economic[0].name}, followed by {top_economic[1].name} in second place and {top_economic[2].name} in third.</p>
            
            <p>{top_economic[0].name}'s strong economic position is attributed to its efficient resource management, favorable tax policies, 
            and strategic trade relationships. With a GDP of approximately {top_economic[0].gdp:,.2f}, the nation has established itself 
            as an economic model for others to follow.</p>
            
            <p>Economists note that sustained economic growth requires balanced population distribution, strategic technology investments, 
            and active participation in global markets.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Global economic rankings: {top_economic[0].name} (1st), {top_economic[1].name} (2nd), {top_economic[2].name} (3rd)",
                category='ranking',
                importance=2,  # Rankings are of moderate importance
                nation1_id=top_economic[0].id,
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
            
        elif ranking_type == 'military' and len(top_military) >= 3:
            title = f"Military Assessment: {top_military[0].name} Commands Most Powerful Forces"
            
            content = f"""
            <p>Defense analysts have published their latest evaluation of global military capabilities, ranking {top_military[0].name} as 
            possessing the world's most formidable armed forces.</p>
            
            <p>The comprehensive assessment, which considers troop strength, equipment quality, and strategic positioning, places 
            {top_military[0].name} at the top, followed by {top_military[1].name} and {top_military[2].name}.</p>
            
            <p>Military experts highlight {top_military[0].name}'s balanced approach to defense, with substantial investments in both 
            conventional forces and advanced military technologies. This strategic approach has created a versatile military capable of 
            responding to various threat scenarios.</p>
            
            <p>The report notes that military power continues to be a crucial component of global influence, affecting diplomatic leverage, 
            alliance opportunities, and territorial security.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Global military rankings: {top_military[0].name} (1st), {top_military[1].name} (2nd), {top_military[2].name} (3rd)",
                category='ranking',
                importance=2,  # Rankings are of moderate importance
                nation1_id=top_military[0].id,
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
            
        elif ranking_type == 'technology' and len(top_technology) >= 3:
            title = f"Innovation Leaders: {top_technology[0].name} At Forefront of Technological Advancement"
            
            content = f"""
            <p>A comprehensive analysis of global technological development rates places {top_technology[0].name} at the forefront of 
            innovation and scientific progress.</p>
            
            <p>The technological index, which evaluates research output, breakthrough technologies, and implementation efficiency, shows 
            {top_technology[0].name} leading the world, with {top_technology[1].name} and {top_technology[2].name} following closely behind.</p>
            
            <p>Experts cite {top_technology[0].name}'s substantial investment in research infrastructure and skilled workforce allocation as 
            key factors in its technological dominance. The nation's focus on balanced development across military, production, and efficiency 
            technologies has created synergistic effects that amplify overall progress.</p>
            
            <p>The report emphasizes that technological leadership translates directly to advantages in economic productivity, military capability, 
            and resource efficiency—making it a critical component of national power.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Global technology rankings: {top_technology[0].name} (1st), {top_technology[1].name} (2nd), {top_technology[2].name} (3rd)",
                category='ranking',
                importance=2,  # Rankings are of moderate importance
                nation1_id=top_technology[0].id,
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
            
        elif ranking_type == 'overall' and len(top_overall) >= 5:
            title = f"Global Power Index: {top_overall[0].name} Ranked World's Leading Nation"
            
            content = f"""
            <p>The latest Global Power Index has been released, ranking {top_overall[0].name} as the world's most powerful nation based on 
            a comprehensive assessment of economic strength, military capability, technological advancement, and diplomatic influence.</p>
            
            <p>The top five positions in this prestigious ranking are:</p>
            
            <ol>
                <li><strong>{top_overall[0].name}</strong> - Maintaining its dominant position through balanced development</li>
                <li><strong>{top_overall[1].name}</strong> - Showing significant gains in economic and technological metrics</li>
                <li><strong>{top_overall[2].name}</strong> - Leveraging military strength and strategic alliances</li>
                <li><strong>{top_overall[3].name}</strong> - Advancing through technological innovation and economic growth</li>
                <li><strong>{top_overall[4].name}</strong> - Emerging as a rising power with rapid development</li>
            </ol>
            
            <p>Analysts note that {top_overall[0].name}'s position at the top reflects its successful integration of economic policies, 
            military development, and technological research—creating a mutually reinforcing system that maximizes national power.</p>
            
            <p>The index serves as a benchmark for nations to assess their relative standing in the international community and identify 
            areas for strategic improvement.</p>
            """
            
            article = NewsArticle(
                title=title,
                content=content,
                summary=f"Global power rankings dominated by {top_overall[0].name}, followed by {top_overall[1].name} and {top_overall[2].name}",
                category='ranking',
                importance=3,  # Overall rankings are more important
                nation1_id=top_overall[0].id,
                is_featured=True,  # Feature the overall rankings
                publication_date=datetime.utcnow()
            )
            
            db.session.add(article)
            articles_created += 1
    
    db.session.commit()
    return articles_created