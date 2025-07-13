"""
Customer Management Models and Schema for HVAR CRM
Comprehensive customer profile management with segmentation and analytics
"""
import logging
import sqlite3
from contextlib import contextmanager
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.models.database import get_db

# Setup logging
logger = logging.getLogger(__name__)

# Customer Management Schema
CUSTOMER_MANAGEMENT_SCHEMA = """
-- Core customer profiles
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(100),
    primary_city VARCHAR(50),
    primary_zone VARCHAR(50),
    primary_district VARCHAR(50),
    primary_address TEXT,
    total_orders INTEGER DEFAULT 0,
    total_value DECIMAL(10,2) DEFAULT 0,
    avg_order_value DECIMAL(10,2) DEFAULT 0,
    first_order_date DATE,
    last_order_date DATE,
    customer_segment VARCHAR(20) DEFAULT 'new',
    return_rate DECIMAL(5,2) DEFAULT 0,
    satisfaction_score DECIMAL(3,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer addresses (multiple addresses per customer)
CREATE TABLE IF NOT EXISTS customer_addresses (
    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    city VARCHAR(50),
    zone VARCHAR(50),
    district VARCHAR(50),
    address_line TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Customer segments and classification rules
CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    segment_name VARCHAR(50),
    min_orders INTEGER DEFAULT 0,
    min_value DECIMAL(10,2) DEFAULT 0,
    max_return_rate DECIMAL(5,2) DEFAULT 100,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer interactions tracking
CREATE TABLE IF NOT EXISTS customer_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    interaction_type VARCHAR(50),
    channel VARCHAR(50),
    subject VARCHAR(200),
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    assigned_agent VARCHAR(100),
    customer_satisfaction VARCHAR(20),
    resolution_time_hours INTEGER,
    follow_up_date DATE,
    follow_up_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Customer service queue
CREATE TABLE IF NOT EXISTS customer_service_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    interaction_id INTEGER,
    priority_score INTEGER DEFAULT 0,
    queue_position INTEGER,
    issue_type VARCHAR(50),
    customer_segment VARCHAR(20),
    estimated_wait_time INTEGER,
    assigned_agent VARCHAR(100),
    status VARCHAR(20) DEFAULT 'waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (interaction_id) REFERENCES customer_interactions(interaction_id)
);

-- Customer analytics and metrics
CREATE TABLE IF NOT EXISTS customer_analytics (
    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    lifetime_value DECIMAL(10,2),
    avg_order_value DECIMAL(10,2),
    order_frequency DECIMAL(5,2),
    return_rate DECIMAL(5,2),
    satisfaction_score DECIMAL(3,2),
    churn_risk_score DECIMAL(3,2),
    next_purchase_prediction DATE,
    customer_health_score DECIMAL(3,2),
    segment_recommendation VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(customer_segment);
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(primary_city);
CREATE INDEX IF NOT EXISTS idx_customer_addresses_customer ON customer_addresses(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_interactions_customer ON customer_interactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_interactions_status ON customer_interactions(status);
CREATE INDEX IF NOT EXISTS idx_customer_service_queue_status ON customer_service_queue(status);
CREATE INDEX IF NOT EXISTS idx_customer_analytics_customer ON customer_analytics(customer_id);
"""

