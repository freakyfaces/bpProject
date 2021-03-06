import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import jdatetime
import matplotlib.dates as mdates


def DIV(selected_row, div, initial_info):
    if div == '--d':  # checking cases for default division
        if selected_row['Category'] == 'Ghabz':
            if selected_row['SubCategory'] == 'avarez':
                return DIV(selected_row, '--e', initial_info)
            else:
                return DIV(selected_row, '--r', initial_info)
        elif selected_row['Category'] == 'nezafat':
            return DIV(selected_row, '--a', initial_info)
        elif selected_row['Category'] == 'parking':
            return DIV(selected_row, '--p', initial_info)
        elif selected_row['Category'] == 'tamirat':
            return DIV(selected_row, '--e', initial_info)
        elif selected_row['Category'] == 'asansor':
            return DIV(selected_row, '--f', initial_info)
        else:
            return DIV(selected_row, '--a', initial_info)
    elif div == '--a':  # division by area 
        t = []
        r = initial_info.area[initial_info.name.isin(selected_row['Units'])].sum()
        for i in selected_row['Units']:
            l = int(initial_info.loc[initial_info['name'] == i, 'area']) / r
            t.append(l * int(selected_row['Total Amount']))
        return t
    elif div == '--p':  # division by number of parkings 
        t = []
        r = initial_info.parkings[initial_info.name.isin(selected_row['Units'])].sum()
        for i in selected_row['Units']:
            l = int(initial_info.loc[initial_info['name'] == i, 'parkings']) / r
            t.append(l * int(selected_row['Total Amount']))
        return t
    elif div == '--r':  # division by residents 
        t = []
        r = initial_info.residents[initial_info.name.isin(selected_row['Units'])].sum()
        for i in selected_row['Units']:
            l = int(initial_info.loc[initial_info['name'] == i, 'residents']) / r
            t.append(l * int(selected_row['Total Amount']))
        return t
    elif div == '--e':  # equal division
        t = []
        for i in selected_row['Units']:
            t.append(l / len(selected_row['Units']))
        return t
    elif div == '--f':  # division by floor
        t = []
        r = initial_info.floor[initial_info.name.isin(selected_row['Units'])].sum()
        for i in selected_row['Units']:
            l = int(initial_info.loc[initial_info['name'] == i, 'floor']) / r
            t.append(l * int(selected_row['Total Amount']))
        return t
    else:  # in case that user inputs type of division by percentage of each unit (like : 40-30-30)
        t = []
        r = 100
        for i in div.split('-'):
            l = int(i) / r
            t.append(l * int(selected_row['Total Amount']))
        return t


def plot(h, saved):
    # selecting datas that are between the given dates !
    h[1] = list(map(lambda x: int(x), h[1].split('-')))
    h[2] = list(map(lambda x: int(x), h[2].split('-')))
    x = saved[(saved['Time'] >= jdatetime.date(*h[1])) & (saved['Time'] <= jdatetime.date(*h[2]))].copy()
    if h[0] == 'units':
        # getting the necessary info for the plot from user !
        info = []
        info.append(input('please enter which units ? (you can write all!)').split())
        info.append(input('please enter which SubCategories or Categories? (you can write all!)').split())
        # getting the all units and categories from saved DataFrame
        if info[0] == ['all']:
            info[0] = pd.Series(saved['Unit'].unique()).dropna()
        if info[1] == ['all']:
            saved['SubCategory'] = saved['SubCategory'].replace('###', np.nan)
            info[1] = pd.Series(saved['Category'].unique()).dropna()
        x = x[(x['SubCategory'].isin(info[1])) | (x['Category'].isin(info[1]))] # selecting datas that are in requested/
        # /category (or subCategory)
        # ploting datas for each unit
        for i in info[0]:
            y = x[x.Unit == i].copy()
            y['Amount'] = y['Amount'].cumsum()
            plt.plot(mdates.num2date(mdates.date2num(y['Time'])), y['Amount'])
        # adding some elements to the plot to make it more exciting!
        labels = ''
        for i in info[1]:
            labels += i + ' '
        plt.xticks(rotation=65)
        plt.legend(info[0])
        plt.xlabel('Time')
        plt.ylabel('Amount')
        plt.title('Amount of {} over Time'.format(labels))
        plt.show()
    elif h[0] == 'plot':
        h.append(input('type SubCategories you want like: bargh Water gaz ... '))
        # plotting datas for each SubCategory
        for i in h[3].split():
            y = x[x['SubCategory'] == i].copy()
            y['Total Amount'] = x['Total Amount'].cumsum()
            plt.plot(mdates.num2date(mdates.date2num(y['Time'])), y['Total Amount'])
        # adding some elements to the plot to make it more exciting!
        plt.xticks(rotation=65)
        plt.legend(h[3].split())
        plt.xlabel('Time')
        plt.ylabel('Amount')
        plt.title('Amount of {} over Time'.format(h[3]))
        plt.show()




