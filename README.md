# Garment Business Management System

A comprehensive REST API for managing garment business operations including inventory, production, sales, and reporting.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (admin, shop_manager, staff)
- **Inventory Management**: Track stock levels, movements, and adjustments across multiple shops
- **Purchase Management**: Handle raw material purchases with automatic stock updates
- **Production Management**: Manage production runs with material consumption tracking
- **Transfer Management**: Transfer products between shops with stock reservation
- **Sales Management**: Process sales with real-time stock validation and simple payment tracking (cash/bank transfer)
- **Returns Management**: Handle product returns with stock adjustments
- **Business Analytics**: Comprehensive dashboard with KPIs, trends, and performance metrics
- **Human Resource Management**: Employee management, performance tracking, and workforce analytics
- **Financial Reporting**: Profit & Loss statements, cash flow analysis, balance sheets, and financial ratios
- **Business Intelligence**: Advanced analytics, comparative analysis, and business health scoring
- **Real-time Updates**: WebSocket support for live notifications
- **Background Jobs**: Celery-based task processing for notifications and reports
- **Comprehensive Testing**: Unit and integration tests with pytest

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy compatible)
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT (OAuth2PasswordBearer)
- **Background Jobs**: Celery with Redis
- **Testing**: pytest with httpx
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd garment
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Create seed data**
   ```bash
   docker-compose exec backend python -m app.db.seed_data
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Create seed data**
   ```bash
   python -m app.db.seed_data
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

### Authentication

All endpoints (except `/auth/login`) require authentication. Include the JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/products/
```

### Payment System

The system supports a simplified payment model with two payment methods:

- **Cash**: Physical cash payments with optional receipt number tracking
- **Bank Transfer**: Bank transfer payments with transaction reference tracking

No POS (Point of Sale) integration is included - all payment details are entered as text fields. The `reference` field can be used for:
- Cash payments: Receipt numbers or cash register references
- Bank transfers: Transaction IDs or bank reference numbers

Example payment objects:
```json
{
  "amount": 50.00,
  "payment_method": "cash",
  "payment_date": "2024-01-15",
  "reference": "RCP-001",
  "notes": "Cash payment received"
}
```

```json
{
  "amount": 100.00,
  "payment_method": "bank_transfer",
  "payment_date": "2024-01-15",
  "reference": "TXN-123456789",
  "notes": "Bank transfer confirmed"
}
```

### Sample API Calls

#### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@garment.com&password=admin123"
```

#### 2. Create a Purchase
```bash
curl -X POST "http://localhost:8000/purchases/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "supplier_name": "Fabric Supplier Co.",
       "supplier_invoice": "INV-001",
       "purchase_date": "2024-01-15",
       "purchase_lines": [
         {
           "raw_material_id": 1,
           "quantity": 100.0,
           "unit_price": 5.50
         }
       ]
     }'
```

#### 3. Create a Production Run
```bash
curl -X POST "http://localhost:8000/production/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "run_number": "PR-2024-001",
       "planned_quantity": 50.0,
       "labor_cost": 200.00,
       "overhead_cost": 100.00,
       "start_date": "2024-01-15",
       "production_lines": [
         {
           "product_id": 1,
           "planned_quantity": 50.0
         }
       ]
     }'
```

#### 4. Complete Production Run
```bash
curl -X POST "http://localhost:8000/production/1/complete" \
     -H "Authorization: Bearer <token>"
```

#### 5. Create a Sale
```bash
curl -X POST "http://localhost:8000/sales/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "sale_number": "SALE-2024-001",
       "shop_id": 2,
       "customer_name": "John Doe",
       "customer_phone": "+1234567890",
       "sale_date": "2024-01-15",
       "sale_lines": [
         {
           "product_id": 1,
           "quantity": 2.0,
           "unit_price": 25.00
         }
       ],
       "payments": [
         {
           "amount": 50.00,
           "payment_method": "cash",
           "payment_date": "2024-01-15",
           "reference": "RCP-001",
           "notes": "Cash payment received"
         }
       ]
     }'
```

#### 6. Check Stock Levels
```bash
curl -X GET "http://localhost:8000/inventory/stocks?shop_id=1" \
     -H "Authorization: Bearer <token>"
```

#### 7. Transfer Products Between Shops
```bash
curl -X POST "http://localhost:8000/transfers/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "transfer_number": "TR-2024-001",
       "from_shop_id": 1,
       "to_shop_id": 2,
       "transfer_date": "2024-01-15",
       "transfer_lines": [
         {
           "product_id": 1,
           "quantity": 10.0,
           "unit_cost": 25.00
         }
       ]
     }'
```

#### 8. Get Business Dashboard
```bash
curl -X GET "http://localhost:8000/analytics/dashboard?start_date=2024-01-01&end_date=2024-01-31" \
     -H "Authorization: Bearer <token>"
```

