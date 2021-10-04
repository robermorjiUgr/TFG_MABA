#!/usr/bin/env python
# coding: utf-8

import pandas as pd

df_origin  = pd.read_csv("forecasting_order.csv",sep=",")
f_order = df_origin
f_order['company'] = 1
f_order['Month'] = 1
f_order.Month.iloc[0:19] = 1
f_order.Month.iloc[19:39] = 2
f_order.Month.iloc[39:] = 3
f_order['timestamp'] = f_order[['Month','WeekMonth','DayWeek']].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
f_order.set_index('timestamp',inplace=True)
f_order.rename(columns={
    'WeekMonth':'WM',
    'DayWeek':'DW',
    'Non-urgent order':'N_urgent',
    'Urgent order':'urgent',
    'Order type A':'OrderA',
    'Order type B':'OrderB',
    'Order type C':'OrderC',
    '%NonUrgent':'per_N_urgent',
    '%Urgent':'per_Urgent',
    '%OrderTypeA':'per_OrderA',
    '%OrderTypeB':'per_OrderB',
    '%OrderTypeC':'per_OrderC',
    'Fiscal sector orders':'FSector',
    'Orders from the traffic controller sector':'TrafficOrder',
    'Banking orders (1)':'B1',
    'Banking orders (2)':'B2',
    'Banking orders (3)':'B3',
    '%FiscalSector':'per_F_Sector',
    '%traffic controller':'per_traffic',
    '% Banking Order(1)':'per_B1',
    '%Banking Order (2)':'per_B2',
    '%Banking Order (3)':'per_B3',
    '% Total Sectores Registrados':'per_T_Reg',
    '%Resto':'per_Resto',
    'Target (Total orders)':'TOrders'
}, inplace=True)
f_order.head()
f_order.to_csv('forecasting_order_new.csv')

