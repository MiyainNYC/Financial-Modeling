#get specified option data from yahoo finance
import csv
import os
import pickle
import requests
import datetime
import shutil
import random
import numpy as np
import pandas as pd

class OptionSpider():
  URL_OPTION = 'https://query1.finance.yahoo.com/v7/finance/options/{!s}?formatted=true&crumb=ITWkCJiVlkA&lang=en-US&region=US&date={!s}&corsDomain=finance.yahoo.com'
  URL_DATES  = 'https://query1.finance.yahoo.com/v7/finance/options/{!s}?formatted=true&crumb=ITWkCJiVlkA&lang=en-US&region=US&corsDomain=finance.yahoo.com'
  TEMP_LAST_KEY = './webcrawler/yahoo/option-lastkey.pickle'

  # member variables
  _optionFolder = 'options'
  _keyList = []
  _isRunning = False

  # constructor
  def __init__(self, keyPath = None, optionFolder = None):
    if(keyPath):
      self._keyList = self._getKeyList(keyPath)
    if(optionFolder):
      self._optionFolder = optionFolder
    # print (self._keyList)

  def crawl(self, forceRestart = False):
    if(forceRestart):
      self._setKeyIndex(0)
      #
      if(os.path.exists(self._optionFolder)):
        shutil.rmtree(self._optionFolder)
    # start
    # test finish # self._setKeyIndex(25230)
    if(not self._isRunning):
      for callee in self._generateList():
        print (callee)
      self._isRunning = True
    
  def getByKey(self, key):
    path = '/'.join([self._optionFolder, key + '.xlsx'])
    options = {'CALL' : {}, 'PUT' : {}}
    if(os.path.isfile(path)):
      f = pd.ExcelFile(path)
      # f.sheet_names # get total sheets
      # DataFrame
      options['PUT'] = f.parse('PUT', index_col='Date')
      options['CALL'] = f.parse('CALL', index_col='Date')
      # print (df.head())
    else:
      dates = self._getDates(key)
      if(len(dates) > 0):
        options = self._getOptionByKey(key, dates)
        print('getting the {!s} option done!'.format(key))
        self._saveWorkbook(options, key)
    # print (options)
    return options

  def crawlByAmount(self, total, isRandom = False):
    indexs = random.sample(range(len(self._keyList)), total)
    if(total <= len(self._keyList)):
      items = indexs if isRandom else range(total)
    else:
      items = indexs if isRandom else range(len(self._keyList))
    #
    for i in items:
      print('trying to get the {!s} option...'.format(self._keyList[i]))
      self.getByKey(self._keyList[i])
    # return indexs

  def _generateList(self):
    index = self._getKeyIndex()
    totalLeft = len(self._keyList) - index
    date = datetime.datetime.today().strftime("%m/%d/%Y %H:%S")
    print ('[{!s}] total left items: [{:d}/{:d}]'.format(date, totalLeft, len(self._keyList)))
    for i in range(totalLeft):
      yield self._getAndSave()

  def _getKeyIndex(self):
    index = 0
    # get current index
    try:
      with open(OptionSpider.TEMP_LAST_KEY, 'rb') as f:
        index = pickle.load(f)
    except Exception as e:
      print (e)
    return index

  def _setKeyIndex(self, index):
    # save current index
    with open(OptionSpider.TEMP_LAST_KEY, 'wb') as f:
      pickle.dump(index, f)

  def _getAndSave(self):
    keyIndex = self._getKeyIndex()
    # just for test # keyIndex = 6
    # https://pyformat.info/
    print('trying to get the option {:d}...'.format(keyIndex + 1))
    if(self._keyList and self._keyList[keyIndex]):
      # get
      key = self._keyList[keyIndex]
      dates = self._getDates(key)
      # print (key)
      # print (len(dates))
      if(len(dates) > 0):
        result = self._getOptionByKey(key, dates)
        # print (result)
        # save to .xlsx
        self._saveWorkbook(result, key)
        print('getting {!s} option done!'.format(key))
      # save current index as an existing one
      keyIndex += 1
      # save current index
      self._setKeyIndex(keyIndex)
    date = datetime.datetime.today().strftime("%m/%d/%Y %H:%S")
    string = '[{!s}] next [{:d}/{:d}]'.format(date, keyIndex + 1, len(self._keyList))
    # last items
    if(keyIndex >= len(self._keyList)):
      string = '[{!s}] all finished!'.format(date)
    return string

  def _getKeyList(self, keyPath):
    items = []
    #
    try:
      # Using with statements, you can get rid of all these try...finally statements at inner levels.
      with open(keyPath, newline='') as file:
        result = csv.reader(file, delimiter=' ', quotechar='|')
        for row in result:
          # print(', '.join(row))
          items.append(row[0])
    except Exception as e:
      print (e)
    return items

  def _getDates(self, key):
    optionUrl = OptionSpider.URL_DATES.format(key)
    response = requests.get(optionUrl)
    result = response.json()
    items = result.get('optionChain', {}).get('result', [])
    if(isinstance(items, list) and len(items) > 0):
      items = items[0].get('expirationDates', [])
    else:
      items = []
    return items

  def _getOptionByKey(self, stock, dates):
    data = {}
    options = {'calls' : [], 'puts' : []}
    #
    for i, timestamp in enumerate(dates):
      # 2016-10-9
      date = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
      # get options
      optionUrl = OptionSpider.URL_OPTION.format(stock, timestamp)
      response = requests.get(optionUrl)
      result = response.json()
      # result['optionChain']
      resultOptions = result.get('optionChain', {}).get('result', [{}])[0].get('options', [])[0]
      # print (date, resultOptions)
      #
      for item in resultOptions['calls']:
        # get Adj Close from latest one
        # index = len(resultStocks) - len(resultOptions['calls']) - 1 + c
        # print ('len resultStocks', len(resultStocks))
        # print ('len resultOptions[calls]', len(resultOptions['calls']))
        # print ('c', c)
        # index = c if c < len(resultStocks) else (len(resultStocks) - 1)
        options['calls'].append(self._rowFormat(item, date))
        # c += 1
      #
      for item in resultOptions['puts']:
        # index = len(resultStocks) - len(resultOptions['puts']) - 1 + c
        # index = p if p < len(resultStocks) else (len(resultStocks) - 1)
        # print ('p', index)
        options['puts'].append(self._rowFormat(item, date))
        # p += 1
    #
    if(len(options.get('calls')) > 0):
      data['CALL'] = pd.DataFrame(options.get('calls'))
      data['CALL'] = data['CALL'].set_index('Date')
    if(len(options.get('puts')) > 0):
      data['PUT'] = pd.DataFrame(options.get('puts'))
      data['PUT'] = data['PUT'].set_index('Date')
    return data

  def _rowFormat(self, row, date, adjClose = None):
    result = {}
    if(row):
      result = {
        'Date'              : date,
        'LastTradeDate'     : row.get('lastTradeDate', {}).get('fmt', ''),
        'Strike'            : row.get('strike', {}).get('raw', ''),
        # 'StockPrice'        : adjClose,
        'ContractName'      : row.get('contractSymbol'),
        'LastPrice'         : row.get('lastPrice', {}).get('raw', ''),
        'Bid'               : row.get('bid', {}).get('raw', ''),
        'Ask'               : row.get('ask', {}).get('raw', ''),
        'Change'            : row.get('change', {}).get('raw', ''),
        '%Change'           : row.get('percentChange', {}).get('raw', ''),
        'Volume'            : row.get('volume', {}).get('raw', ''),
        'OpenInterest'      : row.get('openInterest', {}).get('raw', ''),
        'ImpliedVolatility' : row.get('impliedVolatility', {}).get('raw', ''),
      }
    return result

  def _saveWorkbook(self, options, key):
    path = '/'.join([self._optionFolder, key + '.xlsx'])
    # check the folder
    if not os.path.exists(self._optionFolder):
      os.makedirs(self._optionFolder)
      print('"./{!s}/" does not exist, making a new one...'.format(self._optionFolder))
    #
    writer = pd.ExcelWriter(path)
    for n, key in enumerate(options):
      # print(n, '<---', options[key])
      # options[key].to_excel(writer,'sheet%s' % n + '-' + key)
      options[key].to_excel(writer, key)
    writer.save()

