from fastapi import APIRouter

import sqlalchemy

from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT sku, name, inventory, price, potion_type
                FROM potions
                WHERE inventory > 0
                """
            )
            )
    catalog = []


    pots = result.fetchall()
    for i in pots:
        catalog.append(
                {
                    "sku": i[0],
                    "name": i[1],
                    "quantity": i[2],
                    "price": i[3],
                    "potion_type": i[4],
                }
        )
    
    return catalog