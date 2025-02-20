from dataclasses import dataclass, field
from typing import Dict, List, Optional
from flask_login import UserMixin
from datetime import datetime

@dataclass
class Product:
    id: int
    name: str
    price: float
    seller_id: str
    category: str
    description: str
    file_type: str  # e.g., "pdf", "video", "audio", "software"
    preview_image: str = "https://via.placeholder.com/200"
    additional_images: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OrderItem:
    product_id: int
    name: str
    quantity: int
    price: float
    seller_id: str

@dataclass
class Order:
    id: int
    user_id: str
    items: Dict[str, OrderItem]
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)

class User(UserMixin):
    def __init__(self, id: str, username: str, email: str, password_hash: str, is_admin: bool = False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()

    def get_id(self):
        return str(self.id)

class DataStore:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[int, Product] = {
            1: Product(
                id=1,
                name="Digital Marketing Guide",
                price=29.99,
                seller_id="admin",
                category="E-Books",
                description="Comprehensive digital marketing strategy guide",
                file_type="pdf"
            ),
            2: Product(
                id=2,
                name="Stock Trading Course",
                price=99.99,
                seller_id="admin",
                category="Courses",
                description="Learn stock market trading fundamentals",
                file_type="video"
            ),
            3: Product(
                id=3,
                name="Meditation Music Pack",
                price=19.99,
                seller_id="admin",
                category="Audio",
                description="Collection of calming meditation tracks",
                file_type="audio"
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

    def get_seller_products(self, seller_id: str) -> List[Product]:
        return [p for p in self.products.values() if p.seller_id == seller_id]

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

    def get_seller_orders(self, seller_id: str) -> List[Order]:
        return [o for o in self.orders.values() 
                if any(item.seller_id == seller_id for item in o.items.values())]

    def update_order_status(self, order_id: int, status: str) -> bool:
        if order := self.orders.get(order_id):
            order.status = status
            return True
        return False

# Initialize the data store
store = DataStore()