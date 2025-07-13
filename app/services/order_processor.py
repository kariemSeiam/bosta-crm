"""
Comprehensive Order Processing Service
Handles complete order synchronization from Bosta API with resume capability
"""
import time
import json
import re
import math
import pytz
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
from dateutil.parser import parse as parse_date

from app.models.database import get_db, init_production_db
from app.services.bosta_api import search_orders, get_auth_headers, get_order_details, login
from app.config import API_BASE_URL

# Beautiful Clean Logging System
class CleanLogger:
    """Professional logging with clean, concise output"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 2.0  # Update every 2 seconds
        
    def _get_time(self):
        """Get current time in clean format"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _should_update(self):
        """Check if we should update the display"""
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self.last_update = current_time
            return True
        return False
    
    def info(self, message):
        """Clean info message"""
        print(f"[{self._get_time()}] ℹ️  {message}")
    
    def success(self, message):
        """Clean success message"""
        print(f"[{self._get_time()}] ✅ {message}")
    
    def warning(self, message):
        """Clean warning message"""
        print(f"[{self._get_time()}] ⚠️  {message}")
    
    def error(self, message):
        """Clean error message"""
        print(f"[{self._get_time()}] ❌ {message}")
    
    def progress(self, normal_page, normal_total, pending_page, pending_total, processed):
        """Beautiful progress display"""
        if self._should_update():
            normal_progress = f"{normal_page}/{normal_total}" if normal_total > 0 else f"{normal_page}"
            pending_progress = f"{pending_page}/{pending_total}" if pending_total > 0 else f"{pending_page}"
            
            print(f"[{self._get_time()}] 📊 Normal: {normal_progress} | Pending: {pending_progress} | Total: {processed:,}")
    
    def sync_status(self, status):
        """Sync status display"""
        print(f"[{self._get_time()}] 🔄 {status}")
    
    def schedule_info(self, next_sync):
        """Schedule information"""
        print(f"[{self._get_time()}] ⏰ Next sync: {next_sync}")

# Global clean logger
clean_log = CleanLogger()

# Egyptian timezone
EGYPT_TZ = pytz.timezone('Africa/Cairo')

# Production sync configuration
SEARCH_PAGE_SIZE = 200  # Maximum page size for search API
DETAIL_BATCH_SIZE = 50  # Number of orders to fetch details for in parallel
QUICK_SYNC_PAGES = 10   # Number of pages to sync in quick mode
FULL_SYNC_PAGES = 300   # Maximum pages for full sync (configurable)
MAX_RETRIES = 3  # Maximum number of retries for failed operations
MAX_WORKERS = 20  # Maximum parallel workers for order details fetching
BATCH_SAVE_SIZE = 100  # Number of orders to save in a single database transaction

