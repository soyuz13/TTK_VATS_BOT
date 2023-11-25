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

    def_codes_file_path = Path(__file__).parent / 'abc_def_codes_timezone.csv'

    if def_codes_file_path.is_file():
        df = pd.read_csv(def_codes_file_path, delimiter=';')
        df['start'] = (df['DEF'].astype(str) + df['От'].astype(str)).astype(int)
        df['end'] = (df['DEF'].astype(str) + df['До'].astype(str)).astype(int)
        # df['timezone'] = df['timezone'].astype(str)
        DEF = int(str(num)[:3])
        newdf = df.query('start < @num & end > @num & DEF == @DEF')
        try:
            region = newdf['Регион'].values[0]
            timezone = newdf['timezone'].values[0]
        except:
            return region, timezone

    return region, timezone

