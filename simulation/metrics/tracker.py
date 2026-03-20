import csv
import os

class MetricsTracker:
    def __init__(self, suffix=""):
        self.suffix = suffix

        self.sales = 0
        self.revenue = 0.0
        self.true_claims = 0
        self.false_claims = 0

    def record_sale(self, price, merchant_id):
        self.sales += 1
        self.revenue += price

    def record_claim(self, success):
        if success:
            self.true_claims += 1
        else:
            self.false_claims += 1

    def export(self):
        base_dir = os.path.dirname(__file__)              # simulation/metrics
        output_dir = os.path.abspath(
            os.path.join(base_dir, "..", "output")
        )

        os.makedirs(output_dir, exist_ok=True)

        filename = (
            f"results_{self.suffix}.csv"
            if self.suffix
            else "results.csv"
        )

        file_path = os.path.join(output_dir, filename)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "sales",
                "revenue",
                "true_claims",
                "false_claims",
            ])
            writer.writerow([
                self.sales,
                round(self.revenue, 2),
                self.true_claims,
                self.false_claims,
            ])

    def summary(self):
        return {
            "sales": self.sales,
            "revenue": round(self.revenue, 2),
            "true_claims": self.true_claims,
            "false_claims": self.false_claims,
        }
