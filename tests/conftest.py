"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_session
from app.models import Base
from app.core.security import get_password_hash
from app.models import User, Shop, Product, RawMaterial, StockItem, ItemType


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_db():
    """Set up test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    def override_get_session():
        return db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_shop(db_session: AsyncSession) -> Shop:
    """Create a test shop"""
    shop = Shop(
        name="Test Shop",
        address="123 Test Street",
        phone="+1234567890",
        email="shop@example.com"
    )
    db_session.add(shop)
    await db_session.commit()
    await db_session.refresh(shop)
    return shop


@pytest.fixture
async def test_product(db_session: AsyncSession) -> Product:
    """Create a test product"""
    product = Product(
        name="Test Product",
        description="A test product",
        sku="TEST001",
        category="test",
        unit_price=25.00,
        cost_price=15.00
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest.fixture
async def test_raw_material(db_session: AsyncSession) -> RawMaterial:
    """Create a test raw material"""
    raw_material = RawMaterial(
        name="Test Fabric",
        description="Test fabric material",
        sku="FAB001",
        unit="kg",
        unit_price=5.00
    )
    db_session.add(raw_material)
    await db_session.commit()
    await db_session.refresh(raw_material)
    return raw_material


@pytest.fixture
async def test_stock_item(db_session: AsyncSession, test_shop: Shop, test_product: Product) -> StockItem:
    """Create a test stock item"""
    stock_item = StockItem(
        shop_id=test_shop.id,
        item_type=ItemType.PRODUCT,
        product_id=test_product.id,
        quantity=100.0,
        reserved_quantity=0.0,
        min_stock_level=10.0
    )
    db_session.add(stock_item)
    await db_session.commit()
    await db_session.refresh(stock_item)
    return stock_item


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers"""
    response = await client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
