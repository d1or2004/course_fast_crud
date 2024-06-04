from database import Base
from sqlalchemy import Column, Integer, Boolean, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(27), unique=True)
    email = Column(String(40), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    order = relationship("Order", back_populates="user")  # one-to-many

    def __repr__(self):
        return f"< User {self.username} >"


class Order(Base):
    ORDER_STATUS = (
        ("PENDING", "pending"),
        ("IN_TRANSIT", "in_transit"),
        ("DELIVERED", "delivered")
    )
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=True)
    order_status = Column(ChoiceType(choices=ORDER_STATUS), default="PENDING")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates='order')  # many-to-one
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="order")

    def __repr__(self):
        return f"< Order {self.id} >"


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    order = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"< Product {self.name} >"
