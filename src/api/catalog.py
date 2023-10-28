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
                SELECT potions.sku, potions.name, SUM(ledgers.potion_transactions), potions.price, potions.potion_type
                FROM ledgers
                JOIN potions on ledgers.potions_id = potions.id
                GROUP BY potions.id
                """
            )
            )
    catalog = []


    pots = result.fetchall()
    for i in pots:
        if i[2] > 0:
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