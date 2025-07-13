# HVAR Complete Cycle System
## Comprehensive Order Management, Customer Service & Service Actions with Hierarchy

---

## 📊 System Overview

The HVAR Complete Cycle System integrates **order management**, **customer service**, **service actions**, and **order hierarchy management** into a unified workflow. The system handles customers with or without existing orders, provides automatic order hierarchy detection, and ensures mandatory hub confirmation for all service actions.

### **Complete System Cycle**
```
📦 Main Order → 🔧 Service Request → 📦 Return Order (Bosta) → 🏢 Hub Confirmation → 🛠️ Service Action → ✅ Resolution
     ↓                    ↓                        ↓                        ↓                        ↓
  Order History      Link to Main Order      Product Return          Quality Check          Service Execution
     ↓                    ↓                        ↓                        ↓                        ↓
  Sub-Orders         Create Sub-Order         Hub Scanning           Action Recommendation   Update Hierarchy
```

---

## 🔁 Step-by-Step Expert Prompts for HVAR Complete Cycle (Dynamic Bosta Integration)

> **Instructions:**
> Each step below is a comprehensive, expert-level specification for the HVAR Complete Cycle that is fully integrated with the existing Bosta API data sync system. The entire cycle is dynamic and automatically updates based on real-time Bosta data changes, order state updates, and hierarchy detection. All changes are built on the existing data_sync.py infrastructure without affecting current endpoints.

### **Step 1: Dynamic Order Management with Real-Time Bosta Integration**
**Summary:**
Extend the existing data sync system to automatically detect and classify orders based on real-time Bosta API data, implementing dynamic hierarchy management that updates as order states change.

**Deep Technical Requirements:**

**Enhanced Data Sync Integration:**
- Extend `process_order_data()` function in `data_sync.py` to automatically classify orders:
  ```python
  # Add to process_order_data() function
  def classify_order_dynamically(order_data: Dict) -> Dict:
      # Real-time classification based on current Bosta state
      state_code = order_data.get('state_code')
      cod = order_data.get('cod', 0)
      
      if state_code == 45:  # Delivered
          if cod > 500:
              business_category = 'Real Sales Order'
              service_type = 'main'
              order_level = 0
          elif cod > 0:
              business_category = 'Maintenance Order'
              service_type = 'maintenance'
              order_level = 1
          else:
              business_category = 'Service Order'
              service_type = 'service'
              order_level = 1
      elif cod < 0:
          business_category = 'Refund Order'
          service_type = 'return'
          order_level = 1
      else:
          business_category = 'Operational Order'
          service_type = 'operational'
          order_level = 0
      
      return {
          'business_category': business_category,
          'service_type': service_type,
          'order_level': order_level,
          'hierarchy_status': 'unlinked'  # Will be updated by hierarchy detection
      }
  ```

**Database Schema Extensions:**
- Add hierarchy fields to existing `orders` table during sync:
  ```sql
  ALTER TABLE orders ADD COLUMN original_order_id TEXT;
  ALTER TABLE orders ADD COLUMN order_level INTEGER DEFAULT 0;
  ALTER TABLE orders ADD COLUMN service_type VARCHAR(50);
  ALTER TABLE orders ADD COLUMN hierarchy_status VARCHAR(50) DEFAULT 'unlinked';
  ALTER TABLE orders ADD COLUMN business_category VARCHAR(100);
  ALTER TABLE orders ADD COLUMN last_state_change TIMESTAMP;
  ALTER TABLE orders ADD COLUMN hierarchy_detected_at TIMESTAMP;
  ```

**Dynamic State Change Detection:**
- Implement state change tracking in `save_order()` function:
  ```python
  # Add to save_order() function
  def detect_state_changes(conn, order_data: Dict) -> bool:
      # Check if order state has changed
      cursor = conn.execute("""
          SELECT state_code, hierarchy_status, service_type 
          FROM orders WHERE tracking_number = ?
      """, (order_data['tracking_number'],))
      
      existing = cursor.fetchone()
      if existing:
          old_state = existing[0]
          new_state = order_data['state_code']
          
          if old_state != new_state:
              # State changed - trigger hierarchy re-evaluation
              conn.execute("""
                  UPDATE orders SET 
                      last_state_change = CURRENT_TIMESTAMP,
                      hierarchy_status = 'pending_review'
                  WHERE tracking_number = ?
              """, (order_data['tracking_number'],))
              return True
      return False
  ```

**Real-Time Classification Updates:**
- Automatically update order classification when Bosta data changes
- Trigger hierarchy re-evaluation on state changes
- Maintain audit trail of all classification changes

### **Step 2: Dynamic Order Hierarchy Detection with Bosta Sync**
**Summary:**
Implement automatic hierarchy detection that runs as part of the data sync process, dynamically linking orders based on real-time customer data and order patterns.

**Deep Technical Requirements:**

**Integrated Hierarchy Detection:**
- Add hierarchy detection to `sync_data()` function:
  ```python
  # Add to sync_data() function after processing orders
  def detect_hierarchy_during_sync(conn, processed_orders: List[Dict]):
      """Detect and link order hierarchy during sync process"""
      
      # Group orders by customer phone
      customer_orders = {}
      for order in processed_orders:
          phone = order.get('receiver_phone')
          if phone:
              if phone not in customer_orders:
                  customer_orders[phone] = []
              customer_orders[phone].append(order)
      
      # Process each customer's orders
      for phone, orders in customer_orders.items():
          if len(orders) > 1:
              link_customer_hierarchy(conn, phone, orders)
  
  def link_customer_hierarchy(conn, phone: str, orders: List[Dict]):
      """Link orders for a specific customer"""
      
      # Sort orders by creation date
      sorted_orders = sorted(orders, key=lambda x: x.get('created_at', ''))
      
      # Find main orders (high COD, delivered)
      main_orders = [o for o in sorted_orders 
                    if o.get('service_type') == 'main' and o.get('state_code') == 45]
      
      # Find sub-orders (maintenance, service, return)
      sub_orders = [o for o in sorted_orders 
                   if o.get('service_type') in ['maintenance', 'service', 'return']]
      
      # Link sub-orders to main orders
      for sub_order in sub_orders:
          main_order = find_best_main_order_match(sub_order, main_orders)
          if main_order:
              create_hierarchy_link(conn, main_order, sub_order, 'auto_sync')
  ```

**Dynamic Hierarchy Updates:**
- Re-evaluate hierarchy when new orders are synced
- Update existing links when order states change
- Maintain confidence scores based on data freshness

**Database Schema for Hierarchy:**
- Create `order_hierarchy_management` table during sync:
  ```sql
  CREATE TABLE IF NOT EXISTS order_hierarchy_management (
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
      last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      is_active BOOLEAN DEFAULT 1,
      FOREIGN KEY (main_order_id) REFERENCES orders(id),
      FOREIGN KEY (sub_order_id) REFERENCES orders(id)
  );
  ```

**Sync-Integrated Hierarchy Management:**
- Hierarchy detection runs automatically during data sync
- Links are updated when order states change in Bosta
- Confidence scores adjust based on data consistency