def Bills(t1, t2, saved):
    t1 = list(map(lambda x: int(x), t1.split('-')))
    t2 = list(map(lambda x: int(x), t2.split('-')))
    form = saved[(saved['Time'] >= jdatetime.date(*t1)) & (saved['Time'] <= jdatetime.date(*t2))].copy()
    info = input('which units?(also you can put all!)')
    form['SubCategory'] = form['SubCategory'].replace('###', np.nan)
    if info == 'all':
        info = pd.Series(saved['Unit'].unique()).dropna()
    else:
        info = info.split()
    mainbill = pd.DataFrame()
    for i in info: #for every unit that user wants
        Bill = form[(form['SubCategory'].isnull()) & (form.Unit == i)] #filtering those categories that doesn't have subcategory
        Bill = Bill.groupby('Category').aggregate({'Amount': 'sum'}) #total amount
        B = form[~(form['SubCategory'].isnull()) & (form.Unit == i)]  #filtering those categories that have subcategory
        B = B.groupby('SubCategory').aggregate({'Amount': 'sum'}) #total amount
        Bill = Bill.append(B)
        Bill[i] = Bill["Amount"]
        del Bill["Amount"]
        Bill = pd.DataFrame([Bill[i]], columns=Bill.index[:])
        mainbill = mainbill.append(Bill)
    print(mainbill)
    Q = input('do you want to save the bill? (yes , no)')
    if Q == 'yes':
        mainbill.to_csv('Bills.csv')
    return


def report(main_info):
    main_info['SubCategory'] = main_info['SubCategory'].replace('###', np.nan)
    s = main_info[~main_info['SubCategory'].isnull()]  #filtering those categories that doesn't have subcategory 
    Receipt = s.groupby('SubCategory').aggregate({'Total Amount': 'sum'}) 
    total = s['Total Amount'].sum()
    Receipt['Ratio(%)'] = (Receipt['Total Amount'] * 100) / total 
    Receipt = Receipt.drop(columns='Total Amount')
    costs = main_info[main_info['Category'] != 'charge'] #keeping Costs
    charge = main_info[main_info['Category'] == 'charge'] #keeping incomes
    Report = costs.groupby('Category').aggregate({'Total Amount': 'sum'})
    Charge = charge['Total Amount'].sum() #total amount of incomes
    Costs = costs['Total Amount'].sum() #total amount of costs
    Report['Ratio(%)'] = (Report['Total Amount'] * 100) / Costs
    Report = Report.drop(columns='Total Amount')
    Report = pd.DataFrame([Report['Ratio(%)']], columns=Report.index[:])
    Receipt = pd.DataFrame([Receipt['Ratio(%)']], columns=Receipt.index[:])
    Existence = Charge - Costs
    if Existence < 0:
        if abs(Existence) > (Charge / 2): 
            Status = 'Red'
        elif abs(Existence) <= (Charge / 2) and abs(Existence) > (Charge*0.2):
            Status = 'Yellow'
        else:
            Status='Green'
    else:
        Status = 'Green'
    print('this is the ratio of each SubCategory  : ')
    print(Receipt)
    print('this is the ratio of each category : ')
    print(Report)
    print('the Existence of the building is :')
    print(Existence)
    print('the Statuse of the building is:')
    print(Status)



def balancesheet(t1: str, t2: str, saved):
    t1 = list(map(lambda x: int(x), t1.split('-')))
    t2 = list(map(lambda x: int(x), t2.split('-')))
    form = saved[(saved['Time'] >= jdatetime.date(*t1)) & (saved['Time'] <= jdatetime.date(*t2))].copy()
    charges = form[(form['Category'] == 'charge')].copy()#seprating charges from costs
    costs = form[(form['Category'] != 'charge')].copy()
    costs = costs.groupby('Unit').aggregate({'Amount': 'sum'})
    costs = costs.groupby('Unit').aggregate({'Amount': 'sum'}).reset_index()
    charges = charges.groupby('Unit').aggregate({'Amount': 'sum'}).reset_index()
    for i in costs.index:
        costs['Amount'][i] = (costs['Amount'][i]) * (-1)#making it all negetive so if there is no charghes,
        #the condition will be considered as debtor
    balancesheet = costs.copy()
    balancesheet['Condition'] = np.nan
    for i in charges.index[:]:
        if i in balancesheet.index[:]:
            balancesheet.loc[costs.index == i, 'Amount'] += charges.loc[costs.index == i, 'Amount']
        else:
            balancesheet.loc[costs.index == i, 'Amount'] = charges.loc[costs.index == i, 'Amount']
    for j in balancesheet.index:
        if balancesheet['Amount'][j] < 0:
            balancesheet['Condition'][j] = 'debtor'
        elif balancesheet['Amount'][j] > 0:
            balancesheet['Condition'][j] = 'creditor'
    print(balancesheet)
    return


