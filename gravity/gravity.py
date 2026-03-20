# ============================================================================
# 🧠 Gravity Engine (Core4.AI – FINAL STABLE VERSION)
# Product-driven • Category-based • Clean Architecture
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta

from models.signal import Signal
from models.product import Product
from models.tribe_signal import TribeSignal
from models.gravity_config import GravityConfig
from models.market_intention import MarketIntention

# Auto Campaign trigger
from services.auto_campaign_service import create_auto_campaign


# ---------------------------------------------------------------------------
# Config helper
# ---------------------------------------------------------------------------

def _ensure_config(db: Session, category: str) -> GravityConfig:

    cfg = db.query(GravityConfig).filter(
        GravityConfig.category == category
    ).first()

    if not cfg:
        cfg = GravityConfig(category=category)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)

    return cfg


# ---------------------------------------------------------------------------
# RHO – Conviction Density
# Signals per category via Product join
# ---------------------------------------------------------------------------

def conviction_density_rho(db: Session, category: str) -> float:

    total_signals = (
        db.query(func.count(Signal.id))
        .join(Product, Signal.post_id == Product.id)
        .filter(Product.category == category)
        .scalar()
        or 0
    )

    qualified_signals = (
        db.query(func.count(Signal.id))
        .join(Product, Signal.post_id == Product.id)
        .filter(
            Product.category == category,
            Signal.intent == "interested"
        )
        .scalar()
        or 0
    )

    if total_signals == 0:
        return 0.0

    return float(qualified_signals) / float(total_signals)


# ---------------------------------------------------------------------------
# VN – Narrative Velocity
# Based on MarketIntentions globally
# ---------------------------------------------------------------------------

def narrative_velocity_vn(db: Session, category: str) -> float:

    now = datetime.utcnow()

    last_24h = now - timedelta(hours=24)
    prev_24h = now - timedelta(hours=48)

    recent = (
        db.query(func.count(MarketIntention.id))
        .filter(MarketIntention.created_at >= last_24h)
        .scalar()
        or 0
    )

    previous = (
        db.query(func.count(MarketIntention.id))
        .filter(
            MarketIntention.created_at >= prev_24h,
            MarketIntention.created_at < last_24h,
        )
        .scalar()
        or 0
    )

    raw = (recent - previous) / float(max(previous, 1))

    # Normalize to 0–1
    return max(0.0, min(1.0, (raw + 1.0) / 2.0))


# ---------------------------------------------------------------------------
# CC – Commitment Cohesion
# Tribe reinforcement per category via Product join
# ---------------------------------------------------------------------------

def commitment_cohesion_cc(db: Session, category: str) -> float:

    total = (
        db.query(func.count(TribeSignal.id))
        .join(Product, cast(TribeSignal.product_id, Integer) == Product.id)
        .filter(Product.category == category)
        .scalar()
        or 0
    )

    if total == 0:
        return 0.0

    dominant = (
        db.query(func.count(TribeSignal.id))
        .join(Product, cast(TribeSignal.product_id, Integer) == Product.id)
        .filter(Product.category == category)
        .group_by(TribeSignal.tribe_id)
        .order_by(func.count(TribeSignal.id).desc())
        .limit(1)
        .scalar()
        or 0
    )

    return float(dominant) / float(total)


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def evaluate_category(db: Session, category: str):

    cfg = _ensure_config(db, category)

    rho = conviction_density_rho(db, category)
    vn = narrative_velocity_vn(db, category)
    cc = commitment_cohesion_cc(db, category)

    gi = (
        (cfg.w_rho * rho)
        + (cfg.w_vn * vn)
        + (cfg.w_cc * cc)
    )

    mode = "SUMMONS" if gi >= cfg.gt_threshold else "INCUBATION"

    print(f"[Gravity] Category: {category}")
    print(f"[Gravity] rho={rho} vn={vn} cc={cc}")
    print(f"[Gravity] GI={gi} threshold={cfg.gt_threshold}")
    print(f"[Gravity] Mode={mode}")

    # -----------------------------------------------------------------------
    # 🔥 AUTO CAMPAIGN CREATION
    # -----------------------------------------------------------------------

    if gi >= cfg.gt_threshold:

        print(f"[Gravity] 🚀 Triggering auto campaign for {category}")

        create_auto_campaign(db, category)

    # -----------------------------------------------------------------------

    return {
        "category": category,
        "gi": gi,
        "rho": rho,
        "vn": vn,
        "cc": cc,
        "mode": mode,
    }