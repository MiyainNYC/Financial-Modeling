################################################################

## lcisc5352.lecture.6.demoDataRetrivalVisAndVol.py
## This is a sample file for CISC5352: Financial Data analytics
## Created by Henry Han
## Last update: 10/08/2016

## All right reserved (c) 2015-2016
##################################################################

import numpy                  as  np
import pandas                 as  pd
import pandas_datareader.data as  web
import matplotlib.pylab       as  pylab
import time
import seaborn as sb

## Retrieve data from web: group data into a dictionary

def retrieve_data_from_web(stock_list, source, start_date, end_date):
    i = 0
    stock_data={}
    for stock in stock_list:
        data = web.DataReader(stock,  source, start_date, end_date)
        stock_data[stock] = data
        filename = stock + ".csv"
        data.to_csv(filename)
        i = i+1
        print("{:2d}".format(i) + "  " + filename + " is saved!\n")
        print("\t it has "+"{:6d}".format(len(data))+ "  trading records \n")
        time.sleep(1)
    return stock_data


################################################################
## Module: compute volatility for stock data
## INPUT:
##      Close price of a stock (DataFrame) and window size
##      window size should be 252 days by default
## OUTPUT:
##       volatility
################################################################

def compute_volatility(ticker, window_size):

    S_i             = ticker
    S_i_minus_1     = ticker.shift(1)

    # U sequence: log return ratios
    ticker['U_seqence'] = np.log(S_i / S_i_minus_1)
    U_seqence = ticker['U_seqence']

    # compute rolling std
    ans=ticker['U_seqence'].rolling(window=window_size,center=False).std() * np.sqrt(window_size)

    return ans


###############################################################
## Section 1: Retrieve stock data from Google Finance
###############################################################

# A stock list with ten stock symbols: 5 IT and 5 Bank industry
stock_list = ['GOOG','YHOO', 'AAPL', 'MSFT', 'AMZN',
              'JPM', 'BAC',  'HSBC',  'CIT', 'GS']

s_date = '10/10/2012'  # start
e_date = '10/10/2016'  # end

print("Please, wait,...,")
print("\n I am retrieving stock data from " + s_date + " to " + e_date + "\n")
time.sleep(1)

###########################
## Retrieve data from web
###########################

stock_data = {}
print("\n Each stock dataset will be saved in a csv file\n")
stock_data = retrieve_data_from_web(stock_list, 'google', s_date, e_date)
print("\nData retrival is complete, Check your working directory to find data!\n")

#################################################################
## Visualize data
################################################################

it_stock_list      = stock_list[0:5]
bank_stock_list    = stock_list[5:10]

pylab.close('all')

fig0 = pylab.figure(figsize = (10,8))
pylab.subplot(2,1,1)

pylab.plot(stock_data['GOOG']['Close'], 'r-',  label='GOOG', linewidth=1.5)
pylab.plot(stock_data['YHOO']['Close'], 'b--', label='YHOO', linewidth=1.0)
pylab.plot(stock_data['AAPL']['Close'], 'm-.', label='AAPL', linewidth=2.0)
pylab.plot(stock_data['MSFT']['Close'], 'k-',  label='MSFT', linewidth=1.0)
pylab.plot(stock_data['AMZN']['Close'], 'y-',  label='AMZN', linewidth=1.0)

pylab.ylabel('Close Price')
pylab.setp(pylab.gca().get_xticklabels(), FontSize=8, rotation=45)
h=pylab.legend(loc='upper left')
pylab.title('IT industry stocks')
pylab.grid('on')

pylab.subplot(2,1,2)

pylab.plot(stock_data['JPM']['Close'],  'r-',    label = 'JPM',  linewidth=1.5)
pylab.plot(stock_data['BAC']['Close'],  'b-',    label = 'BAC',  linewidth=1.0)
pylab.plot(stock_data['HSBC']['Close'], 'm:',    label = 'HSBC', linewidth=2.0)
pylab.plot(stock_data['CIT']['Close'],  'k-',    label = 'CIT',  linewidth=2.5)
pylab.plot(stock_data['GS']['Close'],   'y-',    label = 'GS',   linewidth=1.0)

