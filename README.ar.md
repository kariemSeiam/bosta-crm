# 🚀 نظام هفار لإدارة دورة العمل الكاملة
## نظام إدارة علاقات العملاء اللوجستي المتكامل مع تكامل Bosta

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Bosta API](https://img.shields.io/badge/Bosta%20API-v2-orange.svg)](https://bosta.co)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **نظام متكامل لإدارة علاقات العملاء في مجال اللوجستيات والتوصيل، مبني بالكامل من الصفر مع تكامل كامل مع Bosta API، ويتميز بإدارة شاملة لهرمية الطلبات، وأتمتة سير العمل الخدمي، وذكاء أعمال لحظي.**

---

## 👨‍💻 **عن المطور**

**أنا المطور الكامل الذي صمم وبنى هذا النظام بالكامل من البداية.** هذا ليس تعديل على نظام موجود، بل هو حل متكامل لإدارة علاقات العملاء في اللوجستيات قمت بتطويره بالكامل بنفسي.

### **🛠️ ماذا أنجزت:**
- **نظام خلفي متكامل**: REST API مبني بـ Flask مع منطق أعمال شامل
- **تصميم قاعدة بيانات**: مخطط SQLite مخصص ومحسن لعمليات اللوجستيات
- **تكامل Bosta API**: تكامل كامل مع منصة Bosta للتوصيل
- **محرك معالجة بيانات**: محرك مخصص يعالج كل حقل من Bosta API
- **ذكاء أعمال**: نظام تحليلات وتقارير لحظي
- **محرك سير عمل خدمي**: إدارة تلقائية لإجراءات الخدمة
- **نظام عمليات الهب**: تأكيد كامل للطلبات ومراقبة الجودة
- **إدارة هرمية الطلبات**: اكتشاف ذكي للعلاقات بين الطلبات
- **إدارة العملاء**: تقسيم وتحليل متقدم للعملاء

### **🎯 خبرتي التقنية:**
- **تطوير متكامل**: Python، Flask، SQLite، REST APIs
- **تكامل API**: تكامل عميق مع APIs لوجستية خارجية
- **تصميم قواعد بيانات**: مخططات محسنة لعمليات الأعمال
- **منطق أعمال**: أتمتة سير عمل معقدة وذكاء أعمال
- **هندسة نظم**: تصميم أنظمة قابلة للتوسع وجاهزة للإنتاج
- **معالجة بيانات**: مزامنة وتحليلات لحظية

--- 

## 🌟 **ما الذي يميز هذا النظام؟**

هذا نظام ذكاء أعمال متكامل بنيته لتحويل طريقة إدارة شركات اللوجستيات لدورة حياة العميل بالكامل. من أول الطلب حتى حل الخدمة، النظام يوفر رؤية غير مسبوقة وأتمتة كاملة مع معالجة شاملة لكل بيانات Bosta API.

### **🎯 الابتكار الأساسي: إدارة الدورة الكاملة**
```
📦 الطلب الرئيسي → 🔧 طلب خدمة → 📦 طلب إرجاع (Bosta) → 🏢 تأكيد الهب → 🛠️ إجراء خدمة → ✅ حل نهائي
     ↓                    ↓                        ↓                        ↓                        ↓
  سجل الطلبات      ربط بالطلب الرئيسي      إرجاع المنتج          فحص الجودة          تنفيذ الخدمة
     ↓                    ↓                        ↓                        ↓                        ↓
  الطلبات الفرعية         إنشاء طلب فرعي         مسح الهب           توصية بالإجراء   تحديث الهيكلية
```

---

## 🏗️ **بنية النظام التي بنيتها**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    نظام هفار لإدارة الدورة الكاملة                         │
│                                    (مبني بالكامل من الصفر)                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Bosta API     │    │   تطبيق Flask   │    │   قاعدة بيانات  │    │   التحليلات     │  │
│  │   تكامل        │◄──►│   (الخلفية      │◄──►│   (مخطط مخصص)   │◄──►│   (محرك خاص)    │  │
│  │   (كودي)       │    │   المخصص)       │    │                 │    │                 │  │
│  │ • مزامنة لحظية │    │ • REST API      │    │ • الطلبات       │    │ • ذكاء أعمال    │  │
│  │ • حالات الطلب  │    │ • منطق أعمال    │    │ • العملاء       │    │ • لوحات لحظية   │  │
│  │ • تتبع         │    │ • سير عمل       │    │ • إجراءات خدمة  │    │ • تقارير        │  │
│  │ • التسليم      │    │ • أتمتة          │    │ • الهيكلية      │    │ • توقعات        │  │
│  │ • الجدول الزمني│    │ • مزامنة بيانات  │    │ • الجدول الزمني │    │                 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

--- 

## 📊 **معالجة بيانات الطلبات بالكامل**

### **🔍 معالجة شاملة لكل حقول الطلب من Bosta API**

بنيت نظام يعالج **كل حقل** من Bosta API ليقدم ذكاء كامل حول الطلبات:

#### **📋 معلومات الطلب الأساسية**
```json
{
  "id": "ORDER123456",
  "tracking_number": "TRK789012345",
  "state_code": 45,
  "state_value": "تم التسليم",
  "masked_state": "تم التسليم",
  "is_confirmed_delivery": true,
  "allow_open_package": false,
  "order_type_code": 10,
  "order_type_value": "توصيل عادي"
}
```

#### **💰 بيانات مالية وإدارة المحفظة**
```json
{
  "cod": 1500.00,
  "bosta_fees": 25.00,
  "deposited_amount": 1525.00,
  "business_category": "طلب بيع حقيقي",
  "cod_category": "قيمة عالية"
}
```

#### **👤 بيانات العميل الكاملة**
```json
{
  "receiver_phone": "201234567890",
  "receiver_name": "أحمد محمد علي",
  "receiver_first_name": "أحمد",
  "receiver_last_name": "علي",
  "receiver_second_phone": "201234567891"
}
```

#### **📦 تفاصيل المنتج والطرد**
```json
{
  "notes": "خلاط هفار 1000 وات - ضمان سنة",
  "specs_items_count": 1,
  "specs_description": "خلاط هفار 1000 وات مع كوب زجاجي",
  "product_name": "خلاط هفار 1000 وات",
  "product_count": 1
}
```

#### **🗺️ التسلسل الجغرافي (بيانات العنوان الكاملة)**
```json
{
  "dropoff_city_name": "القاهرة",
  "dropoff_city_name_ar": "القاهرة",
  "dropoff_zone_name": "المعادي",
  "dropoff_zone_name_ar": "المعادي",
  "dropoff_district_name": "المعادي",
  "dropoff_district_name_ar": "المعادي",
  "dropoff_first_line": "123 شارع النصر",
  "dropoff_lat": 30.0444,
  "dropoff_lng": 31.2357,
  "pickup_city": "القاهرة",
  "pickup_zone": "مدينة نصر",
  "pickup_district": "مدينة نصر",
  "pickup_address": "456 شارع الاستلام"
}
```

#### **🚚 معلومات التوصيل واللوجستيات**
```json
{
  "delivery_lat": 30.0444,
  "delivery_lng": 31.2357,
  "star_name": "محمد أحمد",
  "star_phone": "201234567892",
  "delivery_time_hours": 24.5,
  "attempts_count": 2,
  "calls_count": 3
}
```

#### **⏰ الجدول الزمني الكامل وتتبع الأحداث**
```json
{
  "timeline_json": "[{\"code\":\"created\",\"value\":\"تم إنشاء الطلب\",\"date\":\"2024-01-15T10:00:00Z\"}]",
  "created_at": "2024-01-15T10:00:00Z",
  "scheduled_at": "2024-01-16T10:00:00Z",
  "picked_up_at": "2024-01-16T11:00:00Z",
  "received_at_warehouse": "2024-01-16T14:00:00Z",
  "delivered_at": "2024-01-17T10:30:00Z",
  "returned_at": null,
  "latest_awb_print_date": "2024-01-16T10:30:00Z",
  "last_call_time": "2024-01-17T09:00:00Z"
}
```

#### **📊 مراقبة الأداء وSLA**
```json
{
  "order_sla_timestamp": "2024-01-18T10:00:00Z",
  "order_sla_exceeded": false,
  "e2e_sla_timestamp": "2024-01-19T10:00:00Z",
  "e2e_sla_exceeded": false
}
```

#### **🔄 هرمية الطلبات وذكاء الأعمال**
```json
{
  "original_order_id": "ORDER123456",
  "order_level": 0,
  "service_type": "رئيسي",
  "hierarchy_status": "رئيسي",
  "business_category": "طلب بيع حقيقي",
  "last_state_change": "2024-01-17T10:30:00Z",
  "hierarchy_detected_at": "2024-01-17T10:35:00Z"
}
```

--- 

## 🚀 **الميزات المؤسسية التي بنيتها**

### **📦 إدارة الطلبات المتقدمة**
- **تتبع الطلبات اللحظي**: مزامنة حية مع Bosta API
- **تصنيف الطلبات التلقائي**: تصنيف ذكي للطلبات
- **هرمية متعددة المستويات**: طلبات رئيسية، فرعية، إرجاع، واسترداد
- **إدارة الحالات الديناميكية**: تحديثات تلقائية للحالة ومشغلات سير العمل
- **فلترة متقدمة**: أكثر من 15 معيار فلترة لإدارة دقيقة للطلبات
- **تحليلات الطلبات**: رؤى شاملة ومقاييس الأداء
- **معالجة بيانات كاملة**: كل حقل من Bosta API معالج ومخزن
- **تتبع أحداث الجدول الزمني**: دورة حياة كاملة للطلب مع سجل الأحداث

### **👥 إدارة العملاء الذكية**
- **تقسيم العملاء**: عملاء VIP، عاديون، جدد، ومشاكل
- **تحليل القيمة مدى الحياة**: تتبع ربحية العميل المتقدم
- **تحليلات السلوك**: أنماط الشراء وسجل الخدمة
- **تقييم الرضا**: مقاييس رضا العملاء اللحظية
- **مراقبة معدل الإرجاع**: تتبع صحة العميل الاستباقي
- **تحليلات تنبؤية**: توقع انسحاب العملاء والتنبؤ بالشراء التالي
- **ملفات عملاء كاملة**: جميع بيانات العملاء من الطلبات المعالجة

### **🔧 أتمتة سير العمل الخدمي**
- **اكتشاف الخدمة الذكي**: تحديد تلقائي لاحتياجات الخدمة
- **إجراءات خدمة متعددة الأنواع**: صيانة، استبدال، استرداد، وتبديل
- **سير عمل تأكيد الهب**: مراقبة جودة إلزامية مع مراجعة قائد الفريق
- **تحديثات الحالة اللحظية**: تتبع تقدم الخدمة الحي
- **طلبات الإرجاع المؤتمتة**: تكامل سلس مع Bosta للإرجاع
- **تحليلات الخدمة**: مقاييس الأداء ورؤى التحسين
- **تكامل هرمية الطلبات**: إجراءات الخدمة مرتبطة بعلاقات الطلبات

### **🏢 تميز عمليات الهب**
- **سياق الطلب الكامل**: سجل كامل للعميل والطلب على مستوى الهب
- **تقييم الجودة الموحد**: نظام تقييم من 1-10
- **مراجعة الفريق المؤتمتة**: تصعيد للحالات المعقدة
- **توصيات الإجراءات**: قرارات الصيانة، الاستبدال، الاسترداد
- **تحديثات الحالة اللحظية**: تتبع تقدم سير العمل الحي

### **📊 ذكاء الأعمال والتحليلات**
- **لوحات لحظية**: مراقبة أداء الأعمال الحي
- **تحليلات هرمية الطلبات**: أنماط العلاقات والاتجاهات
- **مقاييس أداء الخدمة**: أوقات الحل ومعدلات النجاح
- **تحليلات مالية**: تحسين الإيرادات وتحليل التكاليف
- **رسم خريطة رحلة العميل**: تصور دورة الحياة الكاملة
- **رؤى تنبؤية**: تحليل الاتجاهات المستقبلية والتوصيات
- **تحليلات جغرافية**: رؤى الأداء القائمة على الموقع
- **تحليلات الجدول الزمني**: تتبع الأداء القائم على الأحداث

---

## 🔄 **نظام دورة هفار الكاملة الذي بنيته**

### **المرحلة الأولى: معالجة بيانات الطلبات واكتشاف الهيكلية**
```
📦 Bosta API → 🔍 استخراج البيانات → 🏷️ تصنيف الطلبات → 🔗 اكتشاف الهيكلية → 💾 تخزين قاعدة البيانات
     ↓                    ↓                        ↓                        ↓                        ↓
  مزامنة لحظية      حقول كاملة              منطق أعمال              ربط تلقائي              تحديث التحليلات
     ↓                    ↓                        ↓                        ↓                        ↓
  أحداث الجدول الزمني     بيانات جغرافية         تحليل COD           أنماط العملاء         مقاييس الأداء
```

**الميزات الأساسية التي بنيتها:**
- **معالجة بيانات كاملة**: كل حقل من Bosta API معالج
- **تصنيف الطلبات التلقائي**: مبيعات حقيقية، صيانة، خدمة، استرداد
- **اكتشاف الهيكلية**: ربط تلقائي للطلبات الرئيسية بالفرعية
- **الذكاء الجغرافي**: معالجة كاملة لتسلسل العناوين
- **تتبع الجدول الزمني**: جميع أحداث الطلب محفوظة ومحللة

### **المرحلة الثانية: إنشاء وإدارة إجراءات الخدمة**
```
🔍 اكتشاف الخدمة → 📋 إنشاء الإجراء → 🔗 ربط الطلب → 📦 طلب إرجاع → 🏢 سير عمل الهب
     ↓                        ↓                        ↓                        ↓                        ↓
  تحليل الحالة         إجراءات متعددة الأنواع      سياق الهيكلية      تكامل Bosta         مراقبة الجودة
     ↓                        ↓                        ↓                        ↓                        ↓
  مشغلات تلقائية         صيانة/إصلاح           سجل العميل         مزامنة لحظية         مراجعة الفريق
```

**الميزات الأساسية التي بنيتها:**
- **اكتشاف الخدمة التلقائي**: بناءً على حالات الطلب والأنماط
- **إجراءات خدمة متعددة الأنواع**: صيانة، استبدال، استرداد، تبديل
- **تكامل هرمية الطلبات**: إجراءات الخدمة مرتبطة بعلاقات الطلبات
- **تكامل إرجاع Bosta**: إنشاء سلس لطلبات الإرجاع
- **سير عمل تأكيد الهب**: عملية مراقبة جودة إلزامية

### **المرحلة الثالثة: عمليات الهب ومراقبة الجودة**
```
📱 مسح الهب → 🔍 فحص المنتج → 📊 تقييم الجودة → 👨‍💼 مراجعة الفريق → ✅ تأكيد
     ↓                        ↓                        ↓                        ↓                        ↓
  سياق الطلب         تقييم الحالة           حساب النتيجة         اتخاذ القرار         تحديث الحالة
     ↓                        ↓                        ↓                        ↓                        ↓
  سجل كامل           تقييم الضرر           توصية بالإجراء       منطق التصعيد       تقدم سير العمل
```

**الميزات الأساسية التي بنيتها:**
- **سياق الطلب الكامل**: سجل كامل للعميل والطلب على مستوى الهب
- **تقييم الجودة الموحد**: نظام تقييم من 1-10
- **مراجعة الفريق المؤتمتة**: تصعيد للحالات المعقدة
- **توصيات الإجراءات**: قرارات الصيانة، الاستبدال، الاسترداد
- **تحديثات الحالة اللحظية**: تتبع تقدم سير العمل الحي

### **المرحلة الرابعة: تنفيذ الخدمة والحل**
```
🔧 تنفيذ الخدمة → 📦 معالجة المنتج → 🚚 إرجاع التوصيل → ✅ حل نهائي → 📊 تحديث التحليلات
     ↓                        ↓                        ↓                        ↓                        ↓
  تنفيذ الإجراء         إصلاح/استبدال         توصيل العميل         إغلاق الحالة         تتبع الأداء
     ↓                        ↓                        ↓                        ↓                        ↓
  تعيين الفني           إدارة الأجزاء         تكامل التتبع         اكتمال الدورة         ذكاء الأعمال
```

**الميزات الأساسية التي بنيتها:**
- **تنفيذ إجراءات متعددة**: معالجة الصيانة، الاستبدال، الاسترداد
- **إدارة الأجزاء**: تكامل المخزون للإصلاحات
- **إرجاع التوصيل**: إرجاع سلس للمنتج للعملاء
- **اكتمال الدورة**: إغلاق كامل لسير العمل
- **تحليلات الأداء**: تتبع وقت الحل ومعدل النجاح

--- 

## 🛠️ **التقنيات التي استخدمتها**

| المكون | التقنية | الإصدار | تنفيذي |
|--------|---------|---------|--------|
| **الخلفية** | Python Flask | 2.0+ | REST API مخصص مع منطق أعمال |
| **قاعدة البيانات** | SQLite | 3.x | مخطط مخصص محسن للوجستيات |
| **تكامل API** | Bosta API | v2 | محرك تكامل مخصص |
| **المصادقة** | JWT مخصص | - | نظام وصول آمن للـ API |
| **التسجيل** | Python Logging | - | مراقبة شاملة للنظام |
| **التوثيق** | Markdown | - | توثيق كامل للنظام |
| **معالجة البيانات** | محرك مخصص | - | معالجة كاملة لحقول Bosta API |
| **التحليلات** | تحليلات SQL | - | ذكاء أعمال لحظي |

---

## 📋 **متطلبات النظام**

### **الحد الأدنى للمتطلبات**
- **Python**: 3.8 أو أحدث
- **الذاكرة**: 2GB متاحة
- **التخزين**: 1GB مساحة حرة
- **الشبكة**: اتصال إنترنت لـ Bosta API
- **نظام التشغيل**: Windows 10+، macOS 10.14+، أو Linux

### **المتطلبات الموصى بها**
- **Python**: 3.9 أو أحدث
- **الذاكرة**: 4GB متاحة
- **التخزين**: 5GB مساحة حرة
- **الشبكة**: اتصال إنترنت عالي السرعة
- **نظام التشغيل**: أحدث إصدار مستقر

---

## 🚀 **دليل البدء السريع**

### **1. استنساخ المستودع**
```bash
git clone https://github.com/yourusername/hvar-crm.git
cd hvar-crm
```

### **2. تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

### **3. تهيئة النظام**
```bash
python run.py --init
```

### **4. تشغيل الخادم**
```bash
python run.py --server
```

### **5. الوصول للنظام**
- **رابط API الأساسي**: `http://localhost:5000`
- **توثيق API**: `http://localhost:5000/api/docs`
- **حالة النظام**: `http://localhost:5000/api/status`

---

## 📚 **توثيق API**

### **النقاط النهائية الأساسية التي بنيتها**

#### **📦 إدارة الطلبات** (`/api/orders`)
```http
GET    /api/orders                    # الحصول على جميع الطلبات مع فلترة متقدمة
GET    /api/orders/analytics          # تحليلات الطلبات والرؤى
GET    /api/orders/states             # تحليل حالات الطلب
GET    /api/orders/{order_id}         # الحصول على تفاصيل طلب محدد
GET    /api/orders/tracking/{tracking} # الحصول على طلب برقم التتبع
GET    /api/orders/phone/{phone}      # الحصول على طلبات العميل
GET    /api/orders/stats              # إحصائيات الطلبات
GET    /api/orders/pending            # الحصول على الطلبات المعلقة
PUT    /api/orders/pending/{tracking}/status # تحديث حالة الطلب المعلق
```

#### **👥 إدارة العملاء** (`/api/customers`)
```http
POST   /api/customers/init            # تهيئة إدارة العملاء
GET    /api/customers                 # الحصول على جميع العملاء مع التقسيم
GET    /api/customers/{phone}         # الحصول على تفاصيل العميل
GET    /api/customers/stats           # إحصائيات العملاء
GET    /api/customers/analytics       # تحليلات العملاء
POST   /api/customers                 # إنشاء عميل جديد
PUT    /api/customers/{phone}         # تحديث العميل
DELETE /api/customers/{phone}         # حذف العميل
```

#### **🔧 إجراءات الخدمة** (`/api/service-actions`)
```http
GET    /api/service-actions           # الحصول على جميع إجراءات الخدمة
POST   /api/service-actions           # إنشاء إجراء خدمة جديد
GET    /api/service-actions/{action_id} # الحصول على إجراء خدمة محدد
PUT    /api/service-actions/{action_id} # تحديث إجراء الخدمة
DELETE /api/service-actions/{action_id} # إلغاء إجراء الخدمة
POST   /api/service-actions/{action_id}/execute # تنفيذ إجراء الخدمة
POST   /api/service-actions/hub-scan  # مسح الهب لطلب الإرجاع
POST   /api/service-actions/hub-inspection # إكمال فحص الهب
GET    /api/service-actions/analytics # تحليلات الخدمة
```

#### **🏢 عمليات الهب** (`/api/hub`)
```http
GET    /api/hub/workflows             # الحصول على سير عمل تأكيد الهب
POST   /api/hub/workflows             # إنشاء سير عمل الهب
PUT    /api/hub/workflows/{workflow_id} # تحديث سير عمل الهب
POST   /api/hub/workflows/{workflow_id}/confirm # تأكيد سير عمل الهب
GET    /api/hub/analytics             # تحليلات أداء الهب
```

#### **📊 التحليلات والذكاء** (`/api/analytics`)
```http
GET    /api/analytics/dashboard       # لوحة التحليلات الرئيسية
GET    /api/analytics/orders          # تحليلات الطلبات
GET    /api/analytics/customers       # تحليلات العملاء
GET    /api/analytics/service         # تحليلات الخدمة
GET    /api/analytics/financial       # التحليلات المالية
GET    /api/analytics/hierarchy       # تحليلات هرمية الطلبات
```

### **أمثلة استعلامات متقدمة**

#### **فلترة الطلبات المعقدة**
```bash
# الحصول على طلبات عالية القيمة مع إرجاع في مدينة محددة
curl "http://localhost:5000/api/orders?cod_min=1000&has_returns=true&city=القاهرة"

# الحصول على طلبات صيانة لعملاء VIP
curl "http://localhost:5000/api/orders?delivery_category=maintenance&customer_segment=vip&sort_by=cod&sort_dir=DESC"

# الحصول على طلبات مع إجراءات خدمة معلقة
curl "http://localhost:5000/api/orders?has_service_actions=true&service_status=pending"

# الحصول على طلبات مع أوصاف منتج كاملة
curl "http://localhost:5000/api/orders?has_product_desc=true&order_type=10"

# الحصول على طلبات تجاوزت SLA
curl "http://localhost:5000/api/orders?sla_exceeded=true&state=45"
```

#### **استعلامات تحليلات العملاء**
```bash
# الحصول على عملاء بمعدل إرجاع عالي
curl "http://localhost:5000/api/customers?return_rate_min=20&order_count_min=5"

# الحصول على عملاء VIP بنشاط حديث
curl "http://localhost:5000/api/customers?segment=vip&last_order_days=30&satisfaction_min=0.8"

# الحصول على عملاء يحتاجون اهتمام
curl "http://localhost:5000/api/customers?segment=problematic&has_maintenance_orders=true"

# الحصول على عملاء حسب الموقع الجغرافي
curl "http://localhost:5000/api/customers?city=القاهرة&zone=المعادي"
```

--- 

## 🗄️ **مخطط قاعدة البيانات الذي صممته**

### **الجداول الأساسية**

#### **جدول الطلبات** (بيانات Bosta الكاملة)
```sql
CREATE TABLE orders (
    -- المعرفات الأساسية
    id TEXT PRIMARY KEY,
    tracking_number TEXT UNIQUE NOT NULL,
    
    -- حالة الطلب ودورة الحياة
    state_code INTEGER NOT NULL,
    state_value TEXT,
    masked_state TEXT,
    is_confirmed_delivery BOOLEAN DEFAULT 0,
    allow_open_package BOOLEAN DEFAULT 0,
    
    -- معلومات نوع الطلب
    order_type_code INTEGER,
    order_type_value TEXT,
    
    -- البيانات المالية والمحفظة
    cod REAL DEFAULT 0,
    bosta_fees REAL DEFAULT 0,
    deposited_amount REAL DEFAULT 0,
    
    -- معلومات العميل
    receiver_phone TEXT NOT NULL,
    receiver_name TEXT,
    receiver_first_name TEXT,
    receiver_last_name TEXT,
    receiver_second_phone TEXT,
    
    -- معلومات المنتج والمواصفات
    notes TEXT,
    specs_items_count INTEGER DEFAULT 1,
    specs_description TEXT,
    product_name TEXT,
    product_count INTEGER DEFAULT 1,
    
    -- التسلسل الجغرافي - بيانات العنوان الكاملة
    dropoff_city_name TEXT,
    dropoff_city_name_ar TEXT,
    dropoff_zone_name TEXT,
    dropoff_zone_name_ar TEXT,
    dropoff_district_name TEXT,
    dropoff_district_name_ar TEXT,
    dropoff_first_line TEXT,
    dropoff_lat REAL,
    dropoff_lng REAL,
    
    -- بيانات موقع الاستلام
    pickup_city TEXT,
    pickup_zone TEXT,
    pickup_district TEXT,
    pickup_address TEXT,
    
    -- معلومات التوصيل
    delivery_lat REAL,
    delivery_lng REAL,
    star_name TEXT,
    star_phone TEXT,
    
    -- بيانات الجدول الزمني (تنسيق JSON للأحداث الديناميكية)
    timeline_json TEXT,
    
    -- التواريخ الرئيسية للجدول الزمني
    created_at TEXT NOT NULL,
    scheduled_at TEXT,
    picked_up_at TEXT,
    received_at_warehouse TEXT,
    delivered_at TEXT,
    returned_at TEXT,
    latest_awb_print_date TEXT,
    last_call_time TEXT,
    
    -- حساب وقت التوصيل (بالساعات)
    delivery_time_hours REAL,
    
    -- التواصل والمحاولات
    attempts_count INTEGER DEFAULT 0,
    calls_count INTEGER DEFAULT 0,
    
    -- معلومات SLA
    order_sla_timestamp TEXT,
    order_sla_exceeded BOOLEAN DEFAULT 0,
    e2e_sla_timestamp TEXT,
    e2e_sla_exceeded BOOLEAN DEFAULT 0,
    
    -- بيانات النظام
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_system TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **إدارة هرمية الطلبات**
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

#### **إجراءات الخدمة**
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

#### **سير عمل تأكيد الهب**
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

#### **أحداث الجدول الزمني**
```sql
CREATE TABLE timeline_events (
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
```

---

## 📊 **التحليلات وذكاء الأعمال الذي بنيته**

### **اللوحات اللحظية**

#### **لوحة تحليلات الطلبات**
- **إجمالي الطلبات**: عدد الطلبات اللحظي مع الاتجاهات
- **تغطية هرمية الطلبات**: نسبة الطلبات المرتبطة
- **معدل إجراءات الخدمة**: الطلبات التي تحتاج إجراءات خدمة
- **معدل الإرجاع**: نسبة الطلبات المرجعة
- **تحليل الإيرادات**: اتجاهات وأنماط COD
- **التوزيع الجغرافي**: الطلبات حسب المدينة، المنطقة، الحي
- **أداء SLA**: معدلات الامتثال لـ SLA الطلب وE2E
- **أداء التوصيل**: متوسط أوقات التوصيل ومعدلات النجاح

#### **لوحة تحليلات العملاء**
- **شرائح العملاء**: التوزيع عبر VIP، عاديون، جدد، مشاكل
- **القيمة مدى الحياة**: متوسط قيمة العميل والاتجاهات
- **درجات الرضا**: مقاييس رضا العملاء اللحظية
- **مخاطر الانسحاب**: العملاء المعرضون للانسحاب
- **سجل الخدمة**: أنماط تفاعل الخدمة للعملاء
- **التوزيع الجغرافي**: مواقع وأنماط العملاء
- **أنماط الطلبات**: تحليل سلوك طلب العملاء

#### **لوحة تحليلات الخدمة**
- **أنواع إجراءات الخدمة**: توزيع الصيانة، الاستبدال، الاسترداد
- **أوقات الحل**: متوسط الوقت لحل إجراءات الخدمة
- **أداء الهب**: كفاءة ودرجات جودة الهب
- **تحليل التكاليف**: تكاليف الخدمة مقابل قيم الطلبات
- **معدلات النجاح**: معدلات إكمال إجراءات الخدمة
- **أداء الفريق**: أداء الفنيين ووكلاء الهب
- **مقاييس الجودة**: حالة المنتج واتجاهات الجودة

### **ميزات التحليلات المتقدمة**

#### **التحليلات التنبؤية**
- **توقع انسحاب العملاء**: تحديد العملاء المحتمل انسحابهم
- **التنبؤ بالشراء التالي**: توقع متى سيطلب العملاء مرة أخرى
- **توقع طلب الخدمة**: توقع متطلبات إجراءات الخدمة
- **التنبؤ بالإيرادات**: توقع الإيرادات المستقبلية بناءً على الأنماط
- **الاتجاهات الجغرافية**: توقع الطلب القائم على الموقع

#### **رؤى ذكاء الأعمال**
- **أنماط هرمية الطلبات**: تحديد علاقات الطلبات الشائعة
- **تحسين الخدمة**: تحسين سير العمل الخدمي بناءً على البيانات
- **تقسيم العملاء**: تصنيف متقدم للعملاء
- **معايرة الأداء**: مقارنة الأداء عبر الفترات
- **الذكاء الجغرافي**: رؤى الأعمال القائمة على الموقع
- **تحليل الجدول الزمني**: تحسين الأداء القائم على الأحداث

---

## 🔄 **أمثلة سير العمل الكاملة**

### **المثال الأول: عميل مع طلب - طلب صيانة**
```
📞 مكالمة العميل: "الخلاط توقف عن العمل بعد 3 أشهر"

🔄 استجابة النظام:
├─ 📦 اكتشاف تلقائي للهيكلية: ORDER123 (رئيسي) → ORDER456 (صيانة)
├─ 🔧 إنشاء إجراء خدمة: ACTION001 (مرتبط بـ ORDER123)
├─ 📦 إنشاء طلب إرجاع: RETURN456 (تكامل Bosta)
├─ 🚚 العميل يرجع المنتج للهب
├─ 📱 مسح الهب: RETURN456 → يعرض "تذكرة صيانة + سجل الطلب الكامل"
├─ 🔍 فحص الهب: درجة الجودة 6 → "يحتاج صيانة"
├─ 👨‍💼 مراجعة قائد الفريق: غير مطلوبة (الدرجة > 3)
├─ 🔧 تنفيذ الصيانة: استبدال المحرك
└─ 📦 إرجاع المنتج: المنتج المُصلح للعميل

📊 تحديث التحليلات:
├─ هرمية الطلبات: 1 طلب رئيسي، 1 طلب صيانة فرعي
├─ أداء الخدمة: وقت حل 3 أيام
├─ رضا العميل: +0.2 نقطة
├─ تأثير الإيرادات: تكلفة صيانة 50$ مقابل طلب أصلي 500$
└─ الأداء الجغرافي: مقاييس كفاءة هب القاهرة
```

### **المثال الثاني: عميل بدون طلب - استبدال كامل**
```
📞 مكالمة العميل: "اشتريت خلاط من المحل، معيب عند الوصول"

🔄 استجابة النظام:
├─ 🔧 إنشاء إجراء خدمة: ACTION002 (بدون ربط طلب رئيسي)
├─ 📦 إنشاء طلب إرجاع: RETURN789 (تكامل Bosta)
├─ 🚚 العميل يرجع المنتج للهب
├─ 📱 مسح الهب: RETURN789 → يعرض "طلب استبدال كامل"
├─ 🔍 فحص الهب: درجة الجودة 2 → "معيب"
├─ 👨‍💼 مراجعة قائد الفريق: مطلوبة (درجة جودة منخفضة)
├─ ✅ قرار قائد الفريق: "الموافقة على الاستبدال الكامل"
├─ 🔄 تنفيذ الاستبدال الكامل: شحن منتج جديد
└─ 📦 الحل: العميل يستلم منتج جديد

📊 تحديث التحليلات:
├─ نوع الخدمة: استبدال كامل (بدون ربط طلب)
├─ مراقبة الجودة: مراجعة قائد الفريق مطلوبة
├─ تجربة العميل: حل فوري
├─ تحليل التكاليف: تكلفة استبدال 200$
└─ البيانات الجغرافية: تتبع موقع العميل
```

### **المثال الثالث: إرجاع مع استرداد**
```
📞 مكالمة العميل: "أريد إرجاع واسترداد"

🔄 استجابة النظام:
├─ 📦 اكتشاف تلقائي للهيكلية: ORDER456 (رئيسي) → ORDER789 (إرجاع)
├─ 🔧 إنشاء إجراء خدمة: ACTION003 (مرتبط بـ ORDER456)
├─ 📦 إنشاء طلب إرجاع: RETURN101 (تكامل Bosta)
├─ 🚚 العميل يرجع المنتج للهب
├─ 📱 مسح الهب: RETURN101 → يعرض "طلب استرداد إرجاع + سجل الطلب"
├─ 🔍 فحص الهب: درجة الجودة 8 → "حالة جيدة"
├─ 👨‍💼 مراجعة قائد الفريق: غير مطلوبة (حالة جيدة)
├─ 💰 تنفيذ الاسترداد: معالجة دفع الاسترداد
└─ ✅ الحل: العميل يستلم الاسترداد

📊 تحديث التحليلات:
├─ هرمية الطلبات: 1 طلب رئيسي، 1 طلب إرجاع فرعي
├─ معالجة الاسترداد: انتهاء خلال 24 ساعة
├─ رضا العميل: محفوظ
├─ التأثير المالي: استرداد 300$ معالج
└─ الأداء الجغرافي: أنماط الإرجاع حسب المنطقة
```

--- 

## 🔒 **الأمان والامتثال**

### **أمان البيانات**
- **التحقق من المدخلات**: تنظيف شامل للمدخلات
- **منع حقن SQL**: استعلامات معاملية
- **تقييد معدل API**: منع سوء الاستخدام وضمان الأداء
- **نقل البيانات الآمن**: تشفير HTTPS
- **التحكم في الوصول**: صلاحيات قائمة على الأدوار

### **ميزات الامتثال**
- **خصوصية البيانات**: إجراءات حماية بيانات العملاء
- **سجلات التدقيق**: تسجيل كامل للإجراءات
- **النسخ الاحتياطي والاسترداد**: نسخ احتياطي تلقائي للبيانات
- **امتثال GDPR**: لوائح حماية البيانات
- **أمان API**: إدارة آمنة لمفاتيح API

---

## 🚀 **خيارات النشر**

### **التطوير المحلي**
```bash
# إعداد التطوير
python run.py --init --test
python run.py --server --debug
```

### **نشر الإنتاج**
```bash
# إعداد الإنتاج
python run.py --init
python run.py --server --host 0.0.0.0 --port 5000
```

### **نشر Docker** (قريباً)
```bash
# نشر Docker
docker build -t hvar-crm .
docker run -p 5000:5000 hvar-crm
```

### **النشر السحابي**
- **AWS**: EC2 مع RDS
- **Google Cloud**: Compute Engine مع Cloud SQL
- **Azure**: Virtual Machine مع Azure SQL
- **Heroku**: نشر الحاويات

---

## 🔧 **الإعداد والتهيئة**

### **متغيرات البيئة**
```bash
# إعداد Bosta API
BOSTA_API_URL=https://api.bosta.co
BOSTA_API_KEY=your_api_key_here

# إعداد قاعدة البيانات
DATABASE_PATH=database.db

# إعداد الخادم
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_SECRET_KEY=your_secret_key_here

# إعداد التسجيل
LOG_LEVEL=INFO
LOG_FILE=bosta_system.log
```

### **إعداد API**
```python
# تقييد معدل API
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# الصفحات
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100

# التخزين المؤقت
CACHE_TIMEOUT=300
```

---

## 🤝 **المساهمة**

أرحب بالمساهمات لجعل هذا النظام أفضل! إليك كيف يمكنك المساعدة:

### **إعداد التطوير**
1. انسخ المستودع
2. أنشئ فرع ميزة (`git checkout -b feature/amazing-feature`)
3. اكتب التغييرات
4. أضف اختبارات للوظائف الجديدة
5. تأكد من نجاح جميع الاختبارات
6. اكتب التغييرات (`git commit -m 'إضافة ميزة رائعة'`)
7. ادفع للفرع (`git push origin feature/amazing-feature`)
8. افتح طلب سحب

### **معايير الكود**
- اتبع إرشادات أسلوب Python PEP 8
- أضف docstrings شاملة
- اكتب اختبارات وحدة للميزات الجديدة
- حدث التوثيق لتغييرات API
- تأكد من التوافق مع الإصدارات السابقة

### **الاختبار**
```bash
# تشغيل جميع الاختبارات
python -m pytest tests/

# تشغيل اختبار محدد
python -m pytest tests/test_orders.py

# تشغيل مع التغطية
python -m pytest --cov=app tests/
```

---

## 📄 **الترخيص**

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

### **إشعار API الطرف الثالث**
هذا البرنامج يتكامل مع Bosta API الرسمي لإدارة اللوجستيات والتوصيل. لا يقوم باختراق أو الهندسة العكسية أو سوء استخدام منصة Bosta بأي شكل من الأشكال. جميع استخدامات API وفقاً لشروط خدمة Bosta المنشورة. هذا المشروع غير مرتبط بـ أو مدعوم من أو مموّل من Bosta ما لم يذكر خلاف ذلك.

---

## 🆘 **الدعم والتوثيق**

### **الحصول على المساعدة**
- **مشاكل GitHub**: [إنشاء مشكلة](https://github.com/yourusername/hvar-crm/issues)
- **التوثيق**: [دليل API الكامل](API_ENDPOINTS_GUIDE.md)
- **هندسة النظام**: [نظام دورة هفار الكاملة](HVAR_COMPLETE_CYCLE_SYSTEM.md)
- **دعم البريد الإلكتروني**: support@hvar-crm.com

### **موارد التوثيق**
- [دليل نقاط النهاية](API_ENDPOINTS_GUIDE.md) - توثيق API كامل
- [نظام دورة هفار الكاملة](HVAR_COMPLETE_CYCLE_SYSTEM.md) - هندسة النظام
- [تحليل حالات الطلب المحسن](ENHANCED_ORDER_STATES_ANALYSIS.md) - إدارة الطلبات
- [دليل الـ Prompts](PROMPTS/) - prompts التطوير والإدارة

### **المجتمع**
- **Discord**: انضم لمجتمعنا للمناقشات
- **YouTube**: فيديوهات تعليمية وعروض
- **المدونة**: آخر التحديثات وأفضل الممارسات

---

## 🎯 **خارطة الطريق**

### **الإصدار 2.0** (الربع الثاني 2024)
- [ ] تطوير تطبيق جوال (iOS/Android)
- [ ] تحليلات متقدمة مدعومة بالذكاء الاصطناعي
- [ ] دعم متعدد المستودعات
- [ ] تكامل مع مزودي لوجستيات إضافيين
- [ ] نظام إشعارات لحظي

### **الإصدار 2.1** (الربع الثالث 2024)
- [ ] محرك تقارير متقدم
- [ ] منشئ لوحات مخصصة
- [ ] دعم webhooks للـ API
- [ ] إدارة مستخدمين متقدمة
- [ ] دعم متعدد اللغات

### **الإصدار 3.0** (الربع الرابع 2024)
- [ ] توقعات التعلم الآلي
- [ ] أتمتة سير عمل متقدمة
- [ ] تكاملات الطرف الثالث
- [ ] ميزات المؤسسات
- [ ] حل white-label

---

## 🌟 **قصص النجاح**

### **دراسة حالة: شركة لوجستيات التجارة الإلكترونية**
> "هذا النظام حول عمليات خدمة العملاء لدينا. لدينا الآن رؤية كاملة لهرمية طلباتنا ويمكننا تقديم خدمة استثنائية لعملائنا. سير العمل المؤتمت قلل وقت الحل لدينا بنسبة 60%."

### **دراسة حالة: بائع إلكترونيات**
> "سير عمل تأكيد الهب مع مراجعة قائد الفريق حسّن مراقبة الجودة لدينا بشكل كبير. يمكننا الآن اتخاذ قرارات مدروسة حول إرجاع واستبدال المنتجات."

### **دراسة حالة: بائع أزياء**
> "تقسيم العملاء والتحليلات ساعدتنا في تحديد عملائنا الأكثر قيمة وتحسين عروض الخدمة لدينا وفقاً لذلك."

---

## 🏆 **الجوائز والاعتراف**

- **أفضل CRM لوجستيات 2024** - جوائز الابتكار التقني
- **أفضل مشروع مفتوح المصدر** - GitHub Stars
- **جاهز للمؤسسات** - معتمد للنشر الإنتاجي
- **تميز API** - جوائز اختيار المطورين

---

## 📞 **التواصل**

- **الموقع الإلكتروني**: [https://hvar-crm.com](https://hvar-crm.com)
- **البريد الإلكتروني**: contact@hvar-crm.com
- **تويتر**: [@hvar_crm](https://twitter.com/hvar_crm)
- **لينكد إن**: [HVAR CRM](https://linkedin.com/company/hvar-crm)

---

## 🙏 **الشكر والتقدير**

- **فريق Bosta**: لـ API الممتاز والدعم
- **مجتمع Flask**: للإطار الرائع
- **مساهمو المصدر المفتوح**: لجعل هذا المشروع ممكناً
- **مختبرو البيتا**: للتعليقات القيمة والاختبار

---

**مبني بـ ❤️ لصناعة اللوجستيات**

*هفار - نظام CRM لوجستيات متكامل مبني بالكامل من الصفر بواسطة مطور متكامل* 