### **Step 3: Dynamic Service Action Creation with Real-Time Order Data**
**Summary:**
Extend the existing customer service system to automatically create and update service actions based on real-time order state changes and hierarchy updates from Bosta sync.

**Deep Technical Requirements:**

**Automatic Service Action Detection:**
- Add service action detection to `save_order()` function:
  ```python
  # Add to save_order() function
  def detect_service_actions(conn, order_data: Dict):
      """Automatically detect when service actions should be created"""
      
      # Check if order state indicates service need
      state_code = order_data.get('state_code')
      service_type = order_data.get('service_type')
      
      # Auto-create service actions for specific scenarios
      if state_code == 46:  # Returned
          create_service_action_from_order(conn, order_data, 'return_refund')
      elif service_type in ['maintenance', 'service']:
          create_service_action_from_order(conn, order_data, service_type)
  
  def create_service_action_from_order(conn, order_data: Dict, action_type: str):
      """Create service action from order data"""
      
      # Check if service action already exists
      cursor = conn.execute("""
          SELECT action_id FROM service_actions 
          WHERE tracking_number = ? AND action_type = ?
      """, (order_data['tracking_number'], action_type))
      
      if not cursor.fetchone():
          # Create new service action
          conn.execute("""
              INSERT INTO service_actions (
                  customer_phone, tracking_number, action_type, 
                  action_status, service_reason, product_name,
                  created_at, updated_at
              ) VALUES (?, ?, ?, 'requested', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
          """, (
              order_data['receiver_phone'],
              order_data['tracking_number'],
              action_type,
              f"Auto-detected {action_type} from order state",
              order_data.get('product_name', 'Unknown Product')
          ))
  ```

**Dynamic Service Action Updates:**
- Update service action status based on order state changes
- Link service actions to hierarchy automatically
- Maintain real-time synchronization with Bosta data

**Enhanced Service Actions Schema:**
- Extend existing service actions with sync integration:
  ```sql
  ALTER TABLE service_actions ADD COLUMN tracking_number TEXT;
  ALTER TABLE service_actions ADD COLUMN order_state_code INTEGER;
  ALTER TABLE service_actions ADD COLUMN auto_detected BOOLEAN DEFAULT 0;
  ALTER TABLE service_actions ADD COLUMN last_sync_update TIMESTAMP;
  ```

**Real-Time Status Synchronization:**
- Service action status updates automatically with order state changes
- Integration with existing customer service workflow
- Maintain audit trail of all automatic updates

### **Step 4: Dynamic Return Order Management with Bosta Integration**
**Summary:**
Implement automatic return order creation and management that integrates seamlessly with the existing Bosta API sync system, creating return orders when service actions require them.

**Deep Technical Requirements:**

**Automatic Return Order Detection:**
- Add return order detection to service action processing:
  ```python
  # Add to service action management
  def detect_return_order_needs(conn, service_action: Dict):
      """Detect when return orders need to be created"""
      
      action_type = service_action.get('action_type')
      action_status = service_action.get('action_status')
      
      # Determine if return order is needed
      needs_return = action_type in ['return_refund', 'maintenance', 'service']
      has_return = service_action.get('return_tracking_number')
      
      if needs_return and not has_return:
          create_return_order_from_service(conn, service_action)
  
  def create_return_order_from_service(conn, service_action: Dict):
      """Create return order from service action"""
      
      # Generate return tracking number
      return_tracking = f"RETURN_{generate_tracking_number()}"
      
      # Create return order in pending_orders table
      conn.execute("""
          INSERT INTO pending_orders (
              tracking_number, order_type, order_type_code, order_type_value,
              status, receiver_phone, notes, cod, bosta_fees,
              service_action_id, return_type, created_at
          ) VALUES (?, 'CUSTOMER_RETURN_PICKUP', 25, 'Customer Return Pickup',
                   'pending', ?, ?, 0, 25.00, ?, ?, CURRENT_TIMESTAMP)
      """, (
          return_tracking,
          service_action['customer_phone'],
          f"Return for {service_action['action_type']}: {service_action.get('service_reason', '')}",
          service_action['action_id'],
          service_action['action_type']
      ))
      
      # Update service action with return tracking
      conn.execute("""
          UPDATE service_actions 
          SET return_tracking_number = ?, action_status = 'return_ordered'
          WHERE action_id = ?
      """, (return_tracking, service_action['action_id']))
  ```

**Bosta Integration for Return Orders:**
- Integrate return order creation with Bosta API
- Real-time status synchronization with Bosta
- Automatic tracking number management

**Dynamic Return Order Updates:**
- Update return order status based on Bosta state changes
- Link return orders to service actions and hierarchy
- Maintain real-time synchronization

### **Step 5: Dynamic Hub Confirmation Workflow with Real-Time Updates**
**Summary:**
Implement hub confirmation workflow that automatically updates based on real-time Bosta data changes and return order status updates.

**Deep Technical Requirements:**

**Automatic Hub Workflow Creation:**
- Add hub workflow creation to return order processing:
  ```python
  # Add to return order management
  def create_hub_workflow_for_return(conn, return_order: Dict):
      """Create hub confirmation workflow for return order"""
      
      # Check if workflow already exists
      cursor = conn.execute("""
          SELECT workflow_id FROM hub_confirmation_workflow 
          WHERE return_tracking_number = ?
      """, (return_order['tracking_number'],))
      
      if not cursor.fetchone():
          # Create new hub workflow
          conn.execute("""
              INSERT INTO hub_confirmation_workflow (
                  action_id, return_tracking_number, confirmation_type,
                  confirmation_status, main_order_id, sub_order_id,
                  created_at
              ) VALUES (?, ?, 'return_inspection', 'pending', ?, ?, CURRENT_TIMESTAMP)
          """, (
              return_order['service_action_id'],
              return_order['tracking_number'],
              return_order.get('main_order_id'),
              return_order.get('sub_order_id')
          ))
  ```

**Real-Time Hub Status Updates:**
- Update hub workflow status based on Bosta return order state changes
- Automatic status transitions based on order progression
- Integration with existing hub confirmation system

**Dynamic Hub Context:**
- Provide real-time order hierarchy context to hub agents
- Update customer history and service action information
- Maintain audit trail of all hub interactions

### **Step 6: Dynamic Service Action Execution with Real-Time Monitoring**
**Summary:**
Implement service action execution that automatically updates based on real-time order state changes and maintains full traceability with the Bosta sync system.

**Deep Technical Requirements:**

