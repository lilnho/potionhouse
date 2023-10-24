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
        additional_pots = sum(potion.quantity for potion in potions_delivered)
        red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

        for pot in potions_delivered:
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO ledgers (created_at, potions_id, potion_transactions)
            SELECT now(), potions.id, :additional_pots
            FROM potions
            WHERE potions.potion_type = :potion_type
            """  
            ), 
            [{
            "additional_pots": pot.quantity,
            "potion_type": pot.potion_type
            }]
            )
        
        pots = [red_ml, green_ml, blue_ml, dark_ml]
        ml_type = 1
        for i in pots:
            if i > 0:
                connection.execute(
                    sqlalchemy.text(
                    """
                    INSERT INTO ledgers (created_at, barrels_id, ml_transactions)
                    VALUES (now(), :ml_type, :ml_transactions)
                    """
                ),
                [{"ml_type": ml_type, "ml_transactions": (-1) * i}]
            )
            ml_type += 1
        
        
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
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT barrels_id, SUM(ml_transactions) 
                FROM ledgers
                WHERE barrels_id IS NOT NULL
                GROUP BY barrels_id
                """))

        potions = connection.execute(
            sqlalchemy.text(
                """
                SELECT potion_type
                FROM potions
                ORDER BY inventory ASC
                """
            ))

    #potion data
    rows = result.fetchall()
    barrel_mls = [0, 0, 0, 0]
    for barrel in rows:
        barrel_mls[barrel[0]] += barrel[1]
    
    combos = potions.fetchall()

    print(combos)

    red_ml = barrel_mls[0]
    green_ml = barrel_mls[1]
    blue_ml = barrel_mls[2]
    dark_ml = barrel_mls[3]
        
    bottles = []
   
    print("red ml: ", red_ml)
    print("green ml: ", green_ml)
    print("blue ml: ", blue_ml)
    print("dark ml: ", dark_ml)

    
    #while there are still at least 100 mls of a potion left
    #may need to add more/different conditions for the other combos
    while (red_ml >= 100) or (green_ml >= 100) or (blue_ml >= 100) or (dark_ml >= 100):
        #loop through every potion type combo
        for p in combos:
            pot_type = p[0]
            print(pot_type)
            
            #check that there is enough ml for the potion type
            if (red_ml >= pot_type[0]) and (green_ml >= pot_type[1]) and (blue_ml >= pot_type[2]) and (dark_ml >= pot_type[3]):
                #check if the potion has already been put into the list
                if any(pot["potion_type"] == pot_type for pot in bottles):
                    for pot in bottles:
                        if pot["potion_type"] == pot_type:
                            pot["quantity"] += 1
                            break
                else:
                    bottles.append(
                        {
                            "potion_type": pot_type,
                            "quantity": 1,
                        }
                    )
                red_ml -= pot_type[0]
                green_ml -= pot_type[1]
                blue_ml -= pot_type[2]
                dark_ml -= pot_type[3]
                
    print("red ml after: ", red_ml)
    print("green ml after: ", green_ml)
    print("blue ml after: ", blue_ml)
    print("dark ml after: ", dark_ml)
    
                    
    return bottles
