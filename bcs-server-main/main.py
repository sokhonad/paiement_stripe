import os
from collections import Counter
from typing import List, Optional

import stripe
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Request,
                     Response)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database import Base, SessionLocal, engine
from models import Customer, Item, Payment, PurchasedItem
from schemas import (AddItemSchema, CustomerSchema, ItemSchema,
                     PaymentCheckSchema, PaymentCreateSchema, PaymentSchema,
                     PaymentSheetSchema)

Base.metadata.create_all(bind=engine)

origins = ['*']


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sk_stripe: str = os.environ.get("STRIPE_SK")
pk_stripe: str = os.environ.get("STRIPE_PK")
stripe.api_key = sk_stripe


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


def get_db(request: Request):
    return request.state.db


item_router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


@item_router.post("/", response_model=ItemSchema)
def add_item(
    item: AddItemSchema,
    db: Session = Depends(get_db)
):
    db_item: Item = Item(**item.dict())

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


@item_router.get("/{item_id}", response_model=Optional[ItemSchema])
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item: Optional[Item] = db.query(Item).filter(Item.id == item_id).first()

    return item


@item_router.delete("/", response_model=Optional[ItemSchema])
def remove_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item: Optional[Item] = db.query(Item).filter(Item.id == item_id).first()
    db.delete(item)
    db.commit()
    
    return item


payments_router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@payments_router.get('/', response_model=List[PaymentSchema])
def get_payments(
    db: Session = Depends(get_db)
):
    payments: List[Payment] = db.query(Payment).all()

    return payments

@payments_router.get('/{customer_id}', response_model=List[PaymentSchema])
def get_payments_by_customer_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    payments: List[Payment] = db.query(Payment).filter(Payment.customer_id == customer_id).all()

    return payments


@payments_router.post('/', response_model=PaymentSheetSchema)
def create_sheet(
    payment_sheet: PaymentCreateSchema,
    db: Session = Depends(get_db)
):
    customer: Optional[Customer] = db.query(Customer).filter(Customer.id == payment_sheet.customer_id).first()

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found.")

    ephemeral_key = stripe.EphemeralKey.create(
        customer=customer.stripe_id,
        stripe_version='2022-08-01',
    )

    customer_stripe = stripe.Customer.retrieve(
        customer.stripe_id
    )

    payment_intent = stripe.PaymentIntent.create(
        amount=payment_sheet.amount,
        currency='eur',
        customer=customer_stripe,
        automatic_payment_methods={
            'enabled': True,
        },
    )

    payment: Payment = Payment(
        id=payment_intent.id,
        customer_id=payment_sheet.customer_id
    )

    db.add(payment)
    db.commit()

    return {
        "paymentIntent": payment_intent.client_secret,
        "ephemeralKey": ephemeral_key.secret,
        "customer": customer_stripe["id"],
        "publishableKey": pk_stripe
    }


@payments_router.post('/check/{payment_intent_id}')
def check_sheet_status_and_get_purchased_items(
    payment_intent_id: str,
    payment_check: PaymentCheckSchema,
    db: Session = Depends(get_db)
):
    payment: Optional[Payment] = db.query(Payment).filter(
        Payment.customer_id == payment_check.customer_id,
        Payment.id == payment_intent_id,
        Payment.is_checked == False
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or already checked.")

    payment_intent = stripe.PaymentIntent.retrieve(
        payment_intent_id
    )

    if not payment_intent:
        raise HTTPException(status_code=404, detail="Payment intent not found.")

    if not payment_intent.status == "succeeded":
        raise HTTPException(status_code=404, detail="Unsuccessful payment intent.")

    amount: int = payment_intent.amount_received

    items: List[Item] = db.query(Item).filter(Item.id.in_(payment_check.items_id)).all()
    counter_items: Counter = Counter(payment_check.items_id)

    price: int = sum([i.price * counter_items[i.id] for i in items])

    # vérification du prix par rapport au montant payé
    if not price == amount:
        print(price, amount)
        raise HTTPException(status_code=404, detail="Price does not match with amount paid.")

    # ajout des items achetés à la pool
    purchased_items: List[PurchasedItem] = []
    for item in items:
        for j in range(1, counter_items[item.id] + 1):
            purchased_item: PurchasedItem = PurchasedItem(
                customer_id=payment_check.customer_id,
                item_id=item.id,
                payment_id=payment.id
            )
            purchased_items.append(purchased_item)
            db.add(purchased_item)

    # validation du paiement pour éviter une fraude
    payment.is_checked = True

    db.add(payment)
    db.commit()

    for purchased_item in purchased_items:
        db.refresh(purchased_item)

    return {
        "purchased_items": [i.item for i in purchased_items] 
    }


customers_router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@customers_router.get('/', response_model=List[CustomerSchema])
def get_customers(
    db: Session = Depends(get_db)
):
    return db.query(Customer).all()


@customers_router.get('/{customer_id}', response_model=Optional[CustomerSchema])
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Customer).filter(Customer.id == customer_id).first()


@customers_router.post('/')
def add_customer(
    db: Session = Depends(get_db)
):
    customer = stripe.Customer.create()

    customer_db: Customer = Customer(stripe_id=customer["id"])
    db.add(customer_db)
    db.commit()
    db.refresh(customer_db)

    return customer_db


app.include_router(item_router)
app.include_router(payments_router)
app.include_router(customers_router)

