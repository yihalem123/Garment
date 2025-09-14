# Garment Business Management System API

A comprehensive REST API for managing garment manufacturing business operations including purchases, production, transfers, sales, inventory, and analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQLite (for local development)
- Redis (for background tasks)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd garment
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start the application**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 🔐 Authentication

All endpoints require authentication using JWT tokens.

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@garment.com&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /auth/users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "admin@garment.com",
  "full_name": "System Administrator",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 📦 Products & Raw Materials

### Get All Products
```http
GET /products/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "T-shirt Cotton",
    "sku": "MGF-003-mcnt",
    "description": "Cotton T-shirt",
    "category": "T-shirt",
    "unit_price": 240.0,
    "cost_price": 200.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get All Raw Materials
```http
GET /raw-materials/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Dryer",
    "description": "Fabric dryer",
    "unit": "roll",
    "unit_price": 750.0,
    "supplier": "Tigist",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## 📊 Inventory Management

### Get Stock Items
```http
GET /inventory/stocks
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "shop_id": 1,
    "item_type": "product",
    "product_id": 1,
    "raw_material_id": null,
    "quantity": 100.0,
    "reserved_quantity": 0.0,
    "min_stock_level": 10.0,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Stock Movements
```http
GET /inventory/stock-movements
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "shop_id": 1,
    "item_type": "product",
    "product_id": 1,
    "raw_material_id": null,
    "quantity": 10.0,
    "reason": "sale",
    "reference_id": 1,
    "reference_type": "sale",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Adjust Stock
```http
POST /inventory/stocks/adjust
Authorization: Bearer <token>
Content-Type: application/json

{
  "shop_id": 1,
  "item_type": "product",
  "product_id": 1,
  "quantity": 50.0,
  "reason": "adjustment",
  "notes": "Stock adjustment"
}
```

## 🛒 Purchase Management

### Create Purchase
```http
POST /purchases/
Authorization: Bearer <token>
Content-Type: application/json

{
  "supplier_name": "Tigist Supplier",
  "supplier_invoice": "INV-001",
  "purchase_date": "2024-01-01",
  "notes": "Raw material purchase",
  "purchase_lines": [
    {
      "raw_material_id": 1,
      "quantity": 10.0,
      "unit_price": 750.0,
      "total_price": 7500.0
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "supplier_name": "Tigist Supplier",
  "supplier_invoice": "INV-001",
  "status": "received",
  "total_amount": 7500.0,
  "purchase_date": "2024-01-01",
  "notes": "Raw material purchase",
  "created_at": "2024-01-01T00:00:00Z",
  "purchase_lines": [
    {
      "id": 1,
      "purchase_id": 1,
      "raw_material_id": 1,
      "quantity": 10.0,
      "unit_price": 750.0,
      "total_price": 7500.0
    }
  ]
}
```

### Get All Purchases
```http
GET /purchases/
Authorization: Bearer <token>
```

## 🏭 Production Management

### Create Production Run
```http
POST /production/
Authorization: Bearer <token>
Content-Type: application/json

{
  "run_number": "PROD-001",
  "planned_quantity": 100,
  "labor_cost": 500.0,
  "overhead_cost": 200.0,
  "start_date": "2024-01-01",
  "notes": "T-shirt production",
  "production_lines": [
    {
      "product_id": 1,
      "planned_quantity": 100
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "run_number": "PROD-001",
  "planned_quantity": 100,
  "labor_cost": 500.0,
  "overhead_cost": 200.0,
  "status": "planned",
  "start_date": "2024-01-01",
  "notes": "T-shirt production",
  "created_at": "2024-01-01T00:00:00Z",
  "production_lines": [
    {
      "id": 1,
      "production_run_id": 1,
      "product_id": 1,
      "planned_quantity": 100
    }
  ],
  "production_consumptions": []
}
```

### Complete Production Run
```http
POST /production/{production_run_id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "actual_quantities": {
    "1": 95
  }
}
```

## 🚚 Transfer Management

### Create Transfer
```http
POST /transfers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "transfer_number": "TRF-001",
  "from_shop_id": 1,
  "to_shop_id": 2,
  "transfer_date": "2024-01-01",
  "notes": "Transfer to shop",
  "transfer_lines": [
    {
      "product_id": 1,
      "quantity": 50,
      "unit_cost": 200.0,
      "total_cost": 10000.0
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "transfer_number": "TRF-001",
  "from_shop_id": 1,
  "to_shop_id": 2,
  "status": "pending",
  "transfer_date": "2024-01-01",
  "notes": "Transfer to shop",
  "created_at": "2024-01-01T00:00:00Z",
  "transfer_lines": [
    {
      "id": 1,
      "transfer_id": 1,
      "product_id": 1,
      "quantity": 50,
      "unit_cost": 200.0,
      "total_cost": 10000.0
    }
  ]
}
```

### Receive Transfer
```http
POST /transfers/{transfer_id}/receive
Authorization: Bearer <token>
```

## 💰 Sales Management

