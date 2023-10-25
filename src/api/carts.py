from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum


import sqlalchemy

from src import database as db


carts = {}

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


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
        
        gold_res = connection.execute(sqlalchemy.text("SELECT SUM(gold_transactions) FROM ledgers")).fetchone()
        gold_before = gold_res[0]
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
                INSERT INTO ledgers (created_at, carts_id, potions_id, potion_transactions, gold_transactions)
                SELECT now(), :cart_id, potions.id, (-1) * cart_items.quantity, potions.price * cart_items.quantity
                FROM potions
                JOIN cart_items ON potions.id = cart_items.potions_id
                WHERE cart_items.carts_id = :cart_id
                """
                ), [{"cart_id": cart_id}]
            )

        gold_after = connection.execute(sqlalchemy.text("SELECT SUM(gold_transactions) FROM ledgers")).fetchone()[0]
        gold_gained = gold_after - gold_before
        
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM cart_items
            WHERE carts_id = :carts_id
            """
            ),
            [{"carts_id": cart_id}]
            )    


    return {"total_potions_bought": potion_total, "total_gold_paid": gold_gained}
