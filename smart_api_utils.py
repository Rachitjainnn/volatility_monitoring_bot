from SmartApi import SmartConnect
import os
import pyotp
from logzero import logger
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def initialize_api():
    api_key = os.getenv('API_KEY')
    username = os.getenv('USERNAME')
    pwd = os.getenv('PASSWORD')
    try:
        smartApi = SmartConnect(api_key)
    except Exception as e:
        logger.error(f"Error initializing SmartAPI: {e}")
        print(f"Error initializing SmartAPI: {e}")

    try:
        token = os.getenv('TOTP_TOKEN')
        totp = pyotp.TOTP(token).now()
        try:
            data = smartApi.generateSession(username, pwd, totp)
        except Exception as e:
            logger.error(f"Error generating session: {e}")
            print(f"Error generating session: {e}")
        if not data['status']:
            logger.error(data)
            print("data is empty")
            return None
        else:
            return smartApi
    except Exception as e:
        logger.error(f"Invalid Token: {e}")

def initialize_symbol_token_map():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    try:
        response = requests.get(url, timeout=30).json()
        token_df = pd.DataFrame.from_dict(response)
        token_df['strike'] = token_df['strike'].astype(float)
        token_df['expiry'] = pd.to_datetime(token_df['expiry'], format='%d%b%Y')
        return token_df
    except requests.exceptions.ConnectTimeout:
        logger.error("Connection timed out.")
        print("Connection timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred in initialize_symbol_token_map: {e}")
