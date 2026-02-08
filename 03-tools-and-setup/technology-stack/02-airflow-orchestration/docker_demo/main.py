import pandas as pd
from datetime import datetime

df = pd.DataFrame({
    "timestamp": [datetime.now()],
    "temperature": [25.3],
    "humidity": [68]
})

df.to_csv("/data/weather_log.csv", index=False)
print("Data written to /data/weather_log.csv")