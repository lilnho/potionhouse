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

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

    row = result.fetchone()
    num_red_pots = row[0]
    num_red_ml = row[1]
    gold = row[2]
    
    purchase_plan = []
    if num_red_pots < 10:
        purchase_plan.append(
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        })


    print(wholesale_catalog)
    
    return purchase_plan
'''
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]
'''