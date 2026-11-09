from .timeutil import parse_time


def _nonempty_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def validate_snapshot(payload):
    """Check the external snapshot envelope and deployment fields."""
    if not isinstance(payload, dict):
        raise ValueError("snapshot must be an object")
    for field in ("service", "captured_at", "deployments"):
        if field not in payload:
            raise ValueError(f"snapshot is missing {field}")
    service = _nonempty_text(payload["service"], "service")
    captured = _nonempty_text(payload["captured_at"], "captured_at")
    parse_time(captured)
    deployments = payload["deployments"]
    if not isinstance(deployments, list):
        raise ValueError("deployments must be a list")
    seen = set()
    for index, item in enumerate(deployments):
        if not isinstance(item, dict):
            raise ValueError(f"deployment {index} must be an object")
        for field in ("id", "state", "finished_at"):
            if field not in item:
                raise ValueError(f"deployment {index} is missing {field}")
        identity = _nonempty_text(str(item["id"]), f"deployment {index} id")
        _nonempty_text(item["state"], f"deployment {index} state")
        finished = _nonempty_text(item["finished_at"], f"deployment {index} finished_at")
        parse_time(finished)
        if identity in seen:
            raise ValueError(f"duplicate deployment id: {identity}")
        seen.add(identity)
    return service, captured, deployments
