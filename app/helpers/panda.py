import io
import os
import pandas as pd
from sqlalchemy import Engine

def excel_to_db(engine: Engine):
    try:
            with open("helpers/Superstore.xlsx", "rb") as file:
                content = file.read()

            filename = os.path.splitext(os.path.basename(file.name))[0].lower()
            dataframe = pd.read_excel(io.BytesIO(content))
            dataframe.to_sql(filename, engine, if_exists="replace", index=False)

            return filename
    except Exception as e:
        print(e)
        return

