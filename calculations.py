import warnings
import re
import pandas as pd
warnings.filterwarnings("ignore")
from read_data import *
from ui_dict import comp_type_dict
from formpoint import FormPoint

pf_operations = {
    '+': FormPoint.__add__,
    '-': FormPoint.__sub__,
    '*': FormPoint.__mul__,
    '/': FormPoint.__truediv__
}
"""словарь операторов {ключ - 'символ оператора' : значение - функция FormPoint}"""

np_operations = {
    '+': np.add,
    '-': np.subtract,
    '*': np.multiply,
    '/': np.divide
}
"""словарь операторов {ключ - 'символ оператора' : значение - функция numpy}"""

def format_int(x):
    """функция форматирования числа по тысячам"""
    tmp = f"{x: ,}"
    return tmp.replace(',', ' ')

def get_df_param(df, param):
    """
    :param df:
    :param param: номер пункта
    :return: возвращает датафрейм с значениями только выбранного пункта
    """
    return df.loc[df['point_number'] == param]

def check_lk_form_stepback(df, d):
    """
    вызывается когда нужно проверить даты, не выбранные ползователем, но нужные для вычислений
    :param df:
    :param d: дата для проверки
    :return: False(если нет одной из лк в анкете на нужную дату)/True
    """
    lk = df['lk_name'].drop_duplicates()
    if not any(l in dict_filled_forms[d] for l in lk):
        # если нет хотя бы одной лк в анкете на текущую дату
        return False
    return True

def sliding(df, dates, dates_noform_calc):
    """
    :param df: дф, содержащий только нужные имена и только нужный номер пункта
    :param dates: даты для вычисления
    :param dates_noform_calc: даты для вычисления, для которых нет данных
    :return: np.array(res) - список значений ск года для каждой даты пользователя
    """
    res = []
    for d in dates:
        ind = dates_list.index(d)  # переносим в функцию тоже
        quoter_pos = ind % 4 + 1  # номер квартала = остаток от деления на 4 позиции даты в полном списке + 1 (1,2,3,4)
        # результирующий столбец даты = столбец этой даты + столбец последней даты прошлого квартала - столбец год назад
        # записываем два списка дат
        q_date = dates_list[ind - quoter_pos]
        y_date = dates_list[ind - 4]
        if check_lk_form_stepback(df, q_date) and check_lk_form_stepback(df, y_date):  # True если все даты с данными
            res_column = df[d][0:] + df[dates_list[ind - quoter_pos]][0:] - df[dates_list[ind - 4]][0:]
            res.append(res_column.sum())
        else:
            res.append(0)
            if d not in dates_noform_calc:
                dates_noform_calc.append(d)
    return np.array(res)

def average(df, dates, dates_noform_calc):
    """
    :param df: дф, содержащий только нужные имена и только нужный номер пункта
    :param dates: даты для вычисления
    :param dates_noform_calc: даты для вычисления, для которых нет данных
    :return: np.array(res) - массив средних значений за текущую дату и дату год назад
    """
    res = []
    for d in dates:
        ind_prev = dates_list.index(d) - 4  # позиция даты год назад в полном списке
        y_date = dates_list[ind_prev]
        # проверка на наличие данных
        if check_lk_form_stepback(df, y_date):
            sum_column = (df[d] + df[y_date]) / 2  # столбец средних значений
            res.append(sum_column.sum())
        else:
            res.append(0)
            if d not in dates_noform_calc:
                dates_noform_calc.append(d)
    return np.array(res)

def average_byLK(df, dates, dates_noform_calc):
    """
    :param df: дф, содержащий только нужные имена и только нужный номер пункта
    :param dates: даты для вычисления
    :param dates_noform_calc: даты для вычисления, для которых нет данных
    :return: np.array(res) - массив средних значений по ЛК для пункта
    """
    res = []
    for d in dates:
        res.append(df[d].mean())
    return np.array(res)

def diff(df, dates, dates_noform_calc):
    """
    :param df: дф, содержащий только нужные имена и только нужный номер пункта
    :param dates: даты для вычисления
    :param dates_noform_calc: даты для вычисления, для которых нет данных
    :return: np.array(res) - массив изменений пункта за год
    """
    res = []
    for d in dates:
        ind = dates_list.index(d)
        y_date = dates_list[ind - 4]
        # проверка на наличие данных
        if check_lk_form_stepback(df, y_date):
            diff_column = df[d] - df[y_date]
            res.append(diff_column.sum())
        else:
            res.append(0)
            if d not in dates_noform_calc:
                dates_noform_calc.append(d)
    return np.array(res)

def sum_param(df, dates):
    """
    :param df: дф, содержащий только нужные имена и только нужный номер пункта
    :param dates: даты для вычисления
    :return: np.array(res) - массив сумм значений пункта
    """
    res = []
    for d in dates:
        res.append(df[d].sum())
    return np.array(res)

def get_df_param_stepback(df, dates, st, f,
                          dates_noform_calc):
    """
    выполняет вычисления прошлых дат с проверкой на наличие данных
    :param df:
    :param dates:
    :param st: на сколько кварталов делаем шаг назад от даты(1 - квартал, 4 - год)
    :param f: функцию, которую нужно выполнить для полученных дат
    :param dates_noform_calc: даты, для вычисления которых недостаточно данных
    :return: np.array(res) результьат действия функции на нужные прошлые даты
    """
    res = []
    for d in dates:
        ind = dates_list.index(d)
        y_date = dates_list[ind - st]
        # проверка на наличие данных
        if check_lk_form_stepback(df, y_date):  # True, то выполняем функцию
            res.append(f(df, [y_date, ])[0])  # распаковка, тк получаем из вызова функции array с одним числом
        else:
            res.append(0)
            # записываем дату в список дат с неполными данными
            if d not in dates_noform_calc:
                dates_noform_calc.append(0)
    return np.array(res)

'''
def denom_H1(df,dates, with_risks):# вычисление знаменателя показателя Н1 с или без рисков
    #оставляем только пользовательские даты в df
    for d in dates_list:
        if d not in dates:
            df.drop(d)
    #assets
    #идем по паре номер пункта, коэфф-т в словаре из файла констант
    for point_num, koeff in const_data.dict_assets_risk_ratios.items():
        #получаем df с нужным пунктом
        tmp_df=get_df_param(df,point_num)
'''


def custom_divide(arr1, arr2):
    #функция нужная для корректного подсчёта метрики ROE
    result = np.empty(arr1.shape, dtype=object)

    for i in range(len(arr1)):
        if arr2[i] < 0: #проверяет, если каппитал отрицателен
            result[i] = np.exp(1)
        elif arr2[i] < 0 and arr1[i] < 0: # проверяет, если и капитал и чистая прибыль отрицательны 
            result[i] = np.exp(2)
        else:
            result[i] = (arr1[i] * 100) / arr2[i]
    
    return result

