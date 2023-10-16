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
    """    
    num_red_ml = 0
    num_green_ml = 0
    num_blue_ml = 0
    
    num_red_pots = 0
    num_green_pots = 0
    num_blue_pots = 0
    
    for pot in potions_delivered:
        #check red pots
        if (pot.potion_type == [100, 0, 0, 0]):
            num_red_ml += (pot.quantity * 100)
            num_red_pots += pot.quantity
        #check green pots
        elif pot.potion_type == [0, 100, 0, 0]:
            num_green_ml += (pot.quantity * 100)
            num_green_pots += pot.quantity
        #check blue pots
        elif pot.potion_type == [0, 0, 100, 0]:
            num_blue_ml += (pot.quantity * 100)
            num_blue_pots += pot.quantity  
    
    #update data
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                ""
                UPDATE global_inventory 
                SET num_red_potions = num_red_potions + :red_pots, num_red_ml = num_red_ml - :red_ml, 
                num_green_potions = num_green_potions + :green_pots, num_green_ml = num_green_ml - :green_ml, 
                num_blue_potions = num_blue_potions + :blue_pots, num_blue_ml = num_blue_ml - :blue_ml
                ""
                ), 
                [{
                    "red_pots": num_red_pots, 
                    "red_ml": num_red_ml,
                    "green_pots": num_green_pots,
                    "green_ml": num_green_ml,
                    "blue_pots": num_blue_pots,
                    "blue_ml": num_blue_ml
                }])
    """
    
    with db.engine.begin() as connection:
        additional_pots = sum(potion.quantity for potion in potions_delivered)
        red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

        for pot in potions_delivered:
            connection.execute(sqlalchemy.text(
             """
             UPDATE potions
             SET inventory = inventory + :additional_pots
             WHERE type = :potion_type
             """  
            ), 
            [{
            "additional_pots": pot.quantity,
            "potion_type": pot.potion_type
            }]
            )
        
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET
                num_red_ml = num_red_ml - :red_ml,
                num_green_ml = num_green_ml - :green_ml,
                num_blue_ml = num_blue_ml - :blue_ml,
                num_dark_ml = num_dark_ml - :dark_ml
                """
            ),
            [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml}]
        )
        
        
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
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory"))


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
    
    #dark potion data
    num_dark_pots = 0
    num_dark_ml = row[3]
    
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
        
    while num_dark_ml >= 100:
        num_dark_ml -= 100
        num_dark_pots += 1
        
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
    if num_dark_pots > 0:
        bottles.append(
            {
                "potion_type": [0, 0, 0, 100],
                "quantity": num_blue_pots,
            }
        )


    return bottles
