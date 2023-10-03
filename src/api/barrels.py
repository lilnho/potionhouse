from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy

from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, gold FROM global_inventory"))
    
    row = result.fetchone()
    num_red_ml = row[0]
    gold = row[1]
    
    for i in barrels_delivered:
        if i.sku == "SMALL_RED_BARREL":
            price = i.price
            quantity = i.quantity
            ml_in_barrel = i.ml_per_barrel

    red_ml = (quantity * ml_in_barrel) + num_red_ml
    gold -= (price * quantity)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :red_ml, gold = :gold"), {"red_ml": red_ml, "gold": gold})

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    #print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory"))

    row = result.fetchone()
    num_red_pots = row[0]
    gold = row[1]
    price = 0
    quantity = 0
    
    for i in wholesale_catalog:
        if i.sku == "SMALL_RED_BARREL":
            price = i.price
            quantity = i.quantity
    
    print(price)
    
    num_bought = 0
    
    #buys barrels if have less than 10 pots and have more gold than the price of barrel
    if (num_red_pots < 10) and (gold > price) and (quantity > 0):
        num_bought += 1
        #gold -= price

    
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": num_bought,
        }
    ]