**Automatic Execution Status Updates:**
- Add execution status monitoring to order processing:
  ```python
  # Add to save_order() function
  def update_service_action_execution(conn, order_data: Dict):
      """Update service action execution status based on order changes"""
      
      # Find related service actions
      cursor = conn.execute("""
          SELECT action_id, action_type, action_status 
          FROM service_actions 
          WHERE tracking_number = ?
      """, (order_data['tracking_number'],))
      
      service_actions = cursor.fetchall()
      
      for action in service_actions:
          action_id, action_type, current_status = action
          
          # Update status based on order state
          new_status = determine_execution_status(order_data['state_code'], action_type)
          
          if new_status != current_status:
              conn.execute("""
                  UPDATE service_actions 
                  SET action_status = ?, updated_at = CURRENT_TIMESTAMP
                  WHERE action_id = ?
              """, (new_status, action_id))
  
  def determine_execution_status(state_code: int, action_type: str) -> str:
      """Determine service action status based on order state"""
      
      if state_code == 45:  # Delivered
          if action_type == 'return_refund':
              return 'completed'
          elif action_type in ['maintenance', 'service']:
              return 'in_progress'
      elif state_code == 46:  # Returned
          if action_type == 'return_refund':
              return 'return_ordered'
      
      return 'requested'
  ```

**Real-Time Execution Monitoring:**
- Monitor service action progress through order state changes
- Automatic status transitions based on Bosta data
- Integration with existing execution workflow

**Dynamic Execution Tracking:**
- Track execution progress in real-time
- Update completion status automatically
- Maintain audit trail of all execution changes

### **Step 7: Dynamic Analytics with Real-Time Bosta Data**
**Summary:**
Implement comprehensive analytics that automatically update based on real-time Bosta data changes and provide insights into the complete cycle performance.

**Deep Technical Requirements:**

**Real-Time Analytics Updates:**
- Add analytics updates to sync process:
  ```python
  # Add to sync_data() function
  def update_cycle_analytics(conn, processed_orders: List[Dict]):
      """Update cycle analytics with real-time data"""
      
      # Update hierarchy analytics
      update_hierarchy_analytics(conn)
      
      # Update service action analytics
      update_service_analytics(conn)
      
      # Update hub workflow analytics
      update_hub_analytics(conn)
      
      # Update financial analytics
      update_financial_analytics(conn)
  
  def update_hierarchy_analytics(conn):
      """Update hierarchy analytics with current data"""
      
      # Calculate hierarchy coverage
      cursor = conn.execute("""
          SELECT 
              COUNT(*) as total_orders,
              COUNT(CASE WHEN hierarchy_status = 'linked' THEN 1 END) as linked_orders,
              COUNT(CASE WHEN hierarchy_status = 'unlinked' THEN 1 END) as unlinked_orders
          FROM orders
      """)
      
      stats = cursor.fetchone()
      coverage_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
      
      # Store analytics
      conn.execute("""
          INSERT INTO order_hierarchy_analytics (
              date_range_start, date_range_end, total_orders, linked_orders,
              unlinked_orders, hierarchy_coverage_rate, created_at
          ) VALUES (DATE('now', '-1 day'), DATE('now'), ?, ?, ?, ?, CURRENT_TIMESTAMP)
      """, (stats[0], stats[1], stats[2], coverage_rate))
  ```

**Dynamic Analytics Schema:**
- Create analytics tables for real-time tracking:
  ```sql
  CREATE TABLE IF NOT EXISTS cycle_analytics (
      analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
      analytics_date DATE,
      total_orders INTEGER,
      service_actions_created INTEGER,
      return_orders_created INTEGER,
      hub_workflows_active INTEGER,
      cycle_completion_rate DECIMAL(5,2),
      avg_cycle_duration_hours DECIMAL(8,2),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

**Real-Time Performance Monitoring:**
- Monitor cycle performance in real-time
- Track completion rates and durations
- Provide insights for optimization

### **Step 8: Dynamic Cycle Closure with Real-Time Verification**
**Summary:**
Implement comprehensive cycle closure that automatically verifies completion based on real-time Bosta data and maintains system integrity.

**Deep Technical Requirements:**

**Automatic Cycle Closure Detection:**
- Add cycle closure detection to order processing:
  ```python
  # Add to save_order() function
  def detect_cycle_closure(conn, order_data: Dict):
      """Detect when service cycles are complete"""
      
      # Find related service actions
      cursor = conn.execute("""
          SELECT action_id, action_type, action_status 
          FROM service_actions 
          WHERE tracking_number = ?
      """, (order_data['tracking_number'],))
      
      service_actions = cursor.fetchall()
      
      for action in service_actions:
          action_id, action_type, status = action
          
          # Check if cycle is complete
          if is_cycle_complete(order_data, action_type, status):
              close_service_cycle(conn, action_id, order_data)
  
  def is_cycle_complete(order_data: Dict, action_type: str, status: str) -> bool:
      """Determine if service cycle is complete"""
      
      state_code = order_data.get('state_code')
      
      if action_type == 'return_refund' and state_code == 46:
          return True
      elif action_type in ['maintenance', 'service'] and state_code == 45:
          return True
      
      return False
  
  def close_service_cycle(conn, action_id: int, order_data: Dict):
      """Close a completed service cycle"""
      
      conn.execute("""
          UPDATE service_actions 
          SET action_status = 'completed', 
              completed_at = CURRENT_TIMESTAMP,
              closure_status = 'verified',
              closure_verified = 1,
              closure_verified_at = CURRENT_TIMESTAMP
          WHERE action_id = ?
      """, (action_id,))
  ```

**Real-Time Closure Verification:**
- Verify cycle completion based on real-time order states
- Maintain audit trail of all closures
- Ensure data integrity and consistency

**Dynamic System Maintenance:**
- Regular cycle review based on real-time data
- Performance optimization using live metrics
- Continuous improvement through analytics

---

## 🗄️ Enhanced Database Schema

### **Orders Table** (Enhanced with Hierarchy)
```sql
-- Add hierarchy fields to existing orders table
ALTER TABLE orders ADD COLUMN original_order_id TEXT;
ALTER TABLE orders ADD COLUMN order_level INTEGER DEFAULT 0; -- 0=main, 1=sub, 2=sub-sub
ALTER TABLE orders ADD COLUMN service_type VARCHAR(50); -- 'main', 'maintenance', 'service', 'return', 'refund'
ALTER TABLE orders ADD COLUMN hierarchy_status VARCHAR(50) DEFAULT 'unlinked'; -- 'unlinked', 'main', 'sub', 'linked'

-- Update existing orders based on business logic
UPDATE orders SET 
    order_level = 0,
    service_type = 'main',
    hierarchy_status = 'main'
WHERE state_code = 45 AND cod > 500;

UPDATE orders SET 
    order_level = 1,
    service_type = 'maintenance',
    hierarchy_status = 'sub'
WHERE state_code = 45 AND cod <= 500 AND cod > 0;

UPDATE orders SET 
    order_level = 1,
    service_type = 'service',
    hierarchy_status = 'sub'
WHERE state_code = 45 AND cod = 0;

UPDATE orders SET 
    order_level = 1,
    service_type = 'return',
    hierarchy_status = 'sub'
