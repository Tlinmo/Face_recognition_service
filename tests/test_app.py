import schemathesis
from hypothesis import HealthCheck, settings

from app.settings import settings as stgs

schema = schemathesis.from_uri(f"{stgs.base_url}/api/openapi.json")

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@schema.parametrize()
async def test_api(case, auth_token):
    if not case.headers:
        case.headers = {}
        
    case.headers["Authorization"] = f"Bearer {auth_token}"
    response = case.call()
    case.validate_response(response)

