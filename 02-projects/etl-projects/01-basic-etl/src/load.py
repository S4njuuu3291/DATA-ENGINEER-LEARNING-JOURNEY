import pandas as pd
import logging

def load(data,destination,table):
    logging.info("Load data to database..")
    print(data)
    df = pd.DataFrame([data])
    df.to_sql(table,destination,if_exists='append',index=False)
    logging.info("Load success..\n")
    
