-- =========================================================
-- 🔒 Enforce One Email Per Campaign
-- =========================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_campaign_email
ON market_commitments (campaign_id, email);