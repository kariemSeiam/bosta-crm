"""
Production Database Models and Schema for Bosta Integration
Comprehensive order tracking with geographic hierarchy, timeline events, and analytics
"""
import logging
import sqlite3
from contextlib import contextmanager
import os
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Production database schema
PRODUCTION_SCHEMA = """
-- Core Orders table with comprehensive data structure
CREATE TABLE IF NOT EXISTS orders (
    -- Primary identifiers
    id TEXT PRIMARY KEY,
    tracking_number TEXT UNIQUE NOT NULL,
    
    -- Order status & lifecycle
    state_code INTEGER NOT NULL,
    state_value TEXT,
    masked_state TEXT,
    is_confirmed_delivery BOOLEAN DEFAULT 0,
    allow_open_package BOOLEAN DEFAULT 0,
    
    -- Order type information
    order_type_code INTEGER,
    order_type_value TEXT,
    
    -- Financial data & wallet
    cod REAL DEFAULT 0,
    bosta_fees REAL DEFAULT 0,
    deposited_amount REAL DEFAULT 0,
    
    -- Customer information
    receiver_phone TEXT NOT NULL,
    receiver_name TEXT,
    receiver_first_name TEXT,
    receiver_last_name TEXT,
    receiver_second_phone TEXT,
    
    -- Product information & specifications
    notes TEXT,
    specs_items_count INTEGER DEFAULT 1,
    specs_description TEXT,
    product_name TEXT,
    product_count INTEGER DEFAULT 1,
    
    -- Geographic hierarchy - dropoff address (keeping only essential fields)
    dropoff_city_name TEXT,
    dropoff_city_name_ar TEXT,
    dropoff_zone_name TEXT,
    dropoff_zone_name_ar TEXT,
    dropoff_district_name TEXT,
    dropoff_district_name_ar TEXT,
    dropoff_first_line TEXT,
    
    -- Pickup location data
    pickup_city TEXT,
    pickup_zone TEXT,
    pickup_district TEXT,
    pickup_address TEXT,
    
    -- Delivery information
    delivery_lat REAL,
    delivery_lng REAL,
    star_name TEXT,
    star_phone TEXT,
    
    -- Timeline data (JSON format for dynamic events)
    timeline_json TEXT,
    
    -- Key timeline dates
    created_at TEXT NOT NULL,
    scheduled_at TEXT,
    picked_up_at TEXT,
    received_at_warehouse TEXT,
    delivered_at TEXT,
    returned_at TEXT,
    latest_awb_print_date TEXT,
    last_call_time TEXT,
    
    -- Delivery time calculation (in hours)
    delivery_time_hours REAL,
    
    -- Communication & attempts
    attempts_count INTEGER DEFAULT 0,
    calls_count INTEGER DEFAULT 0,
    
    -- SLA information
    order_sla_timestamp TEXT,
    order_sla_exceeded BOOLEAN DEFAULT 0,
    e2e_sla_timestamp TEXT,
    e2e_sla_exceeded BOOLEAN DEFAULT 0,
    
    -- System data
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_system TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pending/Returned Orders table for tracking exchange, return, and sign-and-return orders
CREATE TABLE IF NOT EXISTS pending_orders (
    -- Primary identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_number TEXT UNIQUE NOT NULL,
    order_id TEXT,
    
    -- Reference to main orders table
    original_order_id TEXT,
    
    -- Order type and status
    order_type TEXT NOT NULL, -- 'EXCHANGE', 'CUSTOMER_RETURN_PICKUP'
    order_type_code INTEGER,
    order_type_value TEXT,
    
    -- Current status tracking
    status TEXT DEFAULT 'pending', -- 'pending', 'received', 'processed', 'completed'
    is_received BOOLEAN DEFAULT 0,
    received_at TEXT,
    received_by TEXT,
    received_notes TEXT,
    
    -- Order details from Bosta API
    state_code INTEGER,
    state_value TEXT,
    masked_state TEXT,
    
    -- Customer information
    receiver_phone TEXT,
    receiver_name TEXT,
    receiver_first_name TEXT,
    receiver_last_name TEXT,
    receiver_second_phone TEXT,
    
    -- Product information
    notes TEXT,
    specs_items_count INTEGER DEFAULT 1,
    specs_description TEXT,
    product_name TEXT,
    product_count INTEGER DEFAULT 1,
    
    -- Financial data
    cod REAL DEFAULT 0,
    bosta_fees REAL DEFAULT 0,
    deposited_amount REAL DEFAULT 0,
    
    -- Geographic information
    dropoff_city_name TEXT,
    dropoff_city_name_ar TEXT,
    dropoff_zone_name TEXT,
    dropoff_zone_name_ar TEXT,
    dropoff_district_name TEXT,
    dropoff_district_name_ar TEXT,
    dropoff_first_line TEXT,
    
    pickup_city TEXT,
    pickup_zone TEXT,
    pickup_district TEXT,
    pickup_address TEXT,
    
    -- Delivery information
    delivery_lat REAL,
    delivery_lng REAL,
    star_name TEXT,
    star_phone TEXT,
    
    -- Timeline and dates
    timeline_json TEXT,
    created_at TEXT,
    scheduled_at TEXT,
    picked_up_at TEXT,
    received_at_warehouse TEXT,
    delivered_at TEXT,
    returned_at TEXT,
    latest_awb_print_date TEXT,
    last_call_time TEXT,
    
    -- Communication & attempts
    attempts_count INTEGER DEFAULT 0,
    calls_count INTEGER DEFAULT 0,
    
    -- SLA information
    order_sla_timestamp TEXT,
    order_sla_exceeded BOOLEAN DEFAULT 0,
    e2e_sla_timestamp TEXT,
    e2e_sla_exceeded BOOLEAN DEFAULT 0,
    
    -- System data
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_system TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key reference to main orders table
    FOREIGN KEY (tracking_number) REFERENCES orders(tracking_number) ON DELETE CASCADE
);

-- Timeline Events table for detailed order tracking
CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    tracking_number TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_value TEXT NOT NULL,
    event_date TEXT,
    is_done BOOLEAN DEFAULT 1,
    description TEXT,
    sequence_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tracking_number) REFERENCES orders(tracking_number) ON DELETE CASCADE
);

-- Create indexes separately
CREATE INDEX IF NOT EXISTS idx_timeline_tracking_number ON timeline_events(tracking_number);
CREATE INDEX IF NOT EXISTS idx_timeline_event_code ON timeline_events(event_code);
CREATE INDEX IF NOT EXISTS idx_timeline_event_date ON timeline_events(event_date);

-- Indexes for pending_orders table
CREATE INDEX IF NOT EXISTS idx_pending_tracking_number ON pending_orders(tracking_number);
CREATE INDEX IF NOT EXISTS idx_pending_order_type ON pending_orders(order_type);
CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_orders(status);
CREATE INDEX IF NOT EXISTS idx_pending_received ON pending_orders(is_received);
CREATE INDEX IF NOT EXISTS idx_pending_phone ON pending_orders(receiver_phone);
CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_pending_received_at ON pending_orders(received_at);
CREATE INDEX IF NOT EXISTS idx_pending_original_order ON pending_orders(original_order_id);
"""

