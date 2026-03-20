# ============================================================================
# 💚 Core4.AI – Unified Backend API
# FINAL CLEAN PRODUCTION main.py
# (NO INLINE ROUTES • NO DUPLICATES • NO HACKS)
# ============================================================================

from contextlib import asynccontextmanager


# =========================
# DATABASE
# =========================

from db import Base, engine, SessionLocal

# Register commitment models
from commitment import models

from commitment import market_brackets  # 🔥 ADD THIS

# ============================================================================
# MODELS (flat canonical layout)
# ============================================================================
from models import product
from models import campaign
from models.signal import Signal
from models.value_insights import ValueInsight
from models.product_pricing_mit import ProductPricingMIT
from models.market_intention import MarketIntention

from models.tribe_signal import TribeSignal






# ============================================================================
# SEED (demo only)
# ============================================================================
def seed_initial_data():
    db = SessionLocal()
    try:
        p = db.query(product.Product).filter(product.Product.id == 1).first()
        if not p:
            p = product.Product(
                id=1,
                name="demo",
                price=4567,
                competitor_price=5678,
                category="test",
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            )
            db.add(p)

        mit = db.query(ProductPricingMIT).filter(
            ProductPricingMIT.product_id == 1
        ).first()

        if not mit:
            mit = ProductPricingMIT(
                product_id=1,
                base_price=4567,
                competitor_price=5678,
                smart_price=4800,
                market_floor=4200,
                market_ceiling=5500,
                tribe_hotness=0.6,
                conversion_lift=0.12,
            )
            db.add(mit)

        db.commit()
    finally:
        db.close()

# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================
@asynccontextmanager
async def lifespan(app):
    
    
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield

# ============================================================================
# FASTAPI
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.request_id import RequestIDMiddleware


app = FastAPI(
    title="Core4.AI Backend API",
    version="3.5-beta-hardened",
    description=(
        "Unified backend API with Signal Ingestion, "
        "Human-in-the-loop Governance, "
        "Tribe-Governed Pricing, "
        "Explainability, and Operational Metrics"
    ),
    lifespan=lifespan,
)

from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# =========================
# REQUEST ID (GA HARDENING)
# =========================
app.add_middleware(RequestIDMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTERS (ONE TIME • CANONICAL)
# ============================================================================
from routes.signals import router as signals_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.pulse import router as pulse_router

from routes.market_intentions import router as market_intentions_router
from routes.creator_api import router as creator_api_router

from routes.merchant.products import router as merchant_products_router
from routes.merchant.campaigns import router as merchant_campaigns_router
from routes.merchant.analytics import router as merchant_analytics_router
from routes.merchant.analytics_v2 import router as merchant_analytics_v2_router
from routes.merchant.commission import router as merchant_commission_router

from routes.audience import router as audience_router
from routes.influence import router as influence_router

from routes.creator import router as creator_legacy_router
from routes.analytics import router as analytics_legacy_router

from routes.rnd_routes import router as rnd_router
from routes.pricing_api import router as pricing_router
from routes.tribe_approval import router as tribe_approval_router


from routes.admin_market_health import router as admin_market_health_router

from routes.system_early_warning import router as system_early_warning_router

from routes.admin_market_timeline import router as admin_market_timeline_router

from routes.governance import router as governance_router

from routes.governance_review import router as governance_reviews_router

from routes.governance_metrics import router as governance_metrics_router

from routes.analysis import router as analysis_router





from app.routers.dct import router as dct_router

from app.routers.ghost_posts import router as ghost_posts_router


from routes.merchant.demand_signals import router as merchant_demand_signals_router

from routes.merchant.demand_feedback import router as merchant_feedback_router



from routes.merchant.commitment import router as merchant_commitment_router

from routes.dct.promotion import router as dct_promotion_router



from routes.dct.requirements import router as dct_requirements_router

from routers.gravity_router import router as gravity_router

from routers.market_loop_router import router as market_loop_router

from routers.elasticity_router import router as elasticity_router

from routes.merchant.market_intelligence import router as merchant_market_intelligence_router


from routers.campaign_router import router as campaign_router

from commitment.router import router as commitment_router

from models import market_request

from routers.market_request_router import router as market_router
from routers.merchant_router import router as merchant_router


# ============================================================================
# REGISTER ROUTES
# ============================================================================
app.include_router(signals_router, prefix="/api")

app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(pulse_router, prefix="/api")

app.include_router(market_intentions_router, prefix="/api")
app.include_router(creator_api_router, prefix="/api/creator")

app.include_router(merchant_products_router)
app.include_router(merchant_campaigns_router)
app.include_router(merchant_analytics_router)
app.include_router(merchant_analytics_v2_router)
app.include_router(merchant_commission_router)

app.include_router(audience_router, prefix="/api/audience")
app.include_router(influence_router, prefix="/api/influence")

app.include_router(creator_legacy_router, prefix="/api")
app.include_router(analytics_legacy_router, prefix="/api")

app.include_router(rnd_router, prefix="/api/rnd")


app.include_router(tribe_approval_router)

app.include_router(admin_market_health_router)

app.include_router(system_early_warning_router)

app.include_router(admin_market_timeline_router)

app.include_router(governance_router)

app.include_router(governance_reviews_router)

app.include_router(governance_metrics_router)

app.include_router(analysis_router)




app.include_router(dct_router)

app.include_router(ghost_posts_router)

app.include_router(merchant_demand_signals_router, prefix="/api")

app.include_router(merchant_feedback_router, prefix="/api")


app.include_router(merchant_commitment_router, prefix="/api")

app.include_router(dct_promotion_router, prefix="/api")

app.include_router(dct_requirements_router, prefix="/api")


app.include_router(merchant_market_intelligence_router, prefix="/api")

app.include_router(market_router)
app.include_router(merchant_router)


# =========================================
# MARKET ENGINE
# =========================================

app.include_router(gravity_router)
app.include_router(commitment_router)
app.include_router(campaign_router)
app.include_router(market_loop_router)
app.include_router(pricing_router)
app.include_router(elasticity_router)

# ============================================================================
# HEALTH
# ============================================================================
@app.get("/")
def root():
    return {
        "status": "Core4 Backend Running",
        "version": "3.5-beta-hardened",
        "database": "sqlite (/tmp)",
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return health()
