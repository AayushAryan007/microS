# api/schema.py
import strawberry
from strawberry.types import Info

@strawberry.type
class Query:
    @strawberry.field
    def user_info(self, info: Info) -> str:
        # Example: Forward request to user_service with JWT
        # Use requests.get('http://user_service/api/user', headers={...})
        return "User info"

schema = strawberry.Schema(query=Query)