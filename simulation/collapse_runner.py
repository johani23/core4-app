from agents.buyer import Buyer
from agents.merchant import Merchant
from agents.tribe import Tribe
from engine.market import MarketEngine
from metrics.tracker import MetricsTracker
from data.seed import seed
from config import *

from board_report import generate_board_summary

# =========================
# FEATURE FLAGS (PUBLIC BETA)
# =========================
FEATURE_TRUST_RENEWAL = True
FEATURE_AUTO_CALIBRATION = True
FEATURE_GUARDRAILS = True
FEATURE_BOARD_REPORT = True

WINDOW = 100
COLLAPSE_SALES_FLOOR = 3
COLLAPSE_TRUST_FLOOR = 0.25


def run_collapse_test(
    label,
    claim_rate_multiplier=1.0,
    tribe_strictness_multiplier=1.0,
):
    print(f"\n=== RUNNING COLLAPSE TEST: {label} ===")
    seed()

    buyers = [Buyer(i) for i in range(BUYER_COUNT)]
    merchants = [Merchant(i) for i in range(MERCHANT_COUNT)]
    tribes = [Tribe(i) for i in range(TRIBE_COUNT)]

    for m in merchants:
        m.claim_rate_multiplier = claim_rate_multiplier

    for t in tribes:
        t.strictness_multiplier = tribe_strictness_multiplier

    tracker = MetricsTracker(suffix=f"collapse_{label}")

    market = MarketEngine(
        buyers,
        merchants,
        tribes,
        tracker,
        enable_trust_renewal=FEATURE_TRUST_RENEWAL,
        enable_auto_calibration=FEATURE_AUTO_CALIBRATION,
        enable_guardrails=FEATURE_GUARDRAILS,
    )

    collapse_step = None
    trust_window = []
    sales_checkpoint = tracker.sales

    for step in range(1, SIMULATION_STEPS + 1):
        market.step()

        trust_window.append(
            sum(m.trust for m in merchants) / len(merchants)
        )

        if step % WINDOW == 0:
            avg_trust = sum(trust_window[-WINDOW:]) / WINDOW
            recent_sales = tracker.sales - sales_checkpoint
            sales_checkpoint = tracker.sales

            status = market.last_warning_status

            print(
                f"[{label}] Step {step} | "
                f"Avg Trust: {avg_trust:.2f} | "
                f"Sales (window): {recent_sales} | "
                f"Status: {status}"
            )

            # Collapse only if RED persists
            if (
                status == "RED"
                and recent_sales <= COLLAPSE_SALES_FLOOR
                and avg_trust <= COLLAPSE_TRUST_FLOOR
                and collapse_step is None
            ):
                collapse_step = step
                print(f"🔥 COLLAPSE CONFIRMED at step {step}")
                break

    tracker.export()

    return {
        "label": label,
        "collapse_step": collapse_step,
        "final_sales": tracker.sales,
        "final_revenue": round(tracker.revenue, 2),
        "true_claims": tracker.true_claims,
        "false_claims": tracker.false_claims,
    }


def run_all():
    results = []

    results.append(run_collapse_test("normal"))
    results.append(run_collapse_test("claim_abuse", claim_rate_multiplier=3.0))
    results.append(
        run_collapse_test(
            "claim_abuse_strong_tribes",
            claim_rate_multiplier=3.0,
            tribe_strictness_multiplier=1.5,
        )
    )

    print("\n=== COLLAPSE SUMMARY ===")
    for r in results:
        print(r)

    if FEATURE_BOARD_REPORT:
        print("\n=== BOARD SUMMARY ===")
        print(generate_board_summary(results))


if __name__ == "__main__":
    run_all()
