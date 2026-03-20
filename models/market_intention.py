# ============================================================================
# 🟣 Core4.AI – Market Intention Model
# Represents explicit buyer demand (feature-first, product-agnostic)
# DCT context is linked (not embedded)
# ============================================================================

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text
from datetime import datetime
from db import Base


class MarketIntention(Base):
    __tablename__ = "market_intentions"

    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------------------------
    # Raw & normalized intent
    # ------------------------------------------------------------------------
    feature_text = Column(String, nullable=False)
    normalized_features = Column(JSON, nullable=True)

    # ------------------------------------------------------------------------
    # Category / Signal linkage
    # Needed by DCT flow
    # ------------------------------------------------------------------------
    category = Column(String, nullable=True, index=True)
    signal_id = Column(Integer, nullable=True, index=True)

    # ------------------------------------------------------------------------
    # Price signals (intent only – non-binding)
    # ------------------------------------------------------------------------
    target_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)

    # ------------------------------------------------------------------------
    # Demand context
    # ------------------------------------------------------------------------
    quantity_interest = Column(Integer, default=1)
    time_horizon = Column(String, nullable=True)  # now | soon | later
    buyer_cluster = Column(String, nullable=True)

    # ------------------------------------------------------------------------
    # User / Tribe context
    # Needed by DCT interest aggregation
    # ------------------------------------------------------------------------
    user_id = Column(Integer, nullable=True, index=True)
    tribe_id = Column(Integer, nullable=True, index=True)

    # ------------------------------------------------------------------------
    # Tribe Leader (Initiator)
    # ------------------------------------------------------------------------
    initiator_key = Column(String, nullable=True, index=True)

    # ------------------------------------------------------------------------
    # Qualification (IMMUTABLE ONCE SET)
    # ------------------------------------------------------------------------
    signal_score = Column(Float, default=0)
    qualified = Column(Boolean, default=False)
    qualification_reason = Column(Text, nullable=True)
    score_components = Column(Text, nullable=True)

    # ------------------------------------------------------------------------
    # DCT Status (mirror of DCTRequirement.status)
    # ------------------------------------------------------------------------
    dct_status = Column(String, default="none")  # none | pending | confirmed

    # ------------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------------
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)