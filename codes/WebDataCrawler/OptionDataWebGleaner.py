###############################
###############################

Developed by Miya WANG  10/2016

#################################

from selenium import webdriver
from bs4 import BeautifulSoup
import os
import pandas as pd
from datetime import date
import numpy as np
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import random


class OptionDataWebGleaner(object):
    @property
    def __init__(self):

        ticker = [line.strip() for line in open('Yahoo_ticker_List.csv')]
        self.today = date.today()

        num = int(input("How many stocks you want to download? There are %d options in total\n"% len(ticker)))

        list_chosen = random.sample(range(0, len(ticker)), num)

        stocks = [ticker[i] for i in list_chosen]

        if input('Do you have a stock you want to look particularly? Type Y or yes, N or no\n') == 'Y':
            stocks.append(input('Type the ticker of your stock\n'))

        df_dict = self.data_download(stocks)

        if input('Do you want to process and clean the data? Type Y or yes, N or no\n') == 'Y':
            for stock in df_dict.keys():
                df = df_dict[stock]
                df_dict[stock] = self.clean_data(df)


        if input('Do you want to save the data into csv form? Type Y or yes, N or no\n') == 'Y':
            for stock in df_dict.keys():
                os.chdir("C:\\Users\\Miya\\OneDrive\\Miya'sGithub\\Financial-Modeling\\projectOne\\dataset")
                df_dict[stock].to_csv(stock+'.csv')


        if input("Do you want to remove outliers? Type Y for yes, N or no\n") == 'Y':
            for stock in df_dict.keys():
                print(df_dict[stock].loc[df_dict[stock]['Implied Volatility'] > 2])
                print('Removing outliers...')
                df_dict[stock] = df_dict[stock].loc[df_dict[stock]['Implied Volatility'] <= 2]

        if input("Do you want to visualize? Type Y for yes, N or no\n") == 'Y':
            for stock in df_dict.keys():
                print(stock)
                self.viz(df_dict[stock],stock)

        if input("Do you want to get summery of your stock? Type Y for yes, N or no\n") == 'Y':
            for stock in df_dict.keys():
                self.summary(df_dict[stock])

    def clean_data(self, dataframe):
        columns_to_set = ['Last Price', 'Open Interest', 'Strike', 'Volume', 'Implied Volatility']

        for i in columns_to_set:
            series = dataframe[i]
            series_new = []
            for j in series:
                j = str(j)
                j_new = ''.join(ch for ch in j if (ch != '%') and (ch != ','))
                series_new.append(j_new)
            dataframe[i] = series_new

        print('Unexpected symbols removed...')

        columns_to_change = ['Last Price', 'Open Interest', 'Strike', 'Volume', 'stock_price', 'Implied Volatility']
        for i in columns_to_change:
            dataframe[i] = dataframe[i].astype(float)

        print('Data type changed...')

        ## change the dtype

        dataframe = dataframe.dropna()

        print("Missing values removed...")

        return dataframe

    def data_download(self, stocks):

        chromedriver = "/Users/Miya/Downloads/chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        maturity_dates = [date(2016, 12, 16), date(2017, 1, 20), date(2017, 2, 17)]
        dates = ['1481846400', '1484870400', '1487289600']

        df_dict = {}

        for stock in stocks:
            for d, maturity in zip(dates, maturity_dates):
                url = 'http://finance.yahoo.com/quote/' + stock + '/options?date=' + d
                ## Crawl data
                driver.get(url)
                html_source = driver.page_source
                ## Beautifulsoup
                soup = BeautifulSoup(html_source, 'html.parser')

                if soup.find('table', 'calls') is not None:

                    print('Web Crawling.....')

                    stock_price = [float(i.text) for i in soup.findAll('span', 'Fz(36px)')]
                    title = [i.text for i in soup.find('table', 'calls').find_all('th')]
                    text = [i.text for i in soup.find('table', 'calls').find_all('td')]
                    rows = [row for row in soup.find('table', 'calls').find_all("tr")]

                    print('Crawling Finished!')

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
                    print('Saved into dataframe!')

                    # df.to_csv(stock+date+'.csv')
                    stock_refined = ''.join(ch for ch in stock if (ch != '.') and (ch != '-'))

                    if stock_refined not in df_dict.keys():
                        df_dict[stock_refined] = df
                    else:
                        df_dict[stock_refined] = pd.concat([df_dict[stock_refined], df], ignore_index=True)

        return df_dict

    def viz(self, dataframe,stock):
        time_to_maturity = []
        dataframe = dataframe.sort_values(by='Strike')
        ## grab dataframe, then relevant data
        for i, j in zip(dataframe.maturity_date, dataframe.date):
            time_to_maturity.append((i - j).days / 365)

        print(time_to_maturity)

        strike_price = dataframe['Strike']

        # generate pseudo-implied volatility by using strike price and time-to-maturity as parameters

        implied_vol = dataframe['Implied Volatility'].values

        print(implied_vol)

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
        plot.suptitle(stock)
        os.chdir("C:\\Users\\Miya\\OneDrive\\Miya'sGithub\\Financial-Modeling\\projectOne\\pic")
        fig.savefig(stock+ '.png', dpi=fig.dpi)
        plot.show()

    def summary(self, dataframe):

        print(dataframe.describe())


OptionDataWebGleaner()



