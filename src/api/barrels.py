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
    
    gold_paid = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    
    for barrels in barrels_delivered:
        gold_paid += barrels.price * barrels.quantity
        if barrels.potion_type == [1, 0, 0, 0]:
            red_ml += barrels.ml_per_barrel * barrels.quantity
        elif barrels.potion_type == [0, 1, 0, 0]:
            green_ml += barrels.ml_per_barrel * barrels.quantity
        elif barrels.potion_type == [0, 0, 1, 0]:
            blue_ml += barrels.ml_per_barrel * barrels.quantity
        elif barrels.potion_type == [0, 0, 0, 1]:
            dark_ml += barrels.ml_per_barrel * barrels.quantity
        else:
            raise Exception("Invalid potion type")

    print(f"gold paid: {gold_paid}, red ml: {red_ml}, green ml: {green_ml}, blue ml: {blue_ml}, dark ml: {dark_ml}")
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory SET 
            num_red_ml = num_red_ml + :red_ml, 
            num_green_ml = num_green_ml + :green_ml, 
            num_blue_ml = num_blue_ml + :blue_ml, 
            num_dark_ml = num_dark_ml + :dark_ml,
            gold = gold - :gold
            """), 
        [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml, "gold": gold_paid}])


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    print("catalog in barrel purchase plan: ")
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    row = result.fetchone()
    gold = row[0]
    
    plan = []
    
    total_bought = 0
    
    red_bought = 0
    green_bought = 0
    blue_bought = 0
    dark_bought = 0
    
    for i in wholesale_catalog:
        if (i.potion_type == [1, 0, 0, 0]) and (red_bought == 0):
            #add condition of if gold > price + 50 or however much the largest barrels are maybe
            if (gold >= i.price) and (i.quantity > 0):
                plan.append({
                    "sku": i.sku,
                    "quantity": 1,
                })
                gold -= i.price
                total_bought += 1
                red_bought += 1
        elif (i.potion_type == [0, 1, 0, 0]) and (green_bought == 0):
            if (gold >= i.price) and (i.quantity > 0):
                plan.append({
                    "sku": i.sku,
                    "quantity": 1,
                })
                gold -= i.price
                total_bought += 1
                green_bought += 1
        elif (i.potion_type == [0, 0, 1, 0]) and (blue_bought == 0):
            if (gold >= i.price) and (i.quantity > 0):
                plan.append({
                    "sku": i.sku,
                    "quantity": 1,
                })
                gold -= i.price
                total_bought += 1
                blue_bought += 1
        elif (i.potion_type == [0, 0, 0, 1]) and (dark_bought == 0):
            if (gold >= i.price) and (i.quantity > 0):
                plan.append({
                    "sku": i.sku,
                    "quantity": 1,
                })
                gold -= i.price
                total_bought += 1
                dark_bought += 1
    
    print("Potion Inventory after barrel purchase plan: potions bought {}, gold = {}".format(total_bought, gold))
    print("Purchase plan: ")
    print(plan)
    
    
    return plan