WHERE cod < 0;
```

### **Order Hierarchy Management Table** (NEW)
```sql
CREATE TABLE order_hierarchy_management (
    hierarchy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Main Order Information
    main_order_id TEXT NOT NULL,
    main_tracking_number TEXT NOT NULL,
    main_customer_phone TEXT NOT NULL,
    main_order_date DATE,
    main_cod DECIMAL(10,2),
    
    -- Sub-Order Information
    sub_order_id TEXT NOT NULL,
    sub_tracking_number TEXT NOT NULL,
    sub_order_date DATE,
    sub_cod DECIMAL(10,2),
    sub_service_type VARCHAR(50), -- 'maintenance', 'service', 'return', 'refund'
    
    -- Hierarchy Relationship
    relationship_type VARCHAR(50) NOT NULL, -- 'maintenance', 'service', 'return', 'refund'
    relationship_level INTEGER DEFAULT 1, -- 1=direct sub, 2=sub-sub
    relationship_reason TEXT,
    
    -- Business Logic
    business_rule_applied VARCHAR(100), -- 'cod_based', 'state_based', 'manual_link'
    confidence_score DECIMAL(3,2) DEFAULT 1.00, -- 0.00-1.00
    
    -- Management
    linked_by VARCHAR(100), -- 'system', 'manual', 'api'
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    -- Foreign Keys
    FOREIGN KEY (main_order_id) REFERENCES orders(id),
    FOREIGN KEY (sub_order_id) REFERENCES orders(id)
);
```

### **Service Actions Table** (Enhanced)
```sql
CREATE TABLE service_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Customer Information (Required)
    customer_phone TEXT NOT NULL,
    customer_name TEXT,
    customer_email TEXT,
    
    -- Order Hierarchy Information
    main_order_id TEXT, -- Can be NULL for customers without orders
    main_tracking_number TEXT,
    sub_order_id TEXT, -- Linked sub-order for this service action
    sub_tracking_number TEXT,
    
    -- Service Action Details
    action_type VARCHAR(50) NOT NULL, -- 'replace_part', 'replace_full', 'maintenance', 'return_refund'
    action_subtype VARCHAR(50), -- 'warranty', 'paid', 'exchange', 'refund'
    action_status VARCHAR(50) DEFAULT 'requested', -- 'requested', 'return_ordered', 'hub_confirmed', 'in_progress', 'completed'
    
    -- Product Information
    product_name TEXT,
    product_sku TEXT,
    product_description TEXT,
    original_purchase_date DATE,
    
    -- Service Details
    service_reason TEXT NOT NULL,
    service_notes TEXT,
    estimated_cost DECIMAL(10,2) DEFAULT 0,
    actual_cost DECIMAL(10,2) DEFAULT 0,
    
    -- Return Order Information (Bosta)
    return_tracking_number TEXT,
    return_order_status VARCHAR(50), -- 'pending', 'picked_up', 'delivered_to_hub'
    return_created_at TIMESTAMP,
    return_delivered_at TIMESTAMP,
    
    -- Hub Confirmation
    hub_confirmation_required BOOLEAN DEFAULT 1,
    hub_confirmation_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'confirmed', 'rejected'
    hub_agent_name TEXT,
    hub_confirmation_date TIMESTAMP,
    hub_quality_score INTEGER, -- 1-10
    hub_inspection_notes TEXT,
    hub_recommended_action TEXT,
    
    -- Service Execution
    assigned_technician TEXT,
    service_start_date DATE,
    service_completion_date DATE,
    service_location TEXT,
    parts_used TEXT, -- JSON array
    warranty_applies BOOLEAN DEFAULT 0,
    
    -- Financial Information
    customer_contribution DECIMAL(10,2) DEFAULT 0,
    refund_amount DECIMAL(10,2) DEFAULT 0,
    refund_processed BOOLEAN DEFAULT 0,
    
    -- Timeline
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (main_order_id) REFERENCES orders(id),
    FOREIGN KEY (sub_order_id) REFERENCES orders(id),
    FOREIGN KEY (return_tracking_number) REFERENCES pending_orders(tracking_number)
);
```

### **Hub Confirmation Workflow Table** (Enhanced)
```sql
CREATE TABLE hub_confirmation_workflow (
    workflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id INTEGER NOT NULL,
    return_tracking_number TEXT NOT NULL,
    
    -- Order Hierarchy Information
    main_order_id TEXT,
    main_tracking_number TEXT,
    sub_order_id TEXT,
    sub_tracking_number TEXT,
    
    -- Hub Information
    hub_name TEXT NOT NULL,
    hub_agent_name TEXT NOT NULL,
    hub_location TEXT,
    
    -- Confirmation Process
    confirmation_type VARCHAR(50) NOT NULL, -- 'return_inspection', 'maintenance_verification', 'exchange_verification'
    confirmation_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'scanning', 'inspecting', 'confirmed', 'rejected'
    
    -- Product Condition Assessment
    product_condition VARCHAR(50), -- 'excellent', 'good', 'fair', 'poor', 'damaged'
    missing_parts TEXT, -- JSON array
    visible_damage TEXT,
    functionality_test_result VARCHAR(50), -- 'working', 'partially_working', 'not_working'
    
    -- Quality Scoring
    quality_score INTEGER, -- 1-10
    quality_notes TEXT,
    
    -- Action Recommendations
    recommended_action VARCHAR(50), -- 'maintenance', 'replace_part', 'replace_full', 'refund', 'dispose'
    recommended_priority VARCHAR(20), -- 'low', 'medium', 'high', 'urgent'
    estimated_repair_cost DECIMAL(10,2),
    estimated_repair_time_days INTEGER,
    
    -- Team Leader Review
    team_leader_review_required BOOLEAN DEFAULT 0,
    team_leader_name TEXT,
    team_leader_decision VARCHAR(50), -- 'approved', 'rejected', 'requires_changes'
    team_leader_notes TEXT,
    
    -- Timeline
    scan_timestamp TIMESTAMP,
    inspection_started_at TIMESTAMP,
    inspection_completed_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (action_id) REFERENCES service_actions(action_id),
    FOREIGN KEY (return_tracking_number) REFERENCES pending_orders(tracking_number),
    FOREIGN KEY (main_order_id) REFERENCES orders(id),
    FOREIGN KEY (sub_order_id) REFERENCES orders(id)
);
```

### **Customer Management Tables** (Enhanced)
```sql
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
```

---

## 🔄 Order Hierarchy Management

### **Automatic Order Hierarchy Detection** (Based on Existing Data)
```python
def detect_and_link_order_hierarchy():
    """Automatically detect and link order hierarchy based on existing data patterns"""
    
    with get_db() as conn:
        # Get all customers with multiple orders
        cursor = conn.execute("""
            SELECT receiver_phone, COUNT(*) as order_count
            FROM orders 
            GROUP BY receiver_phone 
            HAVING COUNT(*) > 1
            ORDER BY order_count DESC
        """)
        
        customers = cursor.fetchall()
        
        for customer in customers:
            phone = customer[0]
            
            # Get all orders for this customer
            cursor = conn.execute("""
                SELECT id, tracking_number, cod, state_code, created_at, 
                       receiver_name, product_name
                FROM orders 
                WHERE receiver_phone = ?
                ORDER BY created_at ASC
            """, (phone,))
            
            customer_orders = cursor.fetchall()
            
            # Find main orders (high COD, delivered)
            main_orders = [order for order in customer_orders 
                          if order[2] > 500 and order[3] == 45]
            
            # Find sub-orders (low COD, delivered, or returns)
            sub_orders = [order for order in customer_orders 
                         if (order[2] <= 500 and order[2] > 0 and order[3] == 45) or  # Maintenance
                            (order[2] == 0 and order[3] == 45) or  # Service
                            (order[2] < 0)]  # Returns/Refunds
            
            # Link sub-orders to main orders
            for sub_order in sub_orders:
                main_order = find_best_main_order_match(sub_order, main_orders)
                if main_order:
                    link_order_hierarchy(conn, main_order, sub_order, 'automatic')
        
        conn.commit()
        return {'success': True, 'customers_processed': len(customers)}

