from backend.ml.similar_incidents import (
    get_similar_incidents
)

from backend.ml.explain_prediction import (
    explain_prediction
)

similar = get_similar_incidents(
    "VPN connection failed for multiple users"
)

print(
    explain_prediction(
        similar
    )
)