from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer, default=0)

    purchased_items = relationship("PurchasedItem")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    stripe_id = Column(String)

    purchased_items = relationship("PurchasedItem")
    payments = relationship("Payment")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, autoincrement=False, index=True)
    is_checked = Column(Boolean, default=False)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="payments")

    purchased_items = relationship("PurchasedItem")


class PurchasedItem(Base):
    __tablename__ = "purchased_items"
    
    id = Column(Integer, primary_key=True, index=True)

    payment_id = Column(Integer, ForeignKey("payments.id"))
    payment = relationship("Payment", back_populates="purchased_items")
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="purchased_items") 
    
    item_id = Column(Integer, ForeignKey("items.id"))
    item = relationship("Item", back_populates="purchased_items") 