class OrderProcessor:
    """
    Comprehensive order processor with resume capability and pending order handling
    """
    
    def __init__(self):
        self.is_running = False
        self.normal_is_running = False  # Separate flag for normal orders
        self.pending_is_running = False  # Separate flag for pending orders
        self.normal_current_page = 1  # Separate page counter for normal orders
        self.pending_current_page = 1  # Separate page counter for pending orders
        self.total_pages = 0
        self.processed_orders = 0
        self.sync_lock = Lock()
        self.normal_sync_lock = Lock()  # Separate lock for normal orders
        self.pending_sync_lock = Lock()  # Separate lock for pending orders
        self.last_sync_time = None
        self.EGYPT_TZ = EGYPT_TZ
        
        # Resume state file
        self.resume_file = 'sync_state.json'
        self.load_resume_state()
    
    def convert_timestamp_to_egypt_time(self, timestamp: int) -> datetime:
        """
        Convert millisecond timestamp to Egyptian timezone
        
        Args:
            timestamp: Timestamp in milliseconds (like creationTimestamp from Bosta)
            
        Returns:
            datetime object in Egyptian timezone
        """
        if not timestamp:
            return datetime.now(self.EGYPT_TZ)
        
        try:
            # Convert milliseconds to seconds
            timestamp_seconds = timestamp / 1000
            # Create UTC datetime
            utc_dt = datetime.fromtimestamp(timestamp_seconds, tz=pytz.UTC)
            # Convert to Egyptian timezone
            egypt_dt = utc_dt.astimezone(self.EGYPT_TZ)
            return egypt_dt
        except (ValueError, TypeError) as e:
            clean_log.warning(f"Error converting timestamp {timestamp}: {e}")
            return datetime.now(self.EGYPT_TZ)
    
    def safe_get_dict(self, data, key: str, default=None):
        """
        Safely get a dictionary value, handling cases where the field might be a list or other type
        
        Args:
            data: Source data (could be dict, list, or other)
            key: Key to extract
            default: Default value if key doesn't exist or data is wrong type
            
        Returns:
            Dictionary value or default
        """
        if not isinstance(data, dict):
            return default or {}
        value = data.get(key, default)
        return value if isinstance(value, dict) else (default or {})
    
    def safe_get_list(self, data, key: str, default=None):
        """
        Safely get a list value, handling cases where the field might be a dict or other type
        
        Args:
            data: Source data (could be dict, list, or other)
            key: Key to extract
            default: Default value if key doesn't exist or data is wrong type
            
        Returns:
            List value or default
        """
        if not isinstance(data, dict):
            return default or []
        value = data.get(key, default)
        return value if isinstance(value, list) else (default or [])
    
    def extract_page_metadata(self, page_data: Dict) -> Dict[str, Any]:
        """
        Extract metadata (total orders, page size, total pages) from search API response
        
        Args:
            page_data: Full API response from search_orders API
            
        Returns:
            Dictionary with metadata: total_orders, page_size, total_pages
        """
        try:
            if not isinstance(page_data, dict):
                clean_log.warning("Invalid page_data format for metadata extraction")
                return {}
            
            # Get the first 'data' level
            data_level1 = page_data.get('data', {})
            if not isinstance(data_level1, dict):
                clean_log.warning("Invalid data level 1 format for metadata")
                return {}
            
            # Get the second 'data' level (the actual data)
            data_level2 = data_level1.get('data', {})
            if not isinstance(data_level2, dict):
                clean_log.warning("Invalid data level 2 format for metadata")
                return {}
            
            # Extract metadata
            total_orders = data_level2.get('count', 0)
            page_size = data_level2.get('limit', SEARCH_PAGE_SIZE)
            total_pages = self.calculate_total_pages(total_orders, page_size)
            
            return {
                'total_orders': total_orders,
                'page_size': page_size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            clean_log.error(f"Error extracting page metadata: {e}")
            return {}
    
    def extract_tracking_numbers_from_page(self, page_data: Dict) -> List[str]:
        """
        Extract tracking numbers from a search API page response
        Handles the correct nested structure: page_data -> data -> data -> deliveries
        
        Args:
            page_data: Full API response from search_orders API
            
        Returns:
            List of tracking numbers
        """
        try:
            # The correct structure is: page_data -> data -> data -> deliveries
            if not isinstance(page_data, dict):
                clean_log.warning("Invalid page_data format")
                return []
            
            # Get the first 'data' level
            data_level1 = page_data.get('data', {})
            if not isinstance(data_level1, dict):
                clean_log.warning("Invalid data level 1 format")
                return []
            
            # Get the second 'data' level (the actual data)
            data_level2 = data_level1.get('data', {})
            if not isinstance(data_level2, dict):
                clean_log.warning("Invalid data level 2 format")
                return []
            
            # Get the deliveries list
            deliveries = data_level2.get('deliveries', [])
            if not isinstance(deliveries, list):
                clean_log.warning("Invalid deliveries format")
                return []
            
            # Extract tracking numbers
            tracking_numbers = []
            for order in deliveries:
                if isinstance(order, dict) and order.get('trackingNumber'):
                    tracking_numbers.append(order['trackingNumber'])
            
            clean_log.info(f"Extracted {len(tracking_numbers)} tracking numbers from page")
            return tracking_numbers
            
        except Exception as e:
            clean_log.error(f"Error extracting tracking numbers: {e}")
            return []
    
    def fetch_order_details_parallel(self, tracking_numbers: List[str]) -> Dict[str, Dict]:
        """
        Fetch detailed order data for a batch of orders using parallel processing
        Optimized for speed with ThreadPoolExecutor
        
        Args:
            tracking_numbers: List of tracking numbers
            
        Returns:
            Dictionary mapping tracking numbers to order details
        """
        order_details = {}
        failed_fetches = []
        not_found_orders = []
        api_errors = []
        
        def fetch_single_order(tracking_number: str) -> tuple:
            """Fetch details for a single order with retry logic"""
            if not tracking_number:
                return tracking_number, None, 'invalid'
            
            # Try to fetch order details with retries
            for retry in range(MAX_RETRIES):
                try:
                    detail_result = get_order_details(tracking_number)
                    
                    if detail_result and detail_result.get('success'):
                        # Success: Order found and retrieved
                        api_data = detail_result.get('data', {})
                        if isinstance(api_data, dict) and 'data' in api_data:
                            order_data = api_data['data']
                        else:
                            order_data = api_data
                        return tracking_number, order_data, 'success'
                        
                    elif detail_result and detail_result.get('status_code') == 404:
                        # Order not found - don't retry
                        return tracking_number, None, 'not_found'
                        
                    else:
                        # Other errors - retry if attempts remaining
                        if retry < MAX_RETRIES - 1:
                            clean_log.info(f"API error for {tracking_number}, retry {retry+1}: {detail_result.get('error', 'Unknown error')}")
                            continue
                        else:
                            clean_log.error(f"API error for {tracking_number} after {MAX_RETRIES} attempts: {detail_result.get('error', 'Unknown error')}")
                            return tracking_number, None, 'api_error'
                            
                except Exception as e:
                    if retry < MAX_RETRIES - 1:
                        clean_log.info(f"Exception fetching details for {tracking_number}, retry {retry+1}: {e}")
                        continue
                    else:
                        clean_log.error(f"Exception for {tracking_number} after {MAX_RETRIES} attempts: {e}")
                        return tracking_number, None, 'exception'
            
            return tracking_number, None, 'max_retries'
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_tracking = {
                executor.submit(fetch_single_order, tn): tn 
                for tn in tracking_numbers if tn
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_tracking):
                tracking_number, order_data, status = future.result()
                
                if status == 'success':
                    order_details[tracking_number] = order_data
                elif status == 'not_found':
                    not_found_orders.append(tracking_number)
                elif status == 'api_error':
                    api_errors.append(tracking_number)
                elif status == 'exception':
                    api_errors.append(tracking_number)
                elif status == 'invalid':
                    failed_fetches.append(tracking_number)
                else:
                    failed_fetches.append(tracking_number)
        
        # Comprehensive logging with error categorization
        total_requested = len(tracking_numbers)
        total_successful = len(order_details)
        total_not_found = len(not_found_orders)
        total_api_errors = len(api_errors)
        total_invalid = len(failed_fetches)
        
        success_rate = (total_successful / total_requested * 100) if total_requested > 0 else 0
        
        clean_log.info(f"Parallel batch fetch summary: {total_successful}/{total_requested} orders retrieved ({success_rate:.1f}% success)")
        
        if total_not_found > 0:
            clean_log.warning(f"API inconsistency: {total_not_found} orders found in search but not in details API")
        
        if total_api_errors > 0:
            clean_log.error(f"API errors: {total_api_errors} orders failed due to API/network issues")
        
        if total_invalid > 0:
            clean_log.warning(f"Invalid data: {total_invalid} orders had invalid tracking numbers")
        
        return order_details
    
    def fetch_order_details_batch(self, tracking_numbers: List[str]) -> Dict[str, Dict]:
        """
        Fetch detailed order data for a batch of orders using tracking numbers directly
        Handles Bosta API inconsistencies gracefully with smart error categorization
        (Legacy method - use fetch_order_details_parallel for better performance)
        
        Args:
            tracking_numbers: List of tracking numbers
            
        Returns:
            Dictionary mapping tracking numbers to order details
        """
        return self.fetch_order_details_parallel(tracking_numbers)
    
    def load_resume_state(self):
        """Load resume state from file"""
        try:
            with open(self.resume_file, 'r') as f:
                state = json.load(f)
                # Load separate states for normal and pending orders
                self.normal_current_page = state.get('normal_current_page', 1)
                self.pending_current_page = state.get('pending_current_page', 1)
                self.total_pages = state.get('total_pages', 0)
                self.processed_orders = state.get('processed_orders', 0)
                self.last_sync_time = state.get('last_sync_time')
                clean_log.success(f"Resume: Normal P{self.normal_current_page} | Pending P{self.pending_current_page} | Total: {self.processed_orders:,}")
        except FileNotFoundError:
            clean_log.info("Starting fresh - no resume state found")
        except Exception as e:
            clean_log.error(f"Resume state error: {e}")
    
    def save_resume_state(self):
        """Save current state for resume capability"""
        try:
            state = {
                'normal_current_page': self.normal_current_page,
                'pending_current_page': self.pending_current_page,
                'total_pages': self.total_pages,
                'processed_orders': self.processed_orders,
                'last_sync_time': datetime.now().isoformat()
            }
            with open(self.resume_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            clean_log.error(f"❌ Error saving resume state: {e}")
    
    def process_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process detailed order data from get_order_details API into production database format
        Handles the correct nested structure and validates data integrity
        
        Args:
            order_data: Detailed order data from Bosta API
            
        Returns:
            Dictionary with processed order data for production database schema
        """
        try:
            if not order_data or not isinstance(order_data, dict):
                clean_log.error("Invalid order data received")
                return None
                
    
            # Extract basic order information
            tracking_number = order_data.get('trackingNumber')
            if not tracking_number:
                clean_log.error("Tracking number missing in order data")
                return None
                
            order_id = order_data.get('_id')  # Optional - may not always be present
            creation_timestamp = order_data.get('creationTimestamp')
            
            # Convert creation timestamp to ISO format datetime string for created_at
            created_at = None
            if creation_timestamp:
                creation_timestamp_egypt = self.convert_timestamp_to_egypt_time(creation_timestamp)
                created_at = creation_timestamp_egypt.isoformat()
            else:
                # Fallback to current time if no timestamp provided
                created_at = datetime.now(self.EGYPT_TZ).isoformat()
            
            # Extract state information (safely handle potential list/other types)
            state = self.safe_get_dict(order_data, 'state')
            state_code = state.get('code')
            state_value = state.get('value')
            masked_state = order_data.get('maskedState', state_value)
            
            # Extract order type information (safely handle potential list/other types)
            order_type = self.safe_get_dict(order_data, 'type')
            order_type_code = order_type.get('code')
            order_type_value = order_type.get('value')
            
            # Extract delivery confirmation info
            is_confirmed_delivery = bool(order_data.get('isConfirmedDelivery', False))
            allow_open_package = bool(order_data.get('allowToOpenPackage', False))
            
            # Extract notes
            notes = order_data.get('notes', '')
            
            # Extract financial data from wallet.cashCycle (safely handle potential inconsistent types)
            wallet = self.safe_get_dict(order_data, 'wallet')
            cash_cycle = self.safe_get_dict(wallet, 'cashCycle')
            
            # Extract financial data from the correct nested structure
            cod = 0
            bosta_fees = 0
            deposited_amount = 0
            
            if cash_cycle:
                try:
                    cod_str = cash_cycle.get('cod', '0')
                    cod = float(cod_str) if cod_str else 0
                except (ValueError, TypeError):
                    cod = 0
                    
                try:
                    bosta_fees_str = cash_cycle.get('bosta_fees', '0')
                    bosta_fees = float(bosta_fees_str) if bosta_fees_str else 0
                except (ValueError, TypeError):
                    bosta_fees = 0
                    
                try:
                    deposited_amt = cash_cycle.get('deposited_amt', 0)
                    deposited_amount = float(deposited_amt) if deposited_amt else 0
                except (ValueError, TypeError):
                    deposited_amount = 0
            
            # Extract customer information (safely handle potential inconsistent types)
            receiver = self.safe_get_dict(order_data, 'receiver')
            receiver_phone = receiver.get('phone', '')
            if receiver_phone and receiver_phone.startswith('+'):
                receiver_phone = receiver_phone[1:]  # Remove + prefix
            receiver_name = receiver.get('fullName')
            receiver_first_name = receiver.get('firstName')
            receiver_last_name = receiver.get('lastName')
            receiver_second_phone = receiver.get('secondPhone', '')
            
            # Extract product information from specs (safely handle potential inconsistent types)
            specs = self.safe_get_dict(order_data, 'specs')
            package_details = self.safe_get_dict(specs, 'packageDetails')
            specs_items_count = package_details.get('itemsCount', 1)
            specs_description = package_details.get('description', '')
            
            # Process product name and count
            product_name = None
            product_count = specs_items_count
            
            # Try to extract product name from notes or specs description
            desc = specs_description or notes
            if desc:
                match = re.search(r'(\d+)\s*\*\s*(.+)', desc)
                if match:
                    product_count = int(match.group(1))
                    product_name = match.group(2).strip()
                else:
                    product_name = desc.strip()
            
            # Extract essential dropoff address information (safely handle potential inconsistent types)
            dropoff = self.safe_get_dict(order_data, 'dropOffAddress')
            
            # City information
            city = self.safe_get_dict(dropoff, 'city')
            dropoff_city_name = city.get('name')
            dropoff_city_name_ar = city.get('nameAr')
            
            # Zone information
            zone = self.safe_get_dict(dropoff, 'zone')
            dropoff_zone_name = zone.get('name')
            dropoff_zone_name_ar = zone.get('nameAr')
            
            # District information
            district = self.safe_get_dict(dropoff, 'district')
            dropoff_district_name = district.get('name')
            dropoff_district_name_ar = district.get('nameAr')
            
            # First line address
            dropoff_first_line = dropoff.get('firstLine')
            
           
            
            # Extract pickup address information (safely handle potential inconsistent types)
            pickup = self.safe_get_dict(order_data, 'pickupAddress')
            pickup_city_obj = self.safe_get_dict(pickup, 'city')
            pickup_city = pickup_city_obj.get('name') if pickup_city_obj else None
            pickup_zone_obj = self.safe_get_dict(pickup, 'zone')
            pickup_zone = pickup_zone_obj.get('name') if pickup_zone_obj else None
            pickup_district_obj = self.safe_get_dict(pickup, 'district')
            pickup_district = pickup_district_obj.get('name') if pickup_district_obj else None
            pickup_address = pickup.get('firstLine')
            
            # Extract delivery location information (safely handle potential inconsistent types)
            delivery_location = self.safe_get_dict(order_data, 'deliveryLocation')
            delivery_lat = delivery_location.get('lat')
            delivery_lng = delivery_location.get('lng')
            
            # If delivery coordinates not found in deliveryLocation, try state.delivering.actualAddress
            if not delivery_lat and not delivery_lng:
                delivering_obj = self.safe_get_dict(state, 'delivering')
                actual_address = delivering_obj.get('actualAddress') if delivering_obj else None
                if actual_address and isinstance(actual_address, list) and len(actual_address) >= 2:
                    try:
                        delivery_lat = float(actual_address[0])
                        delivery_lng = float(actual_address[1])
                    except (ValueError, TypeError, IndexError):
                        # Keep as None if conversion fails
                        pass
            
            # Extract star (delivery agent) information (safely handle potential inconsistent types)
            star = self.safe_get_dict(order_data, 'star')
            star_name = star.get('name')
            star_phone = star.get('phone')
            
            # Extract timeline information and convert to JSON (safely handle potential inconsistent types)
            timeline_data = self.safe_get_list(order_data, 'timeline')
            timeline_json = json.dumps(timeline_data) if timeline_data else None
            
            # Extract key timeline dates
            scheduled_at = order_data.get('scheduledAt')
            
            # Extract picked_up_at from state.pickedUpTime (primary source) or fallback to pickedUpAt
            picked_up_at = None
            if state.get('pickedUpTime'):
                picked_up_at = state.get('pickedUpTime')
            elif order_data.get('pickedUpAt'):
                picked_up_at = order_data.get('pickedUpAt')
                
            # Extract received_at_warehouse from state.receivedAtWarehouse.time (primary) or fallback
            received_at_warehouse = None
            received_warehouse_obj = self.safe_get_dict(state, 'receivedAtWarehouse')
            if received_warehouse_obj and received_warehouse_obj.get('time'):
                received_at_warehouse = received_warehouse_obj.get('time')
            elif order_data.get('receivedAtWarehouse'):
                received_at_warehouse = order_data.get('receivedAtWarehouse')
            
            # Extract delivered_at from state.deliveryTime (primary source) or fallback to deliveredAt
            delivered_at = None
            if state.get('deliveryTime'):
                delivered_at = state.get('deliveryTime')
            elif order_data.get('deliveredAt'):
                delivered_at = order_data.get('deliveredAt')
                
            # Extract returned_at from state.returnedToBusiness (primary) for returned orders
            returned_at = None
            if state.get('returnedToBusiness'):
                returned_at = state.get('returnedToBusiness')
            elif order_data.get('returnedAt'):
                returned_at = order_data.get('returnedAt')
            latest_awb_print_date = order_data.get('latestAwbPrintDate')
            last_call_time = order_data.get('lastCallTime')
            
            # Calculate delivery time in hours if both created_at and delivered_at exist
            delivery_time_hours = None
            if created_at and delivered_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    delivered_dt = parse_date(delivered_at)
                    if delivered_dt:
                        # Convert delivered_dt to timezone-aware if it's naive
                        if delivered_dt.tzinfo is None:
                            delivered_dt = self.EGYPT_TZ.localize(delivered_dt)
                        time_diff = delivered_dt - created_dt
                        delivery_time_hours = round(time_diff.total_seconds() / 3600, 2)
                except Exception as e:
                    clean_log.warning(f"Error calculating delivery time for {tracking_number}: {e}")
            
            # Extract communication attempts
            attempts_count = order_data.get('attemptsCount', 0)
            calls_count = order_data.get('callsNumber', 0)  # Updated to use callsNumber
            
            # Extract SLA information from nested sla object
            sla_data = self.safe_get_dict(order_data, 'sla')
            
            # Extract Order SLA information
            order_sla_obj = self.safe_get_dict(sla_data, 'orderSla')
            order_sla = order_sla_obj.get('orderSlaTimestamp') if order_sla_obj else None
            order_sla_exceeded = bool(order_sla_obj.get('isExceededOrderSla', False)) if order_sla_obj else False
            
            # Extract E2E SLA information  
            e2e_sla_obj = self.safe_get_dict(sla_data, 'e2eSla')
            e2e_sla = e2e_sla_obj.get('e2eSlaTimestamp') if e2e_sla_obj else None
            e2e_sla_exceeded = bool(e2e_sla_obj.get('isExceededE2ESla', False)) if e2e_sla_obj else False
            
            # Return processed order data with only the fields we need
            return {
                'id': order_id or tracking_number,  # Use tracking number as fallback ID
                'tracking_number': tracking_number,
                'state_code': state_code,
                'state_value': state_value,
                'masked_state': masked_state,
                'created_at': created_at,  # New field from timestamp conversion
                'is_confirmed_delivery': is_confirmed_delivery,
                'allow_open_package': allow_open_package,
                'order_type_code': order_type_code,
                'order_type_value': order_type_value,
                'cod': cod,
                'bosta_fees': bosta_fees,
                'deposited_amount': deposited_amount,
                'receiver_phone': receiver_phone,
                'receiver_name': receiver_name,
                'receiver_first_name': receiver_first_name,
                'receiver_last_name': receiver_last_name,
                'receiver_second_phone': receiver_second_phone,
                'notes': notes,
                'specs_items_count': specs_items_count,
                'specs_description': specs_description,
                'product_name': product_name,
                'product_count': product_count,
                'dropoff_city_name': dropoff_city_name,
                'dropoff_city_name_ar': dropoff_city_name_ar,
                'dropoff_zone_name': dropoff_zone_name,
                'dropoff_zone_name_ar': dropoff_zone_name_ar,
                'dropoff_district_name': dropoff_district_name,
                'dropoff_district_name_ar': dropoff_district_name_ar,
                'dropoff_first_line': dropoff_first_line,
                'pickup_city': pickup_city,
                'pickup_zone': pickup_zone,
                'pickup_district': pickup_district,
                'pickup_address': pickup_address,
                'delivery_lat': delivery_lat,
                'delivery_lng': delivery_lng,
                'star_name': star_name,
                'star_phone': star_phone,
                'timeline_json': timeline_json,
                'scheduled_at': scheduled_at,
                'picked_up_at': picked_up_at,
                'received_at_warehouse': received_at_warehouse,
                'delivered_at': delivered_at,
                'returned_at': returned_at,
                'latest_awb_print_date': latest_awb_print_date,
                'last_call_time': last_call_time,
                'delivery_time_hours': delivery_time_hours,  # New calculated field
                'attempts_count': attempts_count,
                'calls_count': calls_count,
                'order_sla_timestamp': order_sla,
                'order_sla_exceeded': order_sla_exceeded,
                'e2e_sla_timestamp': e2e_sla,
                'e2e_sla_exceeded': e2e_sla_exceeded,
                'last_synced': datetime.now().isoformat()
            }
        except Exception as e:
            tracking_num = order_data.get('trackingNumber') if isinstance(order_data, dict) else 'unknown'
            clean_log.error(f"Process error for order {tracking_num}: {e}")
            clean_log.debug(f"Order data type: {type(order_data)}")
            if isinstance(order_data, dict):
                clean_log.debug(f"Order data keys: {list(order_data.keys())}")
            return None
    
    def save_orders_batch(self, orders: List[Dict]) -> int:
        """
        Save multiple orders in a single database transaction for better performance
        
        Args:
            orders: List of processed order data dictionaries
            
        Returns:
            Number of orders successfully saved
        """
        if not orders:
            return 0
        
        saved_count = 0
        
        try:
            with get_db() as conn:
                # Check which columns exist in the table
                cursor = conn.execute("PRAGMA table_info(orders)")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Prepare batch insert
                valid_orders = []
                timeline_data = []
                
                for order in orders:
                    if not order:
                        continue
                    
                    # Filter order data to include only existing columns
                    filtered_order = {k: v for k, v in order.items() if k in existing_columns}
                    
                    if filtered_order:
                        valid_orders.append(filtered_order)
                        
                        # Collect timeline data for batch processing
                        if order.get('timeline_json'):
                            timeline_data.append({
                                'order_id': order.get('id'),
                                'tracking_number': order.get('tracking_number'),
                                'timeline_json': order.get('timeline_json')
                            })
                
                if valid_orders:
                    # Batch insert orders
                    columns = list(valid_orders[0].keys())
                    placeholders = ','.join(['?'] * len(columns))
                    sql = f"INSERT OR REPLACE INTO orders ({','.join(columns)}) VALUES ({placeholders})"
                    
                    # Execute batch insert
                    conn.executemany(sql, [list(order.values()) for order in valid_orders])
                    saved_count = len(valid_orders)
                    
                    # Batch save timeline events
                    for timeline_item in timeline_data:
                        self.save_timeline_events(
                            conn, 
                            timeline_item['order_id'], 
                            timeline_item['tracking_number'], 
                            timeline_item['timeline_json']
                        )
                    
                    # Commit all changes
                    conn.commit()
                    
                    clean_log.info(f"Batch saved {saved_count} orders successfully")
                
        except Exception as e:
            clean_log.error(f"Batch save error: {e}")
            return 0
        
        return saved_count
    
    def save_order(self, order: Dict) -> bool:
        """
        Save or update an order in the production database
        
        Args:
            order: Processed order data dictionary
            
        Returns:
            Boolean indicating success
        """
        saved_count = self.save_orders_batch([order])
        return saved_count > 0
    
    def save_timeline_events(self, conn, order_id: str, tracking_number: str, timeline_json: str):
        """
        Save timeline events to the timeline_events table
        
        Args:
            conn: Database connection
            order_id: Order ID (may be None)
            tracking_number: Tracking number (primary identifier)
            timeline_json: JSON string of timeline events
        """
        try:
            timeline = json.loads(timeline_json)
            
            # Clear existing timeline events for this order using tracking_number as primary key
            conn.execute("DELETE FROM timeline_events WHERE tracking_number = ?", (tracking_number,))
            
            # Insert new timeline events
            for i, event in enumerate(timeline):
                event_code = event.get('code')
                event_value = event.get('value')
                event_date = event.get('date')
                is_done = event.get('done', True)
                description = event.get('desc', '')
                
                if event_code and event_value and event_date:
                    conn.execute("""
                        INSERT OR REPLACE INTO timeline_events 
                        (order_id, tracking_number, event_code, event_value, event_date, is_done, description, sequence_order)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, tracking_number, event_code, event_value, event_date, is_done, description, i))
                    
        except Exception as e:
            clean_log.error(f"Error saving timeline events for order {tracking_number}: {e}")
    
    def process_pending_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process detailed order data from get_order_details API for pending/returned orders
        Handles the same structure as normal orders but saves to pending_orders table
        
        Args:
            order_data: Detailed order data from Bosta API
            
        Returns:
            Dictionary with processed pending order data for pending_orders table schema
        """
        try:
            if not order_data or not isinstance(order_data, dict):
                clean_log.error("Invalid pending order data received")
                return None
                

            # Extract basic order information
            tracking_number = order_data.get('trackingNumber')
            if not tracking_number:
                clean_log.error("Tracking number missing in pending order data")
                return None
                
            order_id = order_data.get('_id')  # Optional - may not always be present
            creation_timestamp = order_data.get('creationTimestamp')
            
            # Convert creation timestamp to ISO format datetime string for created_at
            created_at = None
            if creation_timestamp:
                creation_timestamp_egypt = self.convert_timestamp_to_egypt_time(creation_timestamp)
                created_at = creation_timestamp_egypt.isoformat()
            else:
                # Fallback to current time if no timestamp provided
                created_at = datetime.now(self.EGYPT_TZ).isoformat()
            
            # Extract state information (safely handle potential list/other types)
            state = self.safe_get_dict(order_data, 'state')
            state_code = state.get('code')
            state_value = state.get('value')
            masked_state = order_data.get('maskedState', state_value)
            
            # Extract order type information (safely handle potential list/other types)
            order_type = self.safe_get_dict(order_data, 'type')
            order_type_code = order_type.get('code')
            order_type_value = order_type.get('value')
            
            # Determine the specific pending order type
            pending_order_type = None
            if order_type_value:
                if 'EXCHANGE' in order_type_value.upper():
                    pending_order_type = 'EXCHANGE'
                elif 'RETURN' in order_type_value.upper():
                    pending_order_type = 'CUSTOMER_RETURN_PICKUP'
                else:
                    pending_order_type = order_type_value.upper()
            
            # Extract notes
            notes = order_data.get('notes', '')
            
            # Extract financial data from wallet.cashCycle (safely handle potential inconsistent types)
            wallet = self.safe_get_dict(order_data, 'wallet')
            cash_cycle = self.safe_get_dict(wallet, 'cashCycle')
            
            # Extract financial data from the correct nested structure
            cod = 0
            bosta_fees = 0
            deposited_amount = 0
            
            if cash_cycle:
                try:
                    cod_str = cash_cycle.get('cod', '0')
                    cod = float(cod_str) if cod_str else 0
                except (ValueError, TypeError):
                    cod = 0
                    
                try:
                    bosta_fees_str = cash_cycle.get('bosta_fees', '0')
                    bosta_fees = float(bosta_fees_str) if bosta_fees_str else 0
                except (ValueError, TypeError):
                    bosta_fees = 0
                    
                try:
                    deposited_amt = cash_cycle.get('deposited_amt', 0)
                    deposited_amount = float(deposited_amt) if deposited_amt else 0
                except (ValueError, TypeError):
                    deposited_amount = 0
            
            # Extract customer information (safely handle potential inconsistent types)
            receiver = self.safe_get_dict(order_data, 'receiver')
            receiver_phone = receiver.get('phone', '')
            if receiver_phone and receiver_phone.startswith('+'):
                receiver_phone = receiver_phone[1:]  # Remove + prefix
            receiver_name = receiver.get('fullName')
            receiver_first_name = receiver.get('firstName')
            receiver_last_name = receiver.get('lastName')
            receiver_second_phone = receiver.get('secondPhone', '')
            
            # Extract product information from specs (safely handle potential inconsistent types)
            specs = self.safe_get_dict(order_data, 'specs')
            package_details = self.safe_get_dict(specs, 'packageDetails')
            specs_items_count = package_details.get('itemsCount', 1)
            specs_description = package_details.get('description', '')
            
            # Process product name and count
            product_name = None
            product_count = specs_items_count
            
            # Try to extract product name from notes or specs description
            desc = specs_description or notes
            if desc:
                match = re.search(r'(\d+)\s*\*\s*(.+)', desc)
                if match:
                    product_count = int(match.group(1))
                    product_name = match.group(2).strip()
                else:
                    product_name = desc.strip()
            
            # Extract essential dropoff address information (safely handle potential inconsistent types)
            dropoff = self.safe_get_dict(order_data, 'dropOffAddress')
            
            # City information
            city = self.safe_get_dict(dropoff, 'city')
            dropoff_city_name = city.get('name')
            dropoff_city_name_ar = city.get('nameAr')
            
            # Zone information
            zone = self.safe_get_dict(dropoff, 'zone')
            dropoff_zone_name = zone.get('name')
            dropoff_zone_name_ar = zone.get('nameAr')
            
            # District information
            district = self.safe_get_dict(dropoff, 'district')
            dropoff_district_name = district.get('name')
            dropoff_district_name_ar = district.get('nameAr')
            
            # First line address
            dropoff_first_line = dropoff.get('firstLine')
            
            # Extract pickup address information (safely handle potential inconsistent types)
            pickup = self.safe_get_dict(order_data, 'pickupAddress')
            pickup_city_obj = self.safe_get_dict(pickup, 'city')
            pickup_city = pickup_city_obj.get('name') if pickup_city_obj else None
            pickup_zone_obj = self.safe_get_dict(pickup, 'zone')
            pickup_zone = pickup_zone_obj.get('name') if pickup_zone_obj else None
            pickup_district_obj = self.safe_get_dict(pickup, 'district')
            pickup_district = pickup_district_obj.get('name') if pickup_district_obj else None
            pickup_address = pickup.get('firstLine')
            
            # Extract delivery location information (safely handle potential inconsistent types)
            delivery_location = self.safe_get_dict(order_data, 'deliveryLocation')
            delivery_lat = delivery_location.get('lat')
            delivery_lng = delivery_location.get('lng')
            
            # If delivery coordinates not found in deliveryLocation, try state.delivering.actualAddress
            if not delivery_lat and not delivery_lng:
                delivering_obj = self.safe_get_dict(state, 'delivering')
                actual_address = delivering_obj.get('actualAddress') if delivering_obj else None
                if actual_address and isinstance(actual_address, list) and len(actual_address) >= 2:
                    try:
                        delivery_lat = float(actual_address[0])
                        delivery_lng = float(actual_address[1])
                    except (ValueError, TypeError, IndexError):
                        # Keep as None if conversion fails
                        pass
            
            # Extract star (delivery agent) information (safely handle potential inconsistent types)
            star = self.safe_get_dict(order_data, 'star')
            star_name = star.get('name')
            star_phone = star.get('phone')
            
            # Extract timeline information and convert to JSON (safely handle potential inconsistent types)
            timeline_data = self.safe_get_list(order_data, 'timeline')
            timeline_json = json.dumps(timeline_data) if timeline_data else None
            
            # Extract key timeline dates
            scheduled_at = order_data.get('scheduledAt')
            
            # Extract picked_up_at from state.pickedUpTime (primary source) or fallback to pickedUpAt
            picked_up_at = None
            if state.get('pickedUpTime'):
                picked_up_at = state.get('pickedUpTime')
            elif order_data.get('pickedUpAt'):
                picked_up_at = order_data.get('pickedUpAt')
                
            # Extract received_at_warehouse from state.receivedAtWarehouse.time (primary) or fallback
            received_at_warehouse = None
            received_warehouse_obj = self.safe_get_dict(state, 'receivedAtWarehouse')
            if received_warehouse_obj and received_warehouse_obj.get('time'):
                received_at_warehouse = received_warehouse_obj.get('time')
            elif order_data.get('receivedAtWarehouse'):
                received_at_warehouse = order_data.get('receivedAtWarehouse')
            
            # Extract delivered_at from state.deliveryTime (primary source) or fallback to deliveredAt
            delivered_at = None
            if state.get('deliveryTime'):
                delivered_at = state.get('deliveryTime')
            elif order_data.get('deliveredAt'):
                delivered_at = order_data.get('deliveredAt')
                
            # Extract returned_at from state.returnedToBusiness (primary) for returned orders
            returned_at = None
            if state.get('returnedToBusiness'):
                returned_at = state.get('returnedToBusiness')
            elif order_data.get('returnedAt'):
                returned_at = order_data.get('returnedAt')
            latest_awb_print_date = order_data.get('latestAwbPrintDate')
            last_call_time = order_data.get('lastCallTime')
            
            # Extract communication attempts
            attempts_count = order_data.get('attemptsCount', 0)
            calls_count = order_data.get('callsNumber', 0)  # Updated to use callsNumber
            
            # Extract SLA information from nested sla object
            sla_data = self.safe_get_dict(order_data, 'sla')
            
            # Extract Order SLA information
            order_sla_obj = self.safe_get_dict(sla_data, 'orderSla')
            order_sla = order_sla_obj.get('orderSlaTimestamp') if order_sla_obj else None
            order_sla_exceeded = bool(order_sla_obj.get('isExceededOrderSla', False)) if order_sla_obj else False
            
            # Extract E2E SLA information  
            e2e_sla_obj = self.safe_get_dict(sla_data, 'e2eSla')
            e2e_sla = e2e_sla_obj.get('e2eSlaTimestamp') if e2e_sla_obj else None
            e2e_sla_exceeded = bool(e2e_sla_obj.get('isExceededE2ESla', False)) if e2e_sla_obj else False
            
            # Try to find the original order ID from the main orders table
            original_order_id = None
            try:
                with get_db() as conn:
                    cursor = conn.execute("SELECT id FROM orders WHERE tracking_number = ?", (tracking_number,))
                    result = cursor.fetchone()
                    if result:
                        original_order_id = result[0]
            except Exception as e:
                clean_log.warning(f"Could not find original order for tracking number {tracking_number}: {e}")
            
            # Return processed pending order data
            return {
                'tracking_number': tracking_number,
                'order_id': order_id or tracking_number,  # Use tracking number as fallback ID
                'original_order_id': original_order_id,
                'order_type': pending_order_type or 'UNKNOWN',
                'order_type_code': order_type_code,
                'order_type_value': order_type_value,
                'status': 'pending',  # Default status
                'is_received': False,  # Default to not received
                'state_code': state_code,
                'state_value': state_value,
                'masked_state': masked_state,
                'receiver_phone': receiver_phone,
                'receiver_name': receiver_name,
                'receiver_first_name': receiver_first_name,
                'receiver_last_name': receiver_last_name,
                'receiver_second_phone': receiver_second_phone,
                'notes': notes,
                'specs_items_count': specs_items_count,
                'specs_description': specs_description,
                'product_name': product_name,
                'product_count': product_count,
                'cod': cod,
                'bosta_fees': bosta_fees,
                'deposited_amount': deposited_amount,
                'dropoff_city_name': dropoff_city_name,
                'dropoff_city_name_ar': dropoff_city_name_ar,
                'dropoff_zone_name': dropoff_zone_name,
                'dropoff_zone_name_ar': dropoff_zone_name_ar,
                'dropoff_district_name': dropoff_district_name,
                'dropoff_district_name_ar': dropoff_district_name_ar,
                'dropoff_first_line': dropoff_first_line,
                'pickup_city': pickup_city,
                'pickup_zone': pickup_zone,
                'pickup_district': pickup_district,
                'pickup_address': pickup_address,
                'delivery_lat': delivery_lat,
                'delivery_lng': delivery_lng,
                'star_name': star_name,
                'star_phone': star_phone,
                'timeline_json': timeline_json,
                'created_at': created_at,
                'scheduled_at': scheduled_at,
                'picked_up_at': picked_up_at,
                'received_at_warehouse': received_at_warehouse,
                'delivered_at': delivered_at,
                'returned_at': returned_at,
                'latest_awb_print_date': latest_awb_print_date,
                'last_call_time': last_call_time,
                'attempts_count': attempts_count,
                'calls_count': calls_count,
                'order_sla_timestamp': order_sla,
                'order_sla_exceeded': order_sla_exceeded,
                'e2e_sla_timestamp': e2e_sla,
                'e2e_sla_exceeded': e2e_sla_exceeded,
                'last_synced': datetime.now().isoformat()
            }
        except Exception as e:
            tracking_num = order_data.get('trackingNumber') if isinstance(order_data, dict) else 'unknown'
            clean_log.error(f"Process error for pending order {tracking_num}: {e}")
            clean_log.debug(f"Pending order data type: {type(order_data)}")
            if isinstance(order_data, dict):
                clean_log.debug(f"Pending order data keys: {list(order_data.keys())}")
            return None
    
    def save_pending_orders_batch(self, pending_orders: List[Dict]) -> int:
        """
        Save multiple pending orders in a single database transaction for better performance
        
        Args:
            pending_orders: List of processed pending order data dictionaries
            
        Returns:
            Number of pending orders successfully saved
        """
        if not pending_orders:
            return 0
        
        saved_count = 0
        
        try:
            with get_db() as conn:
                # Check which columns exist in the table
                cursor = conn.execute("PRAGMA table_info(pending_orders)")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Prepare batch insert
                valid_pending_orders = []
                timeline_data = []
                
                for pending_order in pending_orders:
                    if not pending_order:
                        continue
                    
                    # Filter pending order data to include only existing columns
                    filtered_pending_order = {k: v for k, v in pending_order.items() if k in existing_columns}
                    
                    if filtered_pending_order:
                        valid_pending_orders.append(filtered_pending_order)
                        
                        # Collect timeline data for batch processing
                        if pending_order.get('timeline_json'):
                            timeline_data.append({
                                'order_id': pending_order.get('order_id'),
                                'tracking_number': pending_order.get('tracking_number'),
                                'timeline_json': pending_order.get('timeline_json')
                            })
                
                if valid_pending_orders:
                    # Batch insert pending orders
                    columns = list(valid_pending_orders[0].keys())
                    placeholders = ','.join(['?'] * len(columns))
                    sql = f"INSERT OR REPLACE INTO pending_orders ({','.join(columns)}) VALUES ({placeholders})"
                    
                    # Execute batch insert
                    conn.executemany(sql, [list(pending_order.values()) for pending_order in valid_pending_orders])
                    saved_count = len(valid_pending_orders)
                    
                    # Batch save timeline events
                    for timeline_item in timeline_data:
                        self.save_timeline_events(
                            conn, 
                            timeline_item['order_id'], 
                            timeline_item['tracking_number'], 
                            timeline_item['timeline_json']
                        )
                    
                    # Commit all changes
                    conn.commit()
                    
                    clean_log.info(f"Batch saved {saved_count} pending orders successfully")
                
        except Exception as e:
            clean_log.error(f"Batch save pending orders error: {e}")
            return 0
        
        return saved_count
    
    def save_pending_order(self, pending_order: Dict) -> bool:
        """
        Save or update a pending order in the pending_orders table
        
        Args:
            pending_order: Processed pending order data dictionary
            
        Returns:
            Boolean indicating success
        """
        saved_count = self.save_pending_orders_batch([pending_order])
        return saved_count > 0
    
    def update_pending_order_status(self, tracking_number: str, status: str, received_by: str = None, received_notes: str = None) -> bool:
        """
        Update the status of a pending order (mark as received, processed, etc.)
        
        Args:
            tracking_number: The tracking number of the pending order
            status: New status ('pending', 'received', 'processed', 'completed')
            received_by: Name of person who received the order (optional)
            received_notes: Notes about receiving the order (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            with get_db() as conn:
                update_data = {
                    'status': status,
                    'last_synced': datetime.now().isoformat()
                }
                
                if status == 'received':
                    update_data['is_received'] = True
                    update_data['received_at'] = datetime.now(self.EGYPT_TZ).isoformat()
                    if received_by:
                        update_data['received_by'] = received_by
                    if received_notes:
                        update_data['received_notes'] = received_notes
                
                # Build update query
                set_clauses = []
                params = []
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
                
                params.append(tracking_number)
                
                sql = f"UPDATE pending_orders SET {', '.join(set_clauses)} WHERE tracking_number = ?"
                cursor = conn.execute(sql, params)
                conn.commit()
                
                if cursor.rowcount > 0:
                    clean_log.info(f"✅ Updated pending order {tracking_number} status to '{status}'")
                    return True
                else:
                    clean_log.warning(f"⚠️ No pending order found with tracking number {tracking_number}")
                    return False
                    
        except Exception as e:
            clean_log.error(f"❌ Error updating pending order status for {tracking_number}: {e}")
            return False
    
    def sync_phone_data(self, phone: str, fetch_all: bool = False) -> Dict:
        """
        Synchronize orders for a specific phone number
        
        Args:
            phone: Phone number to search for
            fetch_all: If True, fetch all pages; otherwise fetch first page only
            
        Returns:
            Dictionary with sync results
        """
        try:
            # Ensure production database exists
            init_production_db()
            
            total_tracking_numbers = []
            processed_orders = 0
            page = 1
            max_pages = 100 if fetch_all else 1
            
            clean_log.info(f"Starting phone sync for {phone}")
            
            # Get orders for this phone number
            while page <= max_pages:
                result = search_orders(page=page, limit=SEARCH_PAGE_SIZE, phone=phone)
                if not result or not result.get('success'):
                    if result and result.get('status_code') == 401:
                        clean_log.info("Authentication failed. Attempting to login...")
                        login_result = login()
                        if login_result.get('success'):
                            clean_log.info("Login successful. Retrying phone sync...")
                            result = search_orders(page=page, limit=SEARCH_PAGE_SIZE, phone=phone)
                        else:
                            error_msg = f"Authentication failed: {login_result.get('error', 'Unknown error')}"
                            clean_log.error(error_msg)
                            return {'success': False, 'error': error_msg, 'orders_processed': 0}
                    else:
                        clean_log.error(f"API error on page {page}: {result}")
                        break
                
                # Validate the API response structure
                if not self.validate_search_response(result):
                    clean_log.error(f"Invalid API response structure on page {page}")
                    break
                
                # Extract tracking numbers from this page
                page_tracking_numbers = self.extract_tracking_numbers_from_page(result)
                if not page_tracking_numbers:
                    clean_log.info("No more orders found for this phone number")
                    break
                
                total_tracking_numbers.extend(page_tracking_numbers)
                clean_log.info(f"Page {page}: extracted {len(page_tracking_numbers)} tracking numbers")
                
                if not fetch_all:
                    break
                
                page += 1
            
            # Fetch detailed order data
            if total_tracking_numbers:
                clean_log.info(f"Fetching detailed data for {len(total_tracking_numbers)} orders...")
                order_details_batch = self.fetch_order_details_batch(total_tracking_numbers)
                
                # Process and save orders
                for tracking_number, order_detail in order_details_batch.items():
                    try:
                        processed_order = self.process_order_data(order_detail)
                        if processed_order:
                            if self.save_order(processed_order):
                                processed_orders += 1
                    except Exception as e:
                        clean_log.error(f"Error processing order {tracking_number}: {e}")
            
            clean_log.info(f"Phone sync completed: {processed_orders} orders processed for {phone}")
            
            return {
                'success': True,
                'orders_found': len(total_tracking_numbers),
                'orders_processed': processed_orders
            }
            
        except Exception as e:
            clean_log.error(f"Phone sync error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_search_response(self, result: Dict) -> bool:
        """
        Validate the structure of search API response
        
        Args:
            result: API response from search_orders
            
        Returns:
            Boolean indicating if response structure is valid
        """
        try:
            if not result or not isinstance(result, dict):
                clean_log.warning("Invalid result format")
                return False
            
            if not result.get('success'):
                clean_log.warning("API request was not successful")
                return False
            
            data_level1 = result.get('data', {})
            if not isinstance(data_level1, dict):
                clean_log.warning("Invalid data level 1 structure")
                return False
            
            data_level2 = data_level1.get('data', {})
            if not isinstance(data_level2, dict):
                clean_log.warning("Invalid data level 2 structure")
                return False
            
            deliveries = data_level2.get('deliveries', [])
            if not isinstance(deliveries, list):
                clean_log.warning("Invalid deliveries structure")
                return False
            
            return True
            
        except Exception as e:
            clean_log.error(f"Error validating search response: {e}")
            return False
    
    def calculate_total_pages(self, total_count, page_size):
        """Calculate total pages based on item count and page size"""
        if total_count <= 0 or page_size <= 0:
            return 0
        return math.ceil(total_count / page_size)
    
    def process_all_orders_optimized(self, order_type: str = "normal") -> Dict[str, Any]:
        """
        Optimized order processing with parallel fetching, batch saving, and total page calculation
        
        Args:
            order_type: Type of orders to process ("normal" or "pending")
            
        Returns:
            Processing result summary
        """
        # Use appropriate lock based on order type
        lock_to_use = self.normal_sync_lock if order_type == "normal" else self.pending_sync_lock
        
        with lock_to_use:
            # Check appropriate running flag
            if order_type == "normal" and self.normal_is_running:
                return {
                    'success': False,
                    'error': 'Normal order processing already running'
                }
            elif order_type == "pending" and self.pending_is_running:
                return {
                    'success': False,
                    'error': 'Pending order processing already running'
                }
            
            # Set appropriate running flag
            if order_type == "normal":
                self.normal_is_running = True
            else:
                self.pending_is_running = True
        
        try:
            clean_log.sync_status(f"Starting {order_type} orders processing")
            
            # Step 1: Get total orders and pages from first API call
            first_result = search_orders(page=1, limit=SEARCH_PAGE_SIZE, order_type=order_type)
            
            if not first_result.get('success'):
                clean_log.error(f"Failed to fetch initial page: {first_result.get('error')}")
                return {'success': False, 'error': 'Failed to fetch initial page'}
            
            # Extract metadata (total orders, pages, etc.)
            metadata = self.extract_page_metadata(first_result)
            if not metadata:
                clean_log.error("Failed to extract page metadata")
                return {'success': False, 'error': 'Failed to extract page metadata'}
            
            total_orders = metadata['total_orders']
            page_size = metadata['page_size']
            total_pages = metadata['total_pages']
            
            clean_log.info(f"{order_type.capitalize()}: {total_orders:,} orders, {total_pages} pages")
            
            # Step 2: Process all pages with optimized flow
            total_processed = 0
            total_orders_found = 0
            start_time = time.time()
            
            # Start from current page (resume capability)
            start_page = self.normal_current_page
            clean_log.info(f"Resuming from page {start_page}")
            
            for page in range(start_page, total_pages + 1):
                page_start_time = time.time()
                
                # Fetch orders for current page
                result = search_orders(page=page, limit=page_size, order_type=order_type)
                
                if not result.get('success'):
                    clean_log.error(f"Failed to fetch page {page}: {result.get('error')}")
                    continue
                
                # Extract tracking numbers from this page
                page_tracking_numbers = self.extract_tracking_numbers_from_page(result)
                if not page_tracking_numbers:
                    continue
                
                total_orders_found += len(page_tracking_numbers)
                
                # Step 3: Parallel fetch order details
                order_details_batch = self.fetch_order_details_parallel(page_tracking_numbers)
                
                # Step 4: Process orders in batches
                processed_orders = []
                for tracking_number, order_detail in order_details_batch.items():
                    try:
                        if not order_detail:
                            clean_log.debug(f"⚠️ No detail data for order {tracking_number}")
                            continue
                            
                        processed_order = self.process_order_data(order_detail)
                        if processed_order:
                            processed_orders.append(processed_order)
                        else:
                            clean_log.debug(f"⚠️ Failed to process order {tracking_number}")
                    except Exception as e:
                        clean_log.error(f"❌ Error processing order {tracking_number}: {e}")
                
                # Step 5: Batch save orders
                if processed_orders:
                    saved_count = self.save_orders_batch(processed_orders)
                    total_processed += saved_count
                    self.processed_orders += saved_count
                else:
                    saved_count = 0
                
                # Update resume state
                self.normal_current_page = page
                self.save_resume_state()
                
                # Show beautiful progress
                clean_log.progress(page, total_pages, 0, 0, total_processed)
            
            # Final summary
            total_time = time.time() - start_time
            overall_rate = total_processed / total_time if total_time > 0 else 0
            success_rate = (total_processed / total_orders_found * 100) if total_orders_found > 0 else 0
            
            clean_log.success(f"{order_type.capitalize()} completed: {total_processed:,} orders ({success_rate:.1f}% success) in {total_time:.1f}s")
            
            # Reset page counter for next run
            if order_type == "normal":
                self.normal_current_page = 1
                self.save_resume_state()
            
            self.last_sync_time = datetime.now().isoformat()
            
            return {
                'success': True,
                'total_found': total_orders_found,
                'total_processed': total_processed,
                'success_rate': success_rate,
                'total_time': total_time,
                'overall_rate': overall_rate,
                'last_sync_time': self.last_sync_time
            }
            
        except Exception as e:
            clean_log.error(f"{order_type.capitalize()} processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Reset appropriate running flag
            if order_type == "normal":
                self.normal_is_running = False
            else:
                self.pending_is_running = False
    
    def process_all_orders(self, order_type: str = "normal") -> Dict[str, Any]:
        """
        Process all orders of specified type with resume capability and improved data validation
        (Legacy method - use process_all_orders_optimized for better performance)
        
        Args:
            order_type: Type of orders to process ("normal" or "pending")
            
        Returns:
            Processing result summary
        """
        return self.process_all_orders_optimized(order_type)
    
    def start_background_sync(self):
        """Start background order synchronization with parallel pending orders processing"""
        def sync_worker():
            while True:
                try:
                    # Process normal orders and pending orders in parallel
                    clean_log.sync_status("Starting parallel sync (normal + pending)")
                    
                    # Start both sync processes in parallel threads (don't wait for completion)
                    normal_thread = Thread(target=self._sync_normal_orders, daemon=True)
                    pending_thread = Thread(target=self._sync_pending_orders, daemon=True)
                    
                    normal_thread.start()
                    pending_thread.start()
                    
                    # Don't wait for threads to complete - let them run independently
                    clean_log.success("Background sync started - running independently")
                    
                    # Wait 30 minutes before next sync cycle
                    next_sync = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")
                    clean_log.schedule_info(f"30min cycle - Next: {next_sync}")
                    time.sleep(30 * 60)  # 30 minutes
                    
                except Exception as e:
                    clean_log.error(f"Background sync error: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        # Start background thread
        Thread(target=sync_worker, daemon=True).start()
        clean_log.success("Background sync started (30min intervals)")
    
    def _sync_normal_orders(self):
        """Sync normal orders with resume capability"""
        try:
            clean_log.sync_status("Normal orders sync started")
            result = self.process_all_orders("normal")
            clean_log.success(f"Normal sync completed: {result.get('total_processed', 0)} orders")
        except Exception as e:
            clean_log.error(f"Normal sync error: {e}")
    
    def _sync_pending_orders(self):
        """Sync pending orders with resume capability"""
        try:
            clean_log.sync_status("Pending orders sync started")
            
            # First, let's test if there are any pending orders at all
            test_result = search_orders(page=1, limit=10, order_type="pending")
            
            result = self.process_all_pending_orders()
            if result.get('success'):
                clean_log.success(f"Pending sync completed: {result.get('total_processed', 0)} orders")
            else:
                clean_log.error(f"Pending sync failed: {result.get('error')}")
        except Exception as e:
            clean_log.error(f"Pending sync error: {e}")
    
    def process_all_pending_orders(self) -> Dict[str, Any]:
        """
        Process all pending/returned orders (EXCHANGE, CUSTOMER_RETURN_PICKUP)
        Uses the same search endpoint but with pending order type filter
        Follows the same resume logic as normal orders
        
        Returns:
            Processing result summary
        """
        with self.pending_sync_lock:
            if self.pending_is_running:
                return {
                    'success': False,
                    'error': 'Order processing already running'
                }
            
            self.pending_is_running = True
        
        try:
            clean_log.sync_status("Starting pending orders processing")
            
            # Step 1: Get total pending orders and pages from first API call
            first_result = search_orders(page=1, limit=SEARCH_PAGE_SIZE, order_type="pending")
            
            
            if not first_result.get('success'):
                clean_log.error(f"Failed to fetch initial pending orders page: {first_result.get('error')}")
                return {'success': False, 'error': 'Failed to fetch initial pending orders page'}
            
            # Extract metadata (total orders, pages, etc.)
            metadata = self.extract_page_metadata(first_result)
            
            if not metadata:
                clean_log.error("Failed to extract pending orders page metadata")
                return {'success': False, 'error': 'Failed to extract pending orders page metadata'}
            
            total_orders = metadata['total_orders']
            page_size = metadata['page_size']
            total_pages = metadata['total_pages']
            
            clean_log.info(f"Pending: {total_orders:,} orders, {total_pages} pages")
            
            # If no pending orders, return early
            if total_orders == 0:
                clean_log.info("📭 No pending orders found in API")
                return {
                    'success': True,
                    'total_found': 0,
                    'total_processed': 0,
                    'success_rate': 100,
                    'total_time': 0,
                    'overall_rate': 0,
                    'last_sync_time': datetime.now().isoformat()
                }
            
            # Step 2: Process all pages with optimized flow (follow same logic as normal orders)
            total_processed = 0
            total_orders_found = 0
            start_time = time.time()
            
            # Start from current page (resume capability)
            start_page = self.pending_current_page
            clean_log.info(f"Resuming from page {start_page}")
            
            for page in range(start_page, total_pages + 1):
                page_start_time = time.time()
                
                # Fetch pending orders for current page
                result = search_orders(page=page, limit=page_size, order_type="pending")
                
                if not result.get('success'):
                    clean_log.error(f"Failed to fetch pending orders page {page}: {result.get('error')}")
                    continue
                
                # Extract tracking numbers from this page
                page_tracking_numbers = self.extract_tracking_numbers_from_page(result)
                
                if not page_tracking_numbers:
                    continue
                
                total_orders_found += len(page_tracking_numbers)
                
                # Step 3: Parallel fetch pending order details
                order_details_batch = self.fetch_order_details_parallel(page_tracking_numbers)
                
                # Step 4: Process pending orders in batches
                processed_pending_orders = []
                for tracking_number, order_detail in order_details_batch.items():
                    try:
                        if not order_detail:
                            clean_log.debug(f"⚠️ No detail data for pending order {tracking_number}")
                            continue
                            
                        processed_pending_order = self.process_pending_order_data(order_detail)
                        if processed_pending_order:
                            processed_pending_orders.append(processed_pending_order)
                        else:
                            clean_log.debug(f"⚠️ Failed to process pending order {tracking_number}")
                    except Exception as e:
                        clean_log.error(f"❌ Error processing pending order {tracking_number}: {e}")
                
                # Step 5: Batch save pending orders
                if processed_pending_orders:
                    saved_count = self.save_pending_orders_batch(processed_pending_orders)
                    total_processed += saved_count
                    self.processed_orders += saved_count
                else:
                    saved_count = 0
                
                # Update resume state (follow same logic as normal orders)
                self.pending_current_page = page
                self.save_resume_state()
                
                # Show beautiful progress
                clean_log.progress(0, 0, page, total_pages, total_processed)
            
            # Final summary
            total_time = time.time() - start_time
            overall_rate = total_processed / total_time if total_time > 0 else 0
            success_rate = (total_processed / total_orders_found * 100) if total_orders_found > 0 else 0
            
            clean_log.success(f"Pending completed: {total_processed:,} orders ({success_rate:.1f}% success) in {total_time:.1f}s")
            
            # Reset page counter for next run (follow same logic as normal orders)
            self.pending_current_page = 1
            self.save_resume_state()
            
            self.last_sync_time = datetime.now().isoformat()
            
            return {
                'success': True,
                'total_found': total_orders_found,
                'total_processed': total_processed,
                'success_rate': success_rate,
                'total_time': total_time,
                'overall_rate': overall_rate,
                'last_sync_time': self.last_sync_time
            }
            
        except Exception as e:
            clean_log.error(f"Pending processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.pending_is_running = False

# Global instance
order_processor = OrderProcessor() 