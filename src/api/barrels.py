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
    
    print("Inventory before barrel delivery: red ml = {}, green ml = {}, blue ml = {}, gold = {}".format(num_red_ml, num_green_ml, num_blue_ml, gold))
    
    '''
    for i in barrels_delivered:
        if (i.sku == "SMALL_RED_BARREL") and (gold > (i.price * i.quantity)):
            gold -= (i.price * i.quantity)
            num_red_ml += (i.quantity * i.ml_per_barrel)
        elif (i.sku == "SMALL_GREEN_BARREL") and (gold > (i.price * i.quantity)):
            gold -= (i.price * i.quantity)
            num_green_ml += (i.quantity * i.ml_per_barrel)
        elif i.sku == ("SMALL_BLUE_BARREL") and (gold > (i.price * i.quantity)):
            gold -= (i.price * i.quantity)
            num_blue_ml += (i.quantity * i.ml_per_barrel)
    '''
    
    for i in barrels_delivered:
        if (i.sku == "SMALL_RED_BARREL") and (gold >= i.price)  and (i.quantity > 0):
             gold -= i.price
             num_red_ml += i.ml_per_barrel
        elif (i.sku == "SMALL_GREEN_BARREL") and (gold >= i.price)  and (i.quantity > 0):
             gold -= i.price
             num_green_ml += i.ml_per_barrel
        elif (i.sku == "SMALL_BLUE_BARREL") and (gold >= i.price)  and (i.quantity > 0):
             gold -= i.price
             num_blue_ml += i.ml_per_barrel  
                       
    print("Inventory after barrel delivery: red ml = {}, green ml = {}, blue ml = {}, gold = {}".format(num_red_ml, num_green_ml, num_blue_ml, gold))

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :red_ml, num_green_ml = :green_ml, num_blue_ml = :blue_ml, gold = :gold"), {"red_ml": num_red_ml, "green_ml": num_green_ml, "blue_ml": num_blue_ml, "gold": gold})

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    print("catalog in barrel purchase plan: ")
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"))

    row = result.fetchone()
    num_red_pots = row[0]
    num_green_pots = row[1]
    num_blue_pots = row[2]
    gold = row[3]
    
    plan = []
    
    num_bought = 0
    total_bought = 0
    
    print("Potion Inventory before barrel purchase plan: red pots = {}, green pots = {}, blue pots = {}, gold = {}".format(num_red_pots, num_green_pots, num_blue_pots, gold))
    
    for i in wholesale_catalog:
        if i.sku == "SMALL_RED_BARREL":
            if (num_red_pots < 10) and (gold >= i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                gold -= i.price
                num_bought = 0
                total_bought += 1
        elif i.sku == "SMALL_GREEN_BARREL":
            if (num_green_pots < 10) and (gold >= i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                gold -= i.price
                num_bought = 0
                total_bought += 1
        elif i.sku == "SMALL_BLUE_BARREL":
            if (num_blue_pots < 10) and (gold >= i.price) and (i.quantity > 0):
                num_bought += 1
                plan.append({
                    "sku": i.sku,
                    "quantity": num_bought,
                })
                gold -= i.price
                num_bought = 0
                total_bought += 1
    
    print("Potion Inventory after barrel purchase plan: potions bought {}, gold = {}".format(total_bought, gold))
    print("Purchase plan: ")
    print(plan)
    
    
    return plan
