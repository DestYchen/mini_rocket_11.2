#Хранение костант

#Словарь с коэффициентами по видам активов
dict_assets_risk_ratios = {
    '5.2': 0.2, #денежные средства и их эквиваленты
    '5.3': 0.5, #депозиты в банках
    '5.6': 1, #оборудование для передачи в лизинг
    '5.7': 1, #авансовые платежи поставщикам и подрядчикам
    '5.54': 1, #финансовые инструменты
    '5.14': 0.7, #активые предназначенные  для продажи по расторгнутым договорам лизинга
    '5.15': 1.5, #прочие активы
    '5.53': 1, #займы
}

# словарь с коэффициентами рисков по сегментам
dict_segments_risk_ratios = {
    '3.1.1.1': 0.75, #легковые автомобили фл
    '3.2.1.1': 0.75, #легковые автомобили ол
    '3.1.1.3': 0.75, #грузовые автомобили фл
    '3.2.1.3': 0.75, #грузовые автомобили ол
    '3.1.1.8': 0.75, #строительная фл
    '3.2.1.8': 0.75, #строительная ол
    '3.1.1.11': 0.75, #сельхоз-техника фл
    '3.2.1.11': 0.75, #сельхоз-техника ол
    '3.1.1.5': 1, #жд фл
    '3.2.1.5': 1, #жд ол
    '3.1.1.7': 1, #авиа фл
    '3.2.1.7': 1, #авиа ол
    '3.1.1.10': 1, #недвижимость фл
    '3.2.1.10': 1, #недвижимость ол
    '3.1.1.13': 1, #суда фл
    '3.2.1.13': 1, #суда ол
    '3.1.1.14': 1, #прочее имущество фл
    '3.2.1.14': 1, #прочее имущество ол
}
