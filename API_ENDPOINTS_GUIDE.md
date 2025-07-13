# HVAR CRM API Endpoints Guide

## Overview
Complete guide to all API endpoints in the enhanced HVAR CRM system with real examples and business logic integration.

---

## 🔄 Orders Management API

### Base URL: `/api/orders`

#### 1. **Get All Orders**
```http
GET /api/orders
```

**Example Links:**
- `http://localhost:5000/api/orders`
- `http://localhost:5000/api/orders?page=1&limit=25`
- `http://localhost:5000/api/orders?sort_by=cod&sort_dir=DESC`
- `http://localhost:5000/api/orders?phone=201234567890`
- `http://localhost:5000/api/orders?state=45`
- `http://localhost:5000/api/orders?tracking=TRK789012`
- `http://localhost:5000/api/orders?city=القاهرة`
- `http://localhost:5000/api/orders?date_from=2024-01-01&date_to=2024-01-31`
- `http://localhost:5000/api/orders?cod_min=500&cod_max=2000`
- `http://localhost:5000/api/orders?order_type=10`
- `http://localhost:5000/api/orders?delivery_category=real_sales`
- `http://localhost:5000/api/orders?delivery_category=maintenance`
- `http://localhost:5000/api/orders?delivery_category=service`
- `http://localhost:5000/api/orders?delivery_category=refunds`
- `http://localhost:5000/api/orders?has_notes=true`
- `http://localhost:5000/api/orders?has_product_desc=true`

#### 2. **Get Order Analytics**
```http
GET /api/orders/analytics
```

**Example Links:**
- `http://localhost:5000/api/orders/analytics`
- `http://localhost:5000/api/orders/analytics?date_from=2024-01-01&date_to=2024-01-31`
- `http://localhost:5000/api/orders/analytics?city=القاهرة`

#### 3. **Get Order States Analysis**
```http
GET /api/orders/states
```

**Example Links:**
- `http://localhost:5000/api/orders/states`

#### 4. **Get Delivery Categories**
```http
GET /api/orders/delivery-categories
```

**Example Links:**
- `http://localhost:5000/api/orders/delivery-categories`

#### 5. **Get Single Order**
```http
GET /api/orders/{order_id}
```

**Example Links:**
- `http://localhost:5000/api/orders/ORD123456`
- `http://localhost:5000/api/orders/ORD789012`

#### 6. **Get Order by Tracking**
```http
GET /api/orders/tracking/{tracking_number}
```

**Example Links:**
- `http://localhost:5000/api/orders/tracking/TRK789012`
- `http://localhost:5000/api/orders/tracking/TRK123456`

#### 7. **Get Orders by Phone**
```http
GET /api/orders/phone/{phone}
```

**Example Links:**
- `http://localhost:5000/api/orders/phone/201234567890`
- `http://localhost:5000/api/orders/phone/01234567890`
- `http://localhost:5000/api/orders/phone/+201234567890`

#### 8. **Get Order Statistics**
```http
GET /api/orders/stats
```

**Example Links:**
- `http://localhost:5000/api/orders/stats`

#### 9. **Get Pending Orders**
```http
GET /api/orders/pending
```

**Example Links:**
- `http://localhost:5000/api/orders/pending`
- `http://localhost:5000/api/orders/pending?page=1&limit=25`
- `http://localhost:5000/api/orders/pending?status=pending`
- `http://localhost:5000/api/orders/pending?status=received`
- `http://localhost:5000/api/orders/pending?status=processed`
- `http://localhost:5000/api/orders/pending?status=completed`
- `http://localhost:5000/api/orders/pending?order_type=EXCHANGE`
- `http://localhost:5000/api/orders/pending?order_type=CUSTOMER_RETURN_PICKUP`
- `http://localhost:5000/api/orders/pending?phone=201234567890`
- `http://localhost:5000/api/orders/pending?tracking=TRK789012`
- `http://localhost:5000/api/orders/pending?is_received=true`
- `http://localhost:5000/api/orders/pending?is_received=false`
- `http://localhost:5000/api/orders/pending?date_from=2024-01-01&date_to=2024-01-31`

