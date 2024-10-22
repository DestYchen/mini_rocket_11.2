import pandas as pd
import numpy as np

def read_data(flag,*args):
    global full_df\
        ,column_names\
        ,dates_list\
        ,lk_names_list\
        ,df_point_51\
        ,date_lk51\
        ,dict_filled_forms\
        ,dict_name_num\
        ,dict_num_name\
        ,unique_rows\
        ,point_number_list\
        ,point_name_list
    if flag:
        full_df = pd.read_excel('TS_2_upload_data_full_final_final.xlsm', header=0)
    else:
        full_df=args[0]
        print('got read_data')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(full_df["31_03_2024"].to_markdown())
    column_names = full_df.columns.values.tolist()
    """список имен всех столбцов в экселе"""
    dates_list = column_names[10:]  # все даты таблицы
    print(f"fdgjhbk{dates_list}")
    """список всех дат"""
    #преобразовываем значения в столбцах дат в числа или 0
    for d in dates_list:
        full_df[d]=pd.to_numeric(full_df[d], errors='coerce')
    lk_names_list = full_df['lk_name'].drop_duplicates()
    """список ЛК из эксель без повторов"""

    '''with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(full_df['31_03_2016'].to_markdown())'''

    #сопоставимость выборки
    df_point_51 = full_df.loc[full_df['point_number'] == '5.1', ['lk_name'] + [d for d in dates_list]].copy()
    """новый df, в котором строки только для 5.1, столбцы: даты"""
    df_point_51 = df_point_51.set_index('lk_name')  # индекс - имя ЛК
    date_lk51 = {key: [] for key in dates_list}
    """словарь {ключ - дата: значение - список сопоставимых по пункту 5.1 ЛК}"""
    for company in lk_names_list:
        tmp = df_point_51.loc[company].to_dict()  # для конкретной ЛК словарь {'date': point_5.1}
        count = 0
        for d in dates_list:
            if tmp[d] == 0:
                count = 0
            else:
                count += 1
                if count >= 7:
                    date_lk51[d].append(company)

    dict_filled_forms={key: [] for key in dates_list}
    """словарь: дата - [лк, кот. сдали анкету(есть хотя бы одно значение не= 0)]"""

    for company in lk_names_list:
        for d in dates_list:
            #ne(0) это не=0 any() - любой, т.е. если есть хотя бы один не 0 в дате
            if full_df.loc[full_df['lk_name'] == company, d].ne(0).any():
                #print(f'write to {d} comp {company}')
                dict_filled_forms[d].append(company)
            else:#все значения 0, значит анкета не сдана, заменяем 0 на None
                #print(f'nan to {company} on {d}')
                full_df.loc[full_df['lk_name'] == company, d]=np.nan

    dict_name_num={}
    """словарь {ключ - имя пункта: значение - номер пункта}"""

    for pn in full_df.point_name.drop_duplicates():
        dict_name_num[pn]=full_df['point_number'][full_df[full_df['point_name']==pn].index[0]]

    dict_num_name={}
    """словарь {ключ - номер пункта: значение - имя пункта}"""

    for pn in full_df.point_number.drop_duplicates():
        dict_num_name[pn]=full_df['point_name'][full_df[full_df['point_number']==pn].index[0]]

    unique_rows = []
    for pn in full_df.point_number.drop_duplicates():
        unique_rows.append(str(pn))

    point_number_list = []
    """список с уникальными номерами пунктов анкеты"""

    point_name_list = []
    """список с уникальными названиями пунктов анкеты"""

    count_1 = 0
    while count_1 < len(unique_rows):
        point_number_list.append(full_df.iloc[count_1, 4])
        point_name_list.append(full_df.iloc[count_1, 5])
        count_1 += 1

read_data(True,[])