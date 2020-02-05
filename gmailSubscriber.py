from google.cloud import pubsub_v1
import pandas as pd

credentials = pd.read_json("credentials.json").installed

project_id = credentials.project_id
#topic_name = 