def func_dict(key, df, dates):
    """
    выполняет формулу из словаря для готового показателя по ключу key
    :param key: пара параметр(ROE и тд) и категория(По данным МСФО и тд)
    :param df:
    :param dates:
    :return: (find_form[0](), find_form[1], find_form[2], dates_noform_calc)
    find_form[0]() - численный ответ, find_form[1] - формула для вывода на экран,
    find_form[2] - кортеж используемых в формуле пунктов
    """
    dates_noform_calc = []
    param_dict = {
        # ЭИ МСФО----------------------------------------------

        ('ROE', 'По данным МСФО'): (lambda: custom_divide((sliding(get_df_param(df, '5.43'), dates, dates_noform_calc)),
                                            (average(get_df_param(df, '5.27'), dates, dates_noform_calc))),
                                    'скользящий год(<b>5.43</b>)/среднее(<b>5.27</b>) (%)', ('5.43', '5.27')),

        ('ROA', 'По данным МСФО'): (lambda: sliding(get_df_param(df, '5.43'), dates, dates_noform_calc) * 100 /
                                            (average(get_df_param(df, '5.1'), dates, dates_noform_calc)),
                                    'скользящий год(<b>5.43</b>)/среднее(<b>5.1</b>) (%)', ('5.43', '5.1')),

        ('CIR', 'По данным МСФО'): (lambda: (-sliding(get_df_param(df, '5.39'), dates, dates_noform_calc) -
                                             sliding(get_df_param(df, '5.41'), dates, dates_noform_calc)) * 100 /
                                            (sliding(get_df_param(df, '5.31'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '5.34'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '5.40'), dates, dates_noform_calc)),
                                    'скользящий год(-<b>5.41</b>(***) - <b>5.39</b>(***))/скользящий год(<b>5.31</b> + <b>5.34</b>(***) '
                                    '+ <b>5.40</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
                                    ('5.41', '5.39', '5.31', '5.34', '5.40')
                                    ),

        ('NIM', 'По данным МСФО'): (lambda: (sliding(get_df_param(df, '5.31'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '5.34'), dates, dates_noform_calc)) * 100 /
                                            (average(get_df_param(df, '5.4'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '5.8'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '5.9'), dates, dates_noform_calc)),
                                    'скользящий год(<b>5.31</b> + <b>5.34</b>(***))/среднее(<b>5.4</b> + <b>5.8</b> '
                                    '+ <b>5.9</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
                                    ('5.31', '5.34', '5.4', '5.8', '5.9')
                                    ),
        ('Leverage', 'По данным МСФО'): (lambda: (sum_param(get_df_param(df, '5.27'), dates) * 100)
                                                 / (sum_param(get_df_param(df, '5.1'), dates)),
                                         '(<b>5.27</b> )/(<b>5.1</b>) (%)',
                                         ('5.27', '5.1')
                                         ),
        ('COR', 'По данным МСФО'): (lambda: (diff(get_df_param(df, '2.1.4'), dates, dates_noform_calc) +
                                             diff(get_df_param(df, '2.2.4'), dates, dates_noform_calc) +
                                             diff(get_df_param(df, '2.1.5'), dates, dates_noform_calc) -
                                             diff(get_df_param(df, '2.1.6'), dates, dates_noform_calc) +
                                             diff(get_df_param(df, '2.2.5'), dates, dates_noform_calc) -
                                             diff(get_df_param(df, '2.2.6'), dates, dates_noform_calc) +
                                             diff(get_df_param(df, '2.1.7'), dates, dates_noform_calc) +
                                             diff(get_df_param(df, '2.2.7'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '2.1.8'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '2.2.8'), dates, dates_noform_calc)) * 100 /
                                            (average(get_df_param(df, '2.1.2'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '2.2.2'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '2.1.7'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '2.2.7'), dates, dates_noform_calc) -
                                             average(get_df_param(df, '2.1.4'), dates, dates_noform_calc) -
                                             average(get_df_param(df, '2.2.4'), dates, dates_noform_calc) -
                                             average(get_df_param(df, '2.1.5'), dates, dates_noform_calc) -
                                             average(get_df_param(df, '2.2.5'), dates, dates_noform_calc)),
                                    '(изменение(за год)(<b>2.1.4</b> + <b>2.2.4</b>+<b>2.1.5</b>-<b>2.1.6</b>+<b>2.2.5</b>'
                                    '- <b>2.2.6</b>+<b>2.1.7</b>+<b>2.2.7</b>) + скользящий год(<b>2.1.8</b>+<b>2.2.8</b>))'
                                    '/(среднее(<b>2.1.2</b> + <b>2.2.2</b> + <b>2.2.7</b> - <b>2.1.4</b> - <b>2.2.4</b> - <b>2.1.5</b>-<b>2.2.5</b>)'
                                    '+ скользящий год(<b>2.1.7</b>)) (%)',
                                    ('2.1.4', '2.2.4', '2.1.5', '2.1.6', '2.2.5', '2.2.6',
                                     '2.1.7', '2.2.7', '2.1.8', '2.2.8', '2.1.2', '2.2.2')
                                    ),

        ('стоимость фондирования', 'По данным МСФО'): (
            lambda: -sliding(get_df_param(df, '5.34'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '5.18'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.20'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.22'), dates, dates_noform_calc)),
            'скользящий год(<b>- 5.34</b>(***) )/среднее(<b>5.18</b> + <b>5.20</b> + <b>5.22</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
            ('5.34', '5.18', '5.20', '5.22')
        ),
        ('процентный спрэд', 'По данным МСФО'): (
            lambda: sliding(get_df_param(df, '5.31'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '5.4'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.53'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.8'), dates, dates_noform_calc)) +
                    sliding(get_df_param(df, '5.34'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '5.18'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.20'), dates, dates_noform_calc) +
                     average(get_df_param(df, '5.22'), dates, dates_noform_calc)),
            '(скользящий год(<b>5.31</b> )/среднее(<b>5.4</b>+<b>5.53</b>+<b>5.8</b>)) + скользящий год(<b>5.34</b>(***))/среднее(<b>5.18</b> + <b>5.20</b> + <b>5.22</b>)) (%) <br>(***) - значения с знаком минус в исходных данных',
            ('5.31', '5.4', '5.53', '5.8', '5.34', '5.18', '5.20', '5.22')
        ),
        ('ОВП', 'По данным МСФО'): (lambda: sum_param(get_df_param(df, '5.46'), dates) +
                                            sum_param(get_df_param(df, '5.66.1'), dates) -
                                            sum_param(get_df_param(df, '5.49'), dates) -
                                            sum_param(get_df_param(df, '5.71'), dates),
                                    '<b>5.46</b> + <b>5.66.1</b> - <b>5.49</b> - <b>5.71</b> (млн руб)',
                                    ('5.46', '5.66.1', '5.49', '5.71')),

        ('доля ОВП в капитале', 'По данным МСФО'): (lambda: (sum_param(get_df_param(df, '5.46'), dates) +
                                                             sum_param(get_df_param(df, '5.66.1'), dates) -
                                                             sum_param(get_df_param(df, '5.49'), dates) -
                                                             sum_param(get_df_param(df, '5.71'), dates)) * 100 /
                                                            sum_param(get_df_param(df, '5.27'), dates),
                                                    '( <b>5.46</b> + <b>5.66.1</b> - <b>5.49</b> - <b>5.71</b> )/ <b>5.27</b>  (%)',
                                                    ('5.46', '5.66.1', '5.49', '5.71', '5.27')),
        ('ЧИЛ', 'По данным МСФО'): (lambda: (sum_param(get_df_param(df, '5.4'), dates)),
                                    '( <b>5.4</b>   (млн руб)',
                                    ('5.4',)),
        # ЭИ ФСБУ----------------------------------------------
        ('ROE', 'По данным ФСБУ'): (lambda: (sliding(get_df_param(df, '4.46'), dates, dates_noform_calc) * 100) /
                                            (average(get_df_param(df, '4.17'), dates, dates_noform_calc)),
                                    'скользящий год(<b>4.46</b>)/среднее(<b>4.17</b>) (%)', ('4.46', '4.17')),
        ('ROA', 'По данным ФСБУ'): (lambda: (sliding(get_df_param(df, '4.46'), dates, dates_noform_calc) * 100) /
                                            (average(get_df_param(df, '4.1'), dates, dates_noform_calc)),
                                    'скользящий год(<b>4.46</b>)/среднее(<b>4.1</b>) (%)', ('4.46', '4.1')),
        ('CIR', 'По данным ФСБУ'): (lambda: (-sliding(get_df_param(df, '4.38'), dates, dates_noform_calc) -
                                             sliding(get_df_param(df, '4.43'), dates, dates_noform_calc) -
                                             sliding(get_df_param(df, '4.37'), dates, dates_noform_calc)) * 100 /
                                            (sliding(get_df_param(df, '4.32'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '4.41'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '4.42'), dates, dates_noform_calc)),
                                    'скользящий год( - <b>4.43</b>(***) - <b>4.38</b>(***) - <b>4.37</b>(***))/скользящий год(<b>4.32</b> + <b>4.41</b> '
                                    '+ <b>4.42</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
                                    ('4.43', '4.38', '4.37', '4.32', '4.41', '4.42')
                                    ),
        ('NIM', 'По данным ФСБУ'): (lambda: (sliding(get_df_param(df, '4.32'), dates, dates_noform_calc) +
                                             sliding(get_df_param(df, '4.41'), dates, dates_noform_calc)) * 100 /
                                            (average(get_df_param(df, '4.69'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '4.66'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '4.71'), dates, dates_noform_calc) +
                                             average(get_df_param(df, '4.72'), dates, dates_noform_calc)),
                                    'скользящий год(<b>4.32</b> + <b>4.41</b>(***))/среднее(<b>4.69</b> + <b>4.66</b> '
                                    '+ <b>4.71</b> + <b>4.72</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
                                    ('4.32', '4.41', '4.69', '4.66', '4.71', '4.72')
                                    ),
        ('Leverage', 'По данным ФСБУ'): (lambda: (sum_param(get_df_param(df, '4.17'), dates) * 100)
                                                 / (sum_param(get_df_param(df, '4.1'), dates)),
                                         '(<b>4.17</b> )/(<b>4.1</b>) (%)',
                                         ('4.17', '4.1')
                                         ),
        ('стоимость фондирования', 'По данным ФСБУ'): (
            lambda: -sliding(get_df_param(df, '4.41'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '4.19'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.25'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.21'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.27'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.23'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.76'), dates, dates_noform_calc)),
            'скользящий год(<b>- 4.41</b>(***) )/среднее(<b>4.19</b> + <b>4.25</b> + <b>4.21</b> + <b>4.27</b> + <b>4.23</b> + <b>4.76</b>) (%) <br>(***) - значения с знаком минус в исходных данных',
            ('4.41', '4.19', '4.25', '4.21', '4.27', '4.23', '4.76')
        ),
        ('процентный спрэд', 'По данным ФСБУ'): (
            lambda: sliding(get_df_param(df, '4.32'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '4.69'), dates, dates_noform_calc)+
                     average(get_df_param(df, '4.66'), dates, dates_noform_calc)+
                     average(get_df_param(df, '4.74'), dates, dates_noform_calc)) +
                    sliding(get_df_param(df, '4.41'), dates, dates_noform_calc) * 100 /
                    (average(get_df_param(df, '4.19'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.25'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.21'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.27'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.23'), dates, dates_noform_calc) +
                     average(get_df_param(df, '4.76'), dates, dates_noform_calc)
                     ),
            'скользящий год(<b>4.32</b> )/среднее(<b>4.69</b>+<b>4.66</b>+<b>4.74</b>) + скользящий год(<b>4.41</b>(**))/среднее(<b>4.19</b> + <b>4.25</b> + <b>4.21</b> + <b>4.27</b> + <b>4.23</b> + <b>4.76</b>)) (%) <br>(***) - значения с знаком минус в исходных данных',
            (
                '4.32', '4.69','4.66','4.74', '4.41', '4.19', '4.25', '4.21', '4.27', '4.23',
                '4.76')
        ),
        # УД все продукты
        ('новый бизнес', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.1'), dates) +
                                                   sum_param(get_df_param(df, '2.2.1'), dates),
                                           '<b>2.1.1</b> + <b>2.2.1</b> (млн руб)', ('2.1.1', '2.2.1')),
        ('темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'): (lambda:
                                                                                       (diff(get_df_param(df, '2.1.1'),
                                                                                             dates,
                                                                                             dates_noform_calc) + diff(
                                                                                           get_df_param(df, '2.2.1'),
                                                                                           dates,
                                                                                           dates_noform_calc)) * 100 / (
                                                                                               get_df_param_stepback(
                                                                                                   get_df_param(df,
                                                                                                                '2.1.1'),
                                                                                                   dates, 4,
                                                                                                   sum_param,
                                                                                                   dates_noform_calc) + get_df_param_stepback(
                                                                                           get_df_param(df,
                                                                                                        '2.2.1'),
                                                                                           dates, 4, sum_param,
                                                                                           dates_noform_calc)),
                                                                                       'изменение(за год)( <b>2.1.1</b> + <b>2.2.1</b> )/(предыдущий год)( <b>2.1.1</b> + <b>2.2.1</b> ) (млн руб)',
                                                                                       ('2.1.1', '2.2.1')),
        ('темп прироста нового бизнеса скользящий год (квартал к кварталу)', 'все продукты'):
            (lambda: (sum_param(get_df_param(df, '2.1.1'), dates) +
                      sum_param(get_df_param(df, '2.2.1'), dates) -
                      (get_df_param_stepback(get_df_param(df, '2.1.1'), dates, 1, sum_param, dates_noform_calc) +
                       get_df_param_stepback(get_df_param(df, '2.2.1'), dates, 1, sum_param,
                                             dates_noform_calc))) * 100 /
                     (get_df_param_stepback(get_df_param(df, '2.1.1'), dates, 1, sum_param, dates_noform_calc) +
                      get_df_param_stepback(get_df_param(df, '2.2.1'), dates, 1, sum_param, dates_noform_calc)),
             'изменение(за квартал)( <b>2.1.1</b> + <b>2.2.1</b> )/(предыдущий квартал)( <b>2.1.1</b> + <b>2.2.1</b> ) (%)',
             ('2.1.1', '2.2.1')),
        ('лизинговый портфель', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.2'), dates) +
                                                          sum_param(get_df_param(df, '2.1.7'), dates) +
                                                          sum_param(get_df_param(df, '5.8'), dates) +
                                                          sum_param(get_df_param(df, '2.2.7'), dates),
                                                  '<b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> + <b>2.2.7</b>  (млн руб)',
                                                  ('2.1.2', '2.1.7', '5.8', '2.2.7')),#fixed (2.1.1 to 2.1.2)
        ('темп прироста лизингового портфеля (год к году)', 'все продукты'): (lambda:
                                                                              (diff(get_df_param(df, '2.1.2'),
                                                                                    dates, dates_noform_calc) +
                                                                               diff(get_df_param(df, '2.1.7'),
                                                                                    dates, dates_noform_calc) +
                                                                               diff(get_df_param(df, '5.8'),
                                                                                    dates, dates_noform_calc) +
                                                                               diff(get_df_param(df, '2.2.7'),
                                                                                    dates, dates_noform_calc)) * 100 /
                                                                              (get_df_param_stepback(
                                                                                  get_df_param(df, '2.1.2'), dates, 4,
                                                                                  sum_param, dates_noform_calc) +
                                                                               get_df_param_stepback(
                                                                                   get_df_param(df, '2.1.7'), dates, 4,
                                                                                   sum_param, dates_noform_calc) +
                                                                               get_df_param_stepback(
                                                                                   get_df_param(df, '5.8'), dates, 4,
                                                                                   sum_param, dates_noform_calc) +
                                                                               get_df_param_stepback(
                                                                                   get_df_param(df, '2.2.7'), dates, 4,
                                                                                   sum_param, dates_noform_calc)),
                                                                              'изменение(за год)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b>)/(предыдущий год)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b> (%))',
                                                                              ('2.1.2', '2.1.7', '5.8', '2.2.7')),
        ('темп прироста лизингового портфеля (квартал к кварталу)', 'все продукты'): (lambda:
                                                                                      (sum_param(
                                                                                          get_df_param(df, '2.1.2'),
                                                                                          dates) +
                                                                                       sum_param(
                                                                                           get_df_param(df, '2.1.7'),
                                                                                           dates) +
                                                                                       sum_param(
                                                                                           get_df_param(df, '5.8'),
                                                                                           dates) +
                                                                                       sum_param(
                                                                                           get_df_param(df, '2.2.7'),
                                                                                           dates) -
                                                                                       (get_df_param_stepback(
                                                                                           get_df_param(df, '2.1.2'),
                                                                                           dates, 1, sum_param,
                                                                                           dates_noform_calc) +
                                                                                        get_df_param_stepback(
                                                                                            get_df_param(df, '2.1.7'),
                                                                                            dates, 1, sum_param,
                                                                                            dates_noform_calc) +
                                                                                        get_df_param_stepback(
                                                                                            get_df_param(df, '5.8'),
                                                                                            dates, 1, sum_param,
                                                                                            dates_noform_calc) +
                                                                                        get_df_param_stepback(
                                                                                            get_df_param(df, '2.2.7'),
                                                                                            dates, 1,
                                                                                            sum_param,
                                                                                            dates_noform_calc))) * 100 /
                                                                                      (get_df_param_stepback(
                                                                                          get_df_param(df, '2.1.2'),
                                                                                          dates, 1, sum_param,
                                                                                          dates_noform_calc) +
                                                                                       get_df_param_stepback(
                                                                                           get_df_param(df, '2.1.7'),
                                                                                           dates, 1, sum_param,
                                                                                           dates_noform_calc) +
                                                                                       get_df_param_stepback(
                                                                                           get_df_param(df, '5.8'),
                                                                                           dates, 1, sum_param,
                                                                                           dates_noform_calc) +
                                                                                       get_df_param_stepback(
                                                                                           get_df_param(df, '2.2.7'),
                                                                                           dates, 1, sum_param,
                                                                                           dates_noform_calc)),
                                                                                      'изменение(за квартал)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b>)/(предыдущий квартал)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b> ) (%)',
                                                                                      ('2.1.2', '2.1.7', '5.8', '2.2.7')
                                                                                      ),
        ('NPL90+', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.4'), dates) +
                                             sum_param(get_df_param(df, '2.2.4'), dates),
                                     '<b>2.1.4</b> + <b>2.2.4</b>  (млн руб)',
                                     ('2.1.4', '2.2.4')),
        ('расторжения', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.7'), dates) +
                                                  sum_param(get_df_param(df, '2.2.7'), dates),
                                          '<b>2.1.7</b> + <b>2.2.7</b>  (млн руб)',
                                          ('2.1.7', '2.2.7')
                                          ),
        ('реструктуризации', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.5'), dates) -
                                                       sum_param(get_df_param(df, '2.1.6'), dates) +
                                                       sum_param(get_df_param(df, '2.2.5'), dates) -
                                                       sum_param(get_df_param(df, '2.2.6'), dates),
                                               '<b>2.1.5</b> - <b>2.1.6</b> + <b>2.2.5</b> - <b>2.2.6</b>  (млн руб)',
                                               ('2.1.5', '2.1.6', '2.2.5', '2.2.6')
                                               ),
        ('проблемные активы', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.1.4'), dates) +
                                                        sum_param(get_df_param(df, '2.2.4'), dates) +
                                                        sum_param(get_df_param(df, '2.1.7'), dates) +
                                                        sum_param(get_df_param(df, '2.2.7'), dates) +
                                                        sum_param(get_df_param(df, '2.1.5'), dates) -
                                                        sum_param(get_df_param(df, '2.1.6'), dates) +
                                                        sum_param(get_df_param(df, '2.2.5'), dates) -
                                                        sum_param(get_df_param(df, '2.2.6'), dates),
                                                '<b>2.1.4</b> + <b>2.2.4</b> + <b>2.1.7</b> + <b>2.2.7</b> + <b>2.1.5</b>'
                                                ' - <b>2.1.6</b> + <b>2.2.5</b> -  <b>2.2.6</b>  (млн руб)',
                                                ('2.1.4', '2.2.4', '2.1.7', '2.2.7', '2.1.5', '2.1.6', '2.2.5', '2.2.6')
                                                ),
        ('доля проблемных активов', 'все продукты'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                               sum_param(get_df_param(df, '2.2.4'), dates) +
                                                               sum_param(get_df_param(df, '2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '2.2.7'), dates) +
                                                               sum_param(get_df_param(df, '2.1.5'), dates) -
                                                               sum_param(get_df_param(df, '2.1.6'), dates) +
                                                               sum_param(get_df_param(df, '2.2.5'), dates) -
                                                               sum_param(get_df_param(df, '2.2.6'), dates)) * 100 /
                                                              (sum_param(get_df_param(df, '2.1.2'), dates) +
                                                               sum_param(get_df_param(df, '2.2.2'), dates) +
                                                               sum_param(get_df_param(df, '2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '2.2.7'), dates)),
                                                      '( <b>2.1.4</b> + <b>2.2.4</b> + <b>2.1.7</b> + <b>2.2.7</b> + <b>2.1.5</b>'
                                                      ' - <b>2.1.6</b> + <b>2.2.5</b> - <b>2.2.6</b> )/ (<b>2.1.2</b> + <b>2.2.2</b> + <b>2.1.7</b> + <b>2.2.7</b>)  (%)',
                                                      ('2.1.4', '2.2.4', '2.1.7', '2.2.7', '2.1.5', '2.1.6', '2.2.5',
                                                       '2.2.6', '2.1.2', '2.2.2')
                                                      ),
        ('доля NPL90+ в портфеле', 'все продукты'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                              sum_param(get_df_param(df, '2.2.4'), dates)) * 100 /
                                                             (sum_param(get_df_param(df, '2.1.2'), dates) +
                                                              sum_param(get_df_param(df, '2.2.2'), dates) +
                                                              sum_param(get_df_param(df, '2.1.7'), dates) +
                                                              sum_param(get_df_param(df, '2.2.7'), dates)),
                                                     '(<b>2.1.4</b> + <b>2.2.4</b>) / (<b>2.1.2</b> + <b>2.2.2</b> + <b>2.1.7</b> + <b>2.2.7</b>)  (%)',
                                                     ('2.1.4', '2.2.4', '2.1.2', '2.2.2', '2.1.7', '2.2.7')
                                                     ),
        ('доля резервов', 'все продукты'): (lambda: (sum_param(get_df_param(df, '5.58'), dates) +
                                                     sum_param(get_df_param(df, '5.57'), dates)) * 100 /
                                                    (sum_param(get_df_param(df, '5.4'), dates) +
                                                     sum_param(get_df_param(df, '5.58'), dates) +
                                                     sum_param(get_df_param(df, '5.8'), dates) +
                                                     sum_param(get_df_param(df, '5.57'), dates) +
                                                     sum_param(get_df_param(df, '5.10'), dates) +
                                                     sum_param(get_df_param(df, '5.12'), dates)),
                                            '(<b>5.58</b> + <b>5.57</b>) / (<b>5.4</b> + <b>5.58</b> + <b>5.8</b> + <b>5.57</b> + <b>5.10</b> + <b>5.12</b>)  (%)',
                                            ('5.58', '5.57', '5.4', '5.8', '5.57', '5.10', '5.12')
                                            ),
        ('покрытие NPL90+ всеми резервами', 'все продукты'): (lambda: (sum_param(get_df_param(df, '5.58'), dates) +
                                                                       sum_param(get_df_param(df, '5.57'),
                                                                                 dates)) * 100 /
                                                                      (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                                       sum_param(get_df_param(df, '2.2.4'), dates)),
                                                              '(<b>5.58</b> + <b>5.57</b>) / (<b>2.1.4</b> + <b>2.2.4</b>)  (%)',
                                                              ('5.58', '5.57', '2.1.4', '2.2.4')
                                                              ),
        ('покрытие проблемных активов всеми резервами', 'все продукты'): (lambda:
                                                                          (sum_param(get_df_param(df, '5.58'), dates) +
                                                                           sum_param(get_df_param(df, '5.57'), dates) +
                                                                           sum_param(get_df_param(df, '5.62'),
                                                                                     dates)) * 100 /
                                                                          (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                                           sum_param(get_df_param(df, '2.2.4'), dates) +
                                                                           sum_param(get_df_param(df, '2.1.7'), dates) +
                                                                           sum_param(get_df_param(df, '2.2.7'), dates) +
                                                                           sum_param(get_df_param(df, '2.1.5'), dates) -
                                                                           sum_param(get_df_param(df, '2.1.6'), dates) +
                                                                           sum_param(get_df_param(df, '2.2.5'), dates) -
                                                                           sum_param(get_df_param(df, '2.2.6'), dates)
                                                                           ),
                                                                          '(<b>5.58</b> + <b>5.57</b> + <b>5.62</b>) / (<b>2.1.4</b> + <b>2.2.4</b> + <b>2.1.7</b> + <b>2.2.7</b>+ <b>2.1.5</b>'
                                                                          ' - <b>2.1.6</b> + <b>2.2.5</b> - <b>2.2.6</b>)  (%)',
                                                                          ('5.58', '5.57', '5.62', '2.1.4', '2.2.4',
                                                                           '2.1.7', '2.2.7', '2.1.5',
                                                                           '2.1.6', '2.2.5', '2.2.6')
                                                                          ),
        ('объем досрочно выкупленного имущества', 'все продукты'): (
            lambda: sum_param(get_df_param(df, '2.1.9'), dates) +
                    sum_param(get_df_param(df, '2.2.9'), dates),
            '<b>2.1.9</b> + <b>2.2.9</b> (млн руб)', ('2.1.9', '2.2.9')),
        ('объем замороженных активов', 'все продукты'): (lambda: sum_param(get_df_param(df, '2.2.10'), dates),
                                                         '<b>2.2.10</b> (млн руб)', ('2.2.10',)),
        ('сегменты: легковые автомобили', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                                    sum_param(get_df_param(df, '3.2.1.1'), dates),
                                                            '<b>3.1.1.1</b> + <b>3.2.1.1</b> (млн руб)',
                                                            ('3.1.1.1', '3.2.1.1')),
        ('сегменты: грузовые автомобили', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                                    sum_param(get_df_param(df, '3.2.1.3'), dates),
                                                            '<b>3.1.1.3</b> + <b>3.2.1.3</b> (млн руб)',
                                                            ('3.1.1.3', '3.2.1.3')
                                                            ),
        ('сегменты: ж/д', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                    sum_param(get_df_param(df, '3.2.1.5'), dates),
                                            '<b>3.1.1.5</b> + <b>3.2.1.5</b> (млн руб)', ('3.1.1.5', '3.2.1.5')
                                            ),
        ('сегменты: авиа', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                     sum_param(get_df_param(df, '3.2.1.7'), dates),
                                             '<b>3.1.1.7</b> + <b>3.2.1.7</b> (млн руб)', ('3.1.1.7', '3.2.1.7')
                                             ),
        ('сегменты: спецтехника', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.8'), dates),
                                                    '<b>3.1.1.8</b> + <b>3.2.1.8</b> (млн руб)', ('3.1.1.8', '3.2.1.8')
                                                    ),
        ('сегменты: недвижимость', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.10'), dates),
                                                     '<b>3.1.1.10</b> + <b>3.2.1.10</b> (млн руб)',
                                                     ('3.1.1.10', '3.2.1.10')
                                                     ),
        ('сегменты: c/x', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                    sum_param(get_df_param(df, '3.2.1.11'), dates),
                                            '<b>3.1.1.11</b> + <b>3.2.1.11</b> (млн руб)', ('3.1.1.11', '3.2.1.11')
                                            ),
        ('сегменты: суда', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                     sum_param(get_df_param(df, '3.2.1.13'), dates),
                                             '<b>3.1.1.13</b> + <b>3.2.1.13</b> (млн руб)', ('3.1.1.13', '3.2.1.13')
                                             ),
        ('сегменты: прочее', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                       sum_param(get_df_param(df, '3.2.1.14'), dates),
                                               '<b>3.1.1.14</b> + <b>3.2.1.14</b> (млн руб)', ('3.1.1.14', '3.2.1.14')
                                               ),
        ('сегменты: субсидии', 'все продукты'): (lambda: sum_param(get_df_param(df, '3.1.1.15'), dates),
                                                 '<b>3.1.1.15</b> (млн руб)', ('3.1.1.15',)
                                                 ),
        ('сегменты: доля легковых', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.1'), dates)) * 100 /
                                                              (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                               ),
                                                      '(<b>3.1.1.1</b> + <b>3.2.1.1</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                      '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                      '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                      '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                      ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                      ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5', '3.2.1.5',
                                                       '3.1.1.7', '3.2.1.7',
                                                       '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                       '3.2.1.11',
                                                       '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                      ),
        ('сегменты: доля грузовых', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.3'), dates)) * 100 /
                                                              (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                               sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                               sum_param(get_df_param(df, '3.2.1.14'), dates)),
                                                      '(<b>3.1.1.3</b> + <b>3.2.1.3</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                      '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                      '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                      '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                      ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                      ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5',
                                                       '3.2.1.5', '3.1.1.7', '3.2.1.7',
                                                       '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                       '3.2.1.11',
                                                       '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                      ),
        ('сегменты: доля ж/д', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.5'), dates)) * 100 /
                                                         (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                          ),
                                                 '(<b>3.1.1.5</b> + <b>3.2.1.5</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                 '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                 '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                 '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                 ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                 ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5', '3.2.1.5',
                                                  '3.1.1.7', '3.2.1.7',
                                                  '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11', '3.2.1.11',
                                                  '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                 ),
        ('сегменты: доля авиа', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.7'), dates)) * 100 /
                                                          (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                           sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                           sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                           ),
                                                  '(<b>3.1.1.7</b> + <b>3.2.1.7</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                  '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                  '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                  '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                  ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                  ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5', '3.2.1.5',
                                                   '3.1.1.7', '3.2.1.7',
                                                   '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11', '3.2.1.11',
                                                   '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                  ),
        ('сегменты: доля спецтехники', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.8'), dates)) * 100 /
                                                                 (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                                  sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                                  sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                                  ),
                                                         '(<b>3.1.1.8</b> + <b>3.2.1.8</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                         '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                         '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                         '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                         ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                         ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5',
                                                          '3.2.1.5', '3.1.1.7', '3.2.1.7',
                                                          '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                          '3.2.1.11',
                                                          '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                         ),
        ('сегменты: доля недвижимости', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.10'),
                                                                             dates)) * 100 /
                                                                  (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                                   sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                                   sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                                   ),
                                                                  '(<b>3.1.1.10</b> + <b>3.2.1.10</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                                  '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                                  '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                                  '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                                  ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                                  (
                                                                      '3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3',
                                                                      '3.1.1.5',
                                                                      '3.2.1.5', '3.1.1.7', '3.2.1.7',
                                                                      '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10',
                                                                      '3.1.1.11', '3.2.1.11',
                                                                      '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                                  ),
        ('сегменты: доля с/х', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.11'), dates)) * 100 /
                                                         (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                          sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                          sum_param(get_df_param(df, '3.2.1.14'), dates)),
                                                          '(<b>3.1.1.11</b> + <b>3.2.1.11</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                          '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                          '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                          '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                          ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                          ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5',
                                                           '3.2.1.5', '3.1.1.7', '3.2.1.7',
                                                           '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                           '3.2.1.11',
                                                           '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')

                                                 ),
        ('сегменты: доля судов', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.13'), dates)) * 100 /
                                                           (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                            sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                            sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                            ),
                                                   '(<b>3.1.1.13</b> + <b>3.2.1.13</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                   '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                   '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                   '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                   ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                   ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5', '3.2.1.5',
                                                    '3.1.1.7', '3.2.1.7',
                                                    '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                    '3.2.1.11',
                                                    '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                   ),
        ('сегменты: доля прочих', 'все продукты'): (lambda: (sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.14'), dates)) * 100 /
                                                            (sum_param(get_df_param(df, '3.1.1.1'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.3'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.5'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.7'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.8'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.10'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.11'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.13'), dates) +
                                                             sum_param(get_df_param(df, '3.1.1.14'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.1'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.3'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.5'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.7'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.8'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.10'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.11'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.13'), dates) +
                                                             sum_param(get_df_param(df, '3.2.1.14'), dates)
                                                             ),
                                                    '(<b>3.1.1.14</b> + <b>3.2.1.14</b>)/(<b>3.1.1.1</b> + <b>3.2.1.1</b> + '
                                                    '<b>3.1.1.3</b> + <b>3.2.1.3</b> + <b>3.1.1.5</b> + <b>3.2.1.5</b> + '
                                                    '<b>3.1.1.7</b> + <b>3.2.1.7</b> + <b>3.1.1.8</b> + <b>3.2.1.8</b> + '
                                                    '<b>3.1.1.10</b> + <b>3.2.1.10</b> + <b>3.1.1.11</b> + <b>3.2.1.11</b>'
                                                    ' + <b>3.1.1.13</b> + <b>3.2.1.13</b> + <b>3.1.1.14</b> + <b>3.2.1.14</b>)  (%)',
                                                    ('3.1.1.1', '3.2.1.1', '3.1.1.3', '3.2.1.3', '3.1.1.5', '3.2.1.5',
                                                     '3.1.1.7', '3.2.1.7',
                                                     '3.1.1.8', '3.2.1.8', '3.1.1.10', '3.2.1.10', '3.1.1.11',
                                                     '3.2.1.11',
                                                     '3.1.1.13', '3.2.1.13', '3.1.1.14', '3.2.1.14')
                                                    ),
        # УД финансовый лизинг
        ('новый бизнес', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.1'), dates),
                                                '<b>2.1.1</b>  (млн руб)', ('2.1.1',)),
        ('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'): (lambda:
                                                                                            diff(get_df_param(df,
                                                                                                              '2.1.1'),
                                                                                                 dates,
                                                                                                 dates_noform_calc) * 100 /
                                                                                            get_df_param_stepback(
                                                                                                get_df_param(df,
                                                                                                             '2.1.1'),
                                                                                                dates, 4, sum_param,
                                                                                                dates_noform_calc),
                                                                                            'изменение(за год)( <b>2.1.1</b>  )/(предыдущий год)( <b>2.1.1</b> ) (%)',
                                                                                            ('2.1.1',)),
        ('темп прироста нового бизнеса скользящий год (квартал к кварталу)', 'финансовый лизинг'): (lambda:
                                                                                                    (sum_param(
                                                                                                        get_df_param(df,
                                                                                                                     '2.1.1'),
                                                                                                        dates) - get_df_param_stepback(
                                                                                                        get_df_param(df,
                                                                                                                     '2.1.1'),
                                                                                                        dates, 1,
                                                                                                        sum_param,
                                                                                                        dates_noform_calc)) * 100 / get_df_param_stepback(
                                                                                                        get_df_param(df,
                                                                                                                     '2.1.1'),
                                                                                                        dates, 1,
                                                                                                        sum_param,
                                                                                                        dates_noform_calc),
                                                                                                    'изменение(за квартал)( <b>2.1.1</b>  )/(предыдущий квартал)( <b>2.1.1</b> ) (%)',
                                                                                                    ('2.1.1',)),

        ('лизинговый портфель', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.2'), dates) +
                                                               sum_param(get_df_param(df, '2.1.7'), dates),
                                                       '<b>2.1.2</b> + <b>2.1.7</b> (млн руб)',
                                                       ('2.1.2', '2.1.7')
                                                       ),
        ('темп прироста лизингового портфеля (год к году)', 'финансовый лизинг'): (lambda:
                                                                                   (diff(get_df_param(df, '2.1.2'),
                                                                                         dates,
                                                                                         dates_noform_calc) + diff(
                                                                                       get_df_param(df, '2.1.7'),
                                                                                       dates,
                                                                                       dates_noform_calc)) * 100 /
                                                                                   (get_df_param_stepback(
                                                                                       get_df_param(df, '2.1.2'), dates,
                                                                                       4,
                                                                                       sum_param,
                                                                                       dates_noform_calc) + get_df_param_stepback(
                                                                                       get_df_param
                                                                                       (df, '2.1.7'), dates, 4,
                                                                                       sum_param, dates_noform_calc)),
                                                                                   'изменение(за год)( <b>2.1.2</b> + <b>2.1.7</b>)/(предыдущий год)( <b>2.1.2</b> + <b>2.1.7</b>) (%)',
                                                                                   ('2.1.2', '2.1.7')),
        ('темп прироста лизингового портфеля (квартал к кварталу)', 'финансовый лизинг'): (lambda:
                                                                                           (sum_param(get_df_param(df,
                                                                                                                   '2.1.2'),
                                                                                                      dates) +
                                                                                            sum_param(get_df_param(df,
                                                                                                                   '2.1.7'),
                                                                                                      dates) -
                                                                                            (get_df_param_stepback(
                                                                                                get_df_param(df,
                                                                                                             '2.1.2'),
                                                                                                dates, 1,
                                                                                                sum_param,
                                                                                                dates_noform_calc) + get_df_param_stepback(
                                                                                                get_df_param
                                                                                                (df, '2.1.7'), dates, 1,
                                                                                                sum_param,
                                                                                                dates_noform_calc))) * 100 / (
                                                                                                   get_df_param_stepback(
                                                                                                       get_df_param(
                                                                                                           df,
                                                                                                           '2.1.2'),
                                                                                                       dates, 1,
                                                                                                       sum_param,
                                                                                                       dates_noform_calc) + get_df_param_stepback(
                                                                                               get_df_param(df,
                                                                                                            '2.1.7'),
                                                                                               dates, 1,
                                                                                               sum_param,
                                                                                               dates_noform_calc)),
                                                                                           'изменение(за квартал)( <b>2.1.2</b> + <b>2.1.7</b>)/(предыдущий квартал)( <b>2.1.2</b> + <b>2.1.7</b>) (%)',
                                                                                           ('2.1.2', '2.1.7')),
        ('NPL90+', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.4'), dates),
                                          '<b>2.1.4</b>  (млн руб)', ('2.1.4',)),
        ('расторжения', 'финансовый лизинг'): (
            lambda: sum_param(get_df_param(df, '2.1.7'), dates), '<b>2.1.7</b>  (млн руб)', ('2.1.7',)),
        ('реструктуризации', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.5'), dates) -
                                                            sum_param(get_df_param(df, '2.1.6'), dates),
                                                    '<b>2.1.5</b> - <b>2.1.6</b> (млн руб)',
                                                    ('2.1.5', '2.1.6')
                                                    ),
        ('проблемные активы', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.4'), dates) +
                                                             sum_param(get_df_param(df, '2.1.7'), dates) +
                                                             sum_param(get_df_param(df, '2.1.5'), dates) -
                                                             sum_param(get_df_param(df, '2.1.6'), dates),
                                                     '<b>2.1.4</b> + <b>2.1.7</b> + <b>2.1.5</b> - <b>2.1.6</b> (млн руб)',
                                                     ('2.1.4', '2.1.7', '2.1.5', '2.1.6')
                                                     ),
        ('доля проблемных активов', 'финансовый лизинг'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                                    sum_param(get_df_param(df, '2.1.7'), dates) +
                                                                    sum_param(get_df_param(df, '2.1.5'), dates) -
                                                                    sum_param(get_df_param(df, '2.1.6'), dates)) * 100 /
                                                                   (sum_param(get_df_param(df, '2.1.2'), dates) +
                                                                    sum_param(get_df_param(df, '2.1.7'), dates)),
                                                           '( <b>2.1.4</b> + <b>2.1.7</b> + <b>2.1.5</b>'
                                                           ' - <b>2.1.6</b>/ (<b>2.1.2</b> + <b>2.1.7</b>)  (%)',
                                                           ('2.1.4', '2.1.7', '2.1.5', '2.1.6', '2.1.2')
                                                           ),
        ('доля проблемных активов', 'Данные ФСБУ: операционная аренда'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                                    sum_param(get_df_param(df, '2.1.7'), dates) +
                                                                    sum_param(get_df_param(df, '2.1.5'), dates) -
                                                                    sum_param(get_df_param(df, '2.1.6'), dates)) * 100 /
                                                                   (sum_param(get_df_param(df, '2.2.2'), dates) +
                                                                    sum_param(get_df_param(df, '2.2.7'), dates)),
                                                           '( <b>2.1.4</b> + <b>2.1.7</b> + <b>2.1.5</b>'
                                                           ' - <b>2.1.6</b>/ (<b>2.2.2</b> + <b>2.2.7</b>)  (%)',
                                                           ('2.1.4', '2.1.7', '2.1.5', '2.1.6', '2.1.2')
                                                           ),
        ('доля проблемных активов', 'Данные ФСБУ: все продукты'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates) +
                                                               sum_param(get_df_param(df, '2.2.4'), dates) +
                                                               sum_param(get_df_param(df, '2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '2.2.7'), dates) +
                                                               sum_param(get_df_param(df, '2.1.5'), dates) -
                                                               sum_param(get_df_param(df, '2.1.6'), dates) +
                                                               sum_param(get_df_param(df, '2.2.5'), dates) -
                                                               sum_param(get_df_param(df, '2.2.6'), dates)) * 100 /
                                                              (sum_param(get_df_param(df, '2.1.2'), dates) +
                                                               sum_param(get_df_param(df, '2.2.2'), dates) +
                                                               sum_param(get_df_param(df, '2.1.7'), dates) +
                                                               sum_param(get_df_param(df, '2.2.7'), dates)),
                                                      '( <b>2.1.4</b> + <b>2.2.4</b> + <b>2.1.7</b> + <b>2.2.7</b> + <b>2.1.5</b>'
                                                      ' - <b>2.1.6</b> + <b>2.2.5</b> - <b>2.2.6</b> )/ (<b>2.1.2</b> + <b>2.2.2</b> + <b>2.1.7</b> + <b>2.2.7</b>)  (%)',
                                                      ('2.1.4', '2.2.4', '2.1.7', '2.2.7', '2.1.5', '2.1.6', '2.2.5',
                                                       '2.2.6', '2.1.2', '2.2.2')
                                                      ),
        ('доля NPL90+ в портфеле', 'финансовый лизинг'): (lambda: (sum_param(get_df_param(df, '2.1.4'), dates)) * 100 /
                                                                  (sum_param(get_df_param(df, '2.1.2'), dates) +
                                                                   sum_param(get_df_param(df, '2.1.7'), dates)),
                                                          '(<b>2.1.4</b>/ (<b>2.1.2</b> + <b>2.1.7</b>)  (%)',
                                                          ('2.1.4', '2.1.2', '2.1.7')
                                                          ),
        ('доля резервов', 'финансовый лизинг'): (lambda: (sum_param(get_df_param(df, '5.58'), dates)) * 100 /
                                                         (sum_param(get_df_param(df, '5.4'), dates) +
                                                          sum_param(get_df_param(df, '5.58'), dates) +
                                                          sum_param(get_df_param(df, '5.10'), dates)),
                                                 '(<b>5.58</b>) / (<b>5.4</b> + <b>5.58</b> + <b>5.10</b>)  (%)',
                                                 ('5.58', '5.4', '5.10')
                                                 ),
        ('покрытие NPL90+ всеми резервами', 'финансовый лизинг'): (lambda: (sum_param(get_df_param(df, '5.58'),
                                                                                      dates)) * 100 /
                                                                           (sum_param(get_df_param(df, '2.1.4'),
                                                                                      dates)),
                                                                   '(<b>5.58</b>) / (<b>2.1.4</b>)  (%)',
                                                                   ('5.58', '2.1.4')
                                                                   ),
        ('покрытие проблемных активов всеми резервами', 'финансовый лизинг'): (lambda:
                                                                               (sum_param(get_df_param(df, '5.58'),
                                                                                          dates) +
                                                                                sum_param(get_df_param(df, '5.62'),
                                                                                          dates)) * 100 /
                                                                               (sum_param(get_df_param(df, '2.1.4'),
                                                                                          dates) +
                                                                                sum_param(get_df_param(df, '2.1.7'),
                                                                                          dates) +
                                                                                sum_param(get_df_param(df, '2.1.5'),
                                                                                          dates) -
                                                                                sum_param(get_df_param(df, '2.1.6'),
                                                                                          dates)
                                                                                ),
                                                                               '(<b>5.58</b> + <b>5.62</b>) / (<b>2.1.4</b> + <b>2.1.7</b> + <b>2.1.5</b> - <b>2.1.6</b>)  (%)',
                                                                               ('5.58', '5.62', '2.1.4',
                                                                                '2.1.7', '2.1.5', '2.1.6')),
        ('объем досрочно выкупленного имущества', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '2.1.9'),
                                                                                           dates),
                                                                         '<b>2.1.9</b> (млн руб)', ('2.1.9',)),
        ('сегменты: легковые автомобили', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.1'), dates),
                                                                 '<b>3.1.1.1</b> (млн руб)', ('3.1.1.1',)),
        ('сегменты: грузовые автомобили', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.3'), dates),
                                                                 '<b>3.1.1.3</b> (млн руб)', ('3.1.1.3',)),
        ('сегменты: ж/д', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.5'), dates),
                                                 '<b>3.1.1.5</b> (млн руб)', ('3.1.1.5',)),
        ('сегменты: авиа', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.7'), dates),
                                                  '<b>3.1.1.7</b> (млн руб)', ('3.1.1.7',)),
        ('сегменты: спецтехника', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.8'), dates),
                                                         '<b>3.1.1.8</b> (млн руб)', ('3.1.1.8',)),
        ('сегменты: недвижимость', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.10'), dates),
                                                          '<b>3.1.1.10</b> (млн руб)', ('3.1.1.10',)),
        ('сегменты: c/x', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.11'), dates),
                                                 '<b>3.1.1.11</b> (млн руб)', ('3.1.1.11',)),
        ('сегменты: суда', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.13'), dates),
                                                  '<b>3.1.1.13</b> (млн руб)', ('3.1.1.13',)),
        ('сегменты: прочее', 'финансовый лизинг'): (lambda: sum_param(get_df_param(df, '3.1.1.14'), dates),
                                                    '<b>3.1.1.14</b> (млн руб)', ('3.1.1.14',)),
        # УД операционная аренда
        ('новый бизнес', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '2.2.1'), dates),
                                                  '<b>2.2.1</b> (млн руб)', ('2.2.1',)),
        ('темп прироста нового бизнеса скользящий год (год к году)', 'операционная аренда'): (lambda:
                                                                                              diff(get_df_param(df,
                                                                                                                '2.2.1'),
                                                                                                   dates,
                                                                                                   dates_noform_calc) * 100 /
                                                                                              get_df_param_stepback(
                                                                                                  get_df_param(df,
                                                                                                               '2.2.1'),
                                                                                                  dates, 4, sum_param,
                                                                                                  dates_noform_calc),
                                                                                              'изменение(за год)( <b>2.2.1</b>  )/(предыдущий год)( <b>2.2.1</b> ) (%)',
                                                                                              ('2.2.1',)),
        ('темп прироста нового бизнеса скользящий год (квартал к кварталу)', 'операционная аренда'): (lambda:
                                                                                                      (sum_param(
                                                                                                          get_df_param(
                                                                                                              df,
                                                                                                              '2.2.1'),
                                                                                                          dates) -
                                                                                                       get_df_param_stepback(
                                                                                                           get_df_param(
                                                                                                               df,
                                                                                                               '2.2.1'),
                                                                                                           dates, 1,
                                                                                                           sum_param,
                                                                                                           dates_noform_calc)) * 100 /
                                                                                                      get_df_param_stepback(
                                                                                                          get_df_param(
                                                                                                              df,
                                                                                                              '2.2.1'),
                                                                                                          dates, 1,
                                                                                                          sum_param,
                                                                                                          dates_noform_calc),
                                                                                                      'изменение(за квартал)( <b>2.2.1</b>  )/(предыдущий квартал)( <b>2.2.1</b> ) (%)',
                                                                                                      ('2.2.1',)),
        ('лизинговый портфель', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '5.8'), dates) +
                                                                 sum_param(get_df_param(df, '2.2.7'), dates),
                                                         '<b>5.8</b> + <b>2.2.7</b> (млн руб)',
                                                         ('5.8', '2.2.7')),
        ('темп прироста лизингового портфеля (год к году)', 'операционная аренда'): (lambda:
                                                                                     (diff(get_df_param(df, '5.8'),
                                                                                           dates,
                                                                                           dates_noform_calc) + diff(
                                                                                         get_df_param(df, '2.2.7'),
                                                                                         dates,
                                                                                         dates_noform_calc)) * 100 /
                                                                                     (get_df_param_stepback(
                                                                                         get_df_param(df, '5.8'), dates,
                                                                                         4,
                                                                                         sum_param,
                                                                                         dates_noform_calc) + get_df_param_stepback
                                                                                      (get_df_param(df, '2.2.7'), dates,
                                                                                       4, sum_param,
                                                                                       dates_noform_calc)),
                                                                                     'изменение(за год)( <b>5.8</b> + <b>2.2.7</b>)/(предыдущий год)( <b>5.8</b> + <b>2.2.7</b>) (%)',
                                                                                     ('5.8', '2.2.7')),
        ('темп прироста лизингового портфеля (квартал к кварталу)', 'операционная аренда'): (lambda:
                                                                                             (sum_param(get_df_param(df,'5.8'),dates) + sum_param(
                                                                                                 get_df_param(df,'2.2.7'),dates) -
                                                                                              (get_df_param_stepback(get_df_param(df,'5.8'),
                                                                                                dates, 1,sum_param,dates_noform_calc) + get_df_param_stepback
                                                                                              (get_df_param(df,'2.2.7'),dates, 1,
                                                                                               sum_param, dates_noform_calc))) * 100 /
                                                                                             (get_df_param_stepback(get_df_param(df,'5.8'),
                                                                                                 dates, 1,sum_param,
                                                                                                 dates_noform_calc) + get_df_param_stepback(
                                                                                                 get_df_param
                                                                                                 (df, '2.2.7'), dates,
                                                                                                 1, sum_param,
                                                                                                 dates_noform_calc)),
                                                                                             'изменение(за квартал)( <b>5.8</b> + <b>2.2.7</b>)/(предыдущий квартал)( <b>5.8</b> + <b>2.2.7</b>)  (%)',
                                                                                             ('5.8', '2.2.7')),
        ('NPL90+', 'операционная аренда'): (
            lambda: sum_param(get_df_param(df, '2.2.4'), dates), '<b>2.2.4</b> (млн руб)', ('2.2.4',)),
        ('расторжения', 'операционная аренда'): (
            lambda: sum_param(get_df_param(df, '2.2.7'), dates), '<b>2.2.7</b> (млн руб)', ('2.2.7',)),
        ('реструктуризации', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '2.2.5'), dates) -
                                                              sum_param(get_df_param(df, '2.2.6'), dates),
                                                      '<b>2.2.5</b> - <b>2.2.6</b> (млн руб)',
                                                      ('2.2.5', '2.2.6')),
        ('проблемные активы', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '2.2.4'), dates) +
                                                               sum_param(get_df_param(df, '2.2.7'), dates) +
                                                               sum_param(get_df_param(df, '2.2.5'), dates) -
                                                               sum_param(get_df_param(df, '2.2.6'), dates),
                                                       '<b>2.2.4</b> + <b>2.2.7</b> + <b>2.2.5</b> - <b>2.2.6</b> (млн руб)',
                                                       ('2.2.4', '2.2.7', '2.2.5', '2.2.6')),
        ('доля проблемных активов', 'операционная аренда'): (lambda: (sum_param(get_df_param(df, '2.2.4'), dates) +
                                                                      sum_param(get_df_param(df, '2.2.7'), dates) +
                                                                      sum_param(get_df_param(df, '2.2.5'), dates) -
                                                                      sum_param(get_df_param(df, '2.2.6'),
                                                                                dates)) * 100 /
                                                                     (sum_param(get_df_param(df, '2.2.2'), dates) +
                                                                      sum_param(get_df_param(df, '2.2.7'), dates)),
                                                             '( <b>2.2.4</b> + <b>2.2.7</b> + <b>2.2.5</b>'
                                                             ' - <b>2.2.6</b>/ (<b>2.2.2</b> + <b>2.2.7</b>)  (%)',
                                                             ('2.2.4', '2.2.7', '2.2.5', '2.2.6', '2.2.2')),
        ('доля NPL90+ в портфеле', 'операционная аренда'): (
            lambda: (sum_param(get_df_param(df, '2.2.4'), dates)) * 100 /
                    (sum_param(get_df_param(df, '2.2.2'), dates) +
                     sum_param(get_df_param(df, '2.2.7'), dates)),
            '(<b>2.2.4</b>/ (<b>2.2.2</b> + <b>2.2.7</b>)  (%)',
            ('2.2.4', '2.2.2', '2.2.7')
        ),
        ('доля резервов', 'операционная аренда'): (lambda: (sum_param(get_df_param(df, '5.57'), dates)) * 100 /
                                                           (sum_param(get_df_param(df, '5.8'), dates) +
                                                            sum_param(get_df_param(df, '5.57'), dates) +
                                                            sum_param(get_df_param(df, '5.12'), dates)),
                                                   '(<b>5.57</b>) / (<b>5.8</b> + <b>5.57</b> + <b>5.12</b>)  (%)',
                                                   ('5.57', '5.8', '5.12')
                                                   ),
        ('покрытие NPL90+ всеми резервами', 'операционная аренда'): (lambda: (sum_param(get_df_param(df, '5.57'),
                                                                                        dates)) * 100 /
                                                                             (sum_param(get_df_param(df, '2.2.4'),
                                                                                        dates)),
                                                                     '(<b>5.57</b>) / (<b>2.2.4</b>)  (%)',
                                                                     ('5.57', '2.2.4')
                                                                     ),
        ('покрытие проблемных активов всеми резервами', 'операционная аренда'): (lambda:
                                                                                 (sum_param(get_df_param(df, '5.57'),
                                                                                            dates) +
                                                                                  sum_param(get_df_param(df, '5.62'),
                                                                                            dates)) * 100 /
                                                                                 (sum_param(get_df_param(df, '2.2.4'),
                                                                                            dates) +
                                                                                  sum_param(get_df_param(df, '2.2.7'),
                                                                                            dates) +
                                                                                  sum_param(get_df_param(df, '2.2.5'),
                                                                                            dates) -
                                                                                  sum_param(get_df_param(df, '2.2.6'),
                                                                                            dates)
                                                                                  ),
                                                                                 '(<b>5.57</b> + <b>5.62</b>) / (<b>2.2.4</b> + <b>2.2.7</b> + <b>2.2.5</b> - <b>2.2.6</b>)  (%)',
                                                                                 ('5.57', '5.62', '2.2.4',
                                                                                  '2.2.7', '2.2.5', '2.2.6')),
        ('объем досрочно выкупленного имущества', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '2.2.9'),
                                                                                             dates),
                                                                           '<b>2.2.9</b> (млн руб)', ('2.2.9',)),
        ('сегменты: легковые автомобили', 'операционная аренда'): (
            lambda: sum_param(get_df_param(df, '3.2.1.1'), dates),
            '<b>3.2.1.1</b> (млн руб)', ('3.2.1.1',)),
        ('сегменты: грузовые автомобили', 'операционная аренда'): (
            lambda: sum_param(get_df_param(df, '3.2.1.3'), dates),
            '<b>3.2.1.3</b> (млн руб)', ('3.2.1.3',)),
        ('сегменты: ж/д', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.5'), dates),
                                                   '<b>3.2.1.5</b> (млн руб)', ('3.2.1.5',)),
        ('сегменты: авиа', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.7'), dates),
                                                    '<b>3.2.1.7</b> (млн руб)', ('3.2.1.7',)),
        ('сегменты: спецтехника', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.8'), dates),
                                                           '<b>3.2.1.8</b> (млн руб)', ('3.2.1.8',)),
        ('сегменты: недвижимость', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.10'), dates),
                                                            '<b>3.2.1.10</b> (млн руб)', ('3.2.1.10',)),
        ('сегменты: c/x', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.11'), dates),
                                                   '<b>3.2.1.1</b> (млн руб)', ('3.2.1.11',)),
        ('сегменты: суда', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.13'), dates),
                                                    '<b>3.2.1.13</b> (млн руб)', ('3.2.1.13',)),
        ('сегменты: прочее', 'операционная аренда'): (lambda: sum_param(get_df_param(df, '3.2.1.14'), dates),
                                                      '<b>3.2.1.14</b> (млн руб)', ('3.2.1.14',)),
        # Данные МСФО
        ('Прочие расходы', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.41'), dates), '<b>5.41</b> (млн руб)', ('5.41',)),
        ('АКТИВЫ', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.1'), dates), '<b>5.1</b> (млн руб)', ('5.1',)),
        ('Денежные средства и их эквиваленты', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.2'), dates), '<b>5.2</b> (млн руб)', ('5.2',)),
        ('Чистые инвестиции в финансовый лизинг', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.4'), dates), '<b>5.4</b> (млн руб)', ('5.4',)),
        ('Оборудование для передачи в лизинг', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.6'), dates), '<b>5.6</b> (млн руб)', ('5.6',)),
        ('Авансовые платежи поставщикам и подрядчикам', 'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.7'),
                                                                                           dates),
                                                                         '<b>5.7</b> (млн руб)', ('5.7',)),
        ('Имущество, переданное в операционную аренду', 'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.8'),
                                                                                           dates),
                                                                         '<b>5.8</b> (млн руб)', ('5.8',)),
        ('Займы выданные', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.53'), dates), '<b>5.53</b> (млн руб)', ('5.53',)),
        ('Дебиторская задолженность по расторгнутым договорам лизинга', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.9'), dates), '<b>5.9</b> (млн руб)', ('5.9',)),
        ('в т.ч. финансовый лизинг', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.10'), dates), '<b>5.10</b> (млн руб)', ('5.10',)),
        ('Финансовые инструменты', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.54'), dates), '<b>5.54</b> (млн руб)', ('5.54',)),
        ('Активы, предназначенные для продажи по расторгнутым договорам лизинга', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.14'), dates), '<b>5.14</b> (млн руб)', ('5.14',)),
        ('Нематериальные активы', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.55'), dates), '<b>5.55</b> (млн руб)', ('5.55',)),
        ('Прочие активы', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.15'), dates), '<b>5.15</b> (млн руб)', ('5.15',)),
        ('КАПИТАЛ И ОБЯЗАТЕЛЬСТВА', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.16'), dates), '<b>5.16</b> (млн руб)', ('5.16',)),
        ('ОБЯЗАТЕЛЬСТВА', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.17'), dates), '<b>5.17</b> (млн руб)', ('5.17',)),
        ('Кредиты полученные', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.18'), dates), '<b>5.18</b> (млн руб)', ('5.18',)),
        ('Займы полученные', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.20'), dates), '<b>5.20</b> (млн руб)', ('5.20',)),
        ('Выпущенные долговые ценные бумаги', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.22'), dates), '<b>5.22</b> (млн руб)', ('5.22',)),
        ('Обязательства по финансовой аренде', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.23'), dates), '<b>5.23</b> (млн руб)', ('5.23',)),
        ('Кредиторская задолженность перед поставщиками оборудования, приобретенного для передачи в лизинг',
         'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.24'), dates), '<b>5.24</b> (млн руб)', ('5.24',)),
        ('Авансы от лизингополучателей', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.25'), dates), '<b>5.25</b> (млн руб)', ('5.25',)),
        ('КАПИТАЛ', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.27'), dates), '<b>5.27</b> (млн руб)', ('5.27',)),
        ('Нераспределенная прибыль', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.30'), dates), '<b>5.30</b> (млн руб)', ('5.30',)),
        ('Выручка (процентный доход)', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.31'), dates), '<b>5.31</b> (млн руб)', ('5.31',)),
        ('выручка в т.ч. финансовый лизинг', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.32'), dates), '<b>5.32</b> (млн руб)', ('5.32',)),
        ('выручка в т.ч. операционный лизинг', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.33'), dates), '<b>5.33</b> (млн руб)', ('5.33',)),
        ('Процентные расходы', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.34'), dates), '<b>5.34</b> (млн руб)', ('5.34',)),
        ('процентные расходы в т.ч. финансовый лизинг', 'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.35'),
                                                                                           dates),
                                                                         '<b>5.35</b> (млн руб)', ('5.35',)),
        ('Изменение резервов по договорам финансового лизинга', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.36'), dates),
            '<b>5.36</b> (млн руб)', ('5.36',)),
        ('Изменение резервов по договорам операционной аренды', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.37'),
            dates), '<b>5.37</b> (млн руб)', ('5.37',)),
        ('Изменение резервов по прочим видам активов', 'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.38'),
                                                                                          dates),
                                                                        '<b>5.38</b> (млн руб)', ('5.38',)),
        ('Административные и операционные расходы', 'Данные МСФО'): (lambda: sum_param(get_df_param(df, '5.39'), dates),
                                                                     '<b>5.39</b> (млн руб)', ('5.39',)),
        ('Переоценка стоимости имущества, переданного в операционную аренду', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.56'), dates), '<b>5.56</b> (млн руб)', ('5.56',)),
        ('Прочие доходы', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.40'), dates), '<b>5.40</b> (млн руб)', ('5.40',)),
        ('Налог на прибыль', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.42'), dates), '<b>5.42</b> (млн руб)', ('5.42',)),
        ('Чистая прибыль (убыток)', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.43'), dates), '<b>5.43</b> (млн руб)', ('5.43',)),
        ('Прочий совокупный доход (расход)', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.44'), dates), '<b>5.44</b> (млн руб)', ('5.44',)),
        ('ИТОГО СОВОКУПНЫЙ ДОХОД (РАСХОД) ЗА ГОД', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.45'), dates), '<b>5.45</b> (млн руб)', ('5.45',)),
        ('Резервы по договорам операционной аренды', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.57'), dates), '<b>5.57</b> (млн руб)', ('5.57',)),
        ('Резервы по договорам финансового лизинга', 'Данные МСФО'): (
            lambda: sum_param(get_df_param(df, '5.58'), dates), '<b>5.58</b> (млн руб)', ('5.58',)),
        ('в т.ч. резервы по необслуживаемым (более 90 дней) договорам', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.59'), dates), '<b>5.59</b> (млн руб)', ('5.59',)),
        ('в т.ч. резервы по реструктурированным договорам', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.60'), dates), '<b>5.60</b> (млн руб)', ('5.60',)),
        ('в т.ч. резервы по расторгнутым договорам', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.61'), dates), '<b>5.61</b> (млн руб)', ('5.61',)),
        ('Прочие резервы', 'Данные МСФО'): (lambda: sum_param(
            get_df_param(df, '5.62'), dates), '<b>5.62</b> (млн руб)', ('5.62',)),
        # Данные ФСБУ----------------------------------------------------------------
        ('Активы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.1'), dates), '<b>4.1</b> (млн руб)', ('4.1',)),
        ('Займы выданные', 'Данные ФСБУ'): (
            lambda: (sum_param(get_df_param(df, '4.67.1'), dates)+sum_param(get_df_param(df, '4.74'), dates)),
            '<b>4.67.1</b>+<b>4.74</b> (млн руб)', ('4.67.1','4.74',)),
        ('Кредиты полученные', 'Данные ФСБУ'): (
            lambda: (sum_param(get_df_param(df, '4.19'), dates) + sum_param(get_df_param(df, '4.25'), dates)),
            '<b>4.19</b>+<b>4.25</b> (млн руб)', ('4.19', '4.25',)),
        ('Займы полученные', 'Данные ФСБУ'): (
            lambda: (sum_param(get_df_param(df, '4.21'), dates) + sum_param(get_df_param(df, '4.27'), dates)),
            '<b>4.21</b>+<b>4.27</b> (млн руб)', ('4.21', '4.27',)),
        ('Выпущенные долговые ценные бумаги', 'Данные ФСБУ'): (
            lambda: (sum_param(get_df_param(df, '4.23'), dates) + sum_param(get_df_param(df, '4.27'), dates)),
            '<b>4.21</b>+<b>4.27</b> (млн руб)', ('4.23', '4.27',)),
        ('Дебиторская задолженность по расторгнутым договорам лизинга', 'Данные ФСБУ'): ( lambda: (sum_param(get_df_param(df, '4.71'), dates)+sum_param(get_df_param(df, '4.72'), dates)),
            '<b>4.71</b>+<b>4.72</b> (млн руб)', ('4.71','4.72',)),
        ('Основные средства', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.3'), dates), '<b>4.3</b> (млн руб)', ('4.3',)),
        ('Доходные вложения в материальные ценности', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.4'), dates), '<b>4.4</b> (млн руб)', ('4.4',)),
        ('в т.ч. стоимость имущества, переданного в операционную аренду', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.66'), dates), '<b>4.66</b> (млн руб)', ('4.66',)),
        ('Денежные средства', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.68'), dates), '<b>4.68</b> (млн руб)', ('4.68',)),
        ('Финансовые вложения до 12 месяцев (за исключением денежных эквивалентов)', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.10'), dates), '<b>4.10</b> (млн руб)', ('4.10',)),
        ('Финансовые вложения более 12 месяцев', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.5'), dates), '<b>4.5</b> (млн руб)', ('4.5',)),
        ('ИТОГО ВНЕОБОРОТНЫЕ АКТИВЫ', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.7'), dates), '<b>4.7</b> (млн руб)', ('4.7',)),
        ('ИТОГО ОБОРОТНЫЕ АКТИВЫ', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.11'), dates), '<b>4.11</b> (млн руб)', ('4.11',)),
        ('Нераспределенная прибыль', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.16'), dates), '<b>4.16</b> (млн руб)', ('4.16',)),
        ('ИТОГО КАПИТАЛ', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.17'), dates), '<b>4.17</b> (млн руб)', ('4.17',)),
        ('Дебиторская задолженность', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.9'), dates), '<b>4.9</b> (млн руб)', ('4.9',)),
        ('в т.ч. чистые инвестиции в лизинг (по договорам финансового лизинга)', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.69'), dates), '<b>4.69</b> (млн руб)', ('4.69',)),
        ('Долгосрочные заемные средства', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.18'), dates), '<b>4.18</b> (млн руб)', ('4.18',)),
        ('Краткосрочные заемные средства', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.24'), dates), '<b>4.24</b> (млн руб)', ('4.24',)),
        ('Кредиторская задолженность', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.29'), dates), '<b>4.29</b> (млн руб)', ('4.29',)),
        ('Нематериальные активы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.2'), dates), '<b>4.2</b> (млн руб)', ('4.2',)),
        ('Выручка', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.32'), dates), '<b>4.32</b> (млн руб)', ('4.32',)),
        ('в т.ч. финансовый лизинг', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.33'), dates), '<b>4.33</b> (млн руб)', ('4.33',)),
        ('в т.ч. операционная аренда', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.34'), dates), '<b>4.34</b> (млн руб)', ('4.34',)),
        ('Себестоимость продаж', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.35'), dates), '<b>4.35</b> (млн руб)', ('4.35',)),
        ('Валовая прибыль (убыток)', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.36'), dates), '<b>4.36</b> (млн руб)', ('4.36',)),
        ('Коммерческие расходы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.37'), dates), '<b>4.37</b> (млн руб)', ('4.37',)),
        ('Управленческие расходы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.38'), dates), '<b>4.38</b> (млн руб)', ('4.38',)),
        ('Прибыль (убыток) от продаж', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.39'), dates), '<b>4.39</b> (млн руб)', ('4.39',)),
        ('Проценты к получению', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.40'), dates), '<b>4.40</b> (млн руб)', ('4.40',)),
        ('Проценты к уплате', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.41'), dates), '<b>4.41</b> (млн руб)', ('4.41',)),
        ('Прочие доходы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.42'), dates), '<b>4.42</b> (млн руб)', ('4.42',)),
        ('Прочие расходы', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.43'), dates), '<b>4.43</b> (млн руб)', ('4.43',)),
        ('Прибыль (убыток) до налогообложения', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.44'), dates), '<b>4.44</b> (млн руб)', ('4.44',)),
        ('Текущий налог на прибыль', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.45'), dates), '<b>4.45</b> (млн руб)', ('4.45',)),
        ('Чистая прибыль (убыток)', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.46'), dates), '<b>4.46</b> (млн руб)', ('4.46',)),
        (
            'Результат от переоценки внеоборотных активов, не включаемый в чистую прибыль (убыток) периода',
            'Данные ФСБУ'):
            (lambda: sum_param(get_df_param(df, '4.47'), dates), '<b>4.47</b> (млн руб)', ('4.47',)),
        ('Результат от прочих операций, не включаемый в чистую прибыль (убыток) периода', 'Данные ФСБУ'):
            (lambda: sum_param(get_df_param(df, '4.48'), dates), '<b>4.48</b> (млн руб)', ('4.48',)),
        ('Совокупный финансовый результат периода', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.49'), dates), '<b>4.49</b> (млн руб)', ('4.49',)),
        ('в т.ч. переоценка стоимости имущества, переданного в операционную аренду', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.77'), dates), '<b>4.77</b> (млн руб)', ('4.77',)),

        ('Резервы по договорам операционной аренды', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.78'), dates), '<b>4.78</b> (млн руб)', ('4.78',)),
        ('Резервы по договорам финансового лизинга', 'Данные ФСБУ'): (
            lambda: sum_param(get_df_param(df, '4.79'), dates), '<b>4.79</b> (млн руб)', ('4.79',)),
        ('в т.ч. резервы по необслуживаемым (более 90 дней) договорам', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.80'), dates), '<b>4.80</b> (млн руб)', ('4.80',)),
        ('в т.ч. резервы по реструктурированным договорам', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.81'), dates), '<b>4.81</b> (млн руб)', ('4.81',)),
        ('в т.ч. резервы по расторгнутым договорам', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.82'), dates), '<b>4.82</b> (млн руб)', ('4.82',)),
        ('Прочие резервы', 'Данные ФСБУ'): (lambda: sum_param(
            get_df_param(df, '4.83'), dates), '<b>4.83</b> (млн руб)', ('4.83',)),
        ('лизинговый портфель', 'Данные ФСБУ: все продукты'): (
            lambda:
            (sum_param(get_df_param(df, '2.1.2'), dates) + sum_param(get_df_param(df, '2.1.7'), dates) +
             sum_param(get_df_param(df, '2.2.2'), dates) + sum_param(get_df_param(df, '2.2.7'), dates)),
            '<b>2.1.2</b> +  <b>2.1.7</b>+<b>2.2.2</b> +  <b>2.2.7</b>', ('2.1.2', '2.1.7', '2.2.2', '2.2.7',)),
        ('лизинговый портфель', 'Данные ФСБУ: операционная аренда'): (
            lambda:
            (sum_param(get_df_param(df, '2.2.2'), dates) + sum_param(get_df_param(df, '2.2.7'), dates)),
            '<b>2.2.2</b> +  <b>2.2.7</b>', ('2.2.2', '2.2.7',)),
        ('темп прироста лизингового портфеля (год к году)', 'Данные ФСБУ: все продукты'): (lambda:
                                                                                           (diff(get_df_param(df,
                                                                                                              '2.1.2'),
                                                                                                 dates,
                                                                                                 dates_noform_calc) +
                                                                                            diff(get_df_param(df,
                                                                                                              '2.2.2'),
                                                                                                 dates,
                                                                                                 dates_noform_calc) +
                                                                                            diff(get_df_param(df,
                                                                                                              '2.1.7'),
                                                                                                 dates,
                                                                                                 dates_noform_calc) +
                                                                                            diff(get_df_param(df,
                                                                                                              '2.2.7'),
                                                                                                 dates,
                                                                                                 dates_noform_calc)) * 100 /
                                                                                           (get_df_param_stepback(
                                                                                               get_df_param(df,
                                                                                                            '2.1.2'),
                                                                                               dates, 4,
                                                                                               sum_param,
                                                                                               dates_noform_calc) +
                                                                                            get_df_param_stepback(
                                                                                                get_df_param(df,
                                                                                                             '2.2.2'),
                                                                                                dates, 4,
                                                                                                sum_param,
                                                                                                dates_noform_calc) +
                                                                                            get_df_param_stepback(
                                                                                                get_df_param(df,
                                                                                                             '2.1.7'),
                                                                                                dates, 4,
                                                                                                sum_param,
                                                                                                dates_noform_calc) +
                                                                                            get_df_param_stepback(
                                                                                                get_df_param(df,
                                                                                                             '2.2.7'),
                                                                                                dates, 4,
                                                                                                sum_param,
                                                                                                dates_noform_calc)),
                                                                                           'изменение(за год)( <b>2.1.2</b> + <b>2.1.7</b> + <b>2.2.2</b> +<b>2.2.7</b>)/(предыдущий год)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b> (%))',
                                                                                           ('2.1.2', '2.1.7', '2.2.2',
                                                                                            '2.2.7')),
        ('темп прироста лизингового портфеля (год к году)', 'Данные ФСБУ: операционная аренда'): (lambda:
                                                                                                  (diff(get_df_param(df,
                                                                                                                     '2.2.2'),
                                                                                                        dates,
                                                                                                        dates_noform_calc) +
                                                                                                   diff(get_df_param(df,
                                                                                                                     '2.2.7'),
                                                                                                        dates,
                                                                                                        dates_noform_calc)) * 100 /
                                                                                                  (
                                                                                                              get_df_param_stepback(
                                                                                                                  get_df_param(
                                                                                                                      df,
                                                                                                                      '2.2.2'),
                                                                                                                  dates,
                                                                                                                  4,
                                                                                                                  sum_param,
                                                                                                                  dates_noform_calc) +
                                                                                                              get_df_param_stepback(
                                                                                                                  get_df_param(
                                                                                                                      df,
                                                                                                                      '2.2.7'),
                                                                                                                  dates,
                                                                                                                  4,
                                                                                                                  sum_param,
                                                                                                                  dates_noform_calc)),
                                                                                                  'изменение(за год)(<b>2.2.2</b> +<b>2.2.7</b>)/(предыдущий год)( <b>2.1.2</b> + <b>2.1.7</b> + <b>5.8</b> +<b>2.2.7</b> (%))',
                                                                                                  ('2.2.2',
                                                                                                   '2.2.7')),

        ('ЧИЛ', 'По данным МСФО'): (lambda: sum_param(get_df_param(df,'5.4'),dates),'<b>5.4</b> (млн руб)', ('5.4',)),
        ('Валютные требования', 'По данным МСФО'):
            (lambda: sum_param(get_df_param(df, '5.46'), dates), '<b>5.46</b> (млн руб)', ('5.46',)),
        ('Валютные обязательства', 'По данным МСФО'):
            (lambda: sum_param(get_df_param(df, '5.49'), dates), '<b>5.49</b> (млн руб)', ('5.49',)),
        ('Выручка', 'По данным МСФО'): (
        lambda: sum_param(get_df_param(df, '5.31'), dates), '<b>5.31</b> (млн руб)', ('5.31',)),
        ('Внебалансовые требования (Всего)', 'По данным МСФО'): (
            lambda: sum_param(get_df_param(df, '5.66.2'), dates), '<b>5.66.2</b> (млн руб)', ('5.66.2',)),
        ('в т.ч. валютные требования', 'По данным МСФО'): (
            lambda: sum_param(get_df_param(df, '5.66.1'), dates), '<b>5.66.1</b> (млн руб)', ('5.66.1',)),
        ('Внебалансовые обязательства (Всего)', 'По данным МСФО'): (
            lambda: sum_param(get_df_param(df, '5.71.1'), dates), '<b>5.71.1</b> (млн руб)', ('5.71.1',)),
        ('в т.ч. валютные обязательства', 'По данным МСФО'): (
            lambda: sum_param(get_df_param(df, '5.71'), dates), '<b>5.71</b> (млн руб)', ('5.71',)),
        ('Объем изъятых активов по остаточной стоимости', 'По данным МСФО'): (
            lambda:
            (sum_param(get_df_param(df, '2.1.7.1'), dates)+sum_param(get_df_param(df, '2.2.7.1'), dates)),
            '<b>2.1.7.1</b> +  <b>2.2.7.1</b>', ('2.1.7.1','2.2.7.1',)),
        ('Объем изъятых активов по фактической стоимости', 'По данным МСФО'): (
            lambda:
            (sum_param(get_df_param(df, '2.1.7.2'), dates) + sum_param(get_df_param(df, '2.2.7.2'), dates)),
            '<b>2.1.7.2</b> +  <b>2.2.7.2</b>', ('2.1.7.2', '2.2.7.2',)),
        ('Объем изъятых активов по остаточной стоимости', 'По данным ФСБУ'): (
            lambda:
            (sum_param(get_df_param(df, '2.1.7.1'), dates) + sum_param(get_df_param(df, '2.2.7.1'), dates)),
            '<b>2.1.7.1</b> +  <b>2.2.7.1</b>', ('2.1.7.1', '2.2.7.1',)),
        ('Объем изъятых активов по фактической стоимости', 'По данным ФСБУ'): (
            lambda:
            (sum_param(get_df_param(df, '2.1.7.2'), dates) + sum_param(get_df_param(df, '2.2.7.2'), dates)),
            '<b>2.1.7.2</b> +  <b>2.2.7.2</b>', ('2.1.7.2', '2.2.7.2',)),
    }
    """словарь с формулами для готовых показателей; key: пара параметр(ROE и тд) и категория(По данным МСФО и тд)"""
    find_form = param_dict[key]
    """find_form[0]() - численный ответ, find_form[1] - формула для вывода на экран, 
    find_form[2] - кортеж используемых в формуле пунктов """
    return (find_form[0](), find_form[1], find_form[2], dates_noform_calc)

def cust_comp_dict(df,comp_params):
    """
    Функция составления сопоставимой выборки по критериям пользователя
    :param df:
    :param comp_params: (количество ненулевых периодов для выборки, [пункты сопоставимости])
    :return: словарь с датами и сопоставимыми ЛК date_lk_comparpoint
    """
    l=[s.split('(')[-1][:-1] for s in comp_params[1]]#список номеров пунктов для сопоставимой выборки
    cond=(df['point_number'] == l[0])#условия для поиска в дф с помощью loc первого пункта списка сопост выборки
    for pn in l[1:]:
        cond=cond|(df['point_number'] == pn)#условием | (т.е. или) добавляем к условию поиска остальные пункты
    #функцией loc находим все строки дф с нужными пунктами
    df_point_comp = df.loc[cond, ['lk_name'] + [d for d in dates_list]].copy()
    df_point_comp = df_point_comp.set_index('lk_name')  # индекс - имя ЛК
    date_lk_comparpoint = {key: [] for key in dates_list}
    tmp={}
    for company in lk_names_list:
        #словарь tmp [дата]:[значения пунктов]
        for d in dates_list:
            tmp[d]=df_point_comp[d].loc[company]
        count = 0
        for d in dates_list:
            if len(l)==1 and (tmp[d]==0 or np.isnan(tmp[d])):#если один пукт в сопоставимой выборке
                count=0
            elif len(l)>1 and any((i==0) or (np.isnan(0)) for i in tmp[d]):
                count=0
            else:
                count += 1
                if count >= comp_params[0]:
                    date_lk_comparpoint[d].append(company)
    return date_lk_comparpoint

def filter_data(df, **kwargs):
    """
    Функция чистки дф от данных, которые пользователь не запросил(нужные ЛК, ск. год),
    проверка на наличие данных - составление списка no_form_all_dates с датами, для которых не будут
    совершаться вычисления и на экран будет выведено "недостаточно данных"
    :param df:
    :param kwargs: 'classprop_type':lk_type/lk_type2, 'desire_type_lk':все ЛК/..,
    'is_not_gtlk': True(удалить гтлк)/False, 'desire_dates_choice': выбранные пользователем даты
    :return: (df, no_form_dates)
    """
    no_form_all_dates = []
    """все даты в дф, для которых недостаточно данных"""
    # даты оставляем все (для вычислений)
    # оставляем в df столбец с выбранной классификацией(цб, ола)
    #  classprop_type(ila,cb)---
    df = df[['lk_name', kwargs['classprop_type'][0], 'point_number'] + [d for d in dates_list]]
    if not kwargs['desire_type_lk'] == 'все ЛК':
        df = df[df[kwargs['classprop_type'][0]] == kwargs['desire_type_lk']]
    # is_not_gtlk---------------
    if kwargs['is_not_gtlk']:  # удаляем АО ГТЛК, если выбрано
        df = df.drop(df[df['lk_name'] == 'АО «ГТЛК»'].index)
    # desire_comparable, selection_names_list ---
    if comp_type_dict[kwargs['desire_comparable']] == 1:  # сопост выборка, берем из последней даты сопост комп
        df = df.loc[df['lk_name'].isin(date_lk51[kwargs['desire_dates_choice'][-1]])]
    elif comp_type_dict[kwargs['desire_comparable']] == 2:  # ручной выбор имен
        df = df.loc[df['lk_name'].isin(kwargs['selection_names_list'])]
    elif comp_type_dict[kwargs['desire_comparable']] == 3:  # настраиваемая сопоставимая выборка
        df = df.loc[df['lk_name'].isin(cust_comp_dict(df,kwargs['comp_params'])[kwargs['desire_dates_choice'][-1]])]
    # если выбран скользящий год
    if kwargs['desire_param'][1]:
        tmp_df = df.copy()
        for ind in range(4, len(dates_list)):
            quoter_pos = ind % 4 + 1
            trio_dates = [dates_list[ind - 4], dates_list[ind - quoter_pos], dates_list[ind]]
            if not any(ch is False for ch in
                       [check_lk_form_stepback(df, trio_dates[2]), check_lk_form_stepback(df, trio_dates[1]),
                        check_lk_form_stepback(df, dates_list[ind - 4])]):
                if not any(d in no_form_all_dates for d in trio_dates):
                    df[trio_dates[2]] = tmp_df[trio_dates[2]][0:].fillna(0) + tmp_df[trio_dates[1]][0:].fillna(0) - \
                                        tmp_df[trio_dates[0]][0:].fillna(0)
            else:
                no_form_all_dates.append(trio_dates[0])
                no_form_all_dates.append(trio_dates[1])
                no_form_all_dates.append(trio_dates[2])
                df[trio_dates[2]] = 0
    for i in range(len(kwargs['desire_dates_choice'])):
        if not check_lk_form_stepback(df, kwargs['desire_dates_choice'][i]):  # not False
            no_form_all_dates.append(kwargs['desire_dates_choice'][i])
    no_form_dates = []
    """список выбранных пользователем дат, у которых недостаточно данных"""
    for p in no_form_all_dates:
        if p in kwargs['desire_dates_choice']:
            ind = kwargs['desire_dates_choice'].index(p)
            no_form_dates.append([ind, kwargs['desire_dates_choice'].pop(ind)])
    return (df, no_form_dates)

def get_number(str_num):
    """
     функция преобразования строки с числом в число типа float или int
    :param str_num: строка, содержащая запись числа типа float/int
    :return: float/int
    """
    return float(str_num) if '.' in str_num else int(str_num)


def get_value(str_value,df):
    """
    выделяет из записи пользовательской формулы следующее значение, с которым
    выполняются операции
    :param str_value: переменная в формуле(может быть числом или массивом чисел,
    строкой с числом или строкой функции и пункта)
    :return: [True(строка с функцией и пунктом)/False(число/массив), значение переменной/имя функции,
    (если строка с функцией)номер пункта]
    """
    num_types = (int, float, np.ndarray, np.int32, np.int64, np.float64)
    if isinstance(str_value, num_types):
        return [False, str_value]
    else:  # если не число особого типа, то или строка с числом, или с функ и пунктом
        if isinstance(str_value, pd.DataFrame):
            return [False, FormPoint(str_value)]
        elif isinstance(str_value, FormPoint):
            return [False, str_value]
        elif str_value.isnumeric():
            return [False, get_number(str_value)]
        # проверяем, является ли строка числом float, для этого убрали . из записи
        elif str_value.replace('.', '0').isnumeric():
            return [False, get_number(str_value)]
        else:
            raise ArithmeticError(f"Ошибка ввода: не удалось прочитать выражение {str_value}")

def q_diff(df, dates, dates_noform_calc):
    """
    Функция нахождения изменения значений за квартал
    :param df:
    :param dates:
    :param dates_noform_calc:
    :return: np.array(res)
    """
    res = []
    for d in dates:
        ind = dates_list.index(d)
        quoter_pos = ind % 4 + 1
        if quoter_pos==1:#первый квартал дает просто значение, без разности
            res.append(df[d].sum())
        else:
            y_date = dates_list[ind - 1]
            # проверка на наличие данных
            if check_lk_form_stepback(df, y_date):
                diff_column = df[d] - df[y_date]
                res.append(diff_column.sum())
            else:
                res.append(0)
                if d not in dates_noform_calc:
                    dates_noform_calc.append(d)
    return np.array(res)

func_type = {
    'без_функции': sum_param,
    'среднее_за_год': average,
    'среднее_по_ЛК': average_byLK,
    'скользящий_год': sliding,
    'изменение_за_год': diff,
    'изменение_за_квартал': q_diff
}
"""словарь перевода имен функций в окне пользователя на имена функций в программном коде"""

custom_type_dict = {
    'Прирост квартал-к-кварталу':
        lambda dates: [dates_list[dates_list.index(d) - 1] for d in dates],
    'Прирост год-к-году':
        lambda dates: [dates_list[dates_list.index(d) - 4] for d in dates]
}
"""словарь формул для вычисления прироста в пользовательском показателе"""


def calc_custom_func(df, dates, func, point,dates_noform_calc):
    """
    Функция вычисления функции в пользовательской формуле
    :param df:
    :param dates:
    :param func: имя функции
    :param point: номер пункта, на который действует функция
    :param dates_noform_calc:
    :return: np.array(res)
    """
    # считаем функцию на выбранный пункт
    res=[]
    df = get_df_param(df, point)  # достаем нужное из датафрейма
    for d in dates:
        if check_lk_form_stepback(df,d):#если есть данные
            if func == 'без_функции':
                res.append(func_type[func](df, [d, ])[0])
            else:
                res.append(func_type[func](df, [d,], dates_noform_calc)[0])
        else:
            res.append(0)
            if d not in dates_noform_calc:
                dates_noform_calc.append(d)
    return np.array(res)

def calc_eq(equation, df, dates,dates_noform_calc, flag):
    """
    Функция вычисления выражения без скобок (вкладка Свой показатель)
    :param eq: выражение для вычисления
    :param df:
    :param dates:
    :param dates_noform_calc:
    :return: res(список значений)
    """
    if flag:
        eq=equation.copy()
        i = 0
        while i < (len(eq) - 1):
            # выполняем вычисления всех приоритетных действий,
            # чтобы осталось выражение из + и -
            if isinstance(eq[i],str):
                if eq[i] in ('*', '/'):
                    a = get_value(eq[i - 1],df)
                    b = get_value(eq[i + 1],df)
                    if a[0]:  # если есть скобка
                        vec = calc_custom_func(df, dates, a[1], a[2],dates_noform_calc)
                        a[1]=vec
                        if isinstance(vec, (np.ndarray, list)):
                            if isinstance(vec[0], (np.ndarray, list)):
                                if len(vec[0]) == 1:
                                    a[1] = np.array([v[0] for v in vec])
                    if b[0]:  # если значение это строка функция(номер пункта)
                        vec = calc_custom_func(df, dates, b[1], b[2],dates_noform_calc)
                        b[1]=vec
                        if isinstance(vec, (np.ndarray, list)):
                            if isinstance(vec[0], (np.ndarray, list)):
                                if len(vec[0]) == 1:
                                    b[1] = np.array([v[0] for v in vec])
                    val = np_operations[eq[i]](a[1], b[1])
                    eq[i - 1] = val  # записываем на место первого числа выражения результат
                    # * или / и второе число удаляем
                    eq[i:i + 2] = []
                    # ставим индекс назад
                    i = i - 1
            i += 1
        a = get_value(eq[0],df)
        if a[0]:  # если значение это строка функция(номер пункта)
            vec = calc_custom_func(df, dates, a[1], a[2], dates_noform_calc)
            a[1]=vec
            if isinstance(vec, (np.ndarray, list)):
                if isinstance(vec[0], (np.ndarray, list)):
                    if len(vec[0]) == 1:
                        a[1] = np.array([v[0] for v in vec])
        res = a[1]  # записываем в результат первое число выраженгия
        # теперь можно считать плюсы и минусы
        # индекс идет по операторам, то есть по нечетным местам (шаг 2)
        for i in range(1, len(eq) - 1, 2):
            b = get_value(eq[i + 1],df)
            if b[0]:  # если значение это строка функция(номер пункта)
                vec = calc_custom_func(df, dates, b[1], b[2], dates_noform_calc)
                b[1]=vec
                if isinstance(vec, (np.ndarray, list)):
                    if isinstance(vec[0], (np.ndarray, list)):
                        if len(vec[0]) == 1:
                            b[1] = np.array([v[0] for v in vec])
            res = np_operations[eq[i]](res, b[1])  # вычисляем
    else:
        eq = equation.copy()
        i = 0
        while i < (len(eq) - 1):
            # выполняем вычисления всех приоритетных действий,
            # чтобы осталось выражение из + и -
            if isinstance(eq[i], str):
                if eq[i] in ('*', '/'):
                    if isinstance(eq[i - 1], str):
                        if eq[i - 1] == '[':
                            # формируем tmp_df
                            tmp_df = get_df_param(df, eq[i])
                            eq[i - 1] = tmp_df
                            eq[i:i + 2] = []
                    a = get_value(eq[i - 1], df)
                    if isinstance(eq[i + 1], str):
                        if eq[i + 1] == '[':
                            # формируем tmp_df
                            tmp_df = get_df_param(df, eq[i + 2])
                            eq[i + 1] = tmp_df
                            eq[i + 2:i + 4] = []
                    b = get_value(eq[i + 1], df)
                    if a[0]:  # если есть скобка
                        vec = calc_custom_func(df, dates, a[1], a[2], dates_noform_calc)
                        a[1]=vec
                        if isinstance(vec, (np.ndarray, list)):
                            if isinstance(vec[0], (np.ndarray, list)):
                                if len(vec[0]) == 1:
                                    a[1] = np.array([v[0] for v in vec])
                    if b[0]:  # если значение это строка функция(номер пункта)
                        vec = calc_custom_func(df, dates, b[1], b[2], dates_noform_calc)
                        b[1]=vec
                        if isinstance(vec, (np.ndarray, list)):
                            if isinstance(vec[0], (np.ndarray, list)):
                                if len(vec[0]) == 1:
                                    b[1] = np.array([v[0] for v in vec])
                    if isinstance(a[1], FormPoint):
                        val = pf_operations[eq[i]](a[1], b[1])
                    elif isinstance(b[1], FormPoint):
                        val = pf_operations[eq[i]](b[1], a[1])
                    else:
                        val = np_operations[eq[i]](a[1], b[1])
                    eq[i - 1] = val  # записываем на место первого числа выражения результат
                    # * или / и второе число удаляем
                    eq[i:i + 2] = []
                    # ставим индекс назад
                    i = i - 1
            i += 1
        if isinstance(eq[0], str):
            if eq[0] == '[':
                # формируем tmp_df
                tmp_df = get_df_param(df, eq[1])
                eq[0] = tmp_df
                eq[1:3] = []
        a = get_value(eq[0], df)
        if a[0]:  # если значение это строка функция(номер пункта)
            vec = calc_custom_func(df, dates, a[1], a[2], dates_noform_calc)
            a[1]=vec
            if isinstance(vec, (np.ndarray, list)):
                if isinstance(vec[0], (np.ndarray, list)):
                    if len(vec[0]) == 1:
                        a[1] = np.array([v[0] for v in vec])
        res = a[1]  # записываем в результат первое число выраженгия
        # теперь можно считать плюсы и минусы
        # индекс идет по операторам, то есть по нечетным местам (шаг 2)
        i=1
        while i<len(eq)-1:
        #for i in range(1, len(eq) - 1, 2):
            if isinstance(eq[i + 1], str):
                if eq[i + 1] == '[':
                    # формируем tmp_df
                    tmp_df = get_df_param(df, eq[i + 2])
                    eq[i + 1] = tmp_df
                    eq[i + 2:i + 4] = []
            b = get_value(eq[i + 1], df)
            if b[0]:  # если значение это строка функция(номер пункта)
                vec = calc_custom_func(df, dates, b[1], b[2], dates_noform_calc)
                b[1]=vec
                if isinstance(vec, (np.ndarray, list)):
                    if isinstance(vec[0], (np.ndarray, list)):
                        if len(vec[0]) == 1:
                            b[1] = np.array([v[0] for v in vec])
            if isinstance(res, FormPoint):
                res = pf_operations[eq[i]](res, b[1])
            elif isinstance(b[1], FormPoint):
                res = pf_operations[eq[i]](b[1], res)
            else:
                res = np_operations[eq[i]](res, b[1])
            i+=2
    return res

def calc_func(equation,func, df, dates,dates_noform_calc):
    """
    Функция вычисления выражения внутри функции (вкладка Свой показатель)
    :param eq: выражение для вычисления
    :param func: имя применяемой функции
    :param df:
    :param dates:
    :param dates_noform_calc:
    :return: res(список значений)
    """
    eq=equation.copy()
    # вычислем выражение в скобках
    i=0
    while i < (len(eq) - 1):
        # выполняем вычисления всех приоритетных действий,
        # чтобы осталось выражение из + и -
        # сначала вычисляем все функции
        if isinstance(eq[i], str):
            if not re.fullmatch('[а-яА-Я_]+',eq[i])==None:
                if eq[i+1]=='[':
                    vec=calc_custom_func(df, dates, eq[i], eq[i + 2],dates_noform_calc)
                    eq[i]=vec
                    if isinstance(vec,(np.ndarray,list)):
                        if isinstance(vec[0],(np.ndarray,list)):
                            if len(vec[0])==1:
                                eq[i]=np.array([v[0] for v in vec])
                    eq[i+1:i + 3] = []
                elif eq[i+1]=='(':
                    eq_func = []
                    func_ind=i
                    # будем записывать формулу в ()
                    k = 0
                    i += 2
                    while not k == 0 or not eq[i] == ')':
                        if eq[i] == '(':
                            k += 1
                        elif eq[i] == ')':
                            k -= 1
                        eq_func.append(eq[i])
                        i += 1
                    vec=calc_func(eq_func, eq[func_ind],df, dates, dates_noform_calc)
                    cur_res=vec
                    if isinstance(vec,(np.ndarray, list)):
                        if isinstance(vec[0],(np.ndarray, list)):
                            if len(vec[0])==1:
                                cur_res=np.array([v[0] for v in vec])
                    eq[func_ind]=cur_res
                    eq[func_ind+1:i+1]=[]
                else:
                    raise ArithmeticError(f"Ошибка ввода показателя: после вызова функции {eq[func_ind]} отсутствует скобка")
        i+=1
    i=0
    while i < (len(eq) - 1):
        # выполняем вычисления всех приоритетных действий,
        # чтобы осталось выражение из + и -
        # вычисляем все операции * /
        if isinstance(eq[i], str):
            if eq[i] in ('*', '/'):
                if isinstance(eq[i-1],str):
                    if eq[i-1]==']':
                        #формируем tmp_df
                        tmp_df = get_df_param(df,eq[i-2])
                        eq[i-3]=tmp_df
                        eq[i-2:i]=[]
                a = get_value(eq[i - 1],df)
                if isinstance(eq[i + 1], str):
                    if eq[i+1]=='[':
                        # формируем tmp_df
                        tmp_df = get_df_param(df, eq[i + 2])
                        eq[i+1]=tmp_df
                        eq[i+2:i+4]=[]
                b = get_value(eq[i + 1],df)
                if isinstance(a[1],FormPoint):
                    val=pf_operations[eq[i]](a[1], b[1])
                elif isinstance(b[1],FormPoint):
                    val = pf_operations[eq[i]](b[1], a[1])
                else:
                    val = np_operations[eq[i]](a[1], b[1])
                eq[i - 1] = val  # записываем на место первого числа выражения результат
                # * или / и второе число удаляем
                eq[i:i + 2] = []
                # ставим индекс назад
                i = i - 1
        i += 1
    if isinstance(eq[0],str):
        if eq[0] == '[':
            # формируем tmp_df
            tmp_df = get_df_param(df, eq[1])
            # вызов функции по имени с передачей временного дф
            eq[0]=tmp_df
            eq[1:3] = []
    a = get_value(eq[0],df)
    cur_res = a[1]  # записываем в результат первое число выраженгия
    # теперь можно считать плюсы и минусы
    # индекс идет по операторам, то есть по нечетным местам (шаг 2)
    str_len=len(eq) - 1
    i=1
    while i<str_len:
        if isinstance(eq[i+1],str):
            if eq[i +1] == '[':
                # формируем tmp_df
                tmp_df = get_df_param(df, eq[i+2])
                # вызов функции по имени с передачей временного дф
                eq[i+1]=tmp_df
                eq[i + 2:i + 4] = []
        b = get_value(eq[i + 1], df)
        if isinstance(cur_res, FormPoint):
            cur_res = pf_operations[eq[i]](cur_res, b[1])
        elif isinstance(b[1], FormPoint):
            cur_res = pf_operations[eq[i]](b[1], cur_res)
        else:
            cur_res = np_operations[eq[i]](cur_res, b[1])
        str_len = len(eq) - 1
        i+=2
    # создаем временный дф с результатом, чтобы применить функцию
    tmp_df = pd.DataFrame(index=np.arange(len(df['lk_name'].drop_duplicates())), columns=df.columns.values.tolist())
    tmp_df['lk_name']=df['lk_name'].drop_duplicates().tolist()

    # записываем результат вычислений на текущую дату
    if len(dates) == 1:
        if isinstance(cur_res,(pd.DataFrame,FormPoint)):
            tmp_df[dates[0]] = cur_res[dates[0]]
        else:
            tmp_df[dates[0]] = np.full(len(df['lk_name'].drop_duplicates()),cur_res[0])
    else:
        if isinstance(cur_res, (pd.DataFrame,FormPoint)):
            for k in range(len(dates)):
                tmp_df[dates[k]] = cur_res[dates[k]]
        else:
            for k in range(len(dates)):
                tmp_df[dates[k]] = np.full(len(df['lk_name'].drop_duplicates()),cur_res[k])
    # вычисления год назад
    if func in ('среднее_за_год', 'скользящий_год', 'изменение_за_год'):
        prev_dates = [dates_list[dates_list.index(d) - 4] for d in dates]
        prev_res = calc_eq(equation, df, prev_dates, dates_noform_calc,False)
        if len(prev_dates) == 1:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                tmp_df[prev_dates[0]] = prev_res[prev_dates[0]]
            else:
                tmp_df[prev_dates[0]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[0])
        else:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = prev_res[prev_dates[k]]
            else:
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[k])
    # последний квартал прошлого года
    if func == 'скользящий_год':
        prev_dates = [dates_list[dates_list.index(d) - (dates_list.index(d) % 4 + 1)] for d in dates]
        prev_res = calc_eq(equation, df, prev_dates, dates_noform_calc, False)
        if len(prev_dates) == 1:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                tmp_df[prev_dates[0]] = prev_res[prev_dates[0]]
            else:
                tmp_df[prev_dates[0]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[0])
        else:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = prev_res[prev_dates[k]]
            else:
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[k])
    # прошлый квартал
    if func == 'изменение_за_квартал':
        prev_dates = [dates_list[dates_list.index(d) - 1] for d in dates]
        prev_res = calc_eq(equation, df, prev_dates, dates_noform_calc, False)
        if len(prev_dates) == 1:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                tmp_df[prev_dates[0]] = prev_res[prev_dates[0]]
            else:
                tmp_df[prev_dates[0]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[0])
        else:
            if isinstance(prev_res, (pd.DataFrame, FormPoint)):
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = prev_res[prev_dates[k]]
            else:
                for k in range(len(prev_dates)):
                    tmp_df[prev_dates[k]] = np.full(len(df['lk_name'].drop_duplicates()), prev_res[k])
    # вызов функции по имени с передачей временного дф
    if func == 'без_функции':
        res = func_type[func](tmp_df, dates)
    else:
        res = func_type[func](tmp_df, dates, dates_noform_calc)
    return res

def find_brackets(list_of_char, df, dates,dates_noform_calc):
    """
    Функция нахождения приоритетных действий, выделенных скобками(вкладка Свой показатель)
    :param list_of_char: формула пользователя, разделенная на составляющие по поставленным пробелам
    :param df:
    :param dates:
    :param dates_noform_calc:
    :return: list_of_char - формула пользователя с приоритетным выражением в скобках,
     замененным на результат его вычисления
    """
    op_brackets = []
    """список открывающийхся скобок"""
    sq_brackets=[]
    """список открывающийхся квадратных скобок"""
    func_list=[]
    """список расположения функций"""
    calculated_eq=[]
    """выражения, которые были вычислены"""
    i = 0
    str_len=len(list_of_char)
    while i < str_len:
        # открывающиеся скобки вносим в список
        if list_of_char[i] == '(':
            op_brackets.append(i)
        elif list_of_char[i] == ')':
            # если была найдена закр-ся скобка, а откр-ся не было, то ввод произведен неверно
            if len(op_brackets) == 0:  # список пустой, ошибка
                raise ArithmeticError('Ошибка ввода показателя: не удалось найти пару к закрывающейся скобке')
            # если были откр-ся скобки, то мы получаем пару этой закр-ся скобки и последней в списке откр-ся
            else:  # пара к последней открывающейся скобке
                # записываем в выражение строку внутри скобок
                eq = list_of_char[op_brackets[-1] + 1:i]  # выражение в скобках для вычисления
                calculated_eq.append(eq.copy())
                # вместо открывающейся скобки в паре пишем результат выражения
                list_of_char[op_brackets[-1]] = calc_eq(eq, df, dates,dates_noform_calc, True)
                # удаляем остальные элементы уже вычисленного выражения
                list_of_char[op_brackets[-1] + 1:i + 1] = []
                # ставим индекс i на место вычисленного выражения
                i = op_brackets[-1]
                del op_brackets[-1]
        elif not re.fullmatch('[а-яА-Я_]+',list_of_char[i])==None:#если слово, то это вызов формулы
            eq_func=[]
            func_list.append(i)#записываем индекс слова
            #eq_func.append(list_of_char[i])
            i+=1
            if list_of_char[i]=='(':#круглые скобки, а значит функция применяется не только к пункту
                #eq_func.append(list_of_char[i])
                #будем записывать формулу в ()
                k=0
                i += 1
                while not k==0 or not list_of_char[i]==')':
                    if list_of_char[i]=='(':
                        k+=1
                    elif list_of_char[i]==')':
                        k-=1
                    eq_func.append(list_of_char[i])
                    i+=1
                #eq_func.append(list_of_char[i])
                vec = calc_func(eq_func,list_of_char[func_list[-1]],
                                  df,dates, dates_noform_calc)
                cur_res=vec
                if isinstance(vec, (np.ndarray, list)):
                    if isinstance(vec[0], (np.ndarray, list)):
                        if len(vec[0]) == 1:
                            cur_res= np.array([v[0] for v in vec])
                #записываем результат
                #удаляем остальную часть выражения
                list_of_char[func_list[-1]]=cur_res
                list_of_char[func_list[-1]+1:i+1]=[]
                i=func_list[-1]
            elif list_of_char[i]=='[':
                #это будет пункт, вызываем вычисления
                #заменяем в строке формулы ответом
                vec = calc_custom_func(df, dates,list_of_char[i-1],list_of_char[i+1], dates_noform_calc)
                cur_res = vec
                if isinstance(vec, (np.ndarray, list)):
                    if len(vec) == 0:
                        raise ArithmeticError('Ошибка ввода показателя: функция не вернула значений')
                    else:
                        if isinstance(vec[0], (np.ndarray,list)):
                            if len(vec[0]) == 1:
                                cur_res= np.array([v[0] for v in vec])
                list_of_char[i-1]=cur_res
                list_of_char[i:i + 3] = []
                i=func_list[-1]
                #del op_brackets[-1]
            else:
                #ошибка
                raise ArithmeticError('Ошибка ввода показателя: запись функции неверная')
        elif list_of_char[i] == '[':
            new_er=' '.join(list_of_char[i:i+3])
            raise ArithmeticError(f'Ошибка ввода показателя: найдена квадратная скобка без вызова функции {new_er}')
        i += 1
        str_len = len(list_of_char)
    if len(op_brackets) > 0:
        raise ArithmeticError('Ошибка ввода показателя: не удалось найти пару к открывающейся скобке')
    if len(sq_brackets) > 0:
        raise ArithmeticError('Ошибка ввода показателя: не удалось найти пару к открывающейся квадратной скобке')
    if len(list_of_char) > 1:  # остались выражения вне скобок
        list_of_char = calc_eq(list_of_char, df, dates,dates_noform_calc, True)
    if isinstance(list_of_char, list):
        if isinstance(list_of_char[0], str):
            if not re.fullmatch('[а-яА-Я_]+',list_of_char[0])==None:
                i=0
                eq_func = []
                func_list.append(0)  # записываем индекс слова
                # eq_func.append(list_of_char[i])
                i += 1
                if list_of_char[i] == '(':  # круглые скобки, а значит функция применяется не только к пункту
                    # eq_func.append(list_of_char[i])
                    # будем записывать формулу в ()
                    k = 0
                    i += 1
                    while not k == 0 or not list_of_char[i] == ')':
                        if list_of_char[i] == '(':
                            k += 1
                        elif list_of_char[i] == ')':
                            k -= 1
                        eq_func.append(list_of_char[i])
                        i += 1
                    # eq_func.append(list_of_char[i])
                    vec = calc_func(eq_func, list_of_char[func_list[-1]],
                                        df, dates, dates_noform_calc)
                    cur_res=vec
                    if isinstance(vec, (np.ndarray, list)):
                        if isinstance(vec[0], (np.ndarray, list)):
                            if len(vec[0]) == 1:
                                cur_res = np.array([v[0] for v in vec])
                    # записываем результат
                    # удаляем остальную часть выражения
                    list_of_char[func_list[-1]] = cur_res
                    list_of_char[func_list[-1] + 1:i] = []
        else:
            fin = get_value(list_of_char[0],df)
            list_of_char = fin[1]
    return list_of_char

def calculate(**kwargs):  # передаем указатель на словарь запроса из файла ui_leasing
    """
    Функция вызова нужных методов вычислений и составления результата для вывода в окно
    :param kwargs: выбранные и введенные пользователем параметры
    :return: [txt, answer, dict_lk_excel]; txt - текст для расположения на главной вкладке,
    answer - численный результат, dict_lk_excel - словарь Лк, для которых выполнялись
    вычисления, с типами (классификации цб и ола)
    """
    tmp = filter_data(full_df, **kwargs)
    """(отфильтрованный дф, даты без данных)"""
    calc_df = tmp[0].fillna(0)  # удаление строк df в соотвествии с выбором пользовател
    """отфильтрованный словарь с заменой nan на 0"""
    # df_zeros=tmp[1]
    no_form_dates = tmp[1]
    """даты пользователя, для которых недостаточно данных в дф"""
    # после сортировки дф, получаем список лк, с кот. проводятся вычисления
    list_lk_excel = calc_df.lk_name.drop_duplicates().values
    """список лк, для которых выполняются вычисления"""
    # записываем в df для excel имена ЛК и типы
    list_cb_excel = [full_df['lk_type'][full_df[full_df['lk_name'] == t].index[0]] for t in list_lk_excel]
    """типы выбранных лк по классицикации цб для excel"""
    list_ola_excel = [full_df['lk_type2'][full_df[full_df['lk_name'] == t].index[0]] for t in list_lk_excel]
    """типы выбранных лк по классицикации ола для excel"""
    dict_lk_excel = {'Имя ЛК': list_lk_excel, 'Классификация ЦБ': list_cb_excel, 'Классификация ОЛА': list_ola_excel}
    """словарь имен выбранных лк и их типам по двум классификациями для excel"""
    # записываем в текст для пользователя его выбор
    g = 'удалять' if kwargs['is_not_gtlk'] else 'не удалять'
    """'удалять' если стоит галочка Исключить ГТЛК, иначе 'не удалять'"""
    if not kwargs['is_custom']:  # вычисляется готовый показатель
        user_choice = kwargs['desire_param'][0]
        """кортеж выбора пользователя, (имя параметра, мсфо/фсбо/все продукты..)"""
        # вычисляем по соответствующей формуле в словаре показатель
        full_answer = func_dict(user_choice, calc_df, kwargs['desire_dates_choice'])
        answer = list(full_answer[0])
        #получаем список индексов, где значение nan
        nan_ind = np.isnan(answer)#список вида [True, True,False]
        inf_ind=np.isinf(answer)
        for i in range(len(answer)):
            #если нужно заменить inf/NaN
            if nan_ind[i] or inf_ind[i]:
                answer[i]='недостаточно данных'
        if kwargs['desire_param'][0][0] == 'ROE':
            for i in range(len(answer)):
                # цикл нужен для замены отрицательных значений на пояснение по поводу знаков значений для Рассчётв ROI
                if answer[i] != 'недостаточно данных':
                    if answer[i] == np.exp(1):
                        answer[i] = " (Капитал отрицательный.)"
                    elif answer[i] == np.exp(2):
                        answer[i] == " (Чистая прибыль и капитал отрицательны.)"
                    elif answer[i] < 0:
                        answer[i] = str(format_int(round((answer[i]), 2))) + " (Чистая прибыль отрицательная.)"
        # даты, для кот. во время вычислений было недостаточно данных
        dates_noform_calc = full_answer[3]
        # добавляем даты, у которых не было анкет
        no_form_dates.reverse()
        for p in no_form_dates:
            kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
            # записываем в answer, что нет анкеты
            answer.insert(p[0], 'недостаточно данных')
        for d in dates_noform_calc:
            ind = kwargs['desire_dates_choice'].index(d)
            answer[ind] = 'недостаточно данных'
        answer=np.array(answer)
        # записываем для вывода на экран
        if comp_type_dict[kwargs['desire_comparable']] == 2:  # при ручном выборе делаем другой вывод классификации
            txt = (
                    '<b>Тип отчета:  </b>' + kwargs['desire_report_type'] + ' ; ' + kwargs['desire_param'][0][
                1] + '<br>' +
                    '<b>Выбор ЛК:  </b>' + kwargs['desire_comparable'] + '<br>')
        else:
            txt = (
                    '<b>Тип отчета:  </b>' + kwargs['desire_report_type'] + ' ; ' + kwargs['desire_param'][0][
                1] + '<br>' +
                    '<b>Выбор ЛК:  </b>' + kwargs['desire_comparable'] + '<br>' +
                    '<b>Удаление АО ГТЛК:  </b>' + g + '<br>' +
                    '<b>Тип классификации:  </b>' + kwargs['classprop_type'][1] + '<br>' +
                    '<b>Тип:  </b>' + kwargs['desire_type_lk'] + '<br>')
        txt = txt + '<h4> Результат </h4>' + 'Вычислен показатель  ' + kwargs['desire_param'][0][0] + '<br>'
        txt = txt + ' по формуле ' + full_answer[1] + '<br><br><br>'
        for j in range(len(answer)):
            tmp = ''
            if isinstance(answer[j], str):
                if answer[j].isnumeric():
                    tmp=f'{str(format_int(get_number(answer[j])))}'
                # проверяем, является ли строка числом float, для этого убрали . из записи
                elif answer[j].replace('.', '0').isnumeric():
                    tmp=f'{str(format_int(round(get_number(answer[j]), 2)))}'
                else:
                    tmp = f'{answer[j]}'
            elif isinstance(answer[j], np.ndarray):
                for k in range(answer[j].size):
                    tmp = tmp + f'{str(format_int(round(answer[j][k], 2)))}'
            else:
                tmp = tmp + f'{str(format_int(round(answer[j], 2)))}'
            txt = txt + kwargs['desire_dates_choice'][j] + ' : ' + tmp + '<br>'
        txt = txt + '<br><br>'
        for j in (full_answer[2]):
            txt = txt + f'<b>{j} - </b> {dict_num_name[j]}' + '<br>'
        dict_lk_answers = {}
        """словарь значений для каждого ЛК выборки {имя ЛК:[answer(array)]}"""
        # вычисляем параметр для каждой ЛК
        for lk in list_lk_excel:
            # меняем параметры kwargs
            kwargs['desire_comparable'] = 'Ручной выбор'
            kwargs['selection_names_list'] = [lk, ]
            tmp = filter_data(full_df, **kwargs)
            lk_df = tmp[0].fillna(0)
            no_form_dates = tmp[1]
            full_ans_lk = func_dict(user_choice, lk_df, kwargs['desire_dates_choice'])
            ans_lk = list(full_ans_lk[0])
            # получаем список индексов, где значение nan
            nan_ind = np.isnan(ans_lk)  # список вида [True, True,False]
            inf_ind = np.isinf(ans_lk)
            for i in range(len(ans_lk)):
                # если нужно заменить inf/NaN
                if nan_ind[i] or inf_ind[i]:
                    ans_lk[i] = 'недостаточно данных'
            # даты, для кот. во время вычислений было недостаточно данных
            dates_noform_calc = full_ans_lk[3]
            # добавляем даты, у которых не было анкет
            no_form_dates.reverse()
            for p in no_form_dates:
                kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
                # записываем в answer, что нет анкеты
                ans_lk.insert(p[0], 'недостаточно данных')
            for d in dates_noform_calc:
                ind = kwargs['desire_dates_choice'].index(d)
                ans_lk[ind] = 'недостаточно данных'
            ans_lk = np.array(ans_lk)
            # записываем для конкретного ЛК ответ
            dict_lk_answers[lk] = ans_lk
    else:  # идут вычисления пользовательского показателя
        
        formula = kwargs['custom'].copy()
        f = kwargs['custom'].copy()
        """строка пользовательской формулы"""
        dates_noform_calc=[]
        #проверяем, что строка формулы не пустая
        if len(kwargs['custom'])<2 or all(s==[] or s==[' '] for s in kwargs['custom']):
            raise ArithmeticError(f"Ошибка ввода: попытка вычислить пустую строку")
        else:
            final_res = find_brackets(kwargs['custom'], calc_df, kwargs['desire_dates_choice'],dates_noform_calc)
            if not kwargs['custom_type'] == 'Не прирост':  # если показатель с приростом, то нужно вычислить
                dates_noform_calc_old=[]
                """даты из шага назад для вычисления прироста(свой показатель),
                 у которых недостаточно данных"""
                # вычисление старых дат
                old_dates=custom_type_dict[kwargs['custom_type']](kwargs['desire_dates_choice'])
                a = find_brackets(formula, calc_df,old_dates,dates_noform_calc_old)
                final_res = (final_res / a - 1) * 100
                #записываем в соответствии dates_noform_calc_old даты в dates_noform_calc
                if len(dates_noform_calc_old)>0:
                    for i in range(len(old_dates)):
                        if old_dates[i] in dates_noform_calc_old:
                            dates_noform_calc.append(kwargs['desire_dates_choice'][i])
            if comp_type_dict[kwargs['desire_comparable']] == 2:  # при ручном выборе делаем другой вывод классификации
                txt = ('<b>Выбор ЛК:  </b>' + kwargs['desire_comparable'] + '<br>')
            else:
                txt = (
                        '<b>Выбор ЛК:  </b>' + kwargs['desire_comparable'] + '<br>' +
                        '<b>Удаление АО ГТЛК:  </b>' + g + '<br>'
                                                           '<b>Тип классификации:  </b>' + kwargs['classprop_type'][
                            1] + '<br>' +
                        '<b>Тип:  </b>' + kwargs['desire_type_lk'] + '<br>')
            answer = final_res
            txt = (txt + '<h4> Результат </h4>' + 'Вычислен показатель по формуле : ' + '<br>' +
                   kwargs['full_form_txt'] + '<br>' +
                   kwargs['custom_type'] + '<br>')
            no_form_dates.reverse()
            if isinstance(answer, np.ndarray):
                answer = list(answer)
                for p in no_form_dates:
                    kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
                    # записываем в answer, что нет анкеты
                    answer.insert(p[0], 'недостаточно данных')
                for d in dates_noform_calc:
                    ind = kwargs['desire_dates_choice'].index(d)
                    answer[ind] = 'недостаточно данных'
                for j in range(len(answer)):
                    tmp = ''
                    if isinstance(answer[j],np.ndarray):
                        tmp = tmp + str(format_int(round(answer[j][0], 2)))
                    elif isinstance(answer[j],str):
                        tmp = tmp+answer[j]
                    elif np.isnan(answer[j]):
                        tmp=tmp+'недостаточно данных(деление на 0)'
                    elif np.isinf(answer[j]):
                        tmp = tmp + 'недостаточно данных(деление на 0)'
                    else:
                        tmp=tmp+str(format_int(round(answer[j], 2)))
                    txt = txt + kwargs['desire_dates_choice'][j] + ' : ' + tmp + '<br>'
            elif isinstance(answer, (int, float, np.int32, np.int64, np.float64)):
                if not len(no_form_dates)==0 or not len(dates_noform_calc)==0:
                    answer=list(answer)
                    for p in no_form_dates:
                        kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
                        # записываем в answer, что нет анкеты
                        answer.insert(p[0], 'недостаточно данных')
                    for d in dates_noform_calc:
                        ind = kwargs['desire_dates_choice'].index(d)
                        answer[ind]= 'недостаточно данных'
                    for j in range(len(answer)):
                        tmp = ''
                        if isinstance(answer[j], str):
                            tmp = tmp + answer[j]
                        elif np.isnan(answer[j]):
                            tmp = tmp + 'недостаточно данных(деление на 0)'
                        elif np.isinf(answer[j]):
                            tmp = tmp + 'недостаточно данных(деление на 0)'
                        else:

                            tmp = tmp + str(format_int(round(answer[j], 2)))
                        txt = txt + kwargs['desire_dates_choice'][j] + ' : ' + tmp + '<br>'
                else:
                    if np.isnan(answer):
                        txt = txt + 'недостаточно данных(деление на 0)' + '<br>'
                    elif np.isinf(answer):
                        txt = txt + 'недостаточно данных(деление на 0)'
                    else:
                        txt = txt + str(format_int(round(answer, 2))) + '<br>'
            else:
                if isinstance(answer[0], (int, float, np.int32, np.int64, np.float64)):
                    if np.isnan(answer[0]):
                        txt = txt + 'недостаточно данных(деление на 0)' + '<br>'
                    elif np.isinf(answer[0]):
                        txt= txt+ 'недостаточно данных(деление на 0)'
                elif isinstance(answer[0],str):
                    txt = txt + answer[0]
                else:
                    txt = txt + str(format_int(round(answer[0], 2))) + '<br>'
            dict_lk_answers = {}
            # для каждого ЛК выборки вычисляем тот же параметр
            for lk in list_lk_excel:
                f1 = f.copy()
                f2 = f.copy()
                dates_noform_calc = []
                kwargs['desire_comparable'] = 'Ручной выбор'
                kwargs['selection_names_list'] = [lk, ]
                tmp = filter_data(full_df, **kwargs)
                lk_df = tmp[0].fillna(0)
                final_res_lk = find_brackets(f1, lk_df, kwargs['desire_dates_choice'], dates_noform_calc)
                if not kwargs['custom_type'] == 'Не прирост':  # если показатель с приростом, то нужно вычислить
                    dates_noform_calc_old = []
                    """даты из шага назад для вычисления прироста(свой показатель),
                     у которых недостаточно данных"""
                    # вычисление старых дат
                    old_dates = custom_type_dict[kwargs['custom_type']](kwargs['desire_dates_choice'])
                    a = find_brackets(f2, lk_df, old_dates, dates_noform_calc_old)
                    final_res_lk = (final_res_lk / a - 1) * 100
                    # записываем в соответствии dates_noform_calc_old даты в dates_noform_calc
                    if len(dates_noform_calc_old) > 0:
                        for i in range(len(old_dates)):
                            if old_dates[i] in dates_noform_calc_old:
                                dates_noform_calc.append(kwargs['desire_dates_choice'][i])
                ans_lk = final_res_lk
                no_form_dates.reverse()
                if isinstance(ans_lk, np.ndarray):
                    ans_lk = list(ans_lk)
                    for p in no_form_dates:
                        kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
                        # записываем в answer, что нет анкеты
                        ans_lk.insert(p[0], 'недостаточно данных')
                    for d in dates_noform_calc:
                        ind = kwargs['desire_dates_choice'].index(d)
                        ans_lk[ind] = 'недостаточно данных'
                elif isinstance(ans_lk, (int, float, np.int32, np.int64, np.float64)):
                    if not len(no_form_dates) == 0 or not len(dates_noform_calc) == 0:
                        ans_lk = list(ans_lk)
                        for p in no_form_dates:
                            kwargs['desire_dates_choice'].insert(p[0], p[1])  # добавляем на прежнюю позицию
                            # записываем в answer, что нет анкеты
                            ans_lk.insert(p[0], 'недостаточно данных')
                        for d in dates_noform_calc:
                            ind = kwargs['desire_dates_choice'].index(d)
                            ans_lk[ind] = 'недостаточно данных'
                        for j in range(len(ans_lk)):
                            if np.isnan(ans_lk[j]):
                                ans_lk[j] = 'недостаточно данных(деление на 0)'
                            elif np.isinf(ans_lk[j]):
                                ans_lk[j] = 'недостаточно данных(деление на 0)'
                    else:
                        if np.isnan(ans_lk[j]):
                            ans_lk[j] = 'недостаточно данных(деление на 0)'
                        elif np.isinf(ans_lk[j]):
                            ans_lk[j] = 'недостаточно данных(деление на 0)'
                else:
                    if isinstance(ans_lk[j][0], (int, float, np.int32, np.int64, np.float64)):
                        if np.isnan(ans_lk[j][0]):
                            ans_lk[j][0] = 'недостаточно данных(деление на 0)'
                        elif np.isinf(ans_lk[j][0]):
                            ans_lk[j][0] = 'недостаточно данных(деление на 0)'
                # записываем для конкретного ЛК ответ
                dict_lk_answers[lk] = ans_lk
    return [txt, answer, dict_lk_excel, dict_lk_answers]