def init_customer_management_db():
    """
    Initialize the customer management database with comprehensive schema
    """
    try:
        with get_db() as conn:
            # Execute the complete schema
            conn.executescript(CUSTOMER_MANAGEMENT_SCHEMA)
            conn.commit()
            
            # Insert default customer segments
            insert_default_segments(conn)
            
            logger.info("✅ Customer management database initialized successfully")
            return {
                'success': True,
                'message': 'Customer management database ready'
            }
            
    except Exception as e:
        logger.error(f"❌ Customer management database initialization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def insert_default_segments(conn):
    """
    Insert default customer segments
    """
    default_segments = [
        ('new', 1, 0, 100, 'New customers with 1-2 orders'),
        ('regular', 3, 0, 30, 'Regular customers with 3-10 orders'),
        ('vip', 10, 5000, 20, 'VIP customers with high value or many orders'),
        ('problematic', 0, 0, 100, 'Customers with high return rates or complaints')
    ]
    
    try:
        conn.executemany("""
            INSERT OR IGNORE INTO customer_segments 
            (segment_name, min_orders, min_value, max_return_rate, description)
            VALUES (?, ?, ?, ?, ?)
        """, default_segments)
        conn.commit()
        logger.info("✅ Default customer segments inserted")
    except Exception as e:
        logger.error(f"❌ Failed to insert default segments: {e}")

class CustomerManager:
    """
    Customer management class for handling customer operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_customers_from_orders(self, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Extract unique customers from existing orders table
        Efficient: fetch all orders in one query, group by phone in memory, process each customer from grouped orders.
        """
        try:
            with get_db() as conn:
                # Fetch all orders in one query
                cursor = conn.execute("""
                    SELECT 
                        receiver_phone,           -- 0
                        receiver_name,            -- 1
                        receiver_first_name,      -- 2
                        receiver_last_name,       -- 3
                        dropoff_city_name,        -- 4
                        dropoff_zone_name,        -- 5
                        dropoff_district_name,    -- 6
                        dropoff_first_line,       -- 7
                        cod,                      -- 8
                        created_at,               -- 9
                        delivered_at,             -- 10
                        returned_at,              -- 11
                        state_code,               -- 12
                        state_value               -- 13
                    FROM orders 
                    WHERE receiver_phone IS NOT NULL AND receiver_phone != ''
                    ORDER BY receiver_phone, created_at
                """)
                orders = cursor.fetchall()
                
                # Group orders by phone in memory
                from collections import defaultdict
                customer_orders = defaultdict(list)
                for order in orders:
                    phone = order[0]
                    if phone:
                        customer_orders[phone].append(order)
                
                self.logger.info(f"🔄 Starting customer extraction for {len(customer_orders)} unique customers (in-memory grouping)")
                
                customers_created = 0
                addresses_created = 0
                processed = 0
                
                for phone, orders in customer_orders.items():
                    try:
                        # Check if customer already exists
                        cursor = conn.execute("SELECT customer_id FROM customers WHERE phone = ?", (phone,))
                        existing_customer = cursor.fetchone()
                        
                        if existing_customer:
                            # Update existing customer with ALL orders
                            self._update_customer_from_orders(conn, existing_customer[0], orders)
                        else:
                            # Create new customer with ALL orders
                            customer_id = self._create_customer_from_orders(conn, phone, orders)
                            if customer_id:
                                customers_created += 1
                                addresses_created += self._create_customer_addresses(conn, customer_id, orders)
                        processed += 1
                        if processed % 100 == 0:
                            self.logger.info(f"📊 Processed {processed}/{len(customer_orders)} customers, "
                                           f"Created {customers_created} customers, {addresses_created} addresses")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to process customer {phone}: {e}")
                        continue
                
                # Update customer analytics
                self._update_customer_analytics(conn)
                self.logger.info(f"✅ Customer extraction completed: "
                               f"{customers_created} customers, {addresses_created} addresses")
                
                return {
                    'success': True,
                    'total_customers_processed': processed,
                    'customers_created': customers_created,
                    'addresses_created': addresses_created
                }
        except Exception as e:
            self.logger.error(f"❌ Customer extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_customer_from_orders(self, conn, phone: str, orders: List) -> Optional[int]:
        """
        Create a new customer from order data
        
        Args:
            conn: Database connection
            phone: Customer phone number
            orders: List of customer orders
            
        Returns:
            Customer ID if created successfully, None otherwise
        """
        try:
            # Calculate customer metrics with correct column indices
            total_orders = len(orders)
            
            # Calculate total_value from COD (column 8) - only positive COD values
            total_value = sum(order[8] or 0 for order in orders if (order[8] or 0) > 0)
            avg_order_value = total_value / total_orders if total_orders > 0 else 0
            
            # Get first and last order dates (column 9 - created_at)
            order_dates = [order[9] for order in orders if order[9]] # Use column 9 for created_at
            first_order_date = min(order_dates) if order_dates else None
            last_order_date = max(order_dates) if order_dates else None
            
            # Calculate return rate based on state_code = 46 (Returned to business)
            returned_orders = sum(1 for order in orders if order[12] == 46)  # state_code = 46
            return_rate = (returned_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Calculate satisfaction score based on return rate and order patterns
            satisfaction_score = self._calculate_satisfaction_score(return_rate, total_orders, total_value)
            
            # Determine customer segment
            customer_segment = self._determine_customer_segment(total_orders, total_value, return_rate)
            
            # Get customer name from most recent order
            latest_order = max(orders, key=lambda x: x[9] or '')  # created_at
            first_name = latest_order[2] or ''  # receiver_first_name
            last_name = latest_order[3] or ''   # receiver_last_name
            full_name = latest_order[1] or f"{first_name} {last_name}".strip()  # receiver_name
            
            # Get primary address from most frequent location
            address_counts = {}
            for order in orders:
                city = order[4]  # dropoff_city_name
                zone = order[5]  # dropoff_zone_name
                district = order[6]  # dropoff_district_name
                address_key = f"{city}|{zone}|{district}"
                address_counts[address_key] = address_counts.get(address_key, 0) + 1
            
            primary_location = max(address_counts.items(), key=lambda x: x[1])[0] if address_counts else None
            primary_city, primary_zone, primary_district = primary_location.split('|') if primary_location else (None, None, None)
            
            # Insert customer
            cursor = conn.execute("""
                INSERT INTO customers (
                    phone, first_name, last_name, full_name,
                    primary_city, primary_zone, primary_district,
                    total_orders, total_value, avg_order_value,
                    first_order_date, last_order_date,
                    customer_segment, return_rate, satisfaction_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                phone, first_name, last_name, full_name,
                primary_city, primary_zone, primary_district,
                total_orders, total_value, avg_order_value,
                first_order_date, last_order_date,
                customer_segment, return_rate, satisfaction_score
            ))
            
            return cursor.lastrowid
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create customer {phone}: {e}")
            return None
    
    def _update_customer_from_orders(self, conn, customer_id: int, orders: List):
        """
        Update existing customer with new order data
        
        Args:
            conn: Database connection
            customer_id: Customer ID to update
            orders: List of customer orders
        """
        try:
            # Recalculate metrics with correct column indices
            total_orders = len(orders)
            
            # Calculate total_value from COD (column 8) - only positive COD values
            total_value = sum(order[8] or 0 for order in orders if (order[8] or 0) > 0)
            avg_order_value = total_value / total_orders if total_orders > 0 else 0
            
            # Get order dates (column 9 - created_at)
            order_dates = [order[9] for order in orders if order[9]] # Use column 9 for created_at
            first_order_date = min(order_dates) if order_dates else None
            last_order_date = max(order_dates) if order_dates else None
            
            # Calculate return rate based on state_code = 46 (Returned to business)
            returned_orders = sum(1 for order in orders if order[12] == 46)  # state_code = 46
            return_rate = (returned_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Calculate satisfaction score
            satisfaction_score = self._calculate_satisfaction_score(return_rate, total_orders, total_value)
            
            # Determine customer segment
            customer_segment = self._determine_customer_segment(total_orders, total_value, return_rate)
            
            # Update customer
            conn.execute("""
                UPDATE customers SET
                    total_orders = ?,
                    total_value = ?,
                    avg_order_value = ?,
                    first_order_date = ?,
                    last_order_date = ?,
                    customer_segment = ?,
                    return_rate = ?,
                    satisfaction_score = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = ?
            """, (
                total_orders, total_value, avg_order_value,
                first_order_date, last_order_date,
                customer_segment, return_rate, satisfaction_score, customer_id
            ))
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update customer {customer_id}: {e}")
    
    def _create_customer_addresses(self, conn, customer_id: int, orders: List) -> int:
        """
        Create customer addresses from order data
        
        Args:
            conn: Database connection
            customer_id: Customer ID
            orders: List of customer orders
            
        Returns:
            Number of addresses created
        """
        try:
            addresses_created = 0
            
            # Group addresses by location with correct column indices
            address_counts = {}
            for order in orders:
                city = order[4]  # dropoff_city_name
                zone = order[5]  # dropoff_zone_name
                district = order[6]  # dropoff_district_name
                address_line = order[7]  # dropoff_first_line
                
                if city and zone:  # Only create addresses with valid city/zone
                    address_key = f"{city}|{zone}|{district}|{address_line}"
                    address_counts[address_key] = address_counts.get(address_key, 0) + 1
            
            # Create addresses, marking the most frequent as primary
            sorted_addresses = sorted(address_counts.items(), key=lambda x: x[1], reverse=True)
            
            for i, (address_key, count) in enumerate(sorted_addresses):
                city, zone, district, address_line = address_key.split('|')
                is_primary = (i == 0)  # First address is primary
                
                # Check if address already exists
                cursor = conn.execute("""
                    SELECT address_id FROM customer_addresses 
                    WHERE customer_id = ? AND city = ? AND zone = ? AND district = ?
                """, (customer_id, city, zone, district))
                
                if not cursor.fetchone():
                    conn.execute("""
                        INSERT INTO customer_addresses (
                            customer_id, city, zone, district, address_line, is_primary
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (customer_id, city, zone, district, address_line, is_primary))
                    addresses_created += 1
            
            return addresses_created
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create addresses for customer {customer_id}: {e}")
            return 0
    
    def _calculate_satisfaction_score(self, return_rate: float, total_orders: int, total_value: float) -> float:
        """
        Calculate customer satisfaction score based on various factors
        
        Args:
            return_rate: Customer return rate percentage
            total_orders: Total number of orders
            total_value: Total order value
            
        Returns:
            Satisfaction score between 0 and 5
        """
        try:
            # Base score starts at 3.0 (neutral)
            score = 3.0
            
            # Adjust based on return rate (lower is better)
            if return_rate <= 5:
                score += 1.5
            elif return_rate <= 10:
                score += 1.0
            elif return_rate <= 20:
                score += 0.5
            elif return_rate > 50:
                score -= 1.5
            
            # Adjust based on order frequency (more orders = more engagement)
            if total_orders >= 10:
                score += 0.5
            elif total_orders >= 5:
                score += 0.3
            elif total_orders >= 2:
                score += 0.1
            
            # Adjust based on order value (higher value = more satisfied)
            # For customers with very low values, don't penalize too much
            if total_value > 10000:
                score += 0.5
            elif total_value > 5000:
                score += 0.3
            elif total_value > 1000:
                score += 0.1
            elif total_value > 100:
                score += 0.05
            elif total_value == 0:
                # For customers with 0 value, assume they might be new or have free orders
                score += 0.1
            
            # Ensure score is within bounds
            return max(1.0, min(5.0, score))  # Minimum score of 1.0
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating satisfaction score: {e}")
            return 3.0  # Default neutral score
    
    def _determine_customer_segment(self, total_orders: int, total_value: float, return_rate: float) -> str:
        """
        Determine customer segment based on order patterns
        
        Args:
            total_orders: Total number of orders
            total_value: Total order value
            return_rate: Return rate percentage
            
        Returns:
            Customer segment string
        """
        # Problematic customers (high return rate)
        if return_rate > 30:
            return 'problematic'
        
        # VIP customers (high value or many orders)
        if total_value > 5000 or total_orders >= 10:
            return 'vip'
        
        # Regular customers (consistent ordering)
        if total_orders >= 3:
            return 'regular'
        
        # New customers
        return 'new'
    
    def _update_customer_analytics(self, conn):
        """
        Update customer analytics after extraction
        
        Args:
            conn: Database connection
        """
        try:
            # Calculate customer lifetime value and other metrics, including next_purchase_prediction and segment_recommendation
            conn.execute("""
                INSERT OR REPLACE INTO customer_analytics (
                    customer_id, lifetime_value, avg_order_value, order_frequency,
                    return_rate, satisfaction_score, churn_risk_score, customer_health_score,
                    next_purchase_prediction, segment_recommendation
                )
                SELECT 
                    c.customer_id,
                    c.total_value as lifetime_value,
                    c.avg_order_value,
                    CASE 
                        WHEN c.total_orders > 0 AND c.first_order_date IS NOT NULL 
                        THEN CAST(c.total_orders AS FLOAT) / 
                             (julianday(c.last_order_date) - julianday(c.first_order_date) + 1) * 30
                        ELSE 0 
                    END as order_frequency,
                    c.return_rate,
                    c.satisfaction_score,
                    CASE 
                        WHEN c.return_rate > 30 THEN 0.8
                        WHEN c.return_rate > 20 THEN 0.6
                        WHEN c.return_rate > 10 THEN 0.4
                        ELSE 0.2
                    END as churn_risk_score,
                    CASE 
                        WHEN c.customer_segment = 'vip' THEN 0.9
                        WHEN c.customer_segment = 'regular' THEN 0.7
                        WHEN c.customer_segment = 'new' THEN 0.5
                        ELSE 0.3
                    END as customer_health_score,
                    CASE 
                        WHEN c.total_orders > 0 AND c.last_order_date IS NOT NULL AND (
                            CAST(c.total_orders AS FLOAT) / (julianday(c.last_order_date) - julianday(c.first_order_date) + 1)
                        ) > 0 THEN date(c.last_order_date, '+' || CAST(30.0 / (CAST(c.total_orders AS FLOAT) / (julianday(c.last_order_date) - julianday(c.first_order_date) + 1)) AS INTEGER) || ' days')
                        ELSE date(c.last_order_date, '+90 days')
                    END as next_purchase_prediction,
                    CASE 
                        WHEN c.total_orders >= 10 AND c.total_value >= 5000 THEN 'vip'
                        WHEN c.total_orders >= 3 THEN 'regular'
                        WHEN c.return_rate > 30 THEN 'problematic'
                        ELSE 'new'
                    END as segment_recommendation
                FROM customers c
            """)
            conn.commit()
            self.logger.info("✅ Customer analytics updated")
        except Exception as e:
            self.logger.error(f"❌ Failed to update customer analytics: {e}")

def get_customer_stats():
    """
    Get customer management statistics
    
    Returns:
        Dictionary with customer statistics
    """
    try:
        with get_db() as conn:
            # Get customer counts by segment
            cursor = conn.execute("""
                SELECT 
                    customer_segment,
                    COUNT(*) as count,
                    AVG(total_value) as avg_value,
                    AVG(return_rate) as avg_return_rate,
                    AVG(satisfaction_score) as avg_satisfaction
                FROM customers 
                GROUP BY customer_segment
            """)
            
            segment_stats = cursor.fetchall()
            
            # Get total customers
            cursor = conn.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]
            
            # Get customers with interactions
            cursor = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM customer_interactions")
            customers_with_interactions = cursor.fetchone()[0]
            
            # Get data quality metrics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN satisfaction_score IS NOT NULL AND satisfaction_score > 0 THEN 1 ELSE 0 END) as satisfaction_filled,
                    SUM(CASE WHEN primary_address IS NOT NULL AND primary_address != '' THEN 1 ELSE 0 END) as address_filled
                FROM customers
            """)
            quality_stats = cursor.fetchone()
            
            return {
                'success': True,
                'total_customers': total_customers,
                'customers_with_interactions': customers_with_interactions,
                'data_quality': {
                    'total': quality_stats[0],
                    'satisfaction_filled': quality_stats[1],
                    'address_filled': quality_stats[2],
                    'satisfaction_percentage': round((quality_stats[1] / quality_stats[0]) * 100, 2) if quality_stats[0] > 0 else 0,
                    'address_percentage': round((quality_stats[2] / quality_stats[0]) * 100, 2) if quality_stats[0] > 0 else 0
                },
                'segment_stats': [
                    {
                        'segment': row[0],
                        'count': row[1],
                        'avg_value': row[2],
                        'avg_return_rate': row[3],
                        'avg_satisfaction': row[4]
                    }
                    for row in segment_stats
                ]
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer stats: {e}")
        return {
            'success': False,
            'error': str(e)
        } 