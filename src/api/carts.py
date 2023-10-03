from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth


import sqlalchemy

from src import database as db


carts = {}

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    global carts
    
    cart_id = len(carts) + 1
    carts[cart_id] = []
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    cart = carts[cart_id]
    return cart
    #return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    global carts

    quantity = cart_item.quantity
    
    for i in carts[cart_id]:
        if item_sku == i[0]:
            i[1] = quantity
            return "OK"
    
    carts[cart_id].append([item_sku, quantity])
    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    global carts

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory"))

    row = result.fetchone()
    
    num_red_pots = row[0]
    gold = row[1]
    
    gold_gained = 0
    
    
    #pots_bought = carts[cart_id][0][1]
    pots_bought = 0
    
    for i in carts[cart_id]:
        while i[1] > 0 and num_red_pots > 0:
            pots_bought += 1
            gold_gained += 50
            num_red_pots -= 1
            i[1] -= 1
    
    gold += gold_gained
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_pots, gold = :gold"), {"red_pots": num_red_pots, "gold": gold})

    
    
    carts.pop(cart_id)

    return {"total_potions_bought": pots_bought, "total_gold_paid": gold_gained}
