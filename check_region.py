import pandas as pd
import re
from pathlib import Path


def clear_tel_number(num):
    cleared_num = re.findall(r'\d+', num)
    cleared_num = ''.join(cleared_num)
    if len(cleared_num) == 11:
        cleared_num = cleared_num[1:]
        return cleared_num
    else:
        return


def get_region(num):
    region = "Регион не определен"
    timezone = "Время MSK--"
    num = int(num)
    if not num:
        return region, timezone

    def_codes_file_path = Path(__file__).parent / 'tel_codes_tz.csv'

    if def_codes_file_path.is_file():

        types = {'Timezone': "int", 'DEF': "int", 'Region': 'str', 'From': 'str', 'To': 'str'}
        df = pd.read_csv(def_codes_file_path, sep=';', header=0, dtype=types)

        df['Start'] = (df['DEF'].astype(str) + df['From'].astype(str)).astype(int)
        df['End'] = (df['DEF'].astype(str) + df['To'].astype(str)).astype(int)
        DEF = int(str(num)[:3])
        newdf = df.query('Start < @num & End > @num')
        try:
            region = newdf['Region'].values[0]
            timezone = newdf['Timezone'].values[0]
        except:
            return region, timezone

    return region, timezone
