"""
Production routes
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_session
from app.models import (
    ProductionRun, ProductionLine, ProductionConsumption,
    StockItem, StockMovement, FabricRule,
    User, ItemType, MovementReason, ProductionStatus
)
from app.schemas.production import (
    ProductionRunCreate, ProductionRunResponse,
    ProductionLineCreate, ProductionConsumptionCreate
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductionRunResponse])
async def get_production_runs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all production runs
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/production/" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(ProductionRun).offset(skip).limit(limit).order_by(ProductionRun.created_at.desc())
    production_runs = await db.exec(statement)
    return production_runs.all()


@router.get("/{production_run_id}", response_model=ProductionRunResponse)
async def get_production_run(
    production_run_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific production run by ID
    """
    statement = select(ProductionRun).where(ProductionRun.id == production_run_id)
    production_run = await db.exec(statement)
    production_run = production_run.first()
    
    if not production_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production run not found"
        )
    
    return production_run


@router.post("/", response_model=ProductionRunResponse)
async def create_production_run(
    production_data: ProductionRunCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new production run
    
    This endpoint creates a production run with planned quantities.
    Use the complete endpoint to actually consume materials and produce goods.
    
    Example request:
    ```json
    {
        "run_number": "PR-2024-001",
        "planned_quantity": 100.0,
        "labor_cost": 500.00,
        "overhead_cost": 200.00,
        "start_date": "2024-01-15",
        "notes": "Monthly production run",
        "production_lines": [
            {
                "product_id": 1,
                "planned_quantity": 100.0
            }
        ],
        "production_consumptions": [
            {
                "raw_material_id": 1,
                "planned_consumption": 250.0
            }
        ]
    }
    ```
    """
    async with db.begin():
        # Check if run number already exists
        statement = select(ProductionRun).where(ProductionRun.run_number == production_data.run_number)
        existing_run = await db.exec(statement)
        if existing_run.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Production run with this number already exists"
            )
        
        # Create production run
        db_production_run = ProductionRun(
            run_number=production_data.run_number,
            planned_quantity=production_data.planned_quantity,
            labor_cost=production_data.labor_cost,
            overhead_cost=production_data.overhead_cost,
            start_date=production_data.start_date,
            notes=production_data.notes,
            status=ProductionStatus.PLANNED
        )
        
        db.add(db_production_run)
        await db.flush()  # Get the ID
        
        # Create production lines
        for line_data in production_data.production_lines:
            production_line = ProductionLine(
                production_run_id=db_production_run.id,
                product_id=line_data.product_id,
                planned_quantity=line_data.planned_quantity
            )
            db.add(production_line)
        
        # Create production consumptions (if provided, otherwise auto-calculate)
        if production_data.production_consumptions:
            for consumption_data in production_data.production_consumptions:
                production_consumption = ProductionConsumption(
                    production_run_id=db_production_run.id,
                    raw_material_id=consumption_data.raw_material_id,
                    planned_consumption=consumption_data.planned_consumption
                )
                db.add(production_consumption)
        else:
            # Auto-calculate consumption based on fabric rules
            for line_data in production_data.production_lines:
                statement = select(FabricRule).where(FabricRule.product_id == line_data.product_id)
                fabric_rules = await db.exec(statement)
                fabric_rules = fabric_rules.all()
                
                for rule in fabric_rules:
                    planned_consumption = rule.consumption_per_unit * line_data.planned_quantity
                    production_consumption = ProductionConsumption(
                        production_run_id=db_production_run.id,
                        raw_material_id=rule.raw_material_id,
                        planned_consumption=planned_consumption
                    )
                    db.add(production_consumption)
        
        await db.commit()
        await db.refresh(db_production_run)
    
    return db_production_run


@router.post("/{production_run_id}/complete", response_model=ProductionRunResponse)
async def complete_production_run(
    production_run_id: int,
    actual_quantities: dict = None,  # Optional: override planned quantities
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Complete a production run
    
    This endpoint:
    1. Validates raw material availability
    2. Deducts raw material stock
    3. Adds product stock
    4. Creates stock movement records
    5. Calculates total production cost
    6. Updates production run status
    
    Example request:
    ```json
    {
        "actual_quantities": {
            "production_lines": [
                {"product_id": 1, "actual_quantity": 95.0}
            ],
            "production_consumptions": [
                {"raw_material_id": 1, "actual_consumption": 240.0}
            ]
        }
    }
    ```
    """
    async with db.begin():
        # Get production run
        statement = select(ProductionRun).where(ProductionRun.id == production_run_id)
        production_run = await db.exec(statement)
        production_run = production_run.first()
        
        if not production_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production run not found"
            )
        
        if production_run.status != ProductionStatus.PLANNED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Production run is not in planned status"
            )
        
        # Get production lines and consumptions
        statement = select(ProductionLine).where(ProductionLine.production_run_id == production_run_id)
        production_lines = await db.exec(statement)
        production_lines = production_lines.all()
        
        statement = select(ProductionConsumption).where(ProductionConsumption.production_run_id == production_run_id)
        production_consumptions = await db.exec(statement)
        production_consumptions = production_consumptions.all()
        
        # Validate raw material availability
        for consumption in production_consumptions:
            statement = select(StockItem).where(
                and_(
                    StockItem.raw_material_id == consumption.raw_material_id,
                    StockItem.item_type == ItemType.RAW_MATERIAL
                )
            )
            stock_item = await db.exec(statement)
            stock_item = stock_item.first()
            
            if not stock_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No stock found for raw material ID {consumption.raw_material_id}"
                )
            
            available_quantity = stock_item.quantity - stock_item.reserved_quantity
            required_quantity = consumption.planned_consumption
            
            if available_quantity < required_quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for raw material ID {consumption.raw_material_id}. "
                           f"Available: {available_quantity}, Required: {required_quantity}"
                )
        
        # Process raw material consumption
        raw_material_cost = Decimal('0')
        for consumption in production_consumptions:
            # Deduct raw material stock
            statement = select(StockItem).where(
                and_(
                    StockItem.raw_material_id == consumption.raw_material_id,
                    StockItem.item_type == ItemType.RAW_MATERIAL
                )
            )
            stock_item = await db.exec(statement)
            stock_item = stock_item.first()
            
            stock_item.quantity -= consumption.planned_consumption
            
            # Create stock movement
            stock_movement = StockMovement(
                shop_id=1,  # Main warehouse
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=consumption.raw_material_id,
                quantity=-consumption.planned_consumption,  # Negative for deduction
                reason=MovementReason.PRODUCTION_CONSUME,
                reference_id=production_run_id,
                reference_type="production_run"
            )
            db.add(stock_movement)
            
            # Calculate raw material cost
            from app.models import RawMaterial
            statement = select(RawMaterial).where(RawMaterial.id == consumption.raw_material_id)
            raw_material = await db.exec(statement)
            raw_material = raw_material.first()
            raw_material_cost += raw_material.unit_price * consumption.planned_consumption
        
        # Process product production
        for line in production_lines:
            # Add product stock
            statement = select(StockItem).where(
                and_(
                    StockItem.product_id == line.product_id,
                    StockItem.item_type == ItemType.PRODUCT
                )
            )
            stock_item = await db.exec(statement)
            stock_item = stock_item.first()
            
            if not stock_item:
                # Create new stock item
                stock_item = StockItem(
                    shop_id=1,  # Main warehouse
                    item_type=ItemType.PRODUCT,
                    product_id=line.product_id,
                    quantity=line.planned_quantity,
                    reserved_quantity=Decimal('0'),
                    min_stock_level=Decimal('10')
                )
                db.add(stock_item)
            else:
                stock_item.quantity += line.planned_quantity
            
            # Create stock movement
            stock_movement = StockMovement(
                shop_id=1,  # Main warehouse
                item_type=ItemType.PRODUCT,
                product_id=line.product_id,
                quantity=line.planned_quantity,
                reason=MovementReason.PRODUCTION_ADD,
                reference_id=production_run_id,
                reference_type="production_run"
            )
            db.add(stock_movement)
        
        # Calculate total cost and update production run
        total_cost = raw_material_cost + production_run.labor_cost + production_run.overhead_cost
        production_run.total_cost = total_cost
        production_run.status = ProductionStatus.COMPLETED
        production_run.actual_quantity = production_run.planned_quantity  # Use planned as actual for now
        
        await db.commit()
        await db.refresh(production_run)
    
    return production_run
