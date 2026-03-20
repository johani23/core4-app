# ============================================================================
# 💚 Core4AI – Orders API (Buyer Checkout + Merchant Orders View)
# GA-HARDENED (Idempotency + Request Tracing)
# ============================================================================

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from services.elasticity_service import register_order_for_market
from db import SessionLocal
from models.product import Product

# Optional (لكن موصى به)
from utils.idempotency import check_idempotency
from utils.logger import log_event

# ============================================================================
# ROUTER
# ============================================================================
router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

# ============================================================================
# Order Input Model
# ============================================================================
class OrderInput(BaseModel):
    product_id: int
    qty: int = 1
    buyer_id: Optional[str] = None

# ============================================================================
# In-Memory Storage (MVP / GA-safe)
# ============================================================================
ORDERS = []

# ============================================================================
# CREATE ORDER
# ============================================================================
@router.post("/")
async def create_order(
    request: Request,
    order: OrderInput,
    x_idempotency_key: Optional[str] = Header(None)
):
    # ------------------------------------------------------------------------
    # Idempotency Guard (GA CRITICAL)
    # ------------------------------------------------------------------------
    if not x_idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="X-Idempotency-Key header is required"
        )

    check_idempotency(x_idempotency_key)

    # ------------------------------------------------------------------------
    # Create Order
    # ------------------------------------------------------------------------
    new_order = {
        "id": len(ORDERS) + 1,
        "product_id": order.product_id,
        "qty": order.qty,
        "buyer_id": order.buyer_id or "guest",
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, "request_id", None),
    }

    ORDERS.append(new_order)

    # ------------------------------------------------------------------------
    # 🔥 Elasticity Hook (Revenue → Learning)
    # ------------------------------------------------------------------------
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            market_id = product.category  # category = market_id
            register_order_for_market(db, market_id)
            db.commit()
    finally:
        db.close()

    # ------------------------------------------------------------------------
    # Structured Log
    # ------------------------------------------------------------------------
    log_event(
        request,
        action="create_order",
        status="success",
        extra={
            "order_id": new_order["id"],
            "product_id": order.product_id,
            "qty": order.qty,
        }
    )

    return {
        "status": "success",
        "order": new_order
    }

# ============================================================================
# LIST ALL ORDERS (Merchant View)
# ============================================================================
@router.get("/")
async def list_orders(request: Request):
    log_event(
        request,
        action="list_orders",
        status="success",
        extra={"count": len(ORDERS)}
    )
    return {"orders": ORDERS}

# ============================================================================
# GET ORDER BY ID
# ============================================================================
@router.get("/{order_id}")
async def get_order(request: Request, order_id: int):
    for order in ORDERS:
        if order["id"] == order_id:
            log_event(
                request,
                action="get_order",
                status="success",
                extra={"order_id": order_id}
            )
            return order

    log_event(
        request,
        action="get_order",
        status="not_found",
        extra={"order_id": order_id}
    )

    raise HTTPException(status_code=404, detail="Order not found")
