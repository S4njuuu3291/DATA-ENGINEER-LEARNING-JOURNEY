import requests
import json
import logging

def extract(source,params=None):
    url = f"{source}?latitude={params['latitude']}&longitude={params['longitude']}&current={params['current']}"
    logging.info("Extracting data from url..")
    response = requests.get(url)
    if response == "":
        logging.warning("Response is empty..")
    else:
        logging.info("Extracting successful..")
    return response.text