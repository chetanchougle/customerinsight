import pandas as pd
from sklearn import ensemble
from sklearn.feature_extraction import DictVectorizer
import locale
import datetime
import numpy as np

# xl = pd.ExcelFile('C:\\Users\\Chetan.Chougle\\Desktop\\Book1.xlsx')
# df = xl.parse("Sheet1")
# print(df.head())
def predict_heuristic(previous_predict, month_predict, actual_previous_value, actual_value):
    """ Heuristic that tries to mark the deviance from real and prediction as
        suspicious or not.
    """
    if (
         actual_value < month_predict and
         abs((actual_value - month_predict) / month_predict) > .3):
        if (
             actual_previous_value < previous_predict and
             abs((previous_predict - actual_previous_value) / actual_previous_value) > .3):
            return False
        else:
            return True
    else:
        return False

def get_dataframe():
    xl = pd.ExcelFile('D:\\customerinsight\\Book2.xlsx')
    # df = xl.parse("Sheet1")
    # rows = df

    df = pd.DataFrame.from_records(
        xl.parse("Sheet1"),
        columns=['CustomerName', 'Sales', 'Month', 'Year','PreviousMonthSales']
    )
    #df["CustomerName"] = df["CustomerName"].astype('category')
    # print(df)
    #print(df['CustomerName'].unique().tolist())
    return df

def missed_customers():
    """ Returns a list of tuples of the customer name, the prediction, and
        the actual amount that the customer has bought.
    """

    raw = get_dataframe()
    vec = DictVectorizer()
    today = datetime.date.today()
    currentMonth = today.month
    currentYear = today.year
    lastMonth = (today.replace(day=1) - datetime.timedelta(days=1)).month
    lastMonthYear = (today.replace(day=1) - datetime.timedelta(days=1)).year
    results = []

    # Exclude this month's value
    #df = raw.loc[(raw['Month'] != currentMonth) & (raw['Year'] != currentYear)]
    df = raw
    print('aa')
    #print(df['CustomerName'].unique())
    #print(df['CustomerName'].unique().tolist())
    for customer in set(df['CustomerName'].unique().tolist()):
        # compare this month's real value to the prediction
        actual_value = 0.0
        actual_previous_value = 0.0
        # print("here2")
        # Get the actual_value and actual_previous_value
        # print("sddjd")
        # print(raw.loc[(raw['CustomerName'] == customer) & (raw['Year'] ==currentYear ) ]['Sales'])
        # print("sdfs")
        # new_raw = raw.loc[(raw['CustomerName'] == customer)     , 'Sales']
        # new_raw2 = new_raw.loc[(raw['Year'] == currentYear)   ]
        # print( new_raw.iloc[0] )
        # print( raw.loc[(raw['CustomerName'] == customer )['Sales']])
        # print("\n")
        # print("Current year")
        # print(currentYear)
        print("currentMonth")
        print(currentMonth)
        # print("last month")
        # print(lastMonth)
        # print("lastMonthYear")
        # print(lastMonthYear)
        print("sales")
        # print(raw.loc[
        #     (raw['CustomerName'] == customer) &
        #     (raw['Year'].astype(float) == currentYear) &
        #     (raw['Month'].astype(float) == currentMonth)
        # ]['Sales'])
        #
        # print(float(pd.to_numeric( raw.loc[
        #     (raw['CustomerName'] == customer) &
        #     (raw['Year'].astype(float) == currentYear) &
        #     (raw['Month'].astype(float) == currentMonth)
        # ]['Sales'])))
        # actual_previous_value = float(raw.loc[    (raw['CustomerName'] == customer) &
        #     (raw['Year'].astype(float) == currentYear )  & (raw['Month'] == int(currentMonth)) ]['Sales'])
        # print(actual_previous_value)
        # print('before me')
        try:
            actual_previous_value = float(
                raw.loc[
                    (raw['CustomerName'] == customer) &
                    (raw['Year'] == currentYear) &
                    (raw['Month'] == currentMonth)
                ]['Sales']
            )
            actual_value = float(
                raw[
                    (raw['CustomerName'] == customer) &
                    (raw['Year'] == lastMonthYear) &
                    (raw['Month'] == lastMonth)
                ]['Sales']
            )
        except TypeError:
            # If the customer had no sales in the target month, then move on
            continue

        # Transforming Data
        print('Data')
        print(actual_previous_value)
        print(actual_value)
        print('before me')
        temp = df.loc[df['CustomerName'] == customer]
        targets = temp['Sales']
        del temp['CustomerName']
        del temp['Sales']
        del temp['PreviousMonthSales']
        records = temp.to_dict(orient="records")
        vec_data = vec.fit_transform(records).toarray()
        #print('\ntemp\n')
        #print(temp)
        #print(records)
        #print(vec_data)
        # Fitting the regressor, and use all available cores
        regressor = ensemble.RandomForestRegressor(n_jobs=-1)
        regressor.fit(vec_data, targets)
        estimators = np.arange(10, 200, 10)
        scores = []
        # for n in estimators:
        #     regressor.set_params(n_estimators=n)
        #     score_eval()



        # Predict the past two months using the regressor
        previous_predict = regressor.predict(vec.transform({
            'Year': lastMonthYear,
            'Month': lastMonth
        }).toarray())[0]
        month_predict = regressor.predict(vec.transform({
            'Year': currentYear,
            'Month': currentMonth
        }).toarray())[0]
        print('bb')
        print(previous_predict)
        print('cc')
        print(month_predict)
        if (predict_heuristic(previous_predict, month_predict, actual_previous_value, actual_value)):
            results.append((
                customer,
                month_predict,
                actual_value
            ))

    return results

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    customers = missed_customers()
    print("here")
    # print(customers)
    for customer in  set(customers):
        print("{} was predicted to buy around {}, they bought only {}".format(
            customer[0],
            locale.currency(customer[1], grouping=True),
            locale.currency(customer[2], grouping=True)
        ))
