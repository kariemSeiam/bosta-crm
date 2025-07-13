# Bosta CRM - Complete Logistics Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Customer Relationship Management (CRM) system specifically designed for logistics and delivery businesses, with full integration to Bosta's delivery platform. This system provides complete order management, customer service, and business intelligence capabilities.

## 🚀 Features

### 📦 **Order Management**
- Real-time order tracking and status updates
- Automatic order classification and hierarchy detection
- Multi-level order management (main orders, sub-orders, returns)
- Advanced filtering and search capabilities
- Order analytics and reporting

### 👥 **Customer Management**
- Complete customer profiles and history
- Customer segmentation (VIP, Regular, New, Problematic)
- Customer satisfaction tracking
- Lifetime value analysis
- Return rate monitoring

### 🔧 **Service Actions**
- Automated service request creation
- Maintenance and repair tracking
- Return and refund management
- Hub confirmation workflows
- Service action analytics

### 📊 **Business Intelligence**
- Real-time analytics dashboard
- Order state analysis
- Delivery category insights
- Customer behavior patterns
- Performance metrics

### 🔗 **Bosta Integration**
- Seamless API integration with Bosta platform
- Real-time data synchronization
- Automatic order state updates
- Tracking number management
- Delivery status monitoring

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite (production-ready)
- **API**: RESTful API with comprehensive endpoints
- **Integration**: Bosta API v2
- **Logging**: Comprehensive system logging
- **Documentation**: Complete API documentation

## 📋 Requirements

- Python 3.8 or higher
- Flask 2.0+
- SQLite3
- Internet connection for Bosta API integration

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bosta-crm.git
cd bosta-crm
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the System
```bash
python run.py --init
```

### 4. Start the Server
```bash
python run.py --server
```

The application will be available at `http://localhost:5000`

## 📚 API Documentation

### Core Endpoints

#### Orders Management
- `GET /api/orders` - Get all orders with advanced filtering
- `GET /api/orders/analytics` - Order analytics and insights
- `GET /api/orders/states` - Order state analysis
- `GET /api/orders/{order_id}` - Get specific order details

#### Customer Management
- `GET /api/customers` - Get all customers with segmentation
- `GET /api/customers/{phone}` - Get customer details
- `GET /api/customers/stats` - Customer statistics

#### Service Actions
- `GET /api/service-actions` - Get all service actions
- `POST /api/service-actions` - Create new service action
- `PUT /api/service-actions/{action_id}` - Update service action

For complete API documentation, see [API_ENDPOINTS_GUIDE.md](API_ENDPOINTS_GUIDE.md)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bosta API     │    │   Flask App     │    │   SQLite DB     │
│                 │◄──►│                 │◄──►│                 │
│ • Order Data    │    │ • API Routes    │    │ • Orders        │
│ • Tracking      │    │ • Business      │    │ • Customers     │
│ • Status Updates│    │   Logic         │    │ • Service       │
└─────────────────┘    └─────────────────┘    │   Actions       │
                                              └─────────────────┘
```

## 📊 Key Features in Detail

### Order Hierarchy Management
- Automatic detection of main orders and sub-orders
- Intelligent linking based on customer patterns
- Real-time hierarchy updates
- Confidence scoring for relationships

### Customer Segmentation
- **VIP Customers**: High-value, low-return customers
- **Regular Customers**: Stable order patterns
- **New Customers**: Recent first-time buyers
- **Problematic Customers**: High return rates or issues

### Service Workflow
1. **Order Detection** → Automatic service need identification
2. **Service Creation** → Automated service action generation
3. **Hub Confirmation** → Mandatory quality check process
4. **Action Execution** → Service completion tracking
5. **Resolution** → Final status update and closure

## 🔧 Configuration

### Environment Variables
```bash
# Bosta API Configuration
BOSTA_API_URL=https://api.bosta.co
BOSTA_API_KEY=your_api_key_here

# Database Configuration
DATABASE_PATH=database.db

# Server Configuration
FLASK_ENV=production
FLASK_DEBUG=false
```

### Database Schema
The system automatically creates and manages the following tables:
- `orders` - Complete order information
- `customers` - Customer profiles and history
- `service_actions` - Service request tracking
- `order_hierarchy_management` - Order relationships
- `pending_orders` - Order processing queue

## 📈 Analytics & Reporting

### Real-time Dashboards
- Order completion rates
- Customer satisfaction scores
- Service action efficiency
- Return rate analysis
- Revenue tracking

### Export Capabilities
- CSV export for all data
- PDF reports generation
- API data access
- Custom report creation

## 🔒 Security Features

- Input validation and sanitization
- SQL injection prevention
- API rate limiting
- Comprehensive error handling
- Secure data transmission

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Initialize production database
python run.py --init

# Start production server
python run.py --server --host 0.0.0.0 --port 5000
```

### Docker Deployment (Coming Soon)
```bash
docker build -t bosta-crm .
docker run -p 5000:5000 bosta-crm
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [API_ENDPOINTS_GUIDE.md](API_ENDPOINTS_GUIDE.md) for detailed documentation
- Review the [HVAR_COMPLETE_CYCLE_SYSTEM.md](HVAR_COMPLETE_CYCLE_SYSTEM.md) for system architecture

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-warehouse support
- [ ] Integration with additional logistics providers
- [ ] AI-powered order prediction
- [ ] Advanced reporting engine

---

**Built with ❤️ for the logistics industry** 