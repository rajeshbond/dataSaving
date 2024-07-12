from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter , BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
from .. import models
from ..functions.chartink import trasferDataToGoogleSheet
import requests,json, datetime
from ..database import get_db

router = APIRouter(
    prefix= '/screener',
     tags=["Screener"]
)

@router.get("/api/screenerfetch")
async  def screenerfetch():
    try:
        trasferDataToGoogleSheet()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "code start Running"}

