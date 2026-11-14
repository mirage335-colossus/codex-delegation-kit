#!/usr/bin/env python3
"""Check the great-circle scale/bearing of the published HF-TEP endpoints.

Coordinates are transcribed from Maruyama & Kawamura (2006), §2. This is a
spherical endpoint-geometry check only; it does not infer reflection points,
hop count, ray length, or a communications channel.
"""

from math import asin, atan2, cos, degrees, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0
ORAI_LAT_LON_DEG = (36.3, 140.6)
SHEPPARTON_LAT_LON_DEG = (-36.2, 145.3)

lat1, lon1 = map(radians, ORAI_LAT_LON_DEG)
lat2, lon2 = map(radians, SHEPPARTON_LAT_LON_DEG)
dlat, dlon = lat2 - lat1, lon2 - lon1
a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
central_angle = 2 * asin(sqrt(a))
distance_km = EARTH_RADIUS_KM * central_angle
bearing_deg = (
    degrees(
        atan2(
            sin(dlon) * cos(lat2),
            cos(lat1) * sin(lat2)
            - sin(lat1) * cos(lat2) * cos(dlon),
        )
    )
    + 360
) % 360
east_of_due_south_deg = 180 - bearing_deg

print(f"spherical_radius_km={EARTH_RADIUS_KM:.1f}")
print(f"central_angle_deg={degrees(central_angle):.3f}")
print(f"great_circle_distance_km={distance_km:.1f}")
print(f"initial_bearing_from_Oarai_deg_clockwise_from_north={bearing_deg:.2f}")
print(f"offset_from_due_south_deg={east_of_due_south_deg:.2f}")
print("source_reports_approx_distance_km=8000")
print("source_reports_bearing_offset_deg_east_of_due_south=4.3")
print("endpoint_geometry_check_only; no ionospheric_path_or_hop_inference")
