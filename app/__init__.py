"""
Flask application factory module.

This module creates and configures the Flask application instance.
"""

import logging
from flask import Flask

from app.config import Config
from app.models.database import load_prices
from app.utils import (
    BASE_PRODUCT_PRICES,
    SERVICE_EXTRA_CHARGES,
    LAUNDRY_BAG_PRICE,
)

# Import blueprints
from app.routes import public, auth, orders, admin


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    # Load prices from database on startup
    try:
        product_prices, service_prices, bag_price = load_prices(
            BASE_PRODUCT_PRICES,
            SERVICE_EXTRA_CHARGES,
            LAUNDRY_BAG_PRICE
        )
        # Update module-level constants
        BASE_PRODUCT_PRICES.update(product_prices)
        SERVICE_EXTRA_CHARGES.update(service_prices)
        LAUNDRY_BAG_PRICE = bag_price
        logger.info("Prices loaded from database successfully")
    except Exception as e:
        logger.warning(f"Could not load prices from database: {e}. Using defaults.")

    # Register blueprints
    app.register_blueprint(public.public_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(orders.orders_bp)
    app.register_blueprint(admin.admin_bp)

    logger.info("Flask application created successfully")

    return app