#### 10. **Get Pending Order by Tracking**
```http
GET /api/orders/pending/{tracking_number}
```

**Example Links:**
- `http://localhost:5000/api/orders/pending/TRK789012`
- `http://localhost:5000/api/orders/pending/TRK123456`

#### 11. **Update Pending Order Status**
```http
PUT /api/orders/pending/{tracking_number}/status
```

**Example Links:**
- `http://localhost:5000/api/orders/pending/TRK789012/status`

**Request Body:**
```json
{
  "status": "received",
  "received_by": "أحمد علي",
  "received_notes": "تم استلام المنتج في حالة جيدة"
}
```

#### 12. **Get Pending Order Statistics**
```http
GET /api/orders/pending/stats
```

**Example Links:**
- `http://localhost:5000/api/orders/pending/stats`

---

## 👥 Customers Management API

### Base URL: `/api/customers`

#### 1. **Initialize Customer Management**
```http
POST /api/customers/init
```

**Example Links:**
- `http://localhost:5000/api/customers/init`

#### 2. **Get Customer Statistics**
```http
GET /api/customers/stats
```

**Example Links:**
- `http://localhost:5000/api/customers/stats`

#### 3. **Get All Customers**
```http
GET /api/customers
```

**Example Links:**
- `http://localhost:5000/api/customers`
- `http://localhost:5000/api/customers?page=1&limit=50`
- `http://localhost:5000/api/customers?segment=vip`
- `http://localhost:5000/api/customers?segment=regular`
- `http://localhost:5000/api/customers?segment=new`
- `http://localhost:5000/api/customers?segment=problematic`
- `http://localhost:5000/api/customers?city=القاهرة`
- `http://localhost:5000/api/customers?search=محمد`
- `http://localhost:5000/api/customers?satisfaction_min=0.8`
- `http://localhost:5000/api/customers?return_rate_max=20`
- `http://localhost:5000/api/customers?order_count_min=5`
- `http://localhost:5000/api/customers?lifetime_value_min=1000`
- `http://localhost:5000/api/customers?last_order_days=30`
- `http://localhost:5000/api/customers?has_maintenance_orders=true`
- `http://localhost:5000/api/customers?has_maintenance_orders=false`
- `http://localhost:5000/api/customers?has_refunds=true`
- `http://localhost:5000/api/customers?has_refunds=false`

#### 4. **Get Customer Details**
```http
GET /api/customers/{phone}
```

**Example Links:**
- `http://localhost:5000/api/customers/201234567890`
- `http://localhost:5000/api/customers/01234567890`
- `http://localhost:5000/api/customers/+201234567890`

#### 5. **Get Customer Orders**
```http
GET /api/customers/{phone}/orders
```

**Example Links:**
- `http://localhost:5000/api/customers/201234567890/orders`
- `http://localhost:5000/api/customers/201234567890/orders?page=1&limit=25`
- `http://localhost:5000/api/customers/201234567890/orders?order_category=real_sales`
- `http://localhost:5000/api/customers/201234567890/orders?order_category=maintenance`
- `http://localhost:5000/api/customers/201234567890/orders?order_category=service`
- `http://localhost:5000/api/customers/201234567890/orders?order_category=refund`
- `http://localhost:5000/api/customers/201234567890/orders?state=45`
- `http://localhost:5000/api/customers/201234567890/orders?date_from=2024-01-01&date_to=2024-01-31`

#### 6. **Get Customer Interactions**
```http
GET /api/customers/{phone}/interactions
```

