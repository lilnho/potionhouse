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
        totals = connection.execute(
            sqlalchemy.text(
                """
                SELECT SUM(gold_transactions) AS gold, SUM(ml_transactions) AS ml, SUM(potion_transactions) AS pots
                FROM ledgers
                """))
    
    totals_row = totals.fetchone()
    
    gold = totals_row[0]
    num_ml = totals_row[1]
    num_pots = totals_row[2]

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