def find_best_main_order_match(sub_order, main_orders):
    """Find the best main order match for a sub-order"""
    
    if not main_orders:
        return None
    
    # If only one main order, use it
    if len(main_orders) == 1:
        return main_orders[0]
    
    # Find main order with closest date
    sub_date = datetime.strptime(sub_order[4], '%Y-%m-%d %H:%M:%S')
    
    best_match = None
    min_date_diff = float('inf')
    
    for main_order in main_orders:
        main_date = datetime.strptime(main_order[4], '%Y-%m-%d %H:%M:%S')
        date_diff = abs((sub_date - main_date).days)
        
        if date_diff < min_date_diff:
            min_date_diff = date_diff
            best_match = main_order
    
    # Only link if within 365 days
    return best_match if min_date_diff <= 365 else None

def link_order_hierarchy(conn, main_order, sub_order, link_method='manual'):
    """Link sub-order to main order in hierarchy"""
    
    # Determine relationship type based on sub-order characteristics
    if sub_order[2] <= 500 and sub_order[2] > 0 and sub_order[3] == 45:
        relationship_type = 'maintenance'
        business_rule = 'cod_based_maintenance'
    elif sub_order[2] == 0 and sub_order[3] == 45:
        relationship_type = 'service'
        business_rule = 'cod_based_service'
    elif sub_order[2] < 0:
        relationship_type = 'return'
        business_rule = 'cod_based_return'
    else:
        relationship_type = 'other'
        business_rule = 'manual_link'
    
    # Check if already linked
    cursor = conn.execute("""
        SELECT hierarchy_id FROM order_hierarchy_management 
        WHERE sub_order_id = ?
    """, (sub_order[0],))
    
    if cursor.fetchone():
        return False  # Already linked
    
    # Create hierarchy link
    cursor = conn.execute("""
        INSERT INTO order_hierarchy_management (
            main_order_id, main_tracking_number, main_customer_phone, main_order_date, main_cod,
            sub_order_id, sub_tracking_number, sub_order_date, sub_cod, sub_service_type,
            relationship_type, relationship_level, relationship_reason, business_rule_applied,
            confidence_score, linked_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        main_order[0], main_order[1], main_order[5], main_order[4], main_order[2],
        sub_order[0], sub_order[1], sub_order[4], sub_order[2], relationship_type,
        relationship_type, 1, f"Auto-linked based on {business_rule}", business_rule,
        0.95, link_method
    ))
    
    # Update orders table
    conn.execute("""
        UPDATE orders 
        SET original_order_id = ?, order_level = 1, service_type = ?, hierarchy_status = 'linked'
        WHERE id = ?
    """, (main_order[0], relationship_type, sub_order[0]))
    
    return True
```

### **Manual Order Hierarchy Management**
```python
def manual_link_orders(main_order_id: str, sub_order_id: str, relationship_reason: str):
    """Manually link orders in hierarchy"""
    
    with get_db() as conn:
        # Get order details
        cursor = conn.execute("""
            SELECT id, tracking_number, cod, state_code, created_at, receiver_phone, receiver_name
            FROM orders WHERE id IN (?, ?)
        """, (main_order_id, sub_order_id))
        
        orders = cursor.fetchall()
        if len(orders) != 2:
            return {'success': False, 'error': 'Orders not found'}
        
        # Determine which is main and which is sub
        main_order = None
        sub_order = None
        
        for order in orders:
            if order[0] == main_order_id:
                main_order = order
            else:
                sub_order = order
        
        if not main_order or not sub_order:
            return {'success': False, 'error': 'Invalid order IDs'}
        
        # Verify they belong to same customer
        if main_order[5] != sub_order[5]:
            return {'success': False, 'error': 'Orders belong to different customers'}
        
        # Link orders
        success = link_order_hierarchy(conn, main_order, sub_order, 'manual')
        
        if success:
            conn.commit()
            return {'success': True, 'message': 'Orders linked successfully'}
        else:
            return {'success': False, 'error': 'Orders already linked'}
```

---

## 🔧 Service Action Management

### **Service Action Creation** (With Order Hierarchy)
```python
def create_service_action(
    customer_phone: str,
    action_type: str,
    service_reason: str,
    main_order_id: str = None,  # Optional main order link
    product_info: dict = None
):
    """Create service action with optional order hierarchy linking"""
    
    with get_db() as conn:
        # Get customer information (create if doesn't exist)
        customer = get_or_create_customer(conn, customer_phone)
        
        # Get main order details if provided
        main_order = None
        sub_order = None
        
        if main_order_id:
            cursor = conn.execute("""
                SELECT id, tracking_number, product_name, product_sku, 
                       created_at, cod, state_code
                FROM orders WHERE id = ?
            """, (main_order_id,))
            main_order = cursor.fetchone()
            
            # Find linked sub-order for this service action
            cursor = conn.execute("""
                SELECT sub_order_id, sub_tracking_number, sub_service_type
                FROM order_hierarchy_management 
                WHERE main_order_id = ? AND relationship_type = ?
            """, (main_order_id, action_type))
            sub_order = cursor.fetchone()
        
        # Create service action
        action_data = {
            'customer_phone': customer_phone,
            'customer_name': customer.get('full_name'),
            'customer_email': customer.get('email'),
            'main_order_id': main_order_id,
            'main_tracking_number': main_order[1] if main_order else None,
            'sub_order_id': sub_order[0] if sub_order else None,
            'sub_tracking_number': sub_order[1] if sub_order else None,
            'action_type': action_type,
            'action_status': 'requested',
            'product_name': product_info.get('name') if product_info else (main_order[2] if main_order else None),
            'product_sku': product_info.get('sku') if product_info else (main_order[3] if main_order else None),
            'original_purchase_date': main_order[4] if main_order else None,
            'service_reason': service_reason,
            'estimated_cost': get_action_type_cost(action_type)
        }
        
        cursor = conn.execute("""
            INSERT INTO service_actions (
                customer_phone, customer_name, customer_email,
                main_order_id, main_tracking_number, sub_order_id, sub_tracking_number,
                action_type, action_status, product_name, product_sku,
                original_purchase_date, service_reason, estimated_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(action_data.values()))
        
        action_id = cursor.lastrowid
        
        # Create return order if required
        if requires_return_order(action_type):
            return_tracking = create_return_order(conn, action_id, customer_phone)
            
            # Update service action with return tracking
            conn.execute("""
                UPDATE service_actions 
                SET return_tracking_number = ?
                WHERE action_id = ?
            """, (return_tracking, action_id))
        
        conn.commit()
        return action_id
```

### **Return Order Creation** (Bosta Integration)
```python
def create_return_order(conn, action_id: int, customer_phone: str):
    """Create return order in Bosta for product return"""
    
    # Get service action details
    cursor = conn.execute("""
        SELECT action_type, product_name, service_reason, main_order_id, sub_order_id
        FROM service_actions WHERE action_id = ?
    """, (action_id,))
    action = cursor.fetchone()
    
    # Generate return tracking number
    return_tracking = f"RETURN_{generate_tracking_number()}"
    
    # Create return order in pending_orders table
    cursor = conn.execute("""
        INSERT INTO pending_orders (
            tracking_number, order_type, order_type_code, order_type_value,
            status, receiver_phone, notes, cod, bosta_fees
        ) VALUES (?, 'CUSTOMER_RETURN_PICKUP', 25, 'Customer Return Pickup',
                 'pending', ?, ?, 0, 25.00)
    """, (return_tracking, customer_phone, f"Return for {action[0]}: {action[2]}"))
    
    # Create hub confirmation workflow with hierarchy info
    cursor = conn.execute("""
        INSERT INTO hub_confirmation_workflow (
            action_id, return_tracking_number, confirmation_type,
            confirmation_status, main_order_id, sub_order_id
        ) VALUES (?, ?, 'return_inspection', 'pending', ?, ?)
    """, (action_id, return_tracking, action[3], action[4]))
    
    return return_tracking
```

---

## 🏢 Hub Confirmation Workflow

### **Enhanced Hub Scanning with Hierarchy**
```python
def hub_scan_return_order_with_hierarchy(return_tracking_number: str, hub_name: str, hub_agent: str):
    """Hub scans returned order with complete hierarchy information"""
    
    with get_db() as conn:
        # Get return order and service action with hierarchy
        cursor = conn.execute("""
            SELECT 
                po.*, sa.action_id, sa.action_type, sa.service_reason,
                sa.main_order_id, sa.main_tracking_number,
                sa.sub_order_id, sa.sub_tracking_number,
                ohm.relationship_type, ohm.relationship_reason
            FROM pending_orders po
            JOIN service_actions sa ON po.tracking_number = sa.return_tracking_number
            LEFT JOIN order_hierarchy_management ohm ON sa.main_order_id = ohm.main_order_id 
                AND sa.sub_order_id = ohm.sub_order_id
            WHERE po.tracking_number = ?
        """, (return_tracking_number,))
        
        result = cursor.fetchone()
        if not result:
            return {'success': False, 'error': 'Return order not found'}
        
        # Update return order status
        conn.execute("""
            UPDATE pending_orders 
            SET status = 'received', is_received = 1, 
                received_at = CURRENT_TIMESTAMP, received_by = ?
            WHERE tracking_number = ?
        """, (hub_agent, return_tracking_number))
        
        # Update hub confirmation workflow with hierarchy info
        conn.execute("""
            UPDATE hub_confirmation_workflow 
            SET hub_name = ?, hub_agent_name = ?, confirmation_status = 'scanning',
                scan_timestamp = CURRENT_TIMESTAMP,
                main_order_id = ?, main_tracking_number = ?,
                sub_order_id = ?, sub_tracking_number = ?
            WHERE return_tracking_number = ?
        """, (hub_name, hub_agent, result['main_order_id'], result['main_tracking_number'],
              result['sub_order_id'], result['sub_tracking_number'], return_tracking_number))
        
        # Update service action status
        conn.execute("""
            UPDATE service_actions 
            SET action_status = 'return_received', return_delivered_at = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, (result['action_id'],))
        
        conn.commit()
        
        return {
            'success': True,
            'action_id': result['action_id'],
            'action_type': result['action_type'],
            'service_reason': result['service_reason'],
            'order_hierarchy': {
                'main_order_id': result['main_order_id'],
                'main_tracking_number': result['main_tracking_number'],
                'sub_order_id': result['sub_order_id'],
                'sub_tracking_number': result['sub_tracking_number'],
                'relationship_type': result['relationship_type'],
                'relationship_reason': result['relationship_reason']
            },
            'has_maintenance_ticket': check_maintenance_ticket(result['action_id']),
            'return_type': determine_return_type(result['action_type'])
        }
```

### **Hub Inspection Process**
```python
def hub_inspection_complete(
    return_tracking_number: str,
    product_condition: str,
    quality_score: int,
    inspection_notes: str,
    recommended_action: str
):
    """Complete hub inspection and provide recommendations"""
    
    with get_db() as conn:
        # Update hub confirmation workflow
        conn.execute("""
            UPDATE hub_confirmation_workflow 
            SET confirmation_status = 'confirmed',
                product_condition = ?,
                quality_score = ?,
                inspection_notes = ?,
                recommended_action = ?,
                inspection_completed_at = CURRENT_TIMESTAMP,
                confirmed_at = CURRENT_TIMESTAMP
            WHERE return_tracking_number = ?
        """, (product_condition, quality_score, inspection_notes, 
              recommended_action, return_tracking_number))
        
        # Get action details
        cursor = conn.execute("""
            SELECT action_id, action_type
            FROM service_actions 
            WHERE return_tracking_number = ?
        """, (return_tracking_number,))
        action = cursor.fetchone()
        
        # Update service action status
        new_status = determine_action_status_from_inspection(action['action_type'], recommended_action)
        conn.execute("""
            UPDATE service_actions 
            SET action_status = ?, hub_confirmation_status = 'confirmed',
                hub_confirmation_date = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, (new_status, action['action_id']))
        
        # Check if team leader review is required
        if quality_score <= 3 or recommended_action in ['refund', 'dispose']:
            conn.execute("""
                UPDATE hub_confirmation_workflow 
                SET team_leader_review_required = 1
                WHERE return_tracking_number = ?
            """, (return_tracking_number,))
        
        conn.commit()
        
        return {
            'success': True,
            'action_id': action['action_id'],
            'new_status': new_status,
            'team_leader_review_required': quality_score <= 3 or recommended_action in ['refund', 'dispose']
        }
```

---

## 🔧 Service Action Execution

### **Service Action Types & Execution**

#### **1. Replace Part**
```python
def execute_replace_part(action_id: int, technician: str, parts_used: list):
    """Execute part replacement service"""
    
    with get_db() as conn:
        # Get action details
        cursor = conn.execute("""
            SELECT * FROM service_actions WHERE action_id = ?
        """, (action_id,))
        action = cursor.fetchone()
        
        # Calculate actual cost
        parts_cost = calculate_parts_cost(parts_used)
        labor_cost = 50.00  # Standard labor cost
        actual_cost = parts_cost + labor_cost
        
        # Update service action
        conn.execute("""
            UPDATE service_actions 
            SET action_status = 'in_progress',
                assigned_technician = ?,
                service_start_date = CURRENT_DATE,
                parts_used = ?,
                actual_cost = ?
            WHERE action_id = ?
        """, (technician, json.dumps(parts_used), actual_cost, action_id))
        
        # Create service order for return
        return_tracking = create_service_return_order(action_id, 'repaired')
        
        conn.commit()
        return {'success': True, 'return_tracking': return_tracking}
```

#### **2. Full Replacement**
```python
def execute_full_replacement(action_id: int, new_product_sku: str):
    """Execute full product replacement"""
    
    with get_db() as conn:
        # Get action details
        cursor = conn.execute("""
            SELECT * FROM service_actions WHERE action_id = ?
        """, (action_id,))
        action = cursor.fetchone()
        
        # Create replacement order
        replacement_tracking = create_replacement_order(
            customer_phone=action['customer_phone'],
            new_product_sku=new_product_sku,
            original_action_id=action_id
        )
        
        # Update service action
        conn.execute("""
            UPDATE service_actions 
            SET action_status = 'completed',
                action_subtype = 'full_replacement',
                completed_at = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, (action_id,))
        
        conn.commit()
        return {'success': True, 'replacement_tracking': replacement_tracking}
```

#### **3. Maintenance**
```python
def execute_maintenance(action_id: int, technician: str, maintenance_notes: str):
    """Execute maintenance service"""
    
    with get_db() as conn:
        # Get action details
        cursor = conn.execute("""
            SELECT * FROM service_actions WHERE action_id = ?
        """, (action_id,))
        action = cursor.fetchone()
        
        # Update service action
        conn.execute("""
            UPDATE service_actions 
            SET action_status = 'in_progress',
                assigned_technician = ?,
                service_start_date = CURRENT_DATE,
                service_notes = ?
            WHERE action_id = ?
        """, (technician, maintenance_notes, action_id))
        
        # Create service return order
        return_tracking = create_service_return_order(action_id, 'maintained')
        
        conn.commit()
        return {'success': True, 'return_tracking': return_tracking}
```

#### **4. Return with Refund**
```python
def execute_return_refund(action_id: int, refund_amount: float):
    """Execute return and refund process"""
    
    with get_db() as conn:
        # Get action details
        cursor = conn.execute("""
            SELECT * FROM service_actions WHERE action_id = ?
        """, (action_id,))
        action = cursor.fetchone()
        
        # Process refund
        refund_processed = process_refund(
            customer_phone=action['customer_phone'],
            amount=refund_amount,
            reason=f"Return refund for {action['service_reason']}"
        )
        
        # Update service action
        conn.execute("""
            UPDATE service_actions 
            SET action_status = 'completed',
                action_subtype = 'refund_processed',
                refund_amount = ?,
                refund_processed = 1,
                completed_at = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, (refund_amount, action_id))
        
        conn.commit()
        return {'success': True, 'refund_processed': refund_processed}
```

---

## 🔌 Enhanced API Endpoints

### **Order Hierarchy Management API** (`/api/orders/hierarchy`)
```http
# Order Hierarchy Management
POST /api/orders/hierarchy/detect              # Auto-detect and link order hierarchy
POST /api/orders/hierarchy/link                # Manually link orders
GET /api/orders/hierarchy/{order_id}           # Get order hierarchy
GET /api/orders/hierarchy/customer/{phone}     # Get customer order hierarchy
PUT /api/orders/hierarchy/{order_id}/unlink    # Unlink order from hierarchy
GET /api/orders/hierarchy/analytics            # Hierarchy analytics

# Service Actions with Order Hierarchy
POST /api/service-actions                      # Create service action (with hierarchy)
GET /api/service-actions/hierarchy/{order_id}  # Get service actions for order hierarchy
POST /api/service-actions/{action_id}/link-order # Link service action to order
```

### **Enhanced Orders API** (`/api/orders`)
```http
# Existing endpoints with hierarchy support
GET /api/orders                                # Get orders with hierarchy info
GET /api/orders/{order_id}                     # Get order with hierarchy details
GET /api/orders/phone/{phone}                  # Get customer orders with hierarchy

# New hierarchy endpoints
GET /api/orders/{order_id}/sub-orders          # Get sub-orders for main order
GET /api/orders/{order_id}/main-order          # Get main order for sub-order
GET /api/orders/hierarchy/status               # Get hierarchy processing status
```

### **Service Actions API** (`/api/service-actions`)
```http
# Service Action Management
POST /api/service-actions                    # Create service action
GET /api/service-actions                     # Get service actions with filtering
GET /api/service-actions/{action_id}         # Get specific service action
PUT /api/service-actions/{action_id}         # Update service action
DELETE /api/service-actions/{action_id}      # Cancel service action

# Service Action Execution
POST /api/service-actions/{action_id}/execute # Execute service action
POST /api/service-actions/{action_id}/replace-part # Replace part
POST /api/service-actions/{action_id}/replace-full # Full replacement
POST /api/service-actions/{action_id}/maintenance # Execute maintenance
POST /api/service-actions/{action_id}/refund # Process refund

# Hub Confirmation
POST /api/service-actions/hub-scan           # Hub scans return order
POST /api/service-actions/hub-inspection     # Complete hub inspection
POST /api/service-actions/team-leader-review # Team leader review

# Analytics
GET /api/service-actions/analytics           # Service analytics
GET /api/service-actions/dashboard           # Service dashboard
```

### **Example API Usage**
```bash
# Auto-detect and link order hierarchy
curl -X POST http://localhost:5000/api/orders/hierarchy/detect

# Manually link orders
curl -X POST http://localhost:5000/api/orders/hierarchy/link \
  -H "Content-Type: application/json" \
  -d '{
    "main_order_id": "ORDER123",
    "sub_order_id": "ORDER456",
    "relationship_reason": "Maintenance order for original purchase"
  }'