**Example Links:**
- `http://localhost:5000/api/customers/201234567890/interactions`
- `http://localhost:5000/api/customers/201234567890/interactions?page=1&limit=20`
- `http://localhost:5000/api/customers/201234567890/interactions?status=pending`
- `http://localhost:5000/api/customers/201234567890/interactions?status=resolved`
- `http://localhost:5000/api/customers/201234567890/interactions?type=complaint`
- `http://localhost:5000/api/customers/201234567890/interactions?type=support`

#### 7. **Create Customer Interaction**
```http
POST /api/customers/{phone}/interactions
```

**Example Links:**
- `http://localhost:5000/api/customers/201234567890/interactions`

**Request Body:**
```json
{
  "interaction_type": "complaint",
  "channel": "phone",
  "subject": "مشكلة في المنتج",
  "description": "المنتج لا يعمل بشكل صحيح",
  "priority": "high",
  "assigned_agent": "أحمد علي"
}
```

#### 8. **Get Customer Segments**
```http
GET /api/customers/segments
```

**Example Links:**
- `http://localhost:5000/api/customers/segments`

#### 9. **Get Customer Analytics**
```http
GET /api/customers/analytics
```

**Example Links:**
- `http://localhost:5000/api/customers/analytics`
- `http://localhost:5000/api/customers/analytics?segment=vip`
- `http://localhost:5000/api/customers/analytics?city=القاهرة`
- `http://localhost:5000/api/customers/analytics?date_from=2024-01-01&date_to=2024-01-31`

---

## 📦 Products Management API

### Base URL: `/products`

#### 1. **Get All Products**
```http
GET /products
```

**Example Links:**
- `http://localhost:5000/products`
- `http://localhost:5000/products?page=1&limit=50`
- `http://localhost:5000/products?search=خلاط`
- `http://localhost:5000/products?category=خلاط هفار`

#### 2. **Create Product**
```http
POST /products
```

**Example Links:**
- `http://localhost:5000/products`

**Request Body:**
```json
{
  "name_ar": "خلاط هفار 1000 وات",
  "name_en": "HVAR Blender 1000W",
  "brand": "هفار",
  "category": "خلاط هفار",
  "unit": "القطعة",
  "selling_price": 299.99,
  "purchase_price": 200.00,
  "alert_quantity": 5,
  "opening_stock": 20
}
```

#### 3. **Get Product by ID**
```http
GET /products/{product_id}
```

**Example Links:**
- `http://localhost:5000/products/1`
- `http://localhost:5000/products/2`

#### 4. **Update Product**
```http
PUT /products/{product_id}
```

**Example Links:**
- `http://localhost:5000/products/1`

**Request Body:**
```json
{
  "name_ar": "خلاط هفار 1200 وات",
  "selling_price": 349.99,
  "alert_quantity": 10
}
```

#### 5. **Delete Product**
```http
DELETE /products/{product_id}
```

**Example Links:**
- `http://localhost:5000/products/1`

#### 6. **Get Product Categories**
```http
GET /products/categories
```

**Example Links:**
- `http://localhost:5000/products/categories`

#### 7. **Get Product Inventory**
```http
GET /products/{product_id}/inventory
```

**Example Links:**
- `http://localhost:5000/products/1/inventory`

#### 8. **Update Product Inventory**
```http
POST /products/{product_id}/inventory
```

**Example Links:**
- `http://localhost:5000/products/1/inventory`

**Request Body:**
```json
{
  "location_id": 1,
  "quantity_change": 10,
  "transaction_type": "purchase",
  "reference_type": "manual",
  "reference_id": "PO123456",
  "notes": "New stock received"
}
```

#### 9. **Get Low Stock Alerts**
```http
GET /inventory/alerts
```

**Example Links:**
- `http://localhost:5000/inventory/alerts`

---

## 🔍 Advanced Filtering Examples

