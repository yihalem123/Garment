"""
WebSocket routes for real-time updates
"""
import json
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import User
from app.api.routes.auth import get_current_user

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    Clients can connect to receive real-time notifications about:
    - Stock updates
    - New sales
    - Production completions
    - Transfer updates
    
    Example connection:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    };
    ```
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back for testing
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Utility functions for broadcasting events
async def broadcast_stock_update(shop_id: int, item_type: str, item_id: int, quantity: float):
    """Broadcast stock update event"""
    message = {
        "type": "stock.update",
        "data": {
            "shop_id": shop_id,
            "item_type": item_type,
            "item_id": item_id,
            "quantity": quantity
        }
    }
    await manager.broadcast(json.dumps(message))


async def broadcast_sale_created(sale_id: int, shop_id: int, total_amount: float):
    """Broadcast new sale event"""
    message = {
        "type": "sale.created",
        "data": {
            "sale_id": sale_id,
            "shop_id": shop_id,
            "total_amount": total_amount
        }
    }
    await manager.broadcast(json.dumps(message))


async def broadcast_production_completed(production_run_id: int, status: str):
    """Broadcast production completion event"""
    message = {
        "type": "production.completed",
        "data": {
            "production_run_id": production_run_id,
            "status": status
        }
    }
    await manager.broadcast(json.dumps(message))


async def broadcast_transfer_updated(transfer_id: int, status: str):
    """Broadcast transfer update event"""
    message = {
        "type": "transfer.updated",
        "data": {
            "transfer_id": transfer_id,
            "status": status
        }
    }
    await manager.broadcast(json.dumps(message))