pylab.xlabel('Trading time')
pylab.ylabel('Close Price')
pylab.legend(loc='upper left')
pylab.setp(pylab.gca().get_xticklabels(), FontSize=8, rotation=45)
pylab.title('Bank industry stocks')
pylab.grid('on')

pylab.show()  ## need to close this to get following new plots!

filename='ITandBankStockJune2012toOct2016.eps'
fig0.savefig(filename, dpi=300)
print(" " + filename + "  is saved!\n")


print("\n Start to calculate volatility...")

window_size = 252
for stock in stock_list:
    stock_data[stock]['Volatility'] = compute_volatility(stock_data[stock]['Close'], window_size)

fig2 = pylab.figure(figsize = (10,6))
pylab.plot(stock_data['GOOG']['Volatility'],  'r-',  label='GOOG', linewidth=3.5)
pylab.plot(stock_data['YHOO']['Volatility'],  'b--', label='YHOO', linewidth=2.0)
pylab.plot(stock_data['AAPL']['Volatility'],  'm-.', label='AAPL', linewidth=2.0)
pylab.plot(stock_data['MSFT']['Volatility'],  'k-',  label='MSFT', linewidth=2.2)
pylab.plot(stock_data['AMZN']['Volatility'],  'y-',  label='AMZN', linewidth=2.0)

pylab.plot(stock_data['JPM']['Volatility'],    'r:',   label='JPM', linewidth=2.5)
pylab.plot(stock_data['BAC']['Volatility'],    'b-',   label='BAC', linewidth=1.0)
pylab.plot(stock_data['HSBC']['Volatility'],   'm-.o', label='HSBC',  markersize=4, linewidth=1.0)
pylab.plot(stock_data['CIT']['Volatility'],    'c-.',  label='CIT',  linewidth=3.0)
pylab.plot(stock_data['GS']['Volatility'],     'g-',   label='GS', linewidth=4.0)

pylab.legend(loc='lower right')
pylab.xlabel('Trading time')
pylab.setp(pylab.gca().get_xticklabels(), FontSize=8, rotation=45)
pylab.ylabel('Volatility')
pylab.ylim(0.1,0.4)
pylab.title('The volatilities of IT stocks and Bank stocks')


filename2 = 'ITandBankStockVolatility.eps'
fig2.savefig(filename2, dpi=300)
print(" " + filename2 + "  is saved!\n")

fig3 = pylab.figure(figsize = (12,5))

pylab.subplot(1,2,1)
pylab.plot(stock_data['GOOG']['Volatility'],  'r-',  label='GOOG', linewidth=3.5)
pylab.plot(stock_data['YHOO']['Volatility'],  'b--', label='YHOO', linewidth=2.0)
pylab.plot(stock_data['AAPL']['Volatility'],  'm-.', label='AAPL', linewidth=2.0)
pylab.plot(stock_data['MSFT']['Volatility'],  'k-',  label='MSFT', linewidth=2.2)
pylab.plot(stock_data['AMZN']['Volatility'],  'y-',  label='AMZN', linewidth=2.0)
pylab.ylim(0.1,0.4)
pylab.legend(loc='lower right')
pylab.xlabel('Trading time')
pylab.ylabel('Volatility')
pylab.setp(pylab.gca().get_xticklabels(), FontSize=8, rotation=45)
pylab.title('The volatilities of IT stocks')

pylab.subplot(1,2,2)
pylab.plot(stock_data['JPM']['Volatility'],    'r:', label='JPM', linewidth=2.5)
pylab.plot(stock_data['BAC']['Volatility'],    'b-', label='BAC', linewidth=1.0)
pylab.plot(stock_data['HSBC']['Volatility'],   'm-.o', label='HSBC',  markersize=4, linewidth=1.0)
pylab.plot(stock_data['CIT']['Volatility'],    'c-.',   label='CIT',  linewidth=3.0)
pylab.plot(stock_data['GS']['Volatility'],     'g-',   label='GS', linewidth=4.0)
pylab.ylim(0.1,.4)
pylab.legend(loc='lower right')
pylab.xlabel('Trading time')
pylab.setp(pylab.gca().get_xticklabels(), FontSize=8, rotation=45)
pylab.ylabel('Volatility')
pylab.title('The volatilities of Bank stocks')

pylab.show()