### **Orders Filtering**
```http
# High-value real sales orders
GET /api/orders?delivery_category=real_sales&cod_min=1000&state=45

# Maintenance orders with notes
GET /api/orders?delivery_category=maintenance&has_notes=true

# Refund orders in specific city
GET /api/orders?delivery_category=refunds&city=القاهرة

# Orders with product descriptions
GET /api/orders?has_product_desc=true&order_type=10

# Recent orders with high COD
GET /api/orders?date_from=2024-01-01&cod_min=500&sort_by=cod&sort_dir=DESC
```

### **Customers Filtering**
```http
# VIP customers with high satisfaction
GET /api/customers?segment=vip&satisfaction_min=0.8

# Problematic customers with high return rate
GET /api/customers?segment=problematic&return_rate_max=50

# Customers with maintenance orders
GET /api/customers?has_maintenance_orders=true&order_count_min=3

# Premium customers in specific city
GET /api/customers?city=القاهرة&lifetime_value_min=5000

# Recent customers with refunds
GET /api/customers?has_refunds=true&last_order_days=90
```

### **Customer Orders Filtering**
```http
# Customer's real sales orders
GET /api/customers/201234567890/orders?order_category=real_sales

# Customer's maintenance history
GET /api/customers/201234567890/orders?order_category=maintenance

# Customer's refund history
GET /api/customers/201234567890/orders?order_category=refund

# Customer's recent orders
GET /api/customers/201234567890/orders?date_from=2024-01-01
```

---

## 📊 Analytics Endpoints

### **Business Intelligence**
```http
# Overall order analytics
GET /api/orders/analytics

# Customer segment analytics
GET /api/customers/analytics

# Order states breakdown
GET /api/orders/states

# Delivery categories analysis
GET /api/orders/delivery-categories

# Customer statistics
GET /api/customers/stats

# Order statistics
GET /api/orders/stats

# Pending order statistics
GET /api/orders/pending/stats
```

---

## 🚀 Quick Start Examples

### **1. Get Dashboard Data**
```http
# Main statistics
GET /api/orders/stats
GET /api/customers/stats

# Recent orders
GET /api/orders?page=1&limit=10&sort_by=created_at&sort_dir=DESC

# Top customers
GET /api/customers?segment=vip&limit=10
```

### **2. Customer Service Workflow**
```http
# Find customer
GET /api/customers/201234567890

# Check customer orders
GET /api/customers/201234567890/orders

# Create interaction
POST /api/customers/201234567890/interactions

# Check maintenance orders
GET /api/customers/201234567890/orders?order_category=maintenance
```

### **3. Inventory Management**
```http
# Check low stock
GET /inventory/alerts

# Update inventory
POST /products/1/inventory

# Product details
GET /products/1
```

### **4. Order Tracking**
```http
# Track by order ID
GET /api/orders/ORD123456

# Track by tracking number
GET /api/orders/tracking/TRK789012

# Customer orders
GET /api/orders/phone/201234567890
```

---

## 📝 Response Format

All endpoints return consistent JSON responses:

```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    // Response data
  },
  "total": 100,
  "page": 1,
  "limit": 25
}
```

Error responses:
```json
{
  "success": false,
  "timestamp": "2024-01-15T10:30:00",
  "error": "Error message"
}
```

---

## 🔧 Business Logic Integration

### **Order Categories**
- **Real Sales**: `state_code=45 AND cod>500`
- **Maintenance**: `state_code=45 AND cod<=500 AND cod>0`
- **Service**: `state_code=45 AND cod=0`
- **Refunds**: `cod<0`

### **Customer Segments**
- **VIP**: `total_orders>=10 OR total_value>=5000`
- **Regular**: `total_orders>=3`
- **Problematic**: `return_rate>=30`
- **New**: Default for new customers

### **Risk Levels**
- **High Risk**: `return_rate>=30`
- **Medium Risk**: `return_rate>=15`
- **Low Risk**: `return_rate<15`

This comprehensive guide provides all the API endpoints with real examples for your enhanced HVAR CRM system. 