def get_database_path():
    """Get the database file path"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

@contextmanager
def get_db():
    """
    Database connection context manager
    Provides a connection to the SQLite database with proper error handling
    Uses a higher timeout and enables WAL mode for better concurrency
    """
    db_path = get_database_path()
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)  # 30s timeout, autocommit
        conn.row_factory = sqlite3.Row  # Enable row factory for named access
        conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode for concurrency
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_production_db():
    """
    Initialize the production database with comprehensive schema
    Creates all tables and indexes if they don't exist
    """
    try:
        with get_db() as conn:
            # Execute the complete schema
            conn.executescript(PRODUCTION_SCHEMA)
            conn.commit()
            
            # Get table information
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"✅ Production database initialized successfully")
            logger.info(f"📊 Tables created: {', '.join(tables)}")
            
            # Get orders count
            cursor = conn.execute("SELECT COUNT(*) FROM orders")
            orders_count = cursor.fetchone()[0]
            logger.info(f"📦 Orders in database: {orders_count}")
            
            return {
                'success': True,
                'tables': tables,
                'orders_count': orders_count
            }
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_db_status():
    """
    Get comprehensive database status and statistics
    """
    try:
        with get_db() as conn:
            # Get table information
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get orders statistics
            cursor = conn.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE state_value = 'Delivered'")
            delivered_orders = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE state_value = 'Returned'")
            returned_orders = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE state_value = 'Terminated'")
            failed_orders = cursor.fetchone()[0]
            
            # Get timeline events count (handle missing table gracefully)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM timeline_events")
                timeline_events = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                timeline_events = 0
            
            # Get customers count (handle missing table gracefully)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM customers")
                customers_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                customers_count = 0
            
            # Get products count (handle missing table gracefully)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM products")
                products_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                products_count = 0
            
            # Get locations count (handle missing table gracefully)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM locations")
                locations_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                locations_count = 0
            
            # Get database file size
            db_path = get_database_path()
            file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            file_size_mb = file_size / (1024 * 1024)
            
            return {
                'success': True,
                'tables': tables,
                'total_orders': total_orders,
                'delivered_orders': delivered_orders,
                'returned_orders': returned_orders,
                'failed_orders': failed_orders,
                'timeline_events': timeline_events,
                'customers_count': customers_count,
                'products_count': products_count,
                'locations_count': locations_count,
                'file_size_mb': round(file_size_mb, 2),
                'database_path': db_path
            }
            
    except Exception as e:
        logger.error(f"❌ Database status check failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def optimize_database():
    """
    Optimize database performance with VACUUM and ANALYZE
    """
    try:
        with get_db() as conn:
            logger.info("🔧 Optimizing database...")
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.commit()
            logger.info("✅ Database optimization completed")
            return {'success': True}
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        return {'success': False, 'error': str(e)}

def backup_database(backup_path=None):
    """
    Create a backup of the database
    """
    try:
        db_path = get_database_path()
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.backup_{timestamp}"
        
        with get_db() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"✅ Database backup created: {backup_path}")
        return {'success': True, 'backup_path': backup_path}
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        return {'success': False, 'error': str(e)} 