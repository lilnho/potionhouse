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
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO carts
                (customer)
                VALUES 
                (:customer)
                RETURNING id
                """
                ),
            {"customer": new_cart.customer}
            )
    cart_id = result.scalar()
    return {"cart_id": cart_id}
    
@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * 
                FROM carts 
                WHERE id = (:cart_id)
                """
            ),
            {"cart_id": cart_id}
            ).fetchone()
    return {"id": result[0], "customer": result[1]}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart_items (carts_id, potions_id, quantity)
                SELECT :cart_id, potions.id, :quantity
                FROM potions WHERE potions.sku = :item_sku
                """
            ), 
            [{"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku}]
            )
    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    
    potion_total = 0

    with db.engine.begin() as connection:
        
        gold_res = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        gold_before = gold_res.scalar_one()
        potion_rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT quantity 
                FROM cart_items 
                WHERE cart_items.carts_id = :carts_id
                """),
                [{"carts_id": cart_id}]
                ).fetchall()
        potion_total = sum(potion[0] for potion in potion_rows)
        

        connection.execute(
            sqlalchemy.text(
                """
                UPDATE potions
                SET inventory = potions.inventory - cart_items.quantity
                FROM cart_items
                WHERE potions.id = cart_items.potions_id and cart_items.carts_id = :cart_id
                """
                ), [{"cart_id": cart_id}]
            )
    
        #add potion price * potion quantity to gold
        gold_total_res = connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory 
                SET gold = global_inventory.gold + 
                (
                SELECT SUM(potions.price * cart_items.quantity)
                FROM potions 
                JOIN cart_items ON potions.id = cart_items.potions_id 
                WHERE cart_items.carts_id = :cart_id
                )
                RETURNING gold
                """
                ), 
            [{"cart_id": cart_id}])
        
        gold_total = gold_total_res.scalar_one()

        gold_gained = gold_total - gold_before
        
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM cart_items
            WHERE carts_id = :carts_id
            """
            ),
            [{"carts_id": cart_id}]
            )    


    return {"total_potions_bought": potion_total, "total_gold_paid": gold_gained}
