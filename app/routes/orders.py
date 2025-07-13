"""
Clean Orders API - Based on Real Analytics
Comprehensive endpoints with business intelligence and COD categorization
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from flask import Blueprint, jsonify, request
from app.models.database import get_db
from app.utils.phone_utils import normalize_phone
import sqlite3

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def create_api_response(
    success: bool, 
    data: Optional[Any] = None, 
    error: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create consistent TypeScript-like API responses
    
    Args:
        success: Whether the request was successful
        data: Response data
        error: Error message if any
        **kwargs: Additional response fields
        
    Returns:
        Dict[str, Any]: Standardized API response
    """
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    response.update(kwargs)
    return response

@bp.route('', methods=['GET'])
def get_orders() -> Dict[str, Any]:
    """
    Get orders with enhanced filtering based on real analytics
    
    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 25, max: 100)
        sort_by: Sort field (default: 'created_at')
        sort_dir: Sort direction (ASC/DESC, default: DESC)
        phone: Filter by customer phone
        state: Filter by order state code
        tracking: Filter by tracking number
        city: Filter by delivery city
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)
        cod_min: Minimum COD value
        cod_max: Maximum COD value
        order_type: Filter by order type code
        delivery_category: Filter by delivery category (real_sales, maintenance, service)
        has_notes: Filter orders with/without notes (true/false)
        has_product_desc: Filter orders with/without product description (true/false)
        
    Returns:
        Dict[str, Any]: Standardized API response with orders data
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 25)), 100)
        offset = (page - 1) * limit
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'created_at')
        sort_dir = request.args.get('sort_dir', 'DESC').upper()
        
        # Filters
        phone = request.args.get('phone')
        state = request.args.get('state')
        tracking = request.args.get('tracking')
        city = request.args.get('city')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        cod_min = request.args.get('cod_min')
        cod_max = request.args.get('cod_max')
        order_type = request.args.get('order_type')
        delivery_category = request.args.get('delivery_category')
        has_notes = request.args.get('has_notes')
        has_product_desc = request.args.get('has_product_desc')
        
        # Validate sort parameters
        valid_sort_fields = {
            'created_at', 'delivered_at', 'state_code', 'id', 'tracking_number', 
            'receiver_phone', 'cod', 'attempts_count', 'calls_count', 'delivery_time_hours'
        }
        
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_dir not in ('ASC', 'DESC'):
            sort_dir = 'DESC'
        
        # Build query
        with get_db() as conn:
            # Build filters
            where_clauses = []
            params = []
            
            if phone:
                normalized_phone = normalize_phone(phone)
                where_clauses.append("receiver_phone LIKE ?")
                params.append(f"%{normalized_phone}%")
            
            if state:
                where_clauses.append("state_code = ?")
                params.append(state)
            
            if tracking:
                where_clauses.append("tracking_number LIKE ?")
                params.append(f"%{tracking}%")
            
            if city:
                where_clauses.append("dropoff_city_name LIKE ?")
                params.append(f"%{city}%")
            
            if date_from:
                where_clauses.append("date(created_at) >= date(?)")
                params.append(date_from)
            
            if date_to:
                where_clauses.append("date(created_at) <= date(?)")
                params.append(date_to)
            
            if cod_min:
                where_clauses.append("cod >= ?")
                params.append(float(cod_min))
            
            if cod_max:
                where_clauses.append("cod <= ?")
                params.append(float(cod_max))
            
            if order_type:
                where_clauses.append("order_type_code = ?")
                params.append(order_type)
            
            # Delivery category filter based on COD value
            if delivery_category:
                if delivery_category == 'real_sales':
                    where_clauses.append("state_code = 45 AND cod > 500")
                elif delivery_category == 'maintenance':
                    where_clauses.append("state_code = 45 AND cod <= 500 AND cod > 0")
                elif delivery_category == 'service':
                    where_clauses.append("state_code = 45 AND cod = 0")
                elif delivery_category == 'refunds':
                    where_clauses.append("cod < 0")
            
            if has_notes is not None:
                if has_notes.lower() == 'true':
                    where_clauses.append("notes IS NOT NULL AND notes != ''")
                else:
                    where_clauses.append("(notes IS NULL OR notes = '')")
            
            if has_product_desc is not None:
                if has_product_desc.lower() == 'true':
                    where_clauses.append("specs_description IS NOT NULL AND specs_description != ''")
                else:
                    where_clauses.append("(specs_description IS NULL OR specs_description = '')")
            
            # Construct where clause
            where_sql = " AND ".join(where_clauses)
            if where_sql:
                where_sql = "WHERE " + where_sql
            
            # Get total count for pagination
            count_sql = f"SELECT COUNT(*) FROM orders {where_sql}"
            total = conn.execute(count_sql, params).fetchone()[0]
            
            # Get ordered data with enhanced business categorization
            query = f"""
                SELECT 
                    *,
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Order'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Order'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Order'
                        WHEN cod < 0 THEN 'Refund Order'
                        ELSE 'Operational Order'
                    END as business_category,
                    CASE 
                        WHEN cod > 500 THEN 'High Value'
                        WHEN cod > 0 AND cod <= 500 THEN 'Low Value'
                        WHEN cod = 0 THEN 'No Value'
                        WHEN cod < 0 THEN 'Refund'
                        ELSE 'No COD'
                    END as cod_category
                FROM orders 
                {where_sql}
                ORDER BY {sort_by} {sort_dir}
                LIMIT ? OFFSET ?
            """
            
            cursor = conn.execute(query, params + [limit, offset])
            
            # Convert to list of dictionaries
            columns = [column[0] for column in cursor.description]
            orders = []
            
            for row in cursor.fetchall():
                order = dict(zip(columns, row))
                # Format financial data
                for field in ['cod', 'bosta_fees', 'deposited_amount']:
                    if field in order and order[field] is not None:
                        order[field] = float(order[field])
                
                # Format delivery time
                if 'delivery_time_hours' in order and order['delivery_time_hours'] is not None:
                    order['delivery_time_hours'] = float(order['delivery_time_hours'])
                
                # Format boolean fields
                for field in ['is_confirmed_delivery', 'allow_open_package', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                    if field in order:
                        order[field] = bool(order[field])
                
                orders.append(order)
            
            return jsonify(create_api_response(
                success=True,
                data=orders,
                total=total,
                page=page,
                limit=limit
            ))
    except Exception as e:
        logger.error(f"Orders error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/analytics', methods=['GET'])
def get_orders_analytics() -> Dict[str, Any]:
    """
    Get comprehensive order analytics based on real data
    
    Query Parameters:
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)
        city: Filter by delivery city
        
    Returns:
        Dict[str, Any]: Standardized API response with analytics data
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        city = request.args.get('city')
        
        with get_db() as conn:
            # Build date filter
            date_filter = ""
            params = []
            
            if date_from:
                date_filter += " AND date(created_at) >= date(?)"
                params.append(date_from)
            
            if date_to:
                date_filter += " AND date(created_at) <= date(?)"
                params.append(date_to)
            
            if city:
                date_filter += " AND dropoff_city_name LIKE ?"
                params.append(f"%{city}%")
            
            # Get comprehensive analytics
            analytics_query = f"""
                SELECT 
                    -- Overall metrics
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN state_code = 45 THEN 1 END) as delivered_orders,
                    COUNT(CASE WHEN state_code = 46 THEN 1 END) as returned_orders,
                    COUNT(CASE WHEN state_code = 48 THEN 1 END) as cancelled_orders,
                    
                    -- COD analysis
                    SUM(CASE WHEN cod > 0 THEN cod ELSE 0 END) as total_cod_revenue,
                    AVG(CASE WHEN cod > 0 THEN cod ELSE NULL END) as avg_cod,
                    COUNT(CASE WHEN cod > 500 THEN 1 END) as high_value_orders,
                    COUNT(CASE WHEN cod > 0 AND cod <= 500 THEN 1 END) as low_value_orders,
                    COUNT(CASE WHEN cod = 0 THEN 1 END) as zero_cod_orders,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders,
                    
                    -- Delivery categorization
                    COUNT(CASE WHEN state_code = 45 AND cod > 500 THEN 1 END) as real_sales_orders,
                    COUNT(CASE WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 1 END) as maintenance_orders,
                    COUNT(CASE WHEN state_code = 45 AND cod = 0 THEN 1 END) as service_orders,
                    
                    -- Financial metrics
                    SUM(CASE WHEN cod < 0 THEN cod ELSE 0 END) as total_refunds,
                    SUM(CASE WHEN cod > 0 THEN cod ELSE 0 END) - ABS(SUM(CASE WHEN cod < 0 THEN cod ELSE 0 END)) as net_revenue,
                    
                    -- Documentation quality
                    COUNT(CASE WHEN notes IS NOT NULL AND notes != '' THEN 1 END) as orders_with_notes,
                    COUNT(CASE WHEN specs_description IS NOT NULL AND specs_description != '' THEN 1 END) as orders_with_product_desc,
                    
                    -- Customer metrics
                    COUNT(DISTINCT receiver_phone) as unique_customers,
                    
                    -- Performance metrics
                    AVG(CASE WHEN delivery_time_hours IS NOT NULL THEN delivery_time_hours ELSE NULL END) as avg_delivery_time,
                    COUNT(CASE WHEN order_sla_exceeded = 1 THEN 1 END) as sla_exceeded_orders,
                    COUNT(CASE WHEN e2e_sla_exceeded = 1 THEN 1 END) as e2e_sla_exceeded_orders
                FROM orders
                WHERE 1=1 {date_filter}
            """
            
            cursor = conn.execute(analytics_query, params)
            result = cursor.fetchone()
            
            # Calculate derived metrics
            total_orders = result[0] or 0
            delivered_orders = result[1] or 0
            returned_orders = result[2] or 0
            
            analytics = {
                'overall_metrics': {
                    'total_orders': total_orders,
                    'delivered_orders': delivered_orders,
                    'returned_orders': returned_orders,
                    'cancelled_orders': result[3] or 0,
                    'delivery_success_rate': round((delivered_orders / total_orders * 100) if total_orders > 0 else 0, 2),
                    'return_rate': round((returned_orders / total_orders * 100) if total_orders > 0 else 0, 2)
                },
                'cod_analysis': {
                    'total_cod_revenue': float(result[4] or 0),
                    'avg_cod': float(result[5] or 0),
                    'high_value_orders': result[6] or 0,
                    'low_value_orders': result[7] or 0,
                    'zero_cod_orders': result[8] or 0,
                    'refund_orders': result[9] or 0,
                    'high_value_percentage': round((result[6] / total_orders * 100) if total_orders > 0 else 0, 2),
                    'refund_rate': round((result[9] / total_orders * 100) if total_orders > 0 else 0, 2)
                },
                'delivery_categorization': {
                    'real_sales_orders': result[10] or 0,
                    'maintenance_orders': result[11] or 0,
                    'service_orders': result[12] or 0,
                    'real_sales_percentage': round((result[10] / delivered_orders * 100) if delivered_orders > 0 else 0, 2),
                    'maintenance_percentage': round((result[11] / delivered_orders * 100) if delivered_orders > 0 else 0, 2),
                    'service_percentage': round((result[12] / delivered_orders * 100) if delivered_orders > 0 else 0, 2)
                },
                'financial_metrics': {
                    'total_refunds': float(result[13] or 0),
                    'net_revenue': float(result[14] or 0),
                    'revenue_at_risk': abs(float(result[13] or 0)),
                    'profit_margin_impact': round((abs(result[13] or 0) / (result[4] or 1) * 100) if result[4] else 0, 2)
                },
                'documentation_quality': {
                    'orders_with_notes': result[15] or 0,
                    'orders_with_product_desc': result[16] or 0,
                    'notes_coverage': round((result[15] / total_orders * 100) if total_orders > 0 else 0, 2),
                    'product_desc_coverage': round((result[16] / total_orders * 100) if total_orders > 0 else 0, 2)
                },
                'customer_metrics': {
                    'unique_customers': result[17] or 0,
                    'avg_orders_per_customer': round(total_orders / (result[17] or 1), 2)
                },
                'performance_metrics': {
                    'avg_delivery_time': float(result[18] or 0),
                    'sla_exceeded_orders': result[19] or 0,
                    'e2e_sla_exceeded_orders': result[20] or 0,
                    'sla_compliance_rate': round(((total_orders - (result[19] or 0)) / total_orders * 100) if total_orders > 0 else 0, 2)
                }
            }
            
            return jsonify(create_api_response(
                success=True,
                data=analytics
            ))
    except Exception as e:
        logger.error(f"Orders analytics error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/states', methods=['GET'])
def get_order_states() -> Dict[str, Any]:
    """
    Get detailed order states analysis
    
    Returns:
        Dict[str, Any]: Standardized API response with states data
    """
    try:
        with get_db() as conn:
            # Get states analysis
            states_query = """
                SELECT 
                    state_code,
                    state_value,
                    masked_state,
                    COUNT(*) as count,
                    AVG(cod) as avg_cod,
                    SUM(cod) as total_cod,
                    COUNT(CASE WHEN cod > 0 THEN 1 END) as orders_with_cod,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders
                FROM orders
                GROUP BY state_code, state_value, masked_state
                ORDER BY count DESC
            """
            
            cursor = conn.execute(states_query)
            states = []
            
            # Before the loop, get total_orders
            cursor_total = conn.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor_total.fetchone()[0] or 1  # avoid division by zero

            for row in cursor.fetchall():
                states.append({
                    'state_code': row[0],
                    'state_value': row[1],
                    'masked_state': row[2],
                    'count': row[3],
                    'avg_cod': float(row[4] or 0),
                    'total_cod': float(row[5] or 0),
                    'orders_with_cod': row[6],
                    'refund_orders': row[7],
                    'percentage': round((row[3] / total_orders * 100), 2)
                })
            
            # Get order types analysis
            types_query = """
                SELECT 
                    order_type_code,
                    order_type_value,
                    COUNT(*) as count,
                    AVG(cod) as avg_cod,
                    SUM(cod) as total_cod,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders
                FROM orders
                GROUP BY order_type_code, order_type_value
                ORDER BY count DESC
            """
            
            cursor = conn.execute(types_query)
            order_types = []
            
            # Before the loop, get total_orders
            cursor_total = conn.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor_total.fetchone()[0] or 1  # avoid division by zero

            for row in cursor.fetchall():
                order_types.append({
                    'order_type_code': row[0],
                    'order_type_value': row[1],
                    'count': row[2],
                    'avg_cod': float(row[3] or 0),
                    'total_cod': float(row[4] or 0),
                    'refund_orders': row[5],
                    'percentage': round((row[2] / total_orders * 100), 2)
                })
            
            return jsonify(create_api_response(
                success=True,
                data={
                    'states': states,
                    'order_types': order_types
                }
            ))
    except Exception as e:
        logger.error(f"Order states error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/delivery-categories', methods=['GET'])
def get_delivery_categories() -> Dict[str, Any]:
    """
    Get delivery categories analysis (Real Sales, Maintenance, Service)
    
    Returns:
        Dict[str, Any]: Standardized API response with delivery categories
    """
    try:
        with get_db() as conn:
            # Get delivery categories analysis
            categories_query = """
                SELECT 
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Orders'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Orders'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Orders'
                        WHEN cod < 0 THEN 'Refund Orders'
                        ELSE 'Operational Orders'
                    END as category,
                    COUNT(*) as count,
                    AVG(cod) as avg_cod,
                    SUM(cod) as total_cod,
                    COUNT(CASE WHEN cod > 0 THEN 1 END) as revenue_orders,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders
                FROM orders
                WHERE state_code = 45 OR cod < 0
                GROUP BY 
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Orders'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Orders'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Orders'
                        WHEN cod < 0 THEN 'Refund Orders'
                        ELSE 'Operational Orders'
                    END
                ORDER BY count DESC
            """
            
            cursor = conn.execute(categories_query)
            categories = []
            
            # Before the loop, get total_orders
            cursor_total = conn.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor_total.fetchone()[0] or 1  # avoid division by zero

            for row in cursor.fetchall():
                categories.append({
                    'category': row[0],
                    'count': row[1],
                    'avg_cod': float(row[2] or 0),
                    'total_cod': float(row[3] or 0),
                    'revenue_orders': row[4],
                    'refund_orders': row[5],
                    'percentage': round((row[1] / total_orders * 100), 2)
                })
            
            return jsonify(create_api_response(
                success=True,
                data=categories
            ))
    except Exception as e:
        logger.error(f"Delivery categories error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/<order_id>', methods=['GET'])
def get_order(order_id: str) -> Dict[str, Any]:
    """
    Get a single order by ID with enhanced business categorization
    
    Args:
        order_id: The order ID to retrieve
        
    Returns:
        Dict[str, Any]: Standardized API response with order data
    """
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT 
                    *,
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Order'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Order'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Order'
                        WHEN cod < 0 THEN 'Refund Order'
                        ELSE 'Operational Order'
                    END as business_category,
                    CASE 
                        WHEN cod > 500 THEN 'High Value'
                        WHEN cod > 0 AND cod <= 500 THEN 'Low Value'
                        WHEN cod = 0 THEN 'No Value'
                        WHEN cod < 0 THEN 'Refund'
                        ELSE 'No COD'
                    END as cod_category
                FROM orders 
                WHERE id = ?
            """, (order_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return jsonify(create_api_response(
                    success=False,
                    error='Order not found'
                )), 404
            
            # Convert to dictionary
            columns = [column[0] for column in cursor.description]
            order = dict(zip(columns, row))
            
            # Format financial data
            for field in ['cod', 'bosta_fees', 'deposited_amount']:
                if field in order and order[field] is not None:
                    order[field] = float(order[field])
            
            # Format boolean fields
            for field in ['is_confirmed_delivery', 'allow_open_package', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                if field in order:
                    order[field] = bool(order[field])
            
            return jsonify(create_api_response(
                success=True,
                data=order
            ))
    except Exception as e:
        logger.error(f"Order detail error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/tracking/<tracking_number>', methods=['GET'])
def get_order_by_tracking(tracking_number: str) -> Dict[str, Any]:
    """
    Get a single order by tracking number with enhanced business categorization
    
    Args:
        tracking_number: The tracking number to search for
        
    Returns:
        Dict[str, Any]: Standardized API response with order data
    """
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT 
                    *,
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Order'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Order'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Order'
                        WHEN cod < 0 THEN 'Refund Order'
                        ELSE 'Operational Order'
                    END as business_category,
                    CASE 
                        WHEN cod > 500 THEN 'High Value'
                        WHEN cod > 0 AND cod <= 500 THEN 'Low Value'
                        WHEN cod = 0 THEN 'No Value'
                        WHEN cod < 0 THEN 'Refund'
                        ELSE 'No COD'
                    END as cod_category
                FROM orders 
                WHERE tracking_number = ?
            """, (tracking_number,))
            
            row = cursor.fetchone()
            
            if not row:
                return jsonify(create_api_response(
                    success=False,
                    error='Order not found'
                )), 404
            
            # Convert to dictionary
            columns = [column[0] for column in cursor.description]
            order = dict(zip(columns, row))
            
            # Format financial data
            for field in ['cod', 'bosta_fees', 'deposited_amount']:
                if field in order and order[field] is not None:
                    order[field] = float(order[field])
            
            # Format boolean fields
            for field in ['is_confirmed_delivery', 'allow_open_package', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                if field in order:
                    order[field] = bool(order[field])
            
            return jsonify(create_api_response(
                success=True,
                data=order
            ))
    except Exception as e:
        logger.error(f"Order tracking lookup error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/phone/<phone>', methods=['GET'])
def get_orders_by_phone(phone: str) -> Dict[str, Any]:
    """
    Get orders by phone number with enhanced business categorization
    
    Args:
        phone: The phone number to search for
        
    Returns:
        Dict[str, Any]: Standardized API response with orders data
    """
    try:
        # Normalize phone number
        normalized_phone = normalize_phone(phone)
        
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT 
                    *,
                    CASE 
                        WHEN state_code = 45 AND cod > 500 THEN 'Real Sales Order'
                        WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 'Maintenance Order'
                        WHEN state_code = 45 AND cod = 0 THEN 'Service Order'
                        WHEN cod < 0 THEN 'Refund Order'
                        ELSE 'Operational Order'
                    END as business_category,
                    CASE 
                        WHEN cod > 500 THEN 'High Value'
                        WHEN cod > 0 AND cod <= 500 THEN 'Low Value'
                        WHEN cod = 0 THEN 'No Value'
                        WHEN cod < 0 THEN 'Refund'
                        ELSE 'No COD'
                    END as cod_category
                FROM orders 
                WHERE receiver_phone LIKE ? 
                ORDER BY created_at DESC
            """, (f"%{normalized_phone}%",))
            
            # Convert to list of dictionaries
            columns = [column[0] for column in cursor.description]
            orders = []
            
            for row in cursor.fetchall():
                order = dict(zip(columns, row))
                # Format financial data
                for field in ['cod', 'bosta_fees', 'deposited_amount']:
                    if field in order and order[field] is not None:
                        order[field] = float(order[field])
                
                # Format boolean fields
                for field in ['is_confirmed_delivery', 'allow_open_package', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                    if field in order:
                        order[field] = bool(order[field])
                
                orders.append(order)
            
            return jsonify(create_api_response(
                success=True,
                total=len(orders),
                data=orders
            ))
    except Exception as e:
        logger.error(f"Orders by phone error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/stats', methods=['GET'])
def get_order_stats() -> Dict[str, Any]:
    """
    Get enhanced order statistics based on real analytics
    
    Returns:
        Dict[str, Any]: Standardized API response with statistics data
    """
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN delivered_at IS NOT NULL THEN 1 END) as delivered_orders,
                    COUNT(CASE WHEN returned_at IS NOT NULL THEN 1 END) as returned_orders,
                    COUNT(CASE WHEN state_code = 48 THEN 1 END) as cancelled_orders,
                    AVG(cod) as avg_cod,
                    SUM(CASE WHEN cod > 0 THEN cod ELSE 0 END) as total_cod_revenue,
                    SUM(CASE WHEN cod < 0 THEN cod ELSE 0 END) as total_refunds,
                    COUNT(DISTINCT receiver_phone) as unique_customers,
                    MAX(created_at) as latest_order_date,
                    COUNT(CASE WHEN state_code = 45 AND cod > 500 THEN 1 END) as real_sales_orders,
                    COUNT(CASE WHEN state_code = 45 AND cod <= 500 AND cod > 0 THEN 1 END) as maintenance_orders,
                    COUNT(CASE WHEN state_code = 45 AND cod = 0 THEN 1 END) as service_orders,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders,
                    COUNT(CASE WHEN notes IS NOT NULL AND notes != '' THEN 1 END) as orders_with_notes,
                    COUNT(CASE WHEN specs_description IS NOT NULL AND specs_description != '' THEN 1 END) as orders_with_product_desc
                FROM orders
            """)
            
            result = cursor.fetchone()
            
            # Get pending orders count (handle missing table gracefully)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM pending_orders")
                pending_orders_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                pending_orders_count = 0
            
            # Get received pending orders count
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM pending_orders WHERE is_received = 1")
                received_pending_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                received_pending_count = 0
            
            total_orders = result[0] or 0
            delivered_orders = result[1] or 0
            
            stats = {
                'total_orders': total_orders,
                'delivered_orders': delivered_orders,
                'returned_orders': result[2] or 0,
                'cancelled_orders': result[3] or 0,
                'avg_cod': float(result[4] or 0),
                'total_cod_revenue': float(result[5] or 0),
                'total_refunds': float(result[6] or 0),
                'net_revenue': float((result[5] or 0) + (result[6] or 0)),
                'unique_customers': result[7] or 0,
                'latest_order_date': result[8],
                'pending_orders': pending_orders_count,
                'received_pending_orders': received_pending_count,
                'delivery_success_rate': round((delivered_orders / total_orders * 100) if total_orders > 0 else 0, 2),
                'business_categories': {
                    'real_sales_orders': result[9] or 0,
                    'maintenance_orders': result[10] or 0,
                    'service_orders': result[11] or 0,
                    'refund_orders': result[12] or 0
                },
                'documentation_quality': {
                    'orders_with_notes': result[13] or 0,
                    'orders_with_product_desc': result[14] or 0,
                    'notes_coverage': round((result[13] / total_orders * 100) if total_orders > 0 else 0, 2),
                    'product_desc_coverage': round((result[14] / total_orders * 100) if total_orders > 0 else 0, 2)
                }
            }
            
            return jsonify(create_api_response(
                success=True,
                data=stats
            ))
    except Exception as e:
        logger.error(f"Order stats error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

# Pending Orders Routes (keeping existing functionality)

@bp.route('/pending', methods=['GET'])
def get_pending_orders() -> Dict[str, Any]:
    """
    Get pending/returned orders with filtering and pagination
    
    Returns:
        Dict[str, Any]: Standardized API response with pending orders data
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 25)), 100)
        offset = (page - 1) * limit
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'created_at')
        sort_dir = request.args.get('sort_dir', 'DESC').upper()
        
        # Filters
        phone = request.args.get('phone')
        status = request.args.get('status')
        order_type = request.args.get('order_type')
        tracking = request.args.get('tracking')
        is_received = request.args.get('is_received')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Validate sort parameters
        valid_sort_fields = {
            'created_at', 'received_at', 'status', 'order_type', 'tracking_number', 
            'receiver_phone', 'cod', 'last_synced'
        }
        
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_dir not in ('ASC', 'DESC'):
            sort_dir = 'DESC'
        
        # Build query
        with get_db() as conn:
            # Check if pending_orders table exists
            try:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_orders'")
                if not cursor.fetchone():
                    return jsonify(create_api_response(
                        success=True,
                        data=[],
                        total=0,
                        page=page,
                        limit=limit
                    ))
            except Exception:
                return jsonify(create_api_response(
                    success=True,
                    data=[],
                    total=0,
                    page=page,
                    limit=limit
                ))
            
            # Build filters
            where_clauses = []
            params = []
            
            if phone:
                normalized_phone = normalize_phone(phone)
                where_clauses.append("receiver_phone LIKE ?")
                params.append(f"%{normalized_phone}%")
            
            if status:
                where_clauses.append("status = ?")
                params.append(status)
            
            if order_type:
                where_clauses.append("order_type = ?")
                params.append(order_type)
            
            if tracking:
                where_clauses.append("tracking_number LIKE ?")
                params.append(f"%{tracking}%")
            
            if is_received is not None:
                where_clauses.append("is_received = ?")
                params.append(1 if is_received.lower() == 'true' else 0)
            
            if date_from:
                where_clauses.append("date(created_at) >= date(?)")
                params.append(date_from)
            
            if date_to:
                where_clauses.append("date(created_at) <= date(?)")
                params.append(date_to)
            
            # Construct where clause
            where_sql = " AND ".join(where_clauses)
            if where_sql:
                where_sql = "WHERE " + where_sql
            
            # Get total count for pagination
            count_sql = f"SELECT COUNT(*) FROM pending_orders {where_sql}"
            total = conn.execute(count_sql, params).fetchone()[0]
            
            # Get ordered data
            query = f"""
                SELECT * FROM pending_orders 
                {where_sql}
                ORDER BY {sort_by} {sort_dir}
                LIMIT ? OFFSET ?
            """
            
            cursor = conn.execute(query, params + [limit, offset])
            
            # Convert to list of dictionaries
            columns = [column[0] for column in cursor.description]
            pending_orders = []
            
            for row in cursor.fetchall():
                pending_order = dict(zip(columns, row))
                # Format financial data
                for field in ['cod', 'bosta_fees', 'deposited_amount']:
                    if field in pending_order and pending_order[field] is not None:
                        pending_order[field] = float(pending_order[field])
                
                # Format boolean fields
                for field in ['is_received', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                    if field in pending_order:
                        pending_order[field] = bool(pending_order[field])
                
                pending_orders.append(pending_order)
            
            return jsonify(create_api_response(
                success=True,
                data=pending_orders,
                total=total,
                page=page,
                limit=limit
            ))
    except Exception as e:
        logger.error(f"Pending orders error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/pending/<tracking_number>', methods=['GET'])
def get_pending_order_by_tracking(tracking_number: str) -> Dict[str, Any]:
    """
    Get a single pending order by tracking number with TypeScript-like response
    
    Args:
        tracking_number: The tracking number to search for
        
    Returns:
        Dict[str, Any]: Standardized API response with pending order data
    """
    try:
        with get_db() as conn:
            # Check if pending_orders table exists
            try:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_orders'")
                if not cursor.fetchone():
                    return jsonify(create_api_response(
                        success=False,
                        error='Pending orders table not found'
                    )), 404
            except Exception:
                return jsonify(create_api_response(
                    success=False,
                    error='Pending orders table not found'
                )), 404
            
            cursor = conn.execute("SELECT * FROM pending_orders WHERE tracking_number = ?", (tracking_number,))
            row = cursor.fetchone()
            
            if not row:
                return jsonify(create_api_response(
                    success=False,
                    error='Pending order not found'
                )), 404
            
            # Convert to dictionary
            columns = [column[0] for column in cursor.description]
            pending_order = dict(zip(columns, row))
            
            # Format financial data
            for field in ['cod', 'bosta_fees', 'deposited_amount']:
                if field in pending_order and pending_order[field] is not None:
                    pending_order[field] = float(pending_order[field])
            
            # Format boolean fields
            for field in ['is_received', 'order_sla_exceeded', 'e2e_sla_exceeded']:
                if field in pending_order:
                    pending_order[field] = bool(pending_order[field])
            
            return jsonify(create_api_response(
                success=True,
                data=pending_order
            ))
    except Exception as e:
        logger.error(f"Pending order tracking lookup error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/pending/<tracking_number>/status', methods=['PUT'])
def update_pending_order_status(tracking_number: str) -> Dict[str, Any]:
    """
    Update the status of a pending order
    
    Args:
        tracking_number: The tracking number of the pending order
        
    Returns:
        Dict[str, Any]: Standardized API response
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_api_response(
                success=False,
                error='No data provided'
            )), 400
        
        status = data.get('status')
        received_by = data.get('received_by')
        received_notes = data.get('received_notes')
        
        if not status:
            return jsonify(create_api_response(
                success=False,
                error='Status is required'
            )), 400
        
        # Validate status
        valid_statuses = ['pending', 'received', 'processed', 'completed']
        if status not in valid_statuses:
            return jsonify(create_api_response(
                success=False,
                error=f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            )), 400
        
        # Import the order processor to update status
        from app.services.order_processor import order_processor
        
        success = order_processor.update_pending_order_status(
            tracking_number=tracking_number,
            status=status,
            received_by=received_by,
            received_notes=received_notes
        )
        
        if success:
            return jsonify(create_api_response(
                success=True,
                data={'message': f'Pending order {tracking_number} status updated to {status}'}
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error='Failed to update pending order status'
            )), 500
            
    except Exception as e:
        logger.error(f"Update pending order status error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500

@bp.route('/pending/stats', methods=['GET'])
def get_pending_order_stats() -> Dict[str, Any]:
    """
    Get pending order statistics with TypeScript-like response
    
    Returns:
        Dict[str, Any]: Standardized API response with pending order statistics
    """
    try:
        with get_db() as conn:
            # Check if pending_orders table exists
            try:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_orders'")
                if not cursor.fetchone():
                    return jsonify(create_api_response(
                        success=True,
                        data={
                            'total_pending_orders': 0,
                            'received_orders': 0,
                            'pending_orders': 0,
                            'processed_orders': 0,
                            'completed_orders': 0,
                            'exchange_orders': 0,
                            'return_orders': 0,
                            'avg_cod': 0,
                            'total_cod': 0
                        }
                    ))
            except Exception:
                return jsonify(create_api_response(
                    success=True,
                    data={
                        'total_pending_orders': 0,
                        'received_orders': 0,
                        'pending_orders': 0,
                        'processed_orders': 0,
                        'completed_orders': 0,
                        'exchange_orders': 0,
                        'return_orders': 0,
                        'avg_cod': 0,
                        'total_cod': 0
                    }
                ))
            
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_pending_orders,
                    COUNT(CASE WHEN is_received = 1 THEN 1 END) as received_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN order_type = 'EXCHANGE' THEN 1 END) as exchange_orders,
                    COUNT(CASE WHEN order_type = 'CUSTOMER_RETURN_PICKUP' THEN 1 END) as return_orders,
                    AVG(cod) as avg_cod,
                    SUM(cod) as total_cod
                FROM pending_orders
            """)
            
            result = cursor.fetchone()
            
            stats = {
                'total_pending_orders': result[0],
                'received_orders': result[1],
                'pending_orders': result[2],
                'processed_orders': result[3],
                'completed_orders': result[4],
                'exchange_orders': result[5],
                'return_orders': result[6],
                'avg_cod': float(result[7]) if result[7] else 0,
                'total_cod': float(result[8]) if result[8] else 0
            }
            
            return jsonify(create_api_response(
                success=True,
                data=stats
            ))
    except Exception as e:
        logger.error(f"Pending order stats error: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500