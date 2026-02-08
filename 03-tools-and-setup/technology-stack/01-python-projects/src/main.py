import logging
from extract import extract
from transform import transform
from load import load
from pathlib import Path
from sqlalchemy import create_engine
import yaml

BASE = Path(__file__).resolve().parent.parent

log_file = BASE / "logs" / "weather.log"
config_file = BASE / "config" / "config.yaml"

logging = logging.basicConfig(
    filename= log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

with open(config_file,"r") as file:
    config = yaml.safe_load(file)

source = config["pipeline"]["steps"]["extract"]["source"]
params = config["pipeline"]["steps"]["extract"]["params"]

engine_name = config["database"]["engine_name"]
engine = create_engine(engine_name)

table_name = config["pipeline"]["steps"]["load"]["table_name"]
city = config["pipeline"]["steps"]["load"]["city_name"]

try:
    raw = extract(source,params)
    data = transform(raw,city)
    load(data,engine,table_name)
except Exception as e:
    logging.error(f"Pipeline failed: {e}")