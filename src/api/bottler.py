from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy

from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    
    with db.engine.begin() as connection:
        red_result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml FROM global_inventory"))

    with db.engine.begin() as connection:
        green_result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory"))

    with db.engine.begin() as connection:
        blue_result = connection.execute(sqlalchemy.text("SELECT num_blue_potions, num_blue_ml FROM global_inventory"))

    #red potion data
    red = red_result.fetchone()
    num_red_pots = red[0]
    num_red_ml = red[1]
    
    #green potion data
    green = green_result.fetchone()
    num_green_pots = green[0]
    num_green_ml = green[1]

    #blue potion data
    blue = blue_result.fetchone()
    num_blue_pots = blue[0]
    num_blue_ml = blue[1]

    
    for i in potions_delivered:
        #check red pots
        if (i.potion_type == [100, 0, 0, 0]):
            num_red_ml -= (i.quantity * 100)
            num_red_pots += i.quantity
        #check green pots
        if i.potion_type == [0, 100, 0, 0]:
            num_green_ml -= (i.quantity * 100)
            num_green_pots += i.quantity
        #check blue pots
        if i.potion_type == [0, 0, 100, 0]:
            num_blue_ml -= (i.quantity * 100)
            num_blue_pots += i.quantity
    
    #update red data
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_pots, num_red_ml = :red_ml"), {"red_pots": num_red_pots, "red_ml": num_red_ml})

    #update green data
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :green_pots, num_green_ml = :green_ml"), {"green_pots": num_green_pots, "green_ml": num_green_ml})

    #update blue data
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :blue_pots, num_blue_ml = :blue_ml"), {"blue_pots": num_blue_pots, "blue_ml": num_blue_ml})

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))


    #red potion data
    row = result.fetchone()
    num_red_pots = 0
    num_red_ml = row[0]
    
    #green potion data
    num_green_pots = 0
    num_green_ml = row[1]

    #blue potion data
    num_blue_pots = 0
    num_blue_ml = row[2]
    
    #calculate red potions to be made
    while num_red_ml >= 100:
        num_red_ml -= 100
        num_red_pots += 1

    #calculate green potions to be made
    while num_green_ml >= 100:
        num_green_ml -= 100
        num_green_pots += 1    

    #calculate blue potions to be made
    while num_blue_ml >= 100:
        num_blue_ml -= 100
        num_blue_pots += 1
        
    bottles = []
    
    if num_red_pots > 0:
        bottles.append(
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": num_red_pots,
                }
        )
    if num_green_pots > 0:
        bottles.append(
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": num_green_pots,
                }
        )
    if num_blue_pots > 0:
        bottles.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": num_blue_pots,
                }
        )

    return bottles
