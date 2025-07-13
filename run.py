#!/usr/bin/env python3
"""
Simple Bosta Integration System
Clean initialization and testing script for orders management
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from app.models.database import init_production_db, get_db_status, optimize_database
from app.services.bosta_api import login
from server import create_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bosta_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_system():
    """Initialize the clean system"""
    logger.info("="*60)
    logger.info("BOSTA INTEGRATION SYSTEM INITIALIZATION")
    logger.info("="*60)
    
    try:
        # Step 1: Initialize database
        logger.info("Step 1: Initializing database...")
        init_success = init_production_db()
        if init_success:
            logger.info("✅ Database initialized successfully")
        else:
            logger.error("❌ Database initialization failed")
            return False
        
        # Step 2: Verify database status
        logger.info("Step 2: Verifying database status...")
        db_status = get_db_status()
        if db_status.get('success'):
            tables = db_status.get('tables', {})
            logger.info(f"✅ Database verification complete - {len(tables)} tables ready")
            for table, count in tables.items():
                logger.info(f"   📊 {table}: {count} records")
        else:
            logger.error(f"❌ Database verification failed: {db_status.get('error')}")
            return False
        
        # Step 3: Test API connectivity (optional)
        logger.info("Step 3: Testing Bosta API connectivity...")
        try:
            login_result = login()
            if login_result.get('success'):
                logger.info("✅ Bosta API connection successful")
            else:
                logger.warning(f"⚠️ Bosta API connection failed: {login_result.get('error')}")
                logger.warning("API connectivity is optional for orders-only mode")
        except Exception as e:
            logger.warning(f"⚠️ API test skipped: {e}")
        
        # Step 4: Optimize database
        logger.info("Step 4: Optimizing database performance...")
        optimize_result = optimize_database()
        if optimize_result.get('success'):
            logger.info("✅ Database optimization complete")
        else:
            logger.warning(f"⚠️ Database optimization failed: {optimize_result.get('error')}")
        
        logger.info("="*60)
        logger.info("🎉 SYSTEM INITIALIZATION COMPLETE")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        return False

def test_system():
    """Test the system functionality"""
    logger.info("="*60)
    logger.info("SYSTEM TESTING")
    logger.info("="*60)
    
    try:
        # Test 1: Database connectivity
        logger.info("Test 1: Database connectivity...")
        db_status = get_db_status()
        if db_status.get('success'):
            logger.info("✅ Database connectivity test passed")
        else:
            logger.error(f"❌ Database connectivity test failed: {db_status.get('error')}")
            return False
        
        # Test 2: API connectivity (optional)
        logger.info("Test 2: API connectivity...")
        try:
            login_result = login()
            if login_result.get('success'):
                logger.info("✅ API connectivity test passed")
            else:
                logger.warning(f"⚠️ API connectivity test failed: {login_result.get('error')}")
        except Exception as e:
            logger.warning(f"⚠️ API test skipped: {e}")
        
        # Test 3: Flask application
        logger.info("Test 3: Flask application...")
        app = create_app(init_db=False)  # Don't re-initialize DB
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                logger.info("✅ Flask application test passed")
            else:
                logger.error(f"❌ Flask application test failed: {response.status_code}")
                return False
        
        logger.info("="*60)
        logger.info("🎉 ALL SYSTEM TESTS PASSED")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ System testing failed: {e}")
        return False

def show_status():
    """Show system status"""
    try:
        # Import clean logger
        from app.services.order_processor import clean_log
        
        # Database status
        db_status = get_db_status()
        if db_status.get('success'):
            clean_log.success("Database: Connected")
            tables = db_status.get('tables', {})
            if isinstance(tables, dict):
                total_records = sum(tables.values())
                clean_log.info(f"Records: {total_records:,} total")
            else:
                clean_log.info("Database ready")
        else:
            clean_log.error(f"Database error: {db_status.get('error')}")
        
        # API status (optional)
        try:
            login_result = login()
            if login_result.get('success'):
                clean_log.success("API: Connected")
            else:
                clean_log.warning(f"API: Disconnected - {login_result.get('error')}")
        except Exception as e:
            clean_log.warning("API: Not configured")
        
    except Exception as e:
        clean_log.error(f"Status check failed: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Bosta Integration System - Orders Only')
    parser.add_argument('--init', action='store_true', help='Initialize the system')
    parser.add_argument('--test', action='store_true', help='Run system tests')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--server', action='store_true', help='Start the server')
    parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Show header
    from app.services.order_processor import clean_log
    clean_log.info("Bosta Integration System - Orders Only")
    
    success = True
    
    # Execute requested actions
    if args.init:
        success = initialize_system() and success
    
    if args.test:
        success = test_system() and success
    
    if args.status:
        show_status()
    
    if args.server:
        clean_log.sync_status("Starting server...")
        app = create_app()
        try:
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug,
                threaded=True
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            success = False
    
    # If no specific action requested, show help
    if not any([args.init, args.test, args.status, args.server]):
        parser.print_help()
        print("\nExamples:")
        print("  python run.py --init          Initialize the system")
        print("  python run.py --test          Run system tests")
        print("  python run.py --status        Show system status")
        print("  python run.py --server        Start the server")
        print("  python run.py --server --debug  Start in debug mode")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 