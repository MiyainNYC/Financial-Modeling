##################################################################
## cisc5352.lecture.6.MaxLi.NewtonMethod.py
## This is a sample file for CISC5352 Financial data analytics
## Author: Max(yanzhe) Li
## Henry Han modified it
## Last modified: Oct 25, 2016
##################################################################

import math as e
from   scipy import stats
from   datetime import date
import time

class bsmNewtonMethod():
    def __init__(self, S, K, T, r, sigma, cStar, optionType, iter):
        self.S     = S
        self.K     = K
        self.T     = T
        self.r     = r
        self.sigma = sigma
        self.cStar = cStar

        self.optionType = optionType
        self.iter       = iter  # max iter

    ## European call/put values from BSM model
    def bsmValue(self):
        d1 = (e.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * e.sqrt(self.T))
        d2 = d1 - self.sigma * e.sqrt(self.T)

        if self.optionType in ['Call', 'call', 'CALL']:
            return self.S * stats.norm.cdf(d1) - self.K * e.exp(-self.r * self.T) * stats.norm.cdf(d2)

        elif self.optionType in ['Put', 'put', 'PUT']:
            return self.K * e.exp(-self.r * self.T) * stats.norm.cdf(-d2) - self.S * stats.norm.cdf(-d1)

        else:
            raise TypeError('the option_type argument must be either "call" or "put"')

    ## Vega in BSM model (f')
    def bsmVega(self):
        d1 = (e.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * e.sqrt(self.T))
        vega = self.S * stats.norm.pdf(d1) * e.sqrt(self.T)
        return vega


   ## Use newton method to predict implied volatility
    def bsmIVprediction(self):
        max_iter  = self.iter
        tolerance = 0.00000001

        for i in range(max_iter):

            f       = self.bsmValue() - self.cStar  # objective function
            f_prime = self.bsmVega()                # compute f_prime

            old_sigma  = self.sigma
            self.sigma = self.sigma - f/f_prime

            #############################################################
            ## check the |X_n+1 -X_n|
            ## A lazy way: if the iteration points are
            ##               no longer update, stop the newton method
            ## A safe version should also check if f is approching zero!
            #############################################################
            if (e.fabs(self.sigma - old_sigma) < tolerance):
                print("total {:d}".format(i) + " iterations in newton method\n")
                return self.sigma



## compute expiration time T

today  = date(2016, 10, 12)
expDay = date(2016, 12, 16)
T    = expDay - today

iter = 100000  # Max iterations

sigma0 = 0.5   # initial point for newton method
r      = 0.02  # 3-month T-bill rate

currentStockPrice = 16.1

#### four BAC options
bacOptionList = [[currentStockPrice, 16.00, T.days / 365, r , sigma0, 0.80, 'call', iter],
                 [currentStockPrice, 17.00, T.days / 365, r, sigma0,  0.38, 'call', iter],
                 [currentStockPrice, 16.00, T.days / 365, r, sigma0,  0.74, 'put', iter],
                 [currentStockPrice, 17.00, T.days / 365, r, sigma0,  1.32, 'put', iter]]

print('The underlying asset is Bank of America (BAC), '
      'current stock price is ${:.2f}, '
      'the expiration date is {:%Y-%m-%d}\n'.format(currentStockPrice, expDay))

for option in bacOptionList:
    impvol = bsmNewtonMethod(option[0],
                             option[1],
                             option[2],
                             option[3],
                             option[4],
                             option[5],
                             option[6],
                             option[7]).bsmIVprediction()

    print('Here is a {0} option.\n'
          'The strike price is ${1:.2f} and option price is ${2:.2f}.'
          '\nThe implied volatility is --->{3:.2%}\n'.format(option[6],
                                                             option[1],
                                                             option[5],
                                                             impvol))
    time.sleep(1)