def constantprices(t1, t2, saved):
    t1 = list(map(lambda x: int(x), t1.split('-')))
    t2 = list(map(lambda x: int(x), t2.split('-')))
    pursestringsmean = saved[(saved['Time'] >= jdatetime.date(*t1)) & (saved['Time'] <= jdatetime.date(*t2))].copy()
    pursestringsmean['Time'] = pursestringsmean['Time'].astype(str)
    prediction = pursestringsmean[['Time', 'Unit', 'Category', 'SubCategory', 'Amount']].reset_index(drop=True)
    prediction['Inflation Amount'] = np.nan
    pursestringsmean.Time = pursestringsmean.Time.str[:4]
    pursestringsmean = pursestringsmean.groupby(['Time', 'Unit', 'Category',
                                                 'SubCategory'], as_index=False).aggregate({'Amount': 'mean'})
    for j in prediction.index:#finding the differences between real amounts and the maen
        for i in pursestringsmean.index:
            if prediction.loc[j, 'Time'][:4] == pursestringsmean.loc[i,'Time'] and prediction[
                'SubCategory'][j] == pursestringsmean['SubCategory'][i] and prediction['Unit'][j]==pursestringsmean['Unit'][i]:
                prediction['Inflation Amount'][j] = prediction['Amount'][j] - pursestringsmean['Amount'][i]
    T1 = '1397-01-01'#to make the type of values of date column as an integer for fitting a line, calculate the days before or after 
    #a specific date until each date in this column
    T1 = datetime.strptime(T1, '%Y-%m-%d')
    for i in prediction.index:
        T2 = prediction['Time'][i]
        if T2[8:] == '31' or T2[5:] == '02-30':
            prediction = prediction.drop([i])
        else:
            T2 = datetime.strptime(T2, '%Y-%m-%d')
            prediction['Time'][i] = (T2 - T1).days
    fprediction = pd.DataFrame(
        columns=(['Year', 'Unit', 'Category', 'SubCategory', 'Amount', 'Inflation', 'Final Amount']))
    for Unit,prediction_Unit in prediction.groupby('Unit'):#fitting a line for inflation and constantprices based on time and amount by filtering category
        for Category, prediction_Category in prediction.groupby('Category'):
            if Category == 'Ghabz':
                for SubCategory, prediction_SubCategory in prediction.groupby('SubCategory'):
                    if SubCategory != '###':
                        constantprices = np.polyfit(prediction_SubCategory['Time'].astype(int),
                                                prediction_SubCategory['Amount'].astype(int), 1)
                        f = np.poly1d(constantprices)
                        Inflations = np.polyfit(prediction_SubCategory['Time'].astype(int),
                                            prediction_SubCategory['Inflation Amount'].astype(int), 1)
                        F = np.poly1d(Inflations)
                        t = int(prediction_SubCategory['Time'].tail(1))
                        if f(t+182)+F(t+182)<0 or f(t+182)<0:
                            FinalAmount='Not Enough Data'
                            TotalAmount='Not Enough Data'
                        else:
                            FinalAmount=f(t+182)+F(t+182)
                            TotalAmount=f(t+182)
                        fprediction=fprediction.append({'Year':int(pursestringsmean['Time'].tail(1))+1,
                                        'Unit':Unit,'Category':Category,'SubCategory':SubCategory, 'Amount':TotalAmount,
                                        'Inflation':F(t+182),'Final Amount':FinalAmount}, ignore_index=(True))
            else:
                constantprices = np.polyfit(prediction_Category['Time'].astype(int),
                                        prediction_Category['Amount'].astype(int), 1)
                f = np.poly1d(constantprices)
                Inflations = np.polyfit(prediction_SubCategory['Time'].astype(int),
                                    prediction_SubCategory['Inflation Amount'].astype(int), 1)
                F = np.poly1d(Inflations)
                t = int(prediction_Category['Time'].tail(1))
                if f(t+182)+F(t+182)<0 or f(t+182)<0:
                    FinalAmount='Not Enough Data'
                    TotalAmount='Not Enough Data'
                else:
                    FinalAmount=f(t+182)+F(t+182)
                    TotalAmount=f(t+182)
                fprediction=fprediction.append({'Year':int(pursestringsmean['Time'].tail(1))+1, 'Unit':Unit,
                            'Category':Category,'SubCategory':'###', 'Amount':TotalAmount, 'Inflation':F(t+182),
                            'Final Amount':FinalAmount}, ignore_index=(True))
    print(fprediction)
    return
