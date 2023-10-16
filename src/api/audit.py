from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy

from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        pot_result = connection.execute(sqlalchemy.text("SELECT inventory FROM potions"))
        
        global_result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold FROM global_inventory"))
    
    potion = pot_result.fetchall()
    glo = global_result.fetchone()
    
    num_pots = 0
    num_ml = glo[0] + glo[1] + glo[2]
    gold = glo[3]
    
    for pot in potion:
        num_pots += pot[0]

    return {"number_of_potions": num_pots, "ml_in_barrels": num_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
