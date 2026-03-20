def generate_board_summary(results):
    lines = []
    lines.append("CORE4.AI — Public Beta Trust Report\n")
    lines.append("Key Findings:\n")

    for r in results:
        label = r["label"]
        collapse = r["collapse_step"]

        if collapse:
            lines.append(
                f"- Scenario '{label}' collapsed at step {collapse} "
                f"with sales={r['final_sales']}."
            )
        else:
            lines.append(
                f"- Scenario '{label}' remained stable throughout the test."
            )

    lines.append("\nConclusion:\n")
    lines.append(
        "Markets without trust renewal inevitably collapse. "
        "Governance delays collapse, but renewal prevents it."
    )

    return "\n".join(lines)
