# Config conversion from config.json in main folder
import json
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential

import os
import sys

sys.path.append(os.environ["autobot_modules"])
from Configs.app_config import ConfigClass


config_location = os.path.join(os.getcwd(), "config.json")
config_exists = os.path.exists(config_location)

if not config_exists:
    CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = CONFIG_PATH.split("\\resources")[0]
    config_location = os.path.join(CONFIG_PATH, "config.json")
    config_exists = os.path.exists(config_location)
    if not config_exists:
        raise FileNotFoundError("config.json not found in main folder")

with open(config_location, "r") as config_file:
    config = json.loads(config_file.read())

# Test Values
TEST_VALUE = config["testValue"]

# Chromedriver
CHROMEDRIVER_PATH = config["chromedriverPath"]

# TS States
STATE_CODES = config["state_codes"]
STATES = list(config["states"].keys())

# Spotio
SPOTIO_TERRITORIES = config["spotio"]["territories"]

# RPA Webpage Permissions
TSA_USERS = config["TSA_USERS"]
ADMIN = config["ADMIN"]

vaults = config["VAULTS"]

KEY_VAULT = os.environ["Azure_Key_Vault_Name"].lower()
KVUri = f"https://{KEY_VAULT}.vault.azure.net"
credential = ClientSecretCredential(
    tenant_id=ConfigClass.TENANT_ID,
    client_id=ConfigClass.CLIENT_ID,
    client_secret=ConfigClass.CLIENT_SECRET,
)
client = SecretClient(vault_url=KVUri, credential=credential)

for vault in vaults:
    retrieved_secret = client.get_secret(vault)
    items = retrieved_secret.value.split(";")
    for item in items:
        id, name = item.split(" ")
        exec(f"{id} = '{name}'", globals())
