from fastapi import APIRouter

import sqlalchemy

from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
    
    row = result.fetchone()
    red_pots = row[0]
    green_pots = row[1]
    blue_pots = row[2]
    
    catalog = []
    
    if red_pots > 0:
        catalog.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": red_pots,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
        )
    if green_pots > 0:
        catalog.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": green_pots,
                    "price": 20,
                    "potion_type": [0, 100, 0, 0],
                }
        )
    if blue_pots > 0:
        catalog.append(
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": blue_pots,
                    "price": 20,
                    "potion_type": [0, 0, 100, 0],
                }
        )

    return catalog