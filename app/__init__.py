#!/usr/bin/env python3
"""
Clean Bosta Integration Application - Orders Only
"""
import os
import logging
import sys
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.models.database import init_production_db
from app.routes import orders, customers, products, customer_service
from app.config import configure_app
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Optional test configuration
        
    Returns:
        Configured Flask application
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Apply proxy fix for proper IP handling
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Configure the application
    configure_app(app)
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_success = init_production_db()
        if init_success:
            logger.info("Database setup complete")
        else:
            logger.error("Database initialization failed")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Continue app startup despite database errors
    
    # Register blueprints
    app.register_blueprint(orders.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(products.products_bp)
    app.register_blueprint(customer_service.bp)
    
    # Add a root route
    @app.route('/')
    def index():
        return {
            "name": "Bosta Integration API - Orders Only",
            "version": "3.0.0",
            "status": "running",
            "features": [
                "Order tracking and management",
                "Customer profile management",
                "Customer segmentation and analytics",
                "Customer interaction tracking",
                "Phone number search",
                "Tracking number lookup",
                "Order filtering and pagination",
                "Basic order statistics",
                "Product catalog and inventory management",
                "Product analytics and performance tracking",
                "Inventory tracking and alerts",
                "Product component management",
                "CSV import and export",
                "Customer service ticket management",
                "Team call scheduling and management",
                "Maintenance and repair cycle management",
                "Replacement management (full/partial)",
                "Hub confirmation system",
                "Team leader action management",
                "Customer follow-up scheduling",
                "Service analytics and reporting",
                "Clean TypeScript-like API responses"
            ]
        }
    
    # Add a health check endpoint
    @app.route('/health')
    def health():
        return {"status": "healthy"}
    
    return app 