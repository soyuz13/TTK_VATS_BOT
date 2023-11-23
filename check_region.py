import pandas as pd
import re


def clear_tel_number(num):
    cleared_num = re.findall(r'\d+', num)
    cleared_num = ''.join(cleared_num)
    if len(cleared_num) == 11:
        cleared_num = cleared_num[1:]
        return cleared_num
    else:
        return


def get_region(num):
    num = int(num)
    if not num:
        return "Регион не определен"
    df = pd.read_csv('abc_def_codes.csv', delimiter=';')
    df['start'] = (df['DEF'].astype(str) + df['От'].astype(str)).astype(int)
    df['end'] = (df['DEF'].astype(str) + df['До'].astype(str)).astype(int)
    DEF = int(str(num)[:3])
    newdf = df.query('start < @num & end > @num & DEF == @DEF')
    try:
        region = newdf['Регион'].values[0]
    except:
        return "Регион не определен"

    return region

