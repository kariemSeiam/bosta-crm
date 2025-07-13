"""
Enhanced Customer Management API - Based on Real Analytics
Comprehensive customer profile and interaction management with business intelligence
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from flask import Blueprint, jsonify, request
from app.models.database import get_db
from app.models.customer_management import CustomerManager, init_customer_management_db, get_customer_stats
from app.utils.phone_utils import normalize_phone
import sqlite3

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('customers', __name__, url_prefix='/api/customers')

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

@bp.route('/init', methods=['POST'])
def initialize_customer_management() -> Dict[str, Any]:
    """
    Initialize customer management database and extract customers from orders
    
    Returns:
        Dict[str, Any]: Standardized API response with initialization results
    """
    try:
        # Initialize customer management database
        init_result = init_customer_management_db()
        if not init_result.get('success'):
            return create_api_response(False, error=init_result.get('error'))
        
        # Extract customers from orders
        customer_manager = CustomerManager()
        extraction_result = customer_manager.extract_customers_from_orders()
        
        if extraction_result.get('success'):
            return create_api_response(
                True,
                data={
                    'message': 'Customer management initialized successfully',
                    'extraction_results': extraction_result
                }
            )
        else:
            return create_api_response(False, error=extraction_result.get('error'))
            
    except Exception as e:
        logger.error(f"❌ Customer management initialization failed: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/stats', methods=['GET'])
def get_customers_stats() -> Dict[str, Any]:
    """
    Get enhanced customer management statistics based on real analytics
    
    Returns:
        Dict[str, Any]: Standardized API response with customer statistics
    """
    try:
        with get_db() as conn:
            # Get comprehensive customer statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_customers,
                    COUNT(CASE WHEN customer_segment = 'vip' THEN 1 END) as vip_customers,
                    COUNT(CASE WHEN customer_segment = 'regular' THEN 1 END) as regular_customers,
                    COUNT(CASE WHEN customer_segment = 'new' THEN 1 END) as new_customers,
                    COUNT(CASE WHEN customer_segment = 'problematic' THEN 1 END) as problematic_customers,
                    AVG(total_orders) as avg_orders_per_customer,
                    AVG(total_value) as avg_lifetime_value,
                    AVG(avg_order_value) as avg_order_value,
                    AVG(return_rate) as avg_return_rate,
                    AVG(satisfaction_score) as avg_satisfaction_score,
                    SUM(total_orders) as total_orders,
                    SUM(total_value) as total_revenue,
                    COUNT(CASE WHEN return_rate >= 30 THEN 1 END) as high_return_customers,
                    COUNT(CASE WHEN satisfaction_score >= 0.8 THEN 1 END) as satisfied_customers,
                    COUNT(CASE WHEN total_orders >= 10 OR total_value >= 5000 THEN 1 END) as premium_customers
                FROM customers
            """
            
            cursor = conn.execute(stats_query)
            result = cursor.fetchone()
            
            total_customers = result[0] or 0
            
            stats = {
                'total_customers': total_customers,
                'segment_distribution': {
                    'vip_customers': result[1] or 0,
                    'regular_customers': result[2] or 0,
                    'new_customers': result[3] or 0,
                    'problematic_customers': result[4] or 0,
                    'vip_percentage': round((result[1] / total_customers * 100) if total_customers > 0 else 0, 2),
                    'regular_percentage': round((result[2] / total_customers * 100) if total_customers > 0 else 0, 2),
                    'new_percentage': round((result[3] / total_customers * 100) if total_customers > 0 else 0, 2),
                    'problematic_percentage': round((result[4] / total_customers * 100) if total_customers > 0 else 0, 2)
                },
                'performance_metrics': {
                    'avg_orders_per_customer': round(result[5] or 0, 2),
                    'avg_lifetime_value': round(result[6] or 0, 2),
                    'avg_order_value': round(result[7] or 0, 2),
                    'avg_return_rate': round(result[8] or 0, 2),
                    'avg_satisfaction_score': round(result[9] or 0, 2)
                },
                'business_metrics': {
                    'total_orders': result[10] or 0,
                    'total_revenue': round(result[11] or 0, 2),
                    'high_return_customers': result[12] or 0,
                    'satisfied_customers': result[13] or 0,
                    'premium_customers': result[14] or 0,
                    'high_return_percentage': round((result[12] / total_customers * 100) if total_customers > 0 else 0, 2),
                    'satisfaction_percentage': round((result[13] / total_customers * 100) if total_customers > 0 else 0, 2),
                    'premium_percentage': round((result[14] / total_customers * 100) if total_customers > 0 else 0, 2)
                }
            }
            
            return create_api_response(True, data=stats)
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer stats: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/', methods=['GET'])
def get_customers() -> Dict[str, Any]:
    """
    Get customers with enhanced filtering based on real analytics
    
    Query Parameters:
        segment: Filter by customer segment (vip, regular, new, problematic)
        city: Filter by primary city
        limit: Number of customers to return (default: 50)
        offset: Number of customers to skip (default: 0)
        search: Search in customer names and phone numbers
        satisfaction_min: Minimum satisfaction score
        return_rate_max: Maximum return rate
        order_count_min: Minimum order count
        lifetime_value_min: Minimum lifetime value
        last_order_days: Days since last order
        has_maintenance_orders: Filter customers with maintenance orders (true/false)
        has_refunds: Filter customers with refunds (true/false)
        
    Returns:
        Dict[str, Any]: Standardized API response with customers data
    """
    try:
        # Get query parameters
        segment = request.args.get('segment')
        city = request.args.get('city')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search')
        satisfaction_min = request.args.get('satisfaction_min')
        return_rate_max = request.args.get('return_rate_max')
        order_count_min = request.args.get('order_count_min')
        lifetime_value_min = request.args.get('lifetime_value_min')
        last_order_days = request.args.get('last_order_days')
        has_maintenance_orders = request.args.get('has_maintenance_orders')
        has_refunds = request.args.get('has_refunds')
        
        with get_db() as conn:
            # Build query with enhanced filters
            query = """
                SELECT 
                    c.customer_id,
                    c.phone,
                    c.first_name,
                    c.last_name,
                    c.full_name,
                    c.email,
                    c.primary_city,
                    c.primary_zone,
                    c.primary_district,
                    c.primary_address,
                    c.total_orders,
                    c.total_value,
                    c.avg_order_value,
                    c.first_order_date,
                    c.last_order_date,
                    c.customer_segment,
                    c.return_rate,
                    c.satisfaction_score,
                    c.created_at,
                    c.updated_at,
                    -- Enhanced analytics
                    CASE 
                        WHEN c.total_orders >= 10 OR c.total_value >= 5000 THEN 'Premium'
                        WHEN c.total_orders >= 3 THEN 'Regular'
                        WHEN c.return_rate >= 30 THEN 'Problematic'
                        ELSE 'New'
                    END as business_segment,
                    CASE 
                        WHEN c.satisfaction_score >= 0.8 THEN 'Satisfied'
                        WHEN c.satisfaction_score >= 0.6 THEN 'Neutral'
                        ELSE 'Dissatisfied'
                    END as satisfaction_level,
                    CASE 
                        WHEN c.return_rate >= 30 THEN 'High Risk'
                        WHEN c.return_rate >= 15 THEN 'Medium Risk'
                        ELSE 'Low Risk'
                    END as risk_level
                FROM customers c
                WHERE 1=1
            """
            params = []
            
            if segment:
                query += " AND c.customer_segment = ?"
                params.append(segment)
            
            if city:
                query += " AND c.primary_city = ?"
                params.append(city)
            
            if search:
                query += """ AND (
                    c.full_name LIKE ? OR 
                    c.first_name LIKE ? OR 
                    c.last_name LIKE ? OR 
                    c.phone LIKE ?
                )"""
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term, search_term])
            
            if satisfaction_min:
                query += " AND c.satisfaction_score >= ?"
                params.append(float(satisfaction_min))
            
            if return_rate_max:
                query += " AND c.return_rate <= ?"
                params.append(float(return_rate_max))
            
            if order_count_min:
                query += " AND c.total_orders >= ?"
                params.append(int(order_count_min))
            
            if lifetime_value_min:
                query += " AND c.total_value >= ?"
                params.append(float(lifetime_value_min))
            
            if last_order_days:
                days_ago = datetime.now() - timedelta(days=int(last_order_days))
                query += " AND c.last_order_date >= ?"
                params.append(days_ago.isoformat())
            
            # Complex filters for maintenance orders and refunds
            if has_maintenance_orders is not None:
                if has_maintenance_orders.lower() == 'true':
                    query += """ AND EXISTS (
                        SELECT 1 FROM orders o 
                        WHERE o.receiver_phone = c.phone 
                        AND o.state_code = 45 
                        AND o.cod <= 500 
                        AND o.cod > 0
                    )"""
                else:
                    query += """ AND NOT EXISTS (
                        SELECT 1 FROM orders o 
                        WHERE o.receiver_phone = c.phone 
                        AND o.state_code = 45 
                        AND o.cod <= 500 
                        AND o.cod > 0
                    )"""
            
            if has_refunds is not None:
                if has_refunds.lower() == 'true':
                    query += """ AND EXISTS (
                        SELECT 1 FROM orders o 
                        WHERE o.receiver_phone = c.phone 
                        AND o.cod < 0
                    )"""
                else:
                    query += """ AND NOT EXISTS (
                        SELECT 1 FROM orders o 
                        WHERE o.receiver_phone = c.phone 
                        AND o.cod < 0
                    )"""
            
            # Add ordering and pagination
            query += " ORDER BY c.last_order_date DESC, c.total_value DESC"
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            cursor = conn.execute(query, params)
            customers = []
            
            for row in cursor.fetchall():
                customers.append({
                    'customer_id': row[0],
                    'phone': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'full_name': row[4],
                    'email': row[5],
                    'primary_city': row[6],
                    'primary_zone': row[7],
                    'primary_district': row[8],
                    'primary_address': row[9],
                    'total_orders': row[10],
                    'total_value': row[11],
                    'avg_order_value': row[12],
                    'first_order_date': row[13],
                    'last_order_date': row[14],
                    'customer_segment': row[15],
                    'return_rate': row[16],
                    'satisfaction_score': row[17],
                    'created_at': row[18],
                    'updated_at': row[19],
                    'business_segment': row[20],
                    'satisfaction_level': row[21],
                    'risk_level': row[22]
                })
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM customers WHERE 1=1"
            count_params = []
            
            if segment:
                count_query += " AND customer_segment = ?"
                count_params.append(segment)
            
            if city:
                count_query += " AND primary_city = ?"
                count_params.append(city)
            
            if search:
                count_query += """ AND (
                    full_name LIKE ? OR 
                    first_name LIKE ? OR 
                    last_name LIKE ? OR 
                    phone LIKE ?
                )"""
                search_term = f"%{search}%"
                count_params.extend([search_term, search_term, search_term, search_term])
            
            if satisfaction_min:
                count_query += " AND satisfaction_score >= ?"
                count_params.append(float(satisfaction_min))
            
            if return_rate_max:
                count_query += " AND return_rate <= ?"
                count_params.append(float(return_rate_max))
            
            if order_count_min:
                count_query += " AND total_orders >= ?"
                count_params.append(int(order_count_min))
            
            if lifetime_value_min:
                count_query += " AND total_value >= ?"
                count_params.append(float(lifetime_value_min))
            
            if last_order_days:
                days_ago = datetime.now() - timedelta(days=int(last_order_days))
                count_query += " AND last_order_date >= ?"
                count_params.append(days_ago.isoformat())
            
            cursor = conn.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            return create_api_response(
                True,
                data={
                    'customers': customers,
                    'pagination': {
                        'total': total_count,
                        'limit': limit,
                        'offset': offset,
                        'has_more': (offset + limit) < total_count
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get customers: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/<phone>', methods=['GET'])
def get_customer(phone: str) -> Dict[str, Any]:
    """
    Get detailed customer information with enhanced analytics and order breakdown
    
    Args:
        phone: Customer phone number (can be 01, 201, etc.)
        
    Returns:
        Dict[str, Any]: Standardized API response with customer details
    """
    try:
        # Normalize phone number to handle different formats
        normalized_phone = normalize_phone(phone)
        
        with get_db() as conn:
            # Get customer basic info by phone number (try both original and normalized)
            cursor = conn.execute("""
                SELECT 
                    customer_id, phone, first_name, last_name, full_name, email,
                    primary_city, primary_zone, primary_district, primary_address,
                    total_orders, total_value, avg_order_value,
                    first_order_date, last_order_date, customer_segment,
                    return_rate, satisfaction_score, created_at, updated_at
                FROM customers 
                WHERE phone = ? OR phone = ?
            """, (phone, normalized_phone))
            
            customer_row = cursor.fetchone()
            if not customer_row:
                return create_api_response(False, error="Customer not found")
            
            customer = {
                'customer_id': customer_row[0],
                'phone': customer_row[1],
                'first_name': customer_row[2],
                'last_name': customer_row[3],
                'full_name': customer_row[4],
                'email': customer_row[5],
                'primary_city': customer_row[6],
                'primary_zone': customer_row[7],
                'primary_district': customer_row[8],
                'primary_address': customer_row[9],
                'total_orders': customer_row[10],
                'total_value': customer_row[11],
                'avg_order_value': customer_row[12],
                'first_order_date': customer_row[13],
                'last_order_date': customer_row[14],
                'customer_segment': customer_row[15],
                'return_rate': customer_row[16],
                'satisfaction_score': customer_row[17],
                'created_at': customer_row[18],
                'updated_at': customer_row[19]
            }
            
            # Get enhanced order analytics for this customer
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN state_code = 45 THEN 1 END) as delivered_orders,
                    COUNT(CASE WHEN state_code = 46 THEN 1 END) as returned_orders,
                    COUNT(CASE WHEN state_code = 48 THEN 1 END) as cancelled_orders,
                    
                    -- COD analysis
                    SUM(CASE WHEN cod > 0 THEN cod ELSE 0 END) as total_cod_revenue,
                    AVG(CASE WHEN cod > 0 THEN cod ELSE NULL END) as avg_cod,
                    COUNT(CASE WHEN cod > 500 THEN 1 END) as high_value_orders,
                    COUNT(CASE WHEN cod > 0 AND cod <= 500 THEN 1 END) as maintenance_orders,
                    COUNT(CASE WHEN cod = 0 THEN 1 END) as service_orders,
                    COUNT(CASE WHEN cod < 0 THEN 1 END) as refund_orders,
                    SUM(CASE WHEN cod < 0 THEN cod ELSE 0 END) as total_refunds,
                    
                    -- Order types
                    COUNT(CASE WHEN order_type_code = 10 THEN 1 END) as send_orders,
                    COUNT(CASE WHEN order_type_code = 20 THEN 1 END) as return_orders,
                    COUNT(CASE WHEN order_type_code = 25 THEN 1 END) as customer_return_orders,
                    COUNT(CASE WHEN order_type_code = 30 THEN 1 END) as exchange_orders,
                    
                    -- Performance metrics
                    AVG(CASE WHEN delivery_time_hours IS NOT NULL THEN delivery_time_hours ELSE NULL END) as avg_delivery_time,
                    COUNT(CASE WHEN order_sla_exceeded = 1 THEN 1 END) as sla_exceeded_orders,
                    COUNT(CASE WHEN e2e_sla_exceeded = 1 THEN 1 END) as e2e_sla_exceeded_orders,
                    
                    -- Documentation
                    COUNT(CASE WHEN notes IS NOT NULL AND notes != '' THEN 1 END) as orders_with_notes,
                    COUNT(CASE WHEN specs_description IS NOT NULL AND specs_description != '' THEN 1 END) as orders_with_product_desc
                FROM orders
                WHERE receiver_phone = ? OR receiver_phone = ?
            """, (phone, normalized_phone))
            
            analytics_row = cursor.fetchone()
            order_analytics = {
                'total_orders': analytics_row[0] or 0,
                'delivered_orders': analytics_row[1] or 0,
                'returned_orders': analytics_row[2] or 0,
                'cancelled_orders': analytics_row[3] or 0,
                'delivery_success_rate': round((analytics_row[1] / analytics_row[0] * 100) if analytics_row[0] > 0 else 0, 2),
                'return_rate': round((analytics_row[2] / analytics_row[0] * 100) if analytics_row[0] > 0 else 0, 2),
                'cod_analysis': {
                    'total_cod_revenue': float(analytics_row[4] or 0),
                    'avg_cod': float(analytics_row[5] or 0),
                    'high_value_orders': analytics_row[6] or 0,
                    'maintenance_orders': analytics_row[7] or 0,
                    'service_orders': analytics_row[8] or 0,
                    'refund_orders': analytics_row[9] or 0,
                    'total_refunds': float(analytics_row[10] or 0),
                    'net_revenue': float((analytics_row[4] or 0) + (analytics_row[10] or 0))
                },
                'order_types': {
                    'send_orders': analytics_row[11] or 0,
                    'return_orders': analytics_row[12] or 0,
                    'customer_return_orders': analytics_row[13] or 0,
                    'exchange_orders': analytics_row[14] or 0
                },
                'performance_metrics': {
                    'avg_delivery_time': float(analytics_row[15] or 0),
                    'sla_exceeded_orders': analytics_row[16] or 0,
                    'e2e_sla_exceeded_orders': analytics_row[17] or 0,
                    'sla_compliance_rate': round(((analytics_row[0] - analytics_row[16]) / analytics_row[0] * 100) if analytics_row[0] > 0 else 0, 2)
                },
                'documentation_quality': {
                    'orders_with_notes': analytics_row[18] or 0,
                    'orders_with_product_desc': analytics_row[19] or 0,
                    'notes_coverage': round((analytics_row[18] / analytics_row[0] * 100) if analytics_row[0] > 0 else 0, 2),
                    'product_desc_coverage': round((analytics_row[19] / analytics_row[0] * 100) if analytics_row[0] > 0 else 0, 2)
                }
            }
            
            # Get customer addresses
            cursor = conn.execute("""
                SELECT address_id, city, zone, district, address_line, is_primary, created_at
                FROM customer_addresses 
                WHERE customer_id = ?
                ORDER BY is_primary DESC, created_at DESC
            """, (customer_row[0],))
            
            addresses = []
            for row in cursor.fetchall():
                addresses.append({
                    'address_id': row[0],
                    'city': row[1],
                    'zone': row[2],
                    'district': row[3],
                    'address_line': row[4],
                    'is_primary': bool(row[5]),
                    'created_at': row[6]
                })
            
            # Get customer analytics
            cursor = conn.execute("""
                SELECT 
                    lifetime_value, avg_order_value, order_frequency,
                    return_rate, satisfaction_score, churn_risk_score,
                    next_purchase_prediction, customer_health_score,
                    segment_recommendation, last_updated
                FROM customer_analytics 
                WHERE customer_id = ?
            """, (customer_row[0],))
            
            analytics_row = cursor.fetchone()
            analytics = None
            if analytics_row:
                analytics = {
                    'lifetime_value': analytics_row[0],
                    'avg_order_value': analytics_row[1],
                    'order_frequency': analytics_row[2],
                    'return_rate': analytics_row[3],
                    'satisfaction_score': analytics_row[4],
                    'churn_risk_score': analytics_row[5],
                    'next_purchase_prediction': analytics_row[6],
                    'customer_health_score': analytics_row[7],
                    'segment_recommendation': analytics_row[8],
                    'last_updated': analytics_row[9]
                }
            
            # Get recent interactions
            cursor = conn.execute("""
                SELECT 
                    interaction_id, interaction_type, channel, subject,
                    priority, status, assigned_agent, customer_satisfaction,
                    created_at, resolved_at
                FROM customer_interactions 
                WHERE customer_id = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (customer_row[0],))
            
            interactions = []
            for row in cursor.fetchall():
                interactions.append({
                    'interaction_id': row[0],
                    'interaction_type': row[1],
                    'channel': row[2],
                    'subject': row[3],
                    'priority': row[4],
                    'status': row[5],
                    'assigned_agent': row[6],
                    'customer_satisfaction': row[7],
                    'created_at': row[8],
                    'resolved_at': row[9]
                })
            
            return create_api_response(
                True,
                data={
                    'customer': customer,
                    'order_analytics': order_analytics,
                    'addresses': addresses,
                    'analytics': analytics,
                    'recent_interactions': interactions
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer {phone}: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/<phone>/orders', methods=['GET'])
def get_customer_orders(phone: str) -> Dict[str, Any]:
    """
    Get customer orders with enhanced business categorization
    
    Args:
        phone: Customer phone number
        
    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 25, max: 100)
        order_category: Filter by order category (real_sales, maintenance, service, refund)
        state: Filter by order state
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)
        
    Returns:
        Dict[str, Any]: Standardized API response with orders data
    """
    try:
        # Normalize phone number
        normalized_phone = normalize_phone(phone)
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 25)), 100)
        offset = (page - 1) * limit
        order_category = request.args.get('order_category')
        state = request.args.get('state')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        with get_db() as conn:
            # Build query with enhanced categorization
            query = """
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
                WHERE (receiver_phone = ? OR receiver_phone = ?)
            """
            params = [phone, normalized_phone]
            
            if order_category:
                if order_category == 'real_sales':
                    query += " AND state_code = 45 AND cod > 500"
                elif order_category == 'maintenance':
                    query += " AND state_code = 45 AND cod <= 500 AND cod > 0"
                elif order_category == 'service':
                    query += " AND state_code = 45 AND cod = 0"
                elif order_category == 'refund':
                    query += " AND cod < 0"
            
            if state:
                query += " AND state_code = ?"
                params.append(state)
            
            if date_from:
                query += " AND date(created_at) >= date(?)"
                params.append(date_from)
            
            if date_to:
                query += " AND date(created_at) <= date(?)"
                params.append(date_to)
            
            # Get total count
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            cursor = conn.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Add ordering and pagination
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            
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
            
            return create_api_response(
                True,
                data={
                    'orders': orders,
                    'pagination': {
                        'total': total_count,
                        'page': page,
                        'limit': limit,
                        'has_more': (offset + limit) < total_count
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer orders {phone}: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/<phone>/interactions', methods=['GET'])
def get_customer_interactions(phone: str) -> Dict[str, Any]:
    """
    Get customer interactions with filtering and pagination
    
    Args:
        phone: Customer phone number (can be 01, 201, etc.)
        
    Query Parameters:
        status: Filter by interaction status
        type: Filter by interaction type
        limit: Number of interactions to return (default: 20)
        offset: Number of interactions to skip (default: 0)
        
    Returns:
        Dict[str, Any]: Standardized API response with interactions data
    """
    try:
        # Normalize phone number to handle different formats
        normalized_phone = normalize_phone(phone)
        
        # Get query parameters
        status = request.args.get('status')
        interaction_type = request.args.get('type')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        with get_db() as conn:
            # First get customer_id from phone (try both original and normalized)
            cursor = conn.execute("SELECT customer_id FROM customers WHERE phone = ? OR phone = ?", (phone, normalized_phone))
            customer_row = cursor.fetchone()
            if not customer_row:
                return create_api_response(False, error="Customer not found")
            
            customer_id = customer_row[0]
            
            # Build query with filters
            query = """
                SELECT 
                    interaction_id, interaction_type, channel, subject, description,
                    priority, status, assigned_agent, customer_satisfaction,
                    resolution_time_hours, follow_up_date, follow_up_notes,
                    created_at, updated_at, resolved_at
                FROM customer_interactions
                WHERE customer_id = ?
            """
            params = [customer_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if interaction_type:
                query += " AND interaction_type = ?"
                params.append(interaction_type)
            
            # Add ordering and pagination
            query += " ORDER BY created_at DESC"
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            cursor = conn.execute(query, params)
            interactions = []
            
            for row in cursor.fetchall():
                interactions.append({
                    'interaction_id': row[0],
                    'interaction_type': row[1],
                    'channel': row[2],
                    'subject': row[3],
                    'description': row[4],
                    'priority': row[5],
                    'status': row[6],
                    'assigned_agent': row[7],
                    'customer_satisfaction': row[8],
                    'resolution_time_hours': row[9],
                    'follow_up_date': row[10],
                    'follow_up_notes': row[11],
                    'created_at': row[12],
                    'updated_at': row[13],
                    'resolved_at': row[14]
                })
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM customer_interactions WHERE customer_id = ?"
            count_params = [customer_id]
            
            if status:
                count_query += " AND status = ?"
                count_params.append(status)
            
            if interaction_type:
                count_query += " AND interaction_type = ?"
                count_params.append(interaction_type)
            
            cursor = conn.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            return create_api_response(
                True,
                data={
                    'interactions': interactions,
                    'pagination': {
                        'total': total_count,
                        'limit': limit,
                        'offset': offset,
                        'has_more': (offset + limit) < total_count
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer interactions {phone}: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/<phone>/interactions', methods=['POST'])
def create_customer_interaction(phone: str) -> Dict[str, Any]:
    """
    Create a new customer interaction
    
    Args:
        phone: Customer phone number (can be 01, 201, etc.)
        
    Request Body:
        interaction_type: Type of interaction
        channel: Communication channel
        subject: Interaction subject
        description: Interaction description
        priority: Priority level
        assigned_agent: Assigned agent name
        
    Returns:
        Dict[str, Any]: Standardized API response with created interaction
    """
    try:
        # Normalize phone number to handle different formats
        normalized_phone = normalize_phone(phone)
        
        data = request.get_json()
        if not data:
            return create_api_response(False, error="No data provided")
        
        required_fields = ['interaction_type', 'channel', 'subject']
        for field in required_fields:
            if field not in data:
                return create_api_response(False, error=f"Missing required field: {field}")
        
        with get_db() as conn:
            # First get customer_id from phone (try both original and normalized)
            cursor = conn.execute("SELECT customer_id FROM customers WHERE phone = ? OR phone = ?", (phone, normalized_phone))
            customer_row = cursor.fetchone()
            if not customer_row:
                return create_api_response(False, error="Customer not found")
            
            customer_id = customer_row[0]
            
            # Insert interaction
            cursor = conn.execute("""
                INSERT INTO customer_interactions (
                    customer_id, interaction_type, channel, subject, description,
                    priority, status, assigned_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_id,
                data['interaction_type'],
                data['channel'],
                data['subject'],
                data.get('description', ''),
                data.get('priority', 'medium'),
                'pending',
                data.get('assigned_agent', '')
            ))
            
            interaction_id = cursor.lastrowid
            conn.commit()
            
            # Get created interaction
            cursor = conn.execute("""
                SELECT 
                    interaction_id, interaction_type, channel, subject, description,
                    priority, status, assigned_agent, created_at
                FROM customer_interactions 
                WHERE interaction_id = ?
            """, (interaction_id,))
            
            interaction_row = cursor.fetchone()
            interaction = {
                'interaction_id': interaction_row[0],
                'interaction_type': interaction_row[1],
                'channel': interaction_row[2],
                'subject': interaction_row[3],
                'description': interaction_row[4],
                'priority': interaction_row[5],
                'status': interaction_row[6],
                'assigned_agent': interaction_row[7],
                'created_at': interaction_row[8]
            }
            
            return create_api_response(
                True,
                data={'interaction': interaction},
                message="Customer interaction created successfully"
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to create customer interaction: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/segments', methods=['GET'])
def get_customer_segments() -> Dict[str, Any]:
    """
    Get customer segments with enhanced statistics
    
    Returns:
        Dict[str, Any]: Standardized API response with segments data
    """
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT 
                    segment_name, min_orders, min_value, max_return_rate, description
                FROM customer_segments
                ORDER BY min_orders, min_value
            """)
            
            segments = []
            for row in cursor.fetchall():
                segments.append({
                    'segment_name': row[0],
                    'min_orders': row[1],
                    'min_value': row[2],
                    'max_return_rate': row[3],
                    'description': row[4]
                })
            
            return create_api_response(True, data={'segments': segments})
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer segments: {e}")
        return create_api_response(False, error=str(e))

@bp.route('/analytics', methods=['GET'])
def get_customer_analytics() -> Dict[str, Any]:
    """
    Get comprehensive customer analytics based on real data
    
    Query Parameters:
        segment: Filter by customer segment
        city: Filter by primary city
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)
        
    Returns:
        Dict[str, Any]: Standardized API response with analytics data
    """
    try:
        segment = request.args.get('segment')
        city = request.args.get('city')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        with get_db() as conn:
            # Build analytics query
            query = """
                SELECT 
                    c.customer_segment,
                    COUNT(*) as customer_count,
                    AVG(c.total_value) as avg_lifetime_value,
                    AVG(c.avg_order_value) as avg_order_value,
                    AVG(c.return_rate) as avg_return_rate,
                    AVG(c.satisfaction_score) as avg_satisfaction,
                    SUM(c.total_orders) as total_orders,
                    SUM(c.total_value) as total_revenue,
                    COUNT(CASE WHEN c.total_orders >= 10 OR c.total_value >= 5000 THEN 1 END) as premium_customers,
                    COUNT(CASE WHEN c.return_rate >= 30 THEN 1 END) as high_return_customers,
                    COUNT(CASE WHEN c.satisfaction_score >= 0.8 THEN 1 END) as satisfied_customers
                FROM customers c
                WHERE 1=1
            """
            params = []
            
            if segment:
                query += " AND c.customer_segment = ?"
                params.append(segment)
            
            if city:
                query += " AND c.primary_city = ?"
                params.append(city)
            
            query += " GROUP BY c.customer_segment"
            
            cursor = conn.execute(query, params)
            analytics = []
            
            for row in cursor.fetchall():
                analytics.append({
                    'segment': row[0],
                    'customer_count': row[1],
                    'avg_lifetime_value': row[2],
                    'avg_order_value': row[3],
                    'avg_return_rate': row[4],
                    'avg_satisfaction': row[5],
                    'total_orders': row[6],
                    'total_revenue': row[7],
                    'premium_customers': row[8],
                    'high_return_customers': row[9],
                    'satisfied_customers': row[10]
                })
            
            # Get overall metrics
            overall_query = """
                SELECT 
                    COUNT(*) as total_customers,
                    AVG(total_value) as avg_lifetime_value,
                    AVG(return_rate) as avg_return_rate,
                    AVG(satisfaction_score) as avg_satisfaction,
                    SUM(total_orders) as total_orders,
                    SUM(total_value) as total_revenue,
                    COUNT(CASE WHEN total_orders >= 10 OR total_value >= 5000 THEN 1 END) as premium_customers,
                    COUNT(CASE WHEN return_rate >= 30 THEN 1 END) as high_return_customers,
                    COUNT(CASE WHEN satisfaction_score >= 0.8 THEN 1 END) as satisfied_customers
                FROM customers
                WHERE 1=1
            """
            overall_params = []
            
            if segment:
                overall_query += " AND customer_segment = ?"
                overall_params.append(segment)
            
            if city:
                overall_query += " AND primary_city = ?"
                overall_params.append(city)
            
            cursor = conn.execute(overall_query, overall_params)
            overall_row = cursor.fetchone()
            
            total_customers = overall_row[0] or 0
            
            overall_metrics = {
                'total_customers': total_customers,
                'avg_lifetime_value': overall_row[1],
                'avg_return_rate': overall_row[2],
                'avg_satisfaction': overall_row[3],
                'total_orders': overall_row[4],
                'total_revenue': overall_row[5],
                'premium_customers': overall_row[6],
                'high_return_customers': overall_row[7],
                'satisfied_customers': overall_row[8],
                'premium_percentage': round((overall_row[6] / total_customers * 100) if total_customers > 0 else 0, 2),
                'high_return_percentage': round((overall_row[7] / total_customers * 100) if total_customers > 0 else 0, 2),
                'satisfaction_percentage': round((overall_row[8] / total_customers * 100) if total_customers > 0 else 0, 2)
            }
            
            return create_api_response(
                True,
                data={
                    'overall_metrics': overall_metrics,
                    'segment_analytics': analytics
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get customer analytics: {e}")
        return create_api_response(False, error=str(e)) 