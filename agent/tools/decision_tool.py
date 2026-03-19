def run_decision_tool(metrics: dict, context: str) -> dict:
    reasons = []
    evidence = []
    score = 0

    preview = metrics.get("metrics", {}).get("preview", [])

    if not preview:
        return {
            "decision": "NEEDS_INFO",
            "reasons": ["No supplier data found"],
            "evidence": [],
            "confidence": 0.0
        }

    columns = metrics.get("metrics", {}).get("columns", [])
    price_col = next((c for c in columns if "price" in c.lower() or "cost" in c.lower()), None)
    name_col = next((c for c in columns if "name" in c.lower() or "supplier" in c.lower()), None)

    if price_col and name_col:
        best = min(preview, key=lambda x: float(str(x.get(price_col, 9999)).replace(",", ".")))
        reasons.append(f"Supplier '{best.get(name_col)}' has the lowest {price_col}: {best.get(price_col)}")
        evidence.append(str(best))
        score = 0.85
        decision = "PASS"
    else:
        reasons.append("Could not find price or supplier name columns for comparison")
        reasons.append(f"Available columns: {columns}")
        decision = "NEEDS_INFO"
        score = 0.4

    if context and context != "No context found.":
        reasons.append("Policy context retrieved and considered")
        evidence.append(f"Policy excerpt: {context[:200]}")

    return {
        "decision": decision,
        "reasons": reasons,
        "evidence": evidence,
        "confidence": score
    }