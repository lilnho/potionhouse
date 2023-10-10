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
        ml_result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))
    with db.engine.begin() as connection:
        pot_result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
    
    pot_row = pot_result.fetchone() 
    ml_row = ml_result.fetchone()  
    
    num_pots =  pot_row[0] + pot_row[1] + pot_row[2]
    num_ml = ml_row[0] + ml_row[1] + ml_row[2]
    gold = ml_row[3]

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
