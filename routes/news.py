"""
Routes for the news system
"""

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime, timedelta

from app import db
from models import NewsArticle, Nation
from utils.news_generator import get_latest_news, generate_daily_news

# Create blueprint
news_bp = Blueprint('news', __name__)

@news_bp.route('/news')
@login_required
def news_page():
    """Display the news page with all articles"""
    
    # Get filter parameters
    category = request.args.get('category')
    days = request.args.get('days', '7')  # Default to 7 days
    
    try:
        days = int(days)
        if days <= 0 or days > 30:
            days = 7  # Default if invalid
    except ValueError:
        days = 7  # Default if not a number
    
    # Get news for the specified time period
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = NewsArticle.query.filter(NewsArticle.publication_date >= cutoff_date)
    
    if category and category != 'all':
        query = query.filter(NewsArticle.category == category)
    
    # Order by publication date (newest first)
    articles = query.order_by(desc(NewsArticle.is_featured), 
                              desc(NewsArticle.importance),
                              desc(NewsArticle.publication_date)).all()
    
    # Get categories for filter dropdown
    categories = db.session.query(NewsArticle.category).distinct().all()
    category_list = [c[0] for c in categories]
    
    return render_template(
        'news.html',
        articles=articles,
        categories=category_list,
        current_category=category if category else 'all',
        current_days=days
    )

@news_bp.route('/news/<int:article_id>')
@login_required
def article_detail(article_id):
    """Display a single news article"""
    article = NewsArticle.query.get_or_404(article_id)
    
    # Get related articles if they exist
    related_articles = []
    
    if article.category:
        related_articles = NewsArticle.query.filter(
            NewsArticle.category == article.category,
            NewsArticle.id != article.id
        ).order_by(desc(NewsArticle.publication_date)).limit(3).all()
    
    return render_template(
        'article.html',
        article=article,
        related_articles=related_articles
    )

@news_bp.route('/api/news/latest')
@login_required
def latest_news_api():
    """API endpoint to get the latest news articles"""
    limit = request.args.get('limit', 5, type=int)
    category = request.args.get('category')
    
    articles = get_latest_news(limit=limit, category=category)
    
    # Convert to JSON-serializable format
    articles_data = []
    for article in articles:
        article_data = {
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'category': article.category,
            'importance': article.importance,
            'publication_date': article.publication_date.strftime('%Y-%m-%d %H:%M'),
            'is_featured': article.is_featured
        }
        articles_data.append(article_data)
    
    return jsonify({
        'status': 'success',
        'data': articles_data
    })

@news_bp.route('/api/news/generate', methods=['POST'])
@login_required
def generate_news_api():
    """Admin endpoint to manually generate news"""
    # Check if user is admin
    if not hasattr(current_user, 'nation') or not current_user.nation:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this endpoint'
        }), 403
    
    # For now, allow anyone to generate news for testing purposes
    # Later, add proper admin checks
    try:
        articles_created = generate_daily_news()
        return jsonify({
            'status': 'success',
            'message': f'Generated {articles_created} news articles',
            'data': {
                'articles_created': articles_created
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error generating news: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error generating news: {str(e)}'
        }), 500