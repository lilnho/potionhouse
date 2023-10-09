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
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))
    
    row = result.fetchone()
    num_red_ml = row[0]
    num_green_ml = row[1]
    num_blue_ml = row[2]
    gold = row[3]
    
    for i in barrels_delivered:
        if i.sku == "SMALL_RED_BARREL":
            gold -= (i.price * i.quantity)
            num_red_ml += (i.quantity * i.ml_per_barrel)
        elif i.sku == "SMALL_GREEN_BARREL":
            gold -= (i.price * i.quantity)
            num_green_ml += (i.quantity * i.ml_per_barrel)
        elif i.sku == "SMALL_BLUE_BARREL":
            gold -= (i.price * i.quantity)
            num_blue_ml += (i.quantity * i.ml_per_barrel)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :red_ml, num_green_ml = :green_ml, num_blue_ml = :blue_ml, gold = :gold"), {"red_ml": num_red_ml, "green_ml": num_green_ml, "blue_ml": num_blue_ml, "gold": gold})

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    #print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"))

    row = result.fetchone()
    num_red_pots = row[0]
    num_green_pots = row[1]
    num_blue_pots = row[2]
    gold = row[3]
    
    plan = []
    
    num_bought = 0
    
    for i in wholesale_catalog:
        if i.sku == "SMALL_RED_BARREL":
            if (num_red_pots < 10) and (gold > i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                num_bought = 0
        elif i.sku == "SMALL_GREEN_BARREL":
            if (num_green_pots < 10) and (gold > i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                num_bought = 0
        elif i.sku == "SMALL_BLUE_BARREL":
            if (num_blue_pots < 10) and (gold > i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                num_bought = 0
    
    return plan
