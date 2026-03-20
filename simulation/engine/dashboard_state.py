class DashboardState:
    def __init__(self):
        self.history = []
        self.interventions = 0

    def log(self, step, avg_trust, recent_sales, status):
        self.history.append({
            "step": step,
            "avg_trust": round(avg_trust, 3),
            "recent_sales": recent_sales,
            "status": status,
            "interventions": self.interventions,
        })

    def record_intervention(self):
        self.interventions += 1

    def latest(self):
        return self.history[-1] if self.history else None

    def estimate_collapse_eta(self):
        """
        Very simple heuristic:
        count RED signals in last windows
        """
        recent = self.history[-5:]
        red_count = sum(1 for h in recent if h["status"] == "RED")

        if red_count >= 3:
            return "IMMINENT"
        elif red_count == 2:
            return "SOON"
        elif red_count == 1:
            return "POSSIBLE"
        return "STABLE"
