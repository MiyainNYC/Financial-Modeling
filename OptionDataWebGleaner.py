from __future__ import division
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import pandas as pd
from datetime import date
import numpy as np
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


class OptionDataWebGleaner(object):
    def __init__(self):

        ticker = pd.read_csv('Yahoo_ticker_List.csv')['AUB.AX'].values
        self.ticker = ticker
        dates = ['1481846400', '1484870400', '1487289600']
        maturity_dates = [date(2016, 12, 16), date(2017, 1, 20), date(2017, 2, 17)]

        chromedriver = "/Users/Miya/Downloads/chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        option = raw_input('Please type the ticker of your option:\n')
        df_dict = {}
        self.today = date.today()

        self.option = option

        for stock in self.ticker:
            for d, maturity in zip(dates, maturity_dates):

                url = 'http://finance.yahoo.com/quote/' + stock + '/options?date=' + d
                ## Crawl data
                driver.get(url)
                html_source = driver.page_source
                ## Beautifulsoup
                soup = BeautifulSoup(html_source, 'html.parser')

                if soup.find('table', 'calls') is not None:

                    stock_price = [float(i.text) for i in soup.findAll('span', 'Fz(36px)')]
                    title = [i.text for i in soup.find('table', 'calls').find_all('th')]
                    text = [i.text for i in soup.find('table', 'calls').find_all('td')]
                    rows = [row for row in soup.find('table', 'calls').find_all("tr")]

                    l_table = len(rows) - 1
                    ## call data
                    dictionary = {}
                    dictionary['maturity_date'] = [maturity] * l_table
                    dictionary['date'] = [self.today] * l_table
                    dictionary['stock_price'] = stock_price * l_table

                    for j in range(10):
                        key = title[j]
                        dictionary[key] = []
                        for i in range(l_table):
                            dictionary[key].append(text[10 * i + j])


                            ## write into dataframe
                    df = pd.DataFrame(dictionary)

                    # df.to_csv(stock+date+'.csv')

                    if stock not in df_dict.keys():
                        df_dict[stock] = df
                    else:
                        df_dict[stock] = pd.concat([df_dict[stock], df], ignore_index=True)

        self.dictionary = df_dict

    def clean_data(self):

        df_dict = self.dictionary
        for stock in self.ticker:

            columns_to_set = ['Last Price', 'Open Interest', 'Strike', 'Volume', 'Implied Volatility']
            dataframe = df_dict[stock]

            for i in columns_to_set:
                series = dataframe[i]
                series_new = []
                for j in series:
                    j = str(j)
                    j_new = ''.join(ch for ch in j if (ch != '%') and (ch != ','))
                    series_new.append(j_new)
                dataframe[i] = series_new

            df_dict[stock] = dataframe

        print('Unexpected symbols removed...')

        for stock in self.ticker:
            columns_to_change = ['Last Price', 'Open Interest', 'Strike', 'Volume', 'stock_price', 'Implied Volatility']
            dataframe = df_dict[stock]
            for i in columns_to_change:
                dataframe[i] = dataframe[i].astype(float)

            df_dict[stock] = dataframe

        print('Data type changed...')

        ## change the dtype

        #for stock in self.ticker:
         #   df_dict[stock] = df_dict[stock].dropna()

        #print("Missing values removed...")

        #for stock in self.ticker:
            #df_dict[stock] = df_dict[stock].loc[df_dict[stock]['Implied Volatility'] <= 2]

        print("Outliers removed...")

        return df_dict

    def save_file(self):

        save_file = raw_input("Do you want to save the file into csv? Type Y for yes, N or no\n ")
        df_dict = self.clean_data()
        if save_file == 'Y':
            for stock in self.ticker:

                csv_name = stock  + '.csv'
                df_dict[stock].to_csv(csv_name)
            print("File Saved!")

    def viz(self):

        df_dict = self.clean_data()
        option = self.option
        time_to_maturity = []
        dataframe = df_dict[option]
        dataframe = dataframe.sort_values(by='Strike')
        ## grab dataframe, then relevant data
        for i, j in zip(dataframe.maturity_date, dataframe.date):
            time_to_maturity.append((i - j).days / 365)

        print time_to_maturity

        strike_price = dataframe['Strike']

        # generate pseudo-implied volatility by using strike price and time-to-maturity as parameters

        implied_vol = dataframe['Implied Volatility'].values

        strike_price, time_to_maturity = np.meshgrid(strike_price, time_to_maturity)

        fig = plot.figure(figsize=(10, 5))  ## a plot object
        ax = Axes3D(fig)  # create a 3D object/handle

        ##plot surface: array row/column stride(step size:2)
        ##plot surface: array row/column stride(step size:2)

        surf = ax.plot_surface(strike_price, time_to_maturity, implied_vol, rstride=2, cstride=2, cmap=cm.coolwarm,
                               linewidth=0.5, antialiased=False)

        # set x,y,a labels
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('time to maturity')
        ax.set_zlabel('implied volatility%')
        plot.suptitle(option)
        plot.show()

    def summary(self):

        df_dict = self.clean_data()
        option = self.option
        dataframe = df_dict[option]
        print(dataframe.describe())


OptionDataWebGleaner().viz()