# Get order hierarchy
curl http://localhost:5000/api/orders/hierarchy/ORDER123

# Create service action with order hierarchy
curl -X POST http://localhost:5000/api/service-actions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "201234567890",
    "action_type": "maintenance",
    "service_reason": "Product not working properly",
    "main_order_id": "ORDER123",
    "link_to_hierarchy": true
  }'

# Hub scans return order
curl -X POST http://localhost:5000/api/service-actions/hub-scan \
  -H "Content-Type: application/json" \
  -d '{
    "return_tracking_number": "RETURN123456789",
    "hub_name": "Cairo Hub",
    "hub_agent": "Ahmed Ali"
  }'

# Complete hub inspection
curl -X POST http://localhost:5000/api/service-actions/hub-inspection \
  -H "Content-Type: application/json" \
  -d '{
    "return_tracking_number": "RETURN123456789",
    "product_condition": "good",
    "quality_score": 7,
    "inspection_notes": "Minor wear, needs maintenance",
    "recommended_action": "maintenance"
  }'

# Execute maintenance
curl -X POST http://localhost:5000/api/service-actions/123/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "technician": "Mohammed Hassan",
    "maintenance_notes": "Replaced motor bearings, cleaned internal parts"
  }'
```

---

## 📊 Complete Analytics & Business Intelligence

### **Order Hierarchy Analytics**
```sql
-- Order hierarchy statistics
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN hierarchy_status = 'main' THEN 1 END) as main_orders,
    COUNT(CASE WHEN hierarchy_status = 'sub' THEN 1 END) as sub_orders,
    COUNT(CASE WHEN hierarchy_status = 'linked' THEN 1 END) as linked_orders,
    COUNT(CASE WHEN hierarchy_status = 'unlinked' THEN 1 END) as unlinked_orders
