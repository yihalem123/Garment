"""
Pydantic schemas for request/response models
"""
from app.schemas.auth import Token, TokenData, UserCreate, UserResponse
from app.schemas.shop import ShopCreate, ShopResponse, ShopUpdate
from app.schemas.product import (
    ProductCreate, ProductResponse, ProductUpdate,
    RawMaterialCreate, RawMaterialResponse, RawMaterialUpdate,
    FabricRuleCreate, FabricRuleResponse
)
from app.schemas.inventory import (
    StockItemResponse, StockMovementResponse,
    StockAdjustmentRequest, StockQueryParams
)
from app.schemas.purchase import (
    PurchaseCreate, PurchaseResponse, PurchaseLineCreate,
    PurchaseLineResponse
)
from app.schemas.production import (
    ProductionRunCreate, ProductionRunResponse, ProductionLineCreate,
    ProductionLineResponse, ProductionConsumptionCreate, ProductionConsumptionResponse
)
from app.schemas.transfer import (
    TransferCreate, TransferResponse, TransferLineCreate, TransferLineResponse
)
from app.schemas.sale import (
    SaleCreate, SaleResponse, SaleLineCreate, SaleLineResponse,
    PaymentCreate, PaymentResponse
)
from app.schemas.return_model import ReturnCreate, ReturnResponse

__all__ = [
    "Token", "TokenData", "UserCreate", "UserResponse",
    "ShopCreate", "ShopResponse", "ShopUpdate",
    "ProductCreate", "ProductResponse", "ProductUpdate",
    "RawMaterialCreate", "RawMaterialResponse", "RawMaterialUpdate",
    "FabricRuleCreate", "FabricRuleResponse",
    "StockItemResponse", "StockMovementResponse",
    "StockAdjustmentRequest", "StockQueryParams",
    "PurchaseCreate", "PurchaseResponse", "PurchaseLineCreate", "PurchaseLineResponse",
    "ProductionRunCreate", "ProductionRunResponse", "ProductionLineCreate",
    "ProductionLineResponse", "ProductionConsumptionCreate", "ProductionConsumptionResponse",
    "TransferCreate", "TransferResponse", "TransferLineCreate", "TransferLineResponse",
    "SaleCreate", "SaleResponse", "SaleLineCreate", "SaleLineResponse",
    "PaymentCreate", "PaymentResponse",
    "ReturnCreate", "ReturnResponse"
]