#### 9. Get Profit & Loss Statement
```bash
curl -X GET "http://localhost:8000/finance/profit-loss-statement?start_date=2024-01-01&end_date=2024-01-31" \
     -H "Authorization: Bearer <token>"
```

#### 10. Get Key Performance Indicators
```bash
curl -X GET "http://localhost:8000/business-intelligence/kpis?start_date=2024-01-01&end_date=2024-01-31" \
     -H "Authorization: Bearer <token>"
```

#### 11. Get Employee Performance
```bash
curl -X GET "http://localhost:8000/hr/performance?start_date=2024-01-01&end_date=2024-01-31" \
     -H "Authorization: Bearer <token>"
```

#### 12. Get Business Health Score
```bash
curl -X GET "http://localhost:8000/business-intelligence/business-health" \
     -H "Authorization: Bearer <token>"
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://garment_user:garment_pass@localhost:5432/garment_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (for notifications)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_TLS=true

# Application
DEBUG=true
ENVIRONMENT=development
ALLOWED_HOSTS=["*"]
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_sales.py

# Run with verbose output
pytest -v
```

## Background Jobs

The system includes several background jobs:

### Low Stock Notifications
Daily task to check for low stock items and send email notifications.

### Daily Sales Reports
Generate daily sales reports with top-selling products.

### Database Cleanup
Clean up old stock movement records to maintain performance.

### Scheduling Jobs

To schedule background jobs, you can use Celery Beat:

```bash
# Start Celery Beat scheduler
celery -A app.core.celery_app beat --loglevel=info

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info
```

## WebSocket Support

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

The WebSocket broadcasts events for:
- Stock updates
- New sales
- Production completions
- Transfer updates

## Database Schema

The system includes the following main entities:

- **Users**: System users with role-based access
- **Shops**: Physical locations/stores
- **Products**: Finished goods
- **Raw Materials**: Materials used in production
- **Stock Items**: Inventory levels per shop
- **Stock Movements**: All inventory transactions
- **Purchases**: Raw material purchases
- **Production Runs**: Manufacturing operations
- **Transfers**: Inter-shop product transfers
- **Sales**: Customer transactions
- **Returns**: Product returns

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/users/me` - Get current user
- `POST /auth/users` - Create user (admin only)

### Products
- `GET /products/` - List products
- `POST /products/` - Create product
- `GET /products/{id}` - Get product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Raw Materials
- `GET /raw-materials/` - List raw materials
- `POST /raw-materials/` - Create raw material
- `GET /raw-materials/{id}` - Get raw material
- `PUT /raw-materials/{id}` - Update raw material
- `DELETE /raw-materials/{id}` - Delete raw material

### Inventory
- `GET /inventory/stocks` - Get stock levels
- `POST /inventory/stocks/adjust` - Adjust stock
- `GET /inventory/stock-movements` - Get stock movements

### Purchases
- `GET /purchases/` - List purchases
- `POST /purchases/` - Create purchase
- `GET /purchases/{id}` - Get purchase

### Production
- `GET /production/` - List production runs
- `POST /production/` - Create production run
- `GET /production/{id}` - Get production run
- `POST /production/{id}/complete` - Complete production run

### Transfers
- `GET /transfers/` - List transfers
- `POST /transfers/` - Create transfer
- `GET /transfers/{id}` - Get transfer
- `POST /transfers/{id}/receive` - Receive transfer

### Sales
- `GET /sales/` - List sales
- `POST /sales/` - Create sale
- `GET /sales/{id}` - Get sale

### Returns
- `GET /returns/` - List returns
- `POST /returns/` - Create return
- `GET /returns/{id}` - Get return

### WebSocket
- `WS /ws` - WebSocket connection for real-time updates

### Business Analytics
- `GET /analytics/dashboard` - Comprehensive business dashboard
- `GET /analytics/profit-loss` - Profit and loss analysis
- `GET /analytics/inventory-report` - Detailed inventory report
- `GET /analytics/financial-summary` - Financial summary and breakdown

### Human Resources
- `GET /hr/employees` - List employees with filtering
- `POST /hr/employees` - Create new employee
- `PUT /hr/employees/{id}` - Update employee information
- `DELETE /hr/employees/{id}` - Deactivate employee
- `GET /hr/performance` - Employee performance metrics
- `GET /hr/workforce-summary` - Workforce statistics and summary

### Business Intelligence
- `GET /business-intelligence/kpis` - Key Performance Indicators
- `GET /business-intelligence/trends` - Business trends over time
- `GET /business-intelligence/comparative-analysis` - Period-over-period analysis
- `GET /business-intelligence/business-health` - Business health score and recommendations

### Finance
- `GET /finance/profit-loss-statement` - Comprehensive P&L statement
- `GET /finance/cash-flow-statement` - Cash flow analysis
- `GET /finance/balance-sheet` - Balance sheet report
- `GET /finance/financial-ratios` - Financial ratios and analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