FROM orders;

-- Hierarchy relationship types
SELECT 
    relationship_type,
    COUNT(*) as relationship_count,
    AVG(confidence_score) as avg_confidence,
    COUNT(CASE WHEN linked_by = 'automatic' THEN 1 END) as auto_linked,
    COUNT(CASE WHEN linked_by = 'manual' THEN 1 END) as manual_linked
FROM order_hierarchy_management 
GROUP BY relationship_type;

-- Customer hierarchy patterns
SELECT 
    COUNT(DISTINCT main_customer_phone) as customers_with_hierarchy,
    AVG(sub_orders_per_main) as avg_sub_orders_per_main,
    MAX(sub_orders_per_main) as max_sub_orders_per_main
FROM (
    SELECT 
        main_customer_phone,
        COUNT(*) as sub_orders_per_main
    FROM order_hierarchy_management 
    GROUP BY main_customer_phone, main_order_id
);
```

### **Service Actions with Hierarchy Analytics**
```sql
-- Service actions by order hierarchy
SELECT 
    CASE 
        WHEN sa.main_order_id IS NOT NULL THEN 'Linked to Main Order'
        WHEN sa.sub_order_id IS NOT NULL THEN 'Linked to Sub Order'
        ELSE 'No Order Link'
    END as hierarchy_status,
    sa.action_type,
    COUNT(*) as action_count,
    AVG(CASE WHEN sa.completed_at IS NOT NULL 
        THEN julianday(sa.completed_at) - julianday(sa.created_at) 
        ELSE NULL END) as avg_resolution_days
