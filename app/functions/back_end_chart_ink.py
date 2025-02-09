import time
import requests
from fastapi import Response, status, HTTPException, Depends, APIRouter
from bs4 import BeautifulSoup as bs
import pandas as pd
import pytz, datetime, os
import asyncio
from pprint import pprint
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from sqlalchemy import text, column
from sqlalchemy.sql import select

# from google_sheet import clean_up, update_google_sheet,update_cell
# t.me/CompoundingFunda_bot
URL = 'https://chartink.com/screener/process'

def scandata(condition, conditionName):
    try:
        db = next(get_db())
        symbol_df = pd.read_sql(db.query(models.Symbol).statement, db.bind)
        
        with requests.session() as s:
            rawData = s.get(URL)
            soup = bs(rawData.content, "lxml")
            meta = soup.find('meta', {"name": "csrf-token"})['content']
            header = {"X-Csrf-Token": meta}
            responseData_scan1 = s.post(url=URL, headers=header, data=condition, timeout=10000)
            if responseData_scan1.content:
                data = responseData_scan1.json()
                stock = data['data']
                stock_list = pd.DataFrame(stock)
                # print(f"-------------------{conditionName}----------------------------")
                # print(stock_list)
                if stock_list.empty:
                    time.sleep(10)
                    print("no data")
                    return
                today = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date())
                stock_list['date'] = today
                now = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))  
                current_time = now.strftime('%H:%M:%S')
                stock_list['time'] = str(current_time)
                stock_list['nsecode'] = stock_list['nsecode'].fillna('NA')
                stock_list['bsecode'] = stock_list['bsecode'].fillna(0)
                datafile = pd.merge(stock_list,  symbol_df[["nsecode", 'igroup_name']], on="nsecode", how='left')
                datafile['igroup_name'] = datafile['igroup_name'].fillna('Others')
                return datafile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def chartinkLogicBankend(condition, conditionName,db_name ):
    try:
        today = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date())
        # Fetch a database session
        db = next(get_db())
        # For Indraday Condition --- start
        if (db_name == "IntradayData" and conditionName == "Champions Intraday"):
            scandataFunc_df = scandata(condition, conditionName)
            selected_columns = ['nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume','date','time','igroup_name']
            newScandataFunc = scandataFunc_df[selected_columns]
            if newScandataFunc.empty:
                print(f"{db_name} {conditionName}data not found in scan")
                return
          
            intra_data = pd.read_sql(db.query(models.IntradayData).statement, db.bind)
            if not intra_data.empty:
                new_intraday_data = newScandataFunc[~newScandataFunc['nsecode'].isin(intra_data.loc[intra_data['date']== today, 'nsecode'])]
                if new_intraday_data.empty:
                    print(f"No new data found for {conditionName}")
                    return
                else:
                    print(f"New data found {conditionName} to dataBase{db_name}....\n")
                    print(new_intraday_data)
                    new_intrday_entry = new_intraday_data.to_dict(orient='records')
                    try:
                        db.bulk_insert_mappings(models.IntradayData, new_intrday_entry)
                        db.commit()
                        pass
                    except Exception as e:
                        print(f"{conditionName}---> error {e}")
                                    
            else:
                print(f"{db_name} {conditionName}data not found in dataBase")
                print(f"Entring the {conditionName} to dataBase{db_name}....")
                data_to_insert = newScandataFunc.to_dict(orient='records')
                try:
                    db.bulk_insert_mappings(models.IntradayData, data_to_insert)
                    db.commit()
                    pass
                except Exception as e:
                    print(f"{conditionName}---> error {e}")
                
        # For OverBroughtData Condition --- start
        elif (db_name == "OverBroughtData" and conditionName == "Champions Over Brought"):
            scandataFunc_df = scandata(condition, conditionName)
            selected_columns = ['nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume','date','time','igroup_name']
            newScandataFunc = scandataFunc_df[selected_columns]
            # print(newScandataFunc)
            if newScandataFunc.empty:
                print(f"{db_name} {conditionName}data not found in scan")
                return
          
            over_brought_data = pd.read_sql(db.query(models.OverBroughtData).statement, db.bind)
            if not over_brought_data.empty:
                # print(f"{db_name} {conditionName}data already exists in dataBase")
                new_overBrought_data = newScandataFunc[~newScandataFunc['nsecode'].isin(over_brought_data.loc[over_brought_data['date']== today, 'nsecode'])]
                if new_overBrought_data.empty:
                    print(f"No new data found for {conditionName}")
                    return
                else:
                    print(f"New data found {conditionName} to dataBase{db_name}....\n")
                    print(new_overBrought_data)
                    new_overBrought_entry = new_overBrought_data.to_dict(orient='records')
                    try:
                        db.bulk_insert_mappings(models.OverBroughtData, new_overBrought_entry)
                        db.commit()
                        pass
                    except Exception as e:
                        print(f"{conditionName}---> error {e}")
                
            else:
                print(f"{db_name} {conditionName}data not found in dataBase")
                print(f"Entring the {conditionName} to dataBase{db_name}....")
                data_to_insert = newScandataFunc.to_dict(orient='records')
                try:
                    db.bulk_insert_mappings(models.OverBroughtData, data_to_insert)
                    db.commit()
                    pass
                except Exception as e:
                    print(f"{conditionName}---> error {e}")
                

        # For PositionalData Condition --- start  
        elif (db_name == "PositionalData" and conditionName == "Champions Positional"):
            scandataFunc_df = scandata(condition, conditionName)
            selected_columns = ['nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume','date','time','igroup_name']
            newScandataFunc = scandataFunc_df[selected_columns]
    
            if newScandataFunc.empty:
                # print(f"{db_name} {conditionName}data not found in scan")
                return
            positonal_data = pd.read_sql(db.query(models.PositionalData).statement, db.bind)
            if not positonal_data.empty:
                # print(f"{db_name} {conditionName}data already exists in dataBase")
                new_positional_data = newScandataFunc[~newScandataFunc['nsecode'].isin(positonal_data.loc[positonal_data['date']== today, 'nsecode'])]
                if new_positional_data.empty:
                    print(f"No new data found for {conditionName}")
                    return
                else:
                    print(f"New data found {conditionName} to dataBase{db_name}....\n")
                    print(new_positional_data)
                    new_positional_entry = new_positional_data.to_dict(orient='records')
                    try:
                        db.bulk_insert_mappings(models.PositionalData, new_positional_entry)
                        db.commit()
                        pass
                    except Exception as e:
                        print(f"{conditionName}---> error {e}")
                
            else:
                print(f"{db_name} {conditionName}data not found in dataBase")
                print(f"Entring the {conditionName} to dataBase{db_name}....")
                data_to_insert = newScandataFunc.to_dict(orient='records')
                try:
                    db.bulk_insert_mappings(models.PositionalData, data_to_insert)
                    db.commit()
                    pass
                except Exception as e:
                    print(f"{conditionName}---> error {e}") 
                

        elif (db_name == "ReversalData" and conditionName == "Champions Reversal Stocks"):
            scandataFunc_df = scandata(condition, conditionName)
            selected_columns = ['nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume','date','time','igroup_name']
            newScandataFunc = scandataFunc_df[selected_columns]
            if newScandataFunc.empty:
                print(f"{db_name} {conditionName}data not found in scan")
                return
          
            reversal_data = pd.read_sql(db.query(models.ReversalData).statement, db.bind)
            if not reversal_data.empty:
                # print(f"{db_name} {conditionName}data already exists in dataBase")
                new_reveral_data = newScandataFunc[~newScandataFunc['nsecode'].isin(reversal_data.loc[reversal_data['date']== today, 'nsecode'])]
                if new_reveral_data.empty:
                    print(f"No new data found for {conditionName}")
                    return
                else:
                    print(f"New data found {conditionName} to dataBase{db_name}....")
                    print(new_reveral_data)
                    new_reversal_entry = new_reveral_data.to_dict(orient='records')
                    try:
                        db.bulk_insert_mappings(models.ReversalData, new_reversal_entry)
                        db.commit()
                        pass
                    except Exception as e:
                        print(f"{conditionName}---> error {e}")
            else:   
                print(f"Entring the {conditionName} to dataBase{db_name}....")
                data_to_insert = newScandataFunc.to_dict(orient='records')
                try:
                    db.bulk_insert_mappings(models.ReversalData, data_to_insert)
                    db.commit()
                    pass
                except Exception as e:
                    print(f"{conditionName}---> error {e}")
                

        elif (db_name == "SwingData" and conditionName == "Champions Swing"):
            scandataFunc_df = scandata(condition, conditionName)
            selected_columns = ['nsecode', 'name', 'bsecode', 'per_chg', 'close', 'volume','date','time','igroup_name']
            newScandataFunc = scandataFunc_df[selected_columns]
            if newScandataFunc.empty:
                print(f"{db_name} {conditionName}data not found in scan")
                return
          
            swing_data = pd.read_sql(db.query(models.SwingData).statement, db.bind)
            if not swing_data.empty:
                # print(f"{db_name} {conditionName}data already exists in dataBase")
                new_swing_data = newScandataFunc[~newScandataFunc['nsecode'].isin(swing_data.loc[swing_data['date']== today, 'nsecode'])]
                if new_swing_data.empty:
                    print(f"No new data found for {conditionName}")
                    return
                else:
                    print(f"New data found Entring the {conditionName} to dataBase{db_name}....\n")
                    print(new_swing_data)
                    new_swing_entry = new_swing_data.to_dict(orient='records')
                    try:
                        db.bulk_insert_mappings(models.SwingData, new_swing_entry)
                        db.commit()
                        pass
                    except Exception as e:
                        print(f"{conditionName}---> error {e}")
                
            else:
                print(f"{db_name} {conditionName}data not found in dataBase")
                print(f"Entring the {conditionName} to dataBase{db_name}....")
                data_to_insert = newScandataFunc.to_dict(orient='records')
                try:
                    db.bulk_insert_mappings(models.SwingData, data_to_insert)
                    db.commit()
                    pass
                except Exception as e:
                    print(f"{conditionName}---> error {e}")   
                
                
        else:
            return

    except Exception as e:
        print(f"chartinkLogicBankend error: {e}")

