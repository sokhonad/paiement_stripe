from typing import List, Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: int

    class Config:
        orm_mode = True


class ItemSchema(ItemBase):
    id: int

    class Config:
        orm_mode = True


class AddItemSchema(ItemBase):
    pass


class RemoveItemSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class PaymentSheetSchema(BaseModel):
    paymentIntent: str
    ephemeralKey: str
    customer: str
    publishableKey: str


class PaymentCheckSchema(BaseModel):
    items_id: List[int]
    customer_id: int


class PaymentCreateSchema(BaseModel):
    amount: int
    customer_id: int


class CustomerSchema(BaseModel):
    id: int
    stripe_id: str

    class Config:
        orm_mode = True


class PurchasedItem(BaseModel):
    item: Optional[ItemSchema]

    class Config:
        orm_mode = True


class PaymentSchema(BaseModel):
    id: str
    is_checked: bool
    customer: Optional[CustomerSchema]
    purchased_items: List[PurchasedItem]

    class Config:
        orm_mode = True