FROM service_actions sa
GROUP BY hierarchy_status, sa.action_type;

-- Hub confirmation with hierarchy
SELECT 
    hcw.confirmation_type,
    COUNT(*) as total_confirmations,
    AVG(hcw.quality_score) as avg_quality_score,
    COUNT(CASE WHEN hcw.team_leader_review_required = 1 THEN 1 END) as review_required_count
FROM hub_confirmation_workflow hcw
LEFT JOIN service_actions sa ON hcw.action_id = sa.action_id
WHERE sa.main_order_id IS NOT NULL OR sa.sub_order_id IS NOT NULL
GROUP BY hcw.confirmation_type;
```

### **Business Intelligence Insights**
```sql
-- Revenue analysis by order hierarchy
SELECT 
    o.service_type,
    COUNT(*) as order_count,
    SUM(o.cod) as total_revenue,
    AVG(o.cod) as avg_revenue,
    COUNT(CASE WHEN o.state_code = 45 THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN o.state_code = 46 THEN 1 END) as returned_orders
FROM orders o
WHERE o.hierarchy_status IN ('main', 'linked')
GROUP BY o.service_type;

-- Customer service metrics by hierarchy
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COUNT(sa.action_id) as service_actions,
    COUNT(CASE WHEN sa.main_order_id IS NOT NULL THEN 1 END) as linked_actions,
    AVG(sa.actual_cost) as avg_service_cost
FROM customers c
LEFT JOIN service_actions sa ON c.phone = sa.customer_phone
GROUP BY c.customer_segment;
```

---

## 🔄 Complete Enhanced Workflow Examples

### **Example 1: Customer with Order - Maintenance**
```
Customer Call: "My blender stopped working"
Action:
├─ Auto-Detect Hierarchy: ORDER123 (Main) → ORDER456 (Maintenance)
├─ Create Service Action: ACTION001 (Linked to ORDER123)
├─ Create Return Order: RETURN456 (Bosta)
├─ Customer Returns Product to Hub
├─ Hub Scans: RETURN456 → Shows "Maintenance Ticket + Order History"
├─ Hub Inspection: Quality Score 6 → "Needs Maintenance"
├─ Team Leader Review: Not Required
├─ Execute Maintenance: Replace motor
└─ Return Product: Repaired product back to customer
```

### **Example 2: Customer without Order - Full Replacement**
```
Customer Call: "Bought blender from store, defective"
Action:
├─ Create Service Action: ACTION002 (No main order link)
├─ Create Return Order: RETURN789 (Bosta)
├─ Customer Returns Product to Hub
├─ Hub Scans: RETURN789 → Shows "Full Replacement Request"
├─ Hub Inspection: Quality Score 2 → "Defective"
├─ Team Leader Review: Required (Low quality score)
├─ Team Leader Decision: "Approve Full Replacement"
├─ Execute Full Replacement: New product shipped
└─ Resolution: Customer receives new product
```

### **Example 3: Return with Refund**
```
Customer Call: "Want to return and get refund"
Action:
├─ Auto-Detect Hierarchy: ORDER456 (Main) → ORDER789 (Return)
├─ Create Service Action: ACTION003 (Linked to ORDER456)
├─ Create Return Order: RETURN101 (Bosta)
├─ Customer Returns Product to Hub
├─ Hub Scans: RETURN101 → Shows "Return Refund Request + Order History"
├─ Hub Inspection: Quality Score 8 → "Good Condition"
├─ Team Leader Review: Not Required
├─ Execute Refund: Process refund payment
└─ Resolution: Customer receives refund
```

---

## 🎯 System Benefits & Strategic Value

### **1. Complete Order History Management**
- **Automatic Hierarchy Detection**: Based on existing data patterns
- **Manual Hierarchy Management**: For complex cases
- **Order Relationship Tracking**: Complete order family trees
- **Business Intelligence**: Service patterns by order type

### **2. Enhanced Service Context**
- **Order History Integration**: Service actions linked to order hierarchy
- **Complete Customer Journey**: From purchase to service to resolution
- **Informed Decision Making**: Hub operations with full context
- **Quality Control**: Enhanced with order relationship data

### **3. Improved Hub Operations**
- **Hierarchy Information**: Hub sees complete order context
- **Better Decision Making**: Informed by order history
- **Quality Control**: Enhanced with order relationship data
- **Efficient Processing**: Streamlined workflows with context

### **4. Comprehensive Analytics**
- **Order Hierarchy Analytics**: Relationship patterns and trends
- **Service Performance**: By order hierarchy status
- **Customer Journey Mapping**: Complete lifecycle tracking
- **Business Intelligence**: Revenue optimization insights

### **5. Customer Service Excellence**
- **No Order Required**: Service for all customers
- **Multiple Resolution Options**: Flexible solutions
- **Complete History**: Full service record
- **Proactive Service**: Based on order patterns

### **6. Financial Management**
- **Revenue Protection**: Track service costs vs. order value
- **Refund Control**: Monitor and prevent unnecessary refunds
- **Cost Optimization**: Service actions based on order hierarchy
- **Profit Margin Analysis**: Service impact on customer lifetime value

This comprehensive system provides complete order hierarchy management integrated with service management workflow, ensuring proper tracking, quality control, and business intelligence for all service actions with full order history context. 