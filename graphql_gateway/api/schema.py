# api/schema.py
import strawberry
from typing import List
import requests
from django.conf import settings
import typing


ORDER_SERVICE_URL = "http://localhost:8002"

@strawberry.type
class UserType:
    id: str
    name: str
    email: str

@strawberry.type
class ProductType:
    id: str
    name: str
    description: str
    price: float
    stock: int

@strawberry.type
class OrderType:
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str
    total_price: float
    created_at: str
    updated_at: str

@strawberry.type
class OrderCreatePayload:
    message: str
    orderId: typing.Optional[str] = None

@strawberry.type
class AuthPayload:
    success: bool
    message: str
    token: typing.Optional[str] = None

def get_headers(info):
    # Forward the Authorization header
    request = info.context["request"]
    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]
    return headers

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        print("Non-JSON response:", resp.text)
        return {}

@strawberry.type
class Query:
    @strawberry.field
    def users(self, info) -> List[UserType]:
        resp = requests.get(f"{settings.USER_SERVICE_URL}/users/", headers=get_headers(info))
        resp.raise_for_status()
        return [UserType(**user) for user in resp.json()]

    @strawberry.field
    def products(self, info) -> List[ProductType]:
        resp = requests.get(f"{settings.INVENTORY_SERVICE_URL}/products/", headers=get_headers(info))
        resp.raise_for_status()
        return [ProductType(**prod) for prod in resp.json()]

    @strawberry.field
    def orders(self, info) -> List[OrderType]:
        resp = requests.get(f"{settings.ORDER_SERVICE_URL}/orders/", headers=get_headers(info))
        resp.raise_for_status()
        orders = resp.json()
        for order in orders:
            order["total_price"] = float(order["total_price"])  # Ensure float type
        return [OrderType(**order) for order in orders]
 
    @strawberry.field
    def landing(self, info) -> str:
        resp = requests.get(f"{settings.USER_SERVICE_URL}/landing/", headers=get_headers(info))
        resp.raise_for_status()
        return resp.text  # or parse JSON if landing returns structured data

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info, email: str, password: str) -> AuthPayload:
        resp = requests.post(
            f"{settings.USER_SERVICE_URL}/api/signin/",
            json={"email": email, "password": password}
        )
        data = safe_json(resp)
        if resp.status_code == 200 and "access" in data:
            return AuthPayload(success=True, message="Login successful", token=data.get("access"))
        return AuthPayload(success=False, message=data.get("error", resp.text))

    @strawberry.mutation
    def signup(self, info, name: str, email: str, password: str) -> AuthPayload:
        resp = requests.post(
            f"{settings.USER_SERVICE_URL}/api/signup/",
            json={"name": name, "email": email, "password": password}
        )
        data = safe_json(resp)
        if resp.status_code == 200 and "user_id" in data:
            return AuthPayload(success=True, message="Signup successful", token=data.get("user_id"))
        return AuthPayload(success=False, message=data.get("error", resp.text))
    
    @strawberry.mutation
    def createOrder(self, info, productId: str, quantity: int) -> OrderCreatePayload:
        resp = requests.post(
            f"{ORDER_SERVICE_URL}/create-order/",
            json={"product_id": productId, "quantity": quantity},
            headers=get_headers(info)
        )
        if resp.status_code == 200:
            data = resp.json()
            return OrderCreatePayload(message=data.get("message", ""), orderId=data.get("order_id"))
        elif resp.status_code == 401:
            return OrderCreatePayload(message="Not authenticated", orderId=None)
        else:
            return OrderCreatePayload(message=resp.text, orderId=None)

schema = strawberry.Schema(query=Query, mutation=Mutation)