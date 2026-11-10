def match_requests(connection, requests):
    result = []
    for request in requests:
        rows = connection.execute(
            "SELECT DISTINCT p.sku FROM products p JOIN aliases a ON a.sku=p.sku "
            "WHERE a.alias=? AND p.region=? AND p.active=1 "
            "ORDER BY p.price_cents, p.sku LIMIT ?",
            (request["term"].strip().casefold(), request["region"], request["limit"]),
        ).fetchall()
        result.append({"request": request["id"], "skus": [row[0] for row in rows]})
    return result
