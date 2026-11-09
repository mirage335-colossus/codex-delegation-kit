from .validation import validate_snapshot


def normalize_state(value):
    value = value.strip().lower()
    aliases = {"succeeded": "succeeded", "success": "succeeded", "failed": "failed", "running": "running"}
    if value not in aliases:
        raise ValueError(f"unknown deployment state: {value!r}")
    return aliases[value]


def normalize_snapshot(payload):
    service, captured_at, items = validate_snapshot(payload)
    deployments = []
    for item in items:
        deployments.append({
            "id": str(item["id"]).strip(),
            "state": normalize_state(item["state"]),
            "finished_at": item["finished_at"].strip(),
        })
    return {"service": service, "captured_at": captured_at, "deployments": deployments}
