# ============================================================================
# 🧠 Gravity Configuration Model
# ============================================================================
from sqlalchemy import Column, Integer, Float, String
from db import Base

class GravityConfig(Base):
    __tablename__ = "gravity_config"

    id = Column(Integer, primary_key=True, index=True)

    # Category this config applies to (e.g. "fitness", "electronics")
    category = Column(String, unique=True, index=True, nullable=False)

    # Gravity threshold (when to trigger SUMMONS)
    gt_threshold = Column(Float, default=0.10)

    # Weights for gravity components
    w_rho = Column(Float, default=0.45)  # Conviction Density
    w_vn  = Column(Float, default=0.30)  # Narrative Velocity
    w_cc  = Column(Float, default=0.25)  # Commitment Cohesion
