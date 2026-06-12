from backend.ml.similar_incidents import (
    get_similar_incidents
)

results = get_similar_incidents(
    "VPN connection failed for multiple users"
)

for r in results:
    print(r)