### Create Sale
```http
POST /sales/
Authorization: Bearer <token>
Content-Type: application/json

{
  "sale_number": "SALE-001",
  "shop_id": 2,
  "customer_name": "John Doe",
  "customer_phone": "1234567890",
  "discount_amount": 0.0,
  "sale_date": "2024-01-01",
  "notes": "Customer purchase",
  "sale_lines": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 240.0,
      "total_price": 480.0
    }
  ],
  "payments": [
    {
      "amount": 480.0,
      "payment_method": "cash",
      "payment_date": "2024-01-01",
      "reference": "CASH-001",
      "notes": "Cash payment"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "sale_number": "SALE-001",
  "shop_id": 2,
  "customer_name": "John Doe",
  "customer_phone": "1234567890",
  "total_amount": 480.0,
  "discount_amount": 0.0,
  "final_amount": 480.0,
  "status": "completed",
  "sale_date": "2024-01-01",
  "notes": "Customer purchase",
  "created_at": "2024-01-01T00:00:00Z",
  "sale_lines": [
    {
      "id": 1,
      "sale_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": 240.0,
      "total_price": 480.0
    }
  ],
  "payments": [
    {
      "id": 1,
      "sale_id": 1,
      "amount": 480.0,
      "payment_method": "cash",
      "payment_date": "2024-01-01",
      "reference": "CASH-001",
      "notes": "Cash payment"
    }
  ]
}
```

## 🔄 Returns Management

### Get All Returns
```http
GET /returns/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "sale_id": 1,
    "return_date": "2024-01-02",
    "reason": "defective",
    "notes": "Product defect",
    "created_at": "2024-01-02T00:00:00Z"
  }
]
```

### Create Return
```http
POST /returns/
Authorization: Bearer <token>
Content-Type: application/json

{
  "sale_id": 1,
  "return_date": "2024-01-02",
  "reason": "defective",
  "notes": "Product defect"
}
```

## 📈 Analytics & Reporting

### Dashboard Analytics
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_sales": 50000.0,
  "total_purchases": 30000.0,
  "total_production": 1000,
  "total_transfers": 500,
  "low_stock_items": 5,
  "recent_activities": [
    {
      "type": "sale",
      "description": "Sale SALE-001 created",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Profit/Loss Analytics
```http
GET /analytics/profit-loss
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_revenue": 50000.0,
  "total_costs": 35000.0,
  "gross_profit": 15000.0,
  "profit_margin": 30.0,
  "monthly_data": [
    {
      "month": "2024-01",
      "revenue": 50000.0,
      "costs": 35000.0,
      "profit": 15000.0
    }
  ]
}
```

## 🧠 Business Intelligence

### KPIs
```http
GET /business-intelligence/kpis
Authorization: Bearer <token>
```

**Response:**
```json
{
  "sales_kpi": {
    "total_sales": 50000.0,
    "sales_growth": 15.5,
    "average_order_value": 250.0
  },
  "inventory_kpi": {
    "total_products": 8,
    "low_stock_count": 2,
    "inventory_turnover": 4.2
  },
  "production_kpi": {
    "total_production": 1000,
    "efficiency_rate": 85.0,
    "waste_percentage": 5.0
  }
}
```

### Business Health
```http
GET /business-intelligence/business-health
Authorization: Bearer <token>
```

**Response:**
```json
{
  "overall_score": 85.0,
  "financial_health": 90.0,
  "operational_health": 80.0,
  "inventory_health": 85.0,
  "recommendations": [
    "Consider increasing production capacity",
    "Monitor low stock items"
  ]
}
```

## 💼 Financial Reporting

### Profit & Loss Statement
```http
GET /finance/profit-loss-statement
Authorization: Bearer <token>
```

**Response:**
```json
{
  "period": "2024-01",
  "revenue": {
    "total": 50000.0,
    "by_payment_method": [
      {
        "payment_method": "cash",
        "amount": 30000.0
      },
      {
        "payment_method": "bank_transfer",
        "amount": 20000.0
      }
    ]
  },
  "costs": {
    "total": 35000.0,
    "purchases": 25000.0,
    "production": 8000.0,
    "overhead": 2000.0
  },
  "profit": {
    "gross_profit": 15000.0,
    "net_profit": 12000.0,
    "profit_margin": 30.0
  }
}
```

## 👥 Human Resources

### Workforce Summary
```http
GET /hr/workforce-summary
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_employees": 25,
  "by_role": {
    "admin": 2,
    "shop_manager": 5,
    "staff": 18
  },
  "by_shop": {
    "1": 10,
    "2": 15
  },
  "recent_hires": [
    {
      "id": 1,
      "full_name": "John Smith",
      "email": "john@example.com",
      "role": "staff",
      "shop_id": 1,
      "shop_name": "Main Warehouse",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 🏪 Shop Management

### Get All Shops
```http
GET /shops/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Main Warehouse",
    "address": "123 Main St",
    "phone": "123-456-7890",
    "manager_id": 1,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## 🔧 Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

## 📝 Common Error Scenarios

### Insufficient Stock
```json
{
  "detail": "Insufficient stock for product ID 1. Available: 5, Required: 10"
}
```

### Duplicate Entry
```json
{
  "detail": "Sale with this number already exists"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

## 🚀 Frontend Integration Examples

### React/JavaScript Example
```javascript
// Login and get token
const login = async (username, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `username=${username}&password=${password}`
  });
  const data = await response.json();
  return data.access_token;
};

// Create a sale
const createSale = async (token, saleData) => {
  const response = await fetch('/sales/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(saleData)
  });
  return await response.json();
};
```

### Vue.js Example
```javascript
// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Get products
const getProducts = () => api.get('/products/');
```

## 🔒 Security Notes

- All endpoints require authentication
- JWT tokens expire after 24 hours
- Use HTTPS in production
- Validate all input data on the frontend
- Implement proper error handling

## 📞 Support

For API support and questions:
- Check the Swagger documentation at `/docs`
- Review the OpenAPI specification at `/openapi.json`
- Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-01  
**API Base URL**: `http://localhost:8000`