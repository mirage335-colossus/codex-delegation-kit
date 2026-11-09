from .timeutil import parse_time


def deployment_rank(item):
    """Return the documented timestamp then ID tie-break ordering."""
    return parse_time(item["finished_at"]), item["id"]


def latest_deployment(snapshot):
    if not snapshot["deployments"]:
        return None
    chosen = max(snapshot["deployments"], key=deployment_rank)
    return {key: chosen[key] for key in ("id", "state", "finished_at")}


def build_dashboard(snapshots):
    return {"services": {
        snapshot["service"]: latest_deployment(snapshot)
        for snapshot in sorted(snapshots, key=lambda item: item["service"])
    }}
