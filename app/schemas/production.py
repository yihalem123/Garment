"""
Production schemas
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class ProductionLineCreate(BaseModel):
    """Production line creation schema"""
    product_id: int
    planned_quantity: Decimal


class ProductionLineResponse(BaseModel):
    """Production line response schema"""
    id: int
    production_run_id: int
    product_id: int
    planned_quantity: Decimal
    actual_quantity: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class ProductionConsumptionCreate(BaseModel):
    """Production consumption creation schema"""
    raw_material_id: int
    planned_consumption: Decimal


class ProductionConsumptionResponse(BaseModel):
    """Production consumption response schema"""
    id: int
    production_run_id: int
    raw_material_id: int
    planned_consumption: Decimal
    actual_consumption: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class ProductionRunCreate(BaseModel):
    """Production run creation schema"""
    run_number: str
    planned_quantity: Decimal
    labor_cost: Decimal = 0
    overhead_cost: Decimal = 0
    start_date: Optional[str] = None
    notes: Optional[str] = None
    production_lines: List[ProductionLineCreate]
    production_consumptions: Optional[List[ProductionConsumptionCreate]] = None


class ProductionRunResponse(BaseModel):
    """Production run response schema"""
    id: int
    run_number: str
    status: str
    planned_quantity: Decimal
    actual_quantity: Optional[Decimal] = None
    labor_cost: Decimal
    overhead_cost: Decimal
    total_cost: Optional[Decimal] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None
    production_lines: List[ProductionLineResponse]
    production_consumptions: List[ProductionConsumptionResponse]
    
    class Config:
        from_attributes = True
