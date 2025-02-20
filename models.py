from dataclasses import dataclass, field
from typing import Dict, List, Optional
from flask_login import UserMixin

@dataclass
class Product:
    id: int
    name: str
    price: float
    category: str
    description: str
    image: str = "https://via.placeholder.com/200"

@dataclass
class OrderItem:
    product_id: int
    name: str
    quantity: int
    price: float

@dataclass
class Order:
    id: int
    user_id: str
    items: Dict[str, OrderItem]
    status: str = "pending"

class User(UserMixin):
    def __init__(self, id: str, username: str, email: str, password_hash: str, is_admin: bool = False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)

class DataStore:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[int, Product] = {
            1: Product(
                id=1,
                name="Laptop",
                price=999.99,
                category="Electronics",
                description="High-performance laptop"
            ),
            2: Product(
                id=2,
                name="Smartphone",
                price=499.99,
                category="Electronics",
                description="Latest smartphone"
            ),
            3: Product(
                id=3,
                name="Headphones",
                price=99.99,
                category="Accessories",
                description="Wireless headphones"
            )
        }
        self.orders: Dict[int, Order] = {}
        self.order_counter: int = 1

    def add_user(self, user: User) -> None:
        self.users[user.id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self.users.values() if u.email == email), None)

    def add_product(self, product: Product) -> None:
        self.products[product.id] = product

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def get_products_by_category(self, category: Optional[str] = None) -> List[Product]:
        if category:
            return [p for p in self.products.values() if p.category == category]
        return list(self.products.values())

    def search_products(self, query: str) -> List[Product]:
        query = query.lower()
        return [p for p in self.products.values() if query in p.name.lower()]

    def create_order(self, user_id: str, items: Dict[str, OrderItem]) -> Order:
        order = Order(
            id=self.order_counter,
            user_id=user_id,
            items=items
        )
        self.orders[order.id] = order
        self.order_counter += 1
        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_user_orders(self, user_id: str) -> List[Order]:
        return [o for o in self.orders.values() if o.user_id == user_id]

    def update_order_status(self, order_id: int, status: str) -> bool:
        if order := self.orders.get(order_id):
            order.status = status
            return True
        return False

# Initialize the data store
store = DataStore()
