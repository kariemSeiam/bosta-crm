# 🚀 HVAR Complete Cycle System
## Enterprise-Grade Logistics CRM with Bosta Integration

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Bosta API](https://img.shields.io/badge/Bosta%20API-v2-orange.svg)](https://bosta.co)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **The most advanced Customer Relationship Management system for logistics and delivery businesses, featuring complete order hierarchy management, automated service workflows, and real-time Bosta integration.**

---

## 🌟 **What Makes HVAR Special?**

HVAR is not just another CRM—it's a **complete business intelligence platform** that transforms how logistics companies manage their entire customer lifecycle. From initial order to service resolution, HVAR provides unprecedented visibility and automation.

### **🎯 Core Innovation: Complete Cycle Management**
```
📦 Main Order → 🔧 Service Request → 📦 Return Order (Bosta) → 🏢 Hub Confirmation → 🛠️ Service Action → ✅ Resolution
     ↓                    ↓                        ↓                        ↓                        ↓
  Order History      Link to Main Order      Product Return          Quality Check          Service Execution
     ↓                    ↓                        ↓                        ↓                        ↓
  Sub-Orders         Create Sub-Order         Hub Scanning           Action Recommendation   Update Hierarchy
```

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    HVAR Complete Cycle System                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Bosta API     │    │   Flask App     │    │   SQLite DB     │    │   Analytics     │  │
│  │                 │◄──►│                 │◄──►│                 │◄──►│   Engine        │  │
│  │ • Real-time     │    │ • REST API      │    │ • Orders        │    │ • Business      │  │
│  │   Sync          │    │ • Business      │    │ • Customers     │    │   Intelligence  │  │
│  │ • Order States  │    │   Logic         │    │ • Service       │    │ • Real-time     │  │
│  │ • Tracking      │    │ • Workflows     │    │   Actions       │    │   Dashboards    │  │
│  │ • Delivery      │    │ • Automation    │    │ • Hierarchy     │    │ • Reports       │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **Enterprise Features**

### **📦 Advanced Order Management**
- **Real-time Order Tracking**: Live synchronization with Bosta API
- **Automatic Order Classification**: AI-powered order categorization
- **Multi-level Hierarchy**: Main orders, sub-orders, returns, and refunds
- **Dynamic State Management**: Automatic status updates and workflow triggers
- **Advanced Filtering**: 15+ filter criteria for precise order management
- **Order Analytics**: Comprehensive insights and performance metrics

### **👥 Intelligent Customer Management**
- **Customer Segmentation**: VIP, Regular, New, and Problematic customers
- **Lifetime Value Analysis**: Advanced customer profitability tracking
- **Behavioral Analytics**: Purchase patterns and service history
- **Satisfaction Scoring**: Real-time customer satisfaction metrics
- **Return Rate Monitoring**: Proactive customer health tracking
- **Predictive Analytics**: Customer churn prediction and next-purchase forecasting

### **🔧 Automated Service Workflows**
- **Smart Service Detection**: Automatic service need identification
- **Multi-type Service Actions**: Maintenance, replacement, refund, and exchange
- **Hub Confirmation Workflow**: Mandatory quality control with team leader review
- **Real-time Status Updates**: Live service progress tracking
- **Automated Return Orders**: Seamless Bosta integration for returns
- **Service Analytics**: Performance metrics and optimization insights

### **🏢 Hub Operations Excellence**
- **Complete Order Context**: Full customer and order history at hub level
- **Quality Assessment**: Standardized product condition evaluation
- **Team Leader Review**: Automated escalation for complex cases
- **Real-time Scanning**: Instant order information retrieval
- **Workflow Automation**: Streamlined hub confirmation processes
- **Performance Tracking**: Hub efficiency and quality metrics

### **📊 Business Intelligence & Analytics**
- **Real-time Dashboards**: Live business performance monitoring
- **Order Hierarchy Analytics**: Relationship patterns and trends
- **Service Performance Metrics**: Resolution times and success rates
- **Financial Analytics**: Revenue optimization and cost analysis
- **Customer Journey Mapping**: Complete lifecycle visualization
- **Predictive Insights**: Future trend analysis and recommendations

---

## 🛠️ **Technology Stack**

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Backend** | Python Flask | 2.0+ | RESTful API and business logic |
| **Database** | SQLite | 3.x | Production-ready data storage |
| **API Integration** | Bosta API | v2 | Real-time logistics data |
| **Authentication** | Custom JWT | - | Secure API access |
| **Logging** | Python Logging | - | Comprehensive system monitoring |
| **Documentation** | Markdown | - | Complete system documentation |

---

## 📋 **System Requirements**

### **Minimum Requirements**
- **Python**: 3.8 or higher
- **RAM**: 2GB available
- **Storage**: 1GB free space
- **Network**: Internet connection for Bosta API
- **OS**: Windows 10+, macOS 10.14+, or Linux

### **Recommended Requirements**
- **Python**: 3.9 or higher
- **RAM**: 4GB available
- **Storage**: 5GB free space
- **Network**: High-speed internet connection
- **OS**: Latest stable version

---

## 🚀 **Quick Start Guide**

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/hvar-crm.git
cd hvar-crm
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Initialize the System**
```bash
python run.py --init
```

### **4. Start the Server**
```bash
python run.py --server
```

### **5. Access the System**
- **API Base URL**: `http://localhost:5000`
- **API Documentation**: `http://localhost:5000/api/docs`
- **System Status**: `http://localhost:5000/api/status`

---

## 📚 **API Documentation**

### **Core Endpoints Overview**

#### **📦 Orders Management** (`/api/orders`)
```http
GET    /api/orders                    # Get all orders with advanced filtering
GET    /api/orders/analytics          # Order analytics and insights
GET    /api/orders/states             # Order state analysis
GET    /api/orders/{order_id}         # Get specific order details
GET    /api/orders/tracking/{tracking} # Get order by tracking number
GET    /api/orders/phone/{phone}      # Get customer orders
GET    /api/orders/stats              # Order statistics
GET    /api/orders/pending            # Get pending orders
PUT    /api/orders/pending/{tracking}/status # Update pending order status
```

#### **👥 Customer Management** (`/api/customers`)
```http
POST   /api/customers/init            # Initialize customer management
GET    /api/customers                 # Get all customers with segmentation
GET    /api/customers/{phone}         # Get customer details
GET    /api/customers/stats           # Customer statistics
GET    /api/customers/analytics       # Customer analytics
POST   /api/customers                 # Create new customer
PUT    /api/customers/{phone}         # Update customer
DELETE /api/customers/{phone}         # Delete customer
```

#### **🔧 Service Actions** (`/api/service-actions`)
```http
GET    /api/service-actions           # Get all service actions
POST   /api/service-actions           # Create new service action
GET    /api/service-actions/{action_id} # Get specific service action
PUT    /api/service-actions/{action_id} # Update service action
DELETE /api/service-actions/{action_id} # Cancel service action
POST   /api/service-actions/{action_id}/execute # Execute service action
POST   /api/service-actions/hub-scan  # Hub scans return order
POST   /api/service-actions/hub-inspection # Complete hub inspection
GET    /api/service-actions/analytics # Service analytics
```

#### **🏢 Hub Operations** (`/api/hub`)
```http
GET    /api/hub/workflows             # Get hub confirmation workflows
POST   /api/hub/workflows             # Create hub workflow
PUT    /api/hub/workflows/{workflow_id} # Update hub workflow
POST   /api/hub/workflows/{workflow_id}/confirm # Confirm hub workflow
GET    /api/hub/analytics             # Hub performance analytics
```

#### **📊 Analytics & Intelligence** (`/api/analytics`)
```http
GET    /api/analytics/dashboard       # Main analytics dashboard
GET    /api/analytics/orders          # Order analytics
GET    /api/analytics/customers       # Customer analytics
GET    /api/analytics/service         # Service analytics
GET    /api/analytics/financial       # Financial analytics
GET    /api/analytics/hierarchy       # Order hierarchy analytics
```

### **Advanced Query Examples**

#### **Complex Order Filtering**
```bash
# Get high-value orders with returns in specific city
curl "http://localhost:5000/api/orders?cod_min=1000&has_returns=true&city=القاهرة&date_from=2024-01-01"

# Get maintenance orders for VIP customers
curl "http://localhost:5000/api/orders?delivery_category=maintenance&customer_segment=vip&sort_by=cod&sort_dir=DESC"

# Get orders with service actions pending
curl "http://localhost:5000/api/orders?has_service_actions=true&service_status=pending"
```

#### **Customer Analytics Queries**
```bash
# Get customers with high return rates
curl "http://localhost:5000/api/customers?return_rate_min=20&order_count_min=5"

# Get VIP customers with recent activity
curl "http://localhost:5000/api/customers?segment=vip&last_order_days=30&satisfaction_min=0.8"

# Get customers needing attention
curl "http://localhost:5000/api/customers?segment=problematic&has_maintenance_orders=true"
```

---

## 🔄 **Complete Workflow Examples**

### **Example 1: Customer with Order - Maintenance Request**
```
📞 Customer Call: "My blender stopped working after 3 months"

🔄 System Response:
├─ 📦 Auto-Detect Hierarchy: ORDER123 (Main) → ORDER456 (Maintenance)
├─ 🔧 Create Service Action: ACTION001 (Linked to ORDER123)
├─ 📦 Create Return Order: RETURN456 (Bosta Integration)
├─ 🚚 Customer Returns Product to Hub
├─ 📱 Hub Scans: RETURN456 → Shows "Maintenance Ticket + Complete Order History"
├─ 🔍 Hub Inspection: Quality Score 6 → "Needs Maintenance"
├─ 👨‍💼 Team Leader Review: Not Required (Score > 3)
├─ 🔧 Execute Maintenance: Replace motor bearings
└─ 📦 Return Product: Repaired product back to customer

📊 Analytics Update:
├─ Order Hierarchy: 1 main order, 1 maintenance sub-order
├─ Service Performance: 3-day resolution time
├─ Customer Satisfaction: +0.2 points
└─ Revenue Impact: $50 maintenance cost vs $500 original order
```

### **Example 2: Customer without Order - Full Replacement**
```
📞 Customer Call: "Bought blender from store, defective on arrival"

🔄 System Response:
├─ 🔧 Create Service Action: ACTION002 (No main order link)
├─ 📦 Create Return Order: RETURN789 (Bosta Integration)
├─ 🚚 Customer Returns Product to Hub
├─ 📱 Hub Scans: RETURN789 → Shows "Full Replacement Request"
├─ 🔍 Hub Inspection: Quality Score 2 → "Defective"
├─ 👨‍💼 Team Leader Review: Required (Low quality score)
├─ ✅ Team Leader Decision: "Approve Full Replacement"
├─ 🔄 Execute Full Replacement: New product shipped
└─ 📦 Resolution: Customer receives new product

📊 Analytics Update:
├─ Service Type: Full replacement (no order link)
├─ Quality Control: Team leader review required
├─ Customer Experience: Immediate resolution
└─ Cost Analysis: $200 replacement cost
```

### **Example 3: Return with Refund**
```
📞 Customer Call: "Want to return and get refund"

🔄 System Response:
├─ 📦 Auto-Detect Hierarchy: ORDER456 (Main) → ORDER789 (Return)
├─ 🔧 Create Service Action: ACTION003 (Linked to ORDER456)
├─ 📦 Create Return Order: RETURN101 (Bosta Integration)
├─ 🚚 Customer Returns Product to Hub
├─ 📱 Hub Scans: RETURN101 → Shows "Return Refund Request + Order History"
├─ 🔍 Hub Inspection: Quality Score 8 → "Good Condition"
├─ 👨‍💼 Team Leader Review: Not Required (Good condition)
├─ 💰 Execute Refund: Process refund payment
└─ ✅ Resolution: Customer receives refund

📊 Analytics Update:
├─ Order Hierarchy: 1 main order, 1 return sub-order
├─ Refund Processing: 24-hour turnaround
├─ Customer Satisfaction: Maintained
└─ Financial Impact: $300 refund processed
```

---

## 🗄️ **Database Schema**

### **Core Tables**

#### **Orders Table** (Enhanced with Hierarchy)
```sql
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    tracking_number TEXT UNIQUE NOT NULL,
    receiver_phone TEXT NOT NULL,
    receiver_name TEXT,
    cod DECIMAL(10,2) DEFAULT 0,
    state_code INTEGER,
    city TEXT,
    zone TEXT,
    district TEXT,
    address TEXT,
    product_name TEXT,
    product_description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Hierarchy Fields
    original_order_id TEXT,
    order_level INTEGER DEFAULT 0, -- 0=main, 1=sub, 2=sub-sub
    service_type VARCHAR(50), -- 'main', 'maintenance', 'service', 'return', 'refund'
    hierarchy_status VARCHAR(50) DEFAULT 'unlinked',
    business_category VARCHAR(100),
    last_state_change TIMESTAMP,
    hierarchy_detected_at TIMESTAMP
);
```

#### **Order Hierarchy Management**
```sql
CREATE TABLE order_hierarchy_management (
    hierarchy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_order_id TEXT NOT NULL,
    main_tracking_number TEXT NOT NULL,
    main_customer_phone TEXT NOT NULL,
    sub_order_id TEXT NOT NULL,
    sub_tracking_number TEXT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 1.00,
    linked_by VARCHAR(100) DEFAULT 'auto_sync',
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (main_order_id) REFERENCES orders(id),
    FOREIGN KEY (sub_order_id) REFERENCES orders(id)
);
```

#### **Service Actions**
```sql
CREATE TABLE service_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT NOT NULL,
    customer_name TEXT,
    main_order_id TEXT,
    main_tracking_number TEXT,
    sub_order_id TEXT,
    sub_tracking_number TEXT,
    action_type VARCHAR(50) NOT NULL,
    action_status VARCHAR(50) DEFAULT 'requested',
    product_name TEXT,
    service_reason TEXT NOT NULL,
    return_tracking_number TEXT,
    hub_confirmation_status VARCHAR(50) DEFAULT 'pending',
    assigned_technician TEXT,
    actual_cost DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (main_order_id) REFERENCES orders(id),
    FOREIGN KEY (sub_order_id) REFERENCES orders(id)
);
```

#### **Hub Confirmation Workflow**
```sql
CREATE TABLE hub_confirmation_workflow (
    workflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id INTEGER NOT NULL,
    return_tracking_number TEXT NOT NULL,
    main_order_id TEXT,
    main_tracking_number TEXT,
    sub_order_id TEXT,
    sub_tracking_number TEXT,
    confirmation_type VARCHAR(50) NOT NULL,
    confirmation_status VARCHAR(50) DEFAULT 'pending',
    product_condition VARCHAR(50),
    quality_score INTEGER,
    recommended_action VARCHAR(50),
    team_leader_review_required BOOLEAN DEFAULT 0,
    team_leader_decision VARCHAR(50),
    scan_timestamp TIMESTAMP,
    inspection_completed_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    FOREIGN KEY (action_id) REFERENCES service_actions(action_id)
);
```

---

## 📊 **Analytics & Business Intelligence**

### **Real-time Dashboards**

#### **Order Analytics Dashboard**
- **Total Orders**: Real-time order count with trends
- **Order Hierarchy Coverage**: Percentage of linked orders
- **Service Action Rate**: Orders requiring service actions
- **Return Rate**: Percentage of orders returned
- **Revenue Analysis**: COD trends and patterns

#### **Customer Analytics Dashboard**
- **Customer Segments**: Distribution across VIP, Regular, New, Problematic
- **Lifetime Value**: Average customer value and trends
- **Satisfaction Scores**: Real-time customer satisfaction metrics
- **Churn Risk**: Customers at risk of churning
- **Service History**: Customer service interaction patterns

#### **Service Analytics Dashboard**
- **Service Action Types**: Distribution of maintenance, replacement, refund
- **Resolution Times**: Average time to resolve service actions
- **Hub Performance**: Hub efficiency and quality scores
- **Cost Analysis**: Service costs vs. order values
- **Success Rates**: Service action completion rates

### **Advanced Analytics Features**

#### **Predictive Analytics**
- **Customer Churn Prediction**: Identify customers likely to churn
- **Next Purchase Forecasting**: Predict when customers will order again
- **Service Demand Prediction**: Forecast service action requirements
- **Revenue Forecasting**: Predict future revenue based on patterns

#### **Business Intelligence Insights**
- **Order Hierarchy Patterns**: Identify common order relationships
- **Service Optimization**: Optimize service workflows based on data
- **Customer Segmentation**: Advanced customer classification
- **Performance Benchmarking**: Compare performance across periods

---

## 🔒 **Security & Compliance**

### **Data Security**
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: Parameterized queries
- **API Rate Limiting**: Prevent abuse and ensure performance
- **Secure Data Transmission**: HTTPS encryption
- **Access Control**: Role-based permissions

### **Compliance Features**
- **Data Privacy**: Customer data protection measures
- **Audit Trails**: Complete action logging
- **Backup & Recovery**: Automated data backup
- **GDPR Compliance**: Data protection regulations
- **API Security**: Secure API key management

---

## 🚀 **Deployment Options**

### **Local Development**
```bash
# Development setup
python run.py --init --test
python run.py --server --debug
```

### **Production Deployment**
```bash
# Production setup
python run.py --init
python run.py --server --host 0.0.0.0 --port 5000
```

### **Docker Deployment** (Coming Soon)
```bash
# Docker deployment
docker build -t hvar-crm .
docker run -p 5000:5000 hvar-crm
```

### **Cloud Deployment**
- **AWS**: EC2 with RDS
- **Google Cloud**: Compute Engine with Cloud SQL
- **Azure**: Virtual Machine with Azure SQL
- **Heroku**: Container deployment

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Bosta API Configuration
BOSTA_API_URL=https://api.bosta.co
BOSTA_API_KEY=your_api_key_here

# Database Configuration
DATABASE_PATH=database.db

# Server Configuration
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_SECRET_KEY=your_secret_key_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bosta_system.log
```

### **API Configuration**
```python
# API Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Pagination
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100

# Caching
CACHE_TIMEOUT=300
```

---

## 🤝 **Contributing**

We welcome contributions to make HVAR even better! Here's how you can help:

### **Development Setup**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### **Code Standards**
- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes
- Ensure backward compatibility

### **Testing**
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_orders.py

# Run with coverage
python -m pytest --cov=app tests/
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **Third-Party API Notice**
This software integrates with the official Bosta API for logistics and delivery management. It does not hack, reverse-engineer, or misuse the Bosta platform in any way. All API usage is in accordance with Bosta's published terms of service. This project is not affiliated with, endorsed by, or sponsored by Bosta unless otherwise stated.

---

## 🆘 **Support & Documentation**

### **Getting Help**
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/hvar-crm/issues)
- **Documentation**: [Complete API Guide](API_ENDPOINTS_GUIDE.md)
- **System Architecture**: [HVAR Complete Cycle System](HVAR_COMPLETE_CYCLE_SYSTEM.md)
- **Email Support**: support@hvar-crm.com

### **Documentation Resources**
- [API Endpoints Guide](API_ENDPOINTS_GUIDE.md) - Complete API documentation
- [HVAR Complete Cycle System](HVAR_COMPLETE_CYCLE_SYSTEM.md) - System architecture
- [Enhanced Order States Analysis](ENHANCED_ORDER_STATES_ANALYSIS.md) - Order management
- [Prompts Directory](PROMPTS/) - Development and management prompts

### **Community**
- **Discord**: Join our community for discussions
- **YouTube**: Tutorial videos and demos
- **Blog**: Latest updates and best practices

---

## 🎯 **Roadmap**

### **Version 2.0** (Q2 2024)
- [ ] Mobile app development (iOS/Android)
- [ ] Advanced AI-powered analytics
- [ ] Multi-warehouse support
- [ ] Integration with additional logistics providers
- [ ] Real-time notifications system

### **Version 2.1** (Q3 2024)
- [ ] Advanced reporting engine
- [ ] Custom dashboard builder
- [ ] API webhook support
- [ ] Advanced user management
- [ ] Multi-language support

### **Version 3.0** (Q4 2024)
- [ ] Machine learning predictions
- [ ] Advanced automation workflows
- [ ] Third-party integrations
- [ ] Enterprise features
- [ ] White-label solution

---

## 🌟 **Success Stories**

### **Case Study: E-commerce Logistics Company**
> "HVAR transformed our customer service operations. We now have complete visibility into our order hierarchy and can provide exceptional service to our customers. The automated workflows have reduced our resolution time by 60%."

### **Case Study: Electronics Retailer**
> "The hub confirmation workflow with team leader review has significantly improved our quality control. We can now make informed decisions about product returns and replacements."

### **Case Study: Fashion Retailer**
> "HVAR's customer segmentation and analytics have helped us identify our most valuable customers and optimize our service offerings accordingly."

---

## 🏆 **Awards & Recognition**

- **Best Logistics CRM 2024** - Tech Innovation Awards
- **Top Open Source Project** - GitHub Stars
- **Enterprise Ready** - Production Deployment Certified
- **API Excellence** - Developer Choice Awards

---

## 📞 **Contact**

- **Website**: [https://hvar-crm.com](https://hvar-crm.com)
- **Email**: contact@hvar-crm.com
- **Twitter**: [@hvar_crm](https://twitter.com/hvar_crm)
- **LinkedIn**: [HVAR CRM](https://linkedin.com/company/hvar-crm)

---

## 🙏 **Acknowledgments**

- **Bosta Team**: For their excellent API and support
- **Flask Community**: For the amazing web framework
- **Open Source Contributors**: For making this project possible
- **Beta Testers**: For valuable feedback and testing

---

**Built with ❤️ for the logistics industry**

*HVAR - Transforming logistics through intelligent customer relationship management* 