"""
Simplified Product Management Models
Core product catalog and inventory management system
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductManagement:
    """Simplified Product Management System for HVAR CRM"""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize simplified product management database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Core product catalog - simplified
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sku VARCHAR(50) UNIQUE NOT NULL,
                        name_ar VARCHAR(500) NOT NULL,
                        name_en VARCHAR(500),
                        brand VARCHAR(100) DEFAULT 'هفار',
                        category VARCHAR(200),
                        unit VARCHAR(50) DEFAULT 'القطعة',
                        selling_price DECIMAL(10,2),
                        purchase_price DECIMAL(10,2),
                        alert_quantity INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Product categories - simplified
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_categories (
                        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_name_ar VARCHAR(200) NOT NULL UNIQUE,
                        category_name_en VARCHAR(200),
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Inventory tracking - simplified
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory (
                        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        location_id INTEGER,
                        quantity_available INTEGER DEFAULT 0,
                        min_stock_level INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                    )
                """)
                
                # Warehouse locations - simplified
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS warehouse_locations (
                        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location_name VARCHAR(200) NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Inventory transactions - simplified
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_transactions (
                        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        location_id INTEGER,
                        transaction_type VARCHAR(20),
                        quantity INTEGER,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(product_id),
                        FOREIGN KEY (location_id) REFERENCES warehouse_locations(location_id)
                    )
                """)
                
                # Initialize default data
                self._init_default_locations(cursor)
                self._init_default_categories(cursor)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _init_default_locations(self, cursor):
        """Initialize default warehouse locations"""
        try:
            cursor.execute("SELECT COUNT(*) FROM warehouse_locations")
            if cursor.fetchone()[0] == 0:
                default_locations = [
                    ('المستودع الرئيسي',),
                    ('المستودع الفرعي',),
                    ('المعرض',)
                ]
                cursor.executemany(
                    "INSERT INTO warehouse_locations (location_name) VALUES (?)",
                    default_locations
                )
        except Exception as e:
            logger.error(f"Error initializing default locations: {e}")
    
    def _init_default_categories(self, cursor):
        """Initialize default product categories"""
        try:
            cursor.execute("SELECT COUNT(*) FROM product_categories")
            if cursor.fetchone()[0] == 0:
                default_categories = [
                    ('كبه', 'Blender'),
                    ('خلاط هفار', 'HVAR Mixer'),
                    ('فرن هفار كهربائي', 'HVAR Electric Oven'),
                    ('قلاية كهربائية', 'Electric Fryer'),
                    ('مكواه بخار هفار', 'HVAR Steam Iron'),
                    ('مكنسة', 'Vacuum Cleaner'),
                    ('عجان', 'Dough Mixer'),
                    ('مطحنه توابل', 'Spice Grinder'),
                    ('هاند بلندر', 'Hand Blender'),
                    ('خامات تصنيع', 'Raw Materials'),
                    ('كرتون', 'Packaging'),
                    ('قطع غيار', 'Spare Parts')
                ]
                cursor.executemany(
                    "INSERT INTO product_categories (category_name_ar, category_name_en) VALUES (?, ?)",
                    default_categories
                )
        except Exception as e:
            logger.error(f"Error initializing default categories: {e}")
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Generate SKU if not provided
                if not product_data.get('sku'):
                    product_data['sku'] = self._generate_sku(product_data['name_ar'])
                # Insert product
                cursor.execute("""
                    INSERT INTO products (
                        sku, name_ar, name_en, brand, category, unit,
                        selling_price, purchase_price, alert_quantity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_data['sku'],
                    product_data['name_ar'],
                    product_data.get('name_en', ''),
                    product_data.get('brand', 'هفار'),
                    product_data.get('category', ''),
                    product_data.get('unit', 'القطعة'),
                    product_data.get('selling_price', 0),
                    product_data.get('purchase_price', 0),
                    product_data.get('alert_quantity', 0)
                ))
                product_id = cursor.lastrowid
                # Initialize inventory
                self._initialize_inventory(cursor, product_id, product_data)
                conn.commit()
                return {
                    'success': True,
                    'product_id': product_id,
                    'sku': product_data['sku'],
                    'message': 'Product created successfully'
                }
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return {
                    'success': False,
                    'error': 'SKU already exists'
                }
            return {
                'success': False,
                'error': 'Database constraint error'
            }
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_sku(self, name_ar: str) -> str:
        """Generate SKU from product name"""
        import re
        # Extract numbers from name
        numbers = re.findall(r'\d+', name_ar)
        if numbers:
            return f"hvar{numbers[0]}"
        
        # Generate based on name hash
        name_hash = hash(name_ar) % 10000
        return f"hvar{name_hash:04d}"
    
    def _initialize_inventory(self, cursor, product_id: int, product_data: Dict[str, Any]):
        """Initialize inventory for new product"""
        try:
            # Get default location
            cursor.execute("SELECT location_id FROM warehouse_locations WHERE is_active = 1 LIMIT 1")
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result[0]
                # Create inventory record
                cursor.execute("""
                    INSERT INTO inventory (product_id, location_id, quantity_available, min_stock_level)
                    VALUES (?, ?, ?, ?)
                """, (
                    product_id,
                    location_id,
                    product_data.get('opening_stock', 0),
                    product_data.get('alert_quantity', 0)
                ))
        except Exception as e:
            logger.error(f"Error initializing inventory: {e}")
    
    def get_product(self, product_id: int = None, sku: str = None) -> Dict[str, Any]:
        """Get product by ID or SKU"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if product_id:
                    cursor.execute("""
                        SELECT p.*, i.quantity_available, i.min_stock_level
                        FROM products p
                        LEFT JOIN inventory i ON p.product_id = i.product_id
                        WHERE p.product_id = ? AND p.is_active = 1
                    """, (product_id,))
                elif sku:
                    cursor.execute("""
                        SELECT p.*, i.quantity_available, i.min_stock_level
                        FROM products p
                        LEFT JOIN inventory i ON p.product_id = i.product_id
                        WHERE p.sku = ? AND p.is_active = 1
                    """, (sku,))
                else:
                    return {
                        'success': False,
                        'error': 'Product ID or SKU is required'
                    }
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    product = dict(zip(columns, row))
                    return {
                        'success': True,
                        'product': product
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Product not found'
                    }
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                update_fields = []
                update_values = []
                
                allowed_fields = ['name_ar', 'name_en', 'brand', 'category', 'unit', 
                                'selling_price', 'purchase_price', 'alert_quantity']
                
                for field in allowed_fields:
                    if field in update_data:
                        update_fields.append(f"{field} = ?")
                        update_values.append(update_data[field])
                
                if not update_fields:
                    return {
                        'success': False,
                        'error': 'No valid fields to update'
                    }
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(product_id)
                
                # Execute update
                cursor.execute(f"""
                    UPDATE products 
                    SET {', '.join(update_fields)}
                    WHERE product_id = ?
                """, update_values)
                
                if cursor.rowcount == 0:
                    return {
                        'success': False,
                        'error': 'Product not found'
                    }
                
                conn.commit()
                
                return {
                    'success': True,
                    'product_id': product_id,
                    'message': 'Product updated successfully'
                }
                
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Soft delete product"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE products 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                """, (product_id,))
                
                if cursor.rowcount == 0:
                    return {
                        'success': False,
                        'error': 'Product not found'
                    }
                
                conn.commit()
                
                return {
                    'success': True,
                    'product_id': product_id,
                    'message': 'Product deleted successfully'
                }
                
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_products(self, filters: Dict[str, Any] = None, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """List products with filtering and pagination"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                query = """
                    SELECT p.*, i.quantity_available, i.min_stock_level
                    FROM products p
                    LEFT JOIN inventory i ON p.product_id = i.product_id
                    WHERE p.is_active = 1
                """
                query_params = []
                
                # Apply filters
                if filters:
                    if filters.get('search'):
                        search_term = f"%{filters['search']}%"
                        query += " AND (p.name_ar LIKE ? OR p.name_en LIKE ? OR p.sku LIKE ?)"
                        query_params.extend([search_term, search_term, search_term])
                
                    if filters.get('category'):
                        query += " AND p.category = ?"
                        query_params.append(filters['category'])
                
                # Get total count
                count_query = query.replace("SELECT p.*, i.quantity_available, i.min_stock_level", "SELECT COUNT(*)")
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()[0]
                
                # Add pagination
                query += " ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
                offset = (page - 1) * limit
                query_params.extend([limit, offset])
                
                # Execute query
                cursor.execute(query, query_params)
                rows = cursor.fetchall()
                
                # Format results
                columns = [description[0] for description in cursor.description]
                products = [dict(zip(columns, row)) for row in rows]
                
                # Calculate pagination info
                total_pages = (total_count + limit - 1) // limit
                
                return {
                    'success': True,
                    'products': products,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total_count': total_count,
                        'total_pages': total_pages
                    }
                }
                
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_product_categories(self) -> Dict[str, Any]:
        """Get product categories"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT category_id, category_name_ar, category_name_en
                    FROM product_categories
                    WHERE is_active = 1 
                    ORDER BY category_name_ar
                """)
                
                rows = cursor.fetchall()
                categories = [
                    {
                        'category_id': row[0],
                        'category_name_ar': row[1],
                        'category_name_en': row[2]
                    }
                    for row in rows
                ]
                
                return {
                    'success': True,
                    'categories': categories
                }
                
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_inventory(self, product_id: int, location_id: int, quantity_change: int, 
                        transaction_type: str, reference_type: str = 'manual', 
                        reference_id: str = None, notes: str = None) -> Dict[str, Any]:
        """Update product inventory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get current inventory
                cursor.execute("""
                    SELECT quantity_available FROM inventory
                    WHERE product_id = ? AND location_id = ?
                """, (product_id, location_id))
                result = cursor.fetchone()
                if result:
                    current_quantity = result[0]
                    new_quantity = current_quantity + quantity_change
                    if new_quantity < 0:
                        return {
                            'success': False,
                            'error': 'Insufficient stock'
                        }
                    # Update inventory
                    cursor.execute("""
                        UPDATE inventory 
                        SET quantity_available = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE product_id = ? AND location_id = ?
                    """, (new_quantity, product_id, location_id))
                else:
                    # Create new inventory record
                    if quantity_change < 0:
                        return {
                            'success': False,
                            'error': 'No inventory record found'
                        }
                    cursor.execute("""
                        INSERT INTO inventory (product_id, location_id, quantity_available)
                        VALUES (?, ?, ?)
                    """, (product_id, location_id, quantity_change))
                    new_quantity = quantity_change
                # Record transaction
                cursor.execute("""
                    INSERT INTO inventory_transactions (
                        product_id, location_id, transaction_type, quantity, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (product_id, location_id, transaction_type, quantity_change, notes))
                conn.commit()
                return {
                    'success': True,
                    'new_quantity': new_quantity,
                    'change': quantity_change,
                    'message': 'Inventory updated successfully'
                }
        except Exception as e:
            logger.error(f"Error updating inventory: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_inventory_status(self, product_id: int = None, location_id: int = None) -> Dict[str, Any]:
        """Get inventory status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if product_id:
                    cursor.execute("""
                        SELECT p.name_ar, p.sku, i.quantity_available, i.min_stock_level,
                               wl.location_name
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    JOIN warehouse_locations wl ON i.location_id = wl.location_id
                        WHERE i.product_id = ?
                    """, (product_id,))
                elif location_id:
                    cursor.execute("""
                        SELECT p.name_ar, p.sku, i.quantity_available, i.min_stock_level,
                               wl.location_name
                        FROM inventory i
                        JOIN products p ON i.product_id = p.product_id
                        JOIN warehouse_locations wl ON i.location_id = wl.location_id
                        WHERE i.location_id = ?
                    """, (location_id,))
                else:
                    cursor.execute("""
                        SELECT p.name_ar, p.sku, i.quantity_available, i.min_stock_level,
                               wl.location_name
                        FROM inventory i
                        JOIN products p ON i.product_id = p.product_id
                        JOIN warehouse_locations wl ON i.location_id = wl.location_id
                    """)
                
                rows = cursor.fetchall()
                inventory = [
                    {
                        'name_ar': row[0],
                        'sku': row[1],
                        'quantity_available': row[2],
                        'min_stock_level': row[3],
                        'location_name': row[4]
                    }
                    for row in rows
                ]
                
                return {
                    'success': True,
                    'inventory': inventory
                }
                
        except Exception as e:
            logger.error(f"Error getting inventory status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_low_stock_alerts(self) -> Dict[str, Any]:
        """Get low stock alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT p.name_ar, p.sku, i.quantity_available, i.min_stock_level,
                           wl.location_name
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    JOIN warehouse_locations wl ON i.location_id = wl.location_id
                    WHERE i.quantity_available <= i.min_stock_level
                    AND i.quantity_available > 0
                    ORDER BY i.quantity_available ASC
                """)
                
                rows = cursor.fetchall()
                alerts = [
                    {
                        'name_ar': row[0],
                        'sku': row[1],
                        'quantity_available': row[2],
                        'min_stock_level': row[3],
                        'location_name': row[4]
                    }
                    for row in rows
                ]
                
                return {
                    'success': True,
                    'alerts': alerts,
                    'count': len(alerts)
                }
                
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            return {
                'success': False,
                'error': str(e)
            } 