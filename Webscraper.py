from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime
import datetime as dt
import time


def option_chain(Ticker):
    
    #get maturity dates of all options available
    maturities = get_all_maturities(Ticker)
    
    #get option data for every maturity of the ticker
    option_chain_list = get_all_options_all_maturities(Ticker, maturities)
    
    #create DataFrame from the list of lists
    option_chain = pd.DataFrame(option_chain_list,columns=["Contract Name", "Last Day Traded", "Strike", "Last Price", "Bid", "Ask", "Change", "Percent Change", "Volume", "Open Interest", "Implied Volatility", "Price of Underlying", "Date", "Maturity Date", "Option Type"])
    
    return option_chain


def get_current_date_and_price_of_underlying(Ticker):
    #get adjusted close price of underlying on the history tab of 
    #yahoo finance and also get the date
    page = requests.get("https://finance.yahoo.com/quote/" + Ticker + "/history?p=" + Ticker)
    soup = BeautifulSoup(page.content, "html.parser")
    histprices = soup.select('table[data-test*="historical-prices"]')
    
    adj_close = list(list(list(histprices[0].children)[1])[0].children)[5].get_text()
    date_of_info = list(list(list(histprices[0].children)[1])[0].children)[0].get_text()
    
    date_and_underlying_price = []
    date_and_underlying_price.append(date_of_info)
    date_and_underlying_price.append(adj_close)
    
    return date_and_underlying_price


def get_all_maturities(Ticker):
    maturities = []
    page = requests.get("https://www.nasdaq.com/symbol/" + Ticker + "/option-chain?dateindex=-1")
    _get_maturity_from_nasdaq_page(page, maturities)
    
    for i in range (2,6):
        page = requests.get("https://www.nasdaq.com/symbol/" + Ticker + "/option-chain?dateindex=-1&page=" + str(i))
        _get_maturity_from_nasdaq_page(page, maturities)

    return maturities
    

def _get_maturity_from_nasdaq_page(page, maturities):
    soup = BeautifulSoup(page.content, "html.parser")
    beginning_of_optionstable = soup.select('tr[class*="groupheader"]', limit = 1)
    options_table = beginning_of_optionstable[0].find_next_siblings()
    
    for sibling in options_table:
        try:
            maturity = list(sibling.children)[1].get_text()
            if maturity not in maturities:
                maturities.append(maturity)
        except IndexError:
            pass
    
    return maturities


def get_all_options_all_maturities(Ticker, maturities):
    #get the basic date and underlying price, true for all options
    date_and_underlying_price = get_current_date_and_price_of_underlying(Ticker)
    adj_close = date_and_underlying_price[1]
    date_of_info = date_and_underlying_price[0]
    
    #set up list of lists with all data on one Ticker
    all_options_of_ticker = []
    
    for maturity in maturities:
        _get_all_options_of_one_maturity(Ticker, maturity, all_options_of_ticker, adj_close, date_of_info)

    return all_options_of_ticker
        
        
def _get_all_options_of_one_maturity(Ticker, maturity, all_options_of_ticker, adj_close, date_of_info):
    #get the table with all option info for a given date
    maturity_as_datetimeobject = datetime.strptime(maturity,'%b %d, %Y')
    unixtime_maturity = int(time.mktime(maturity_as_datetimeobject.timetuple()) + 7200)
    page = requests.get("https://finance.yahoo.com/quote/" + Ticker + "/options?p=" + Ticker + "&date=" + str(unixtime_maturity))
    soup = BeautifulSoup(page.content, "html.parser")
    all_options = soup.select('tr[class*="data-row"]')
    all_options_of_tick = all_options_of_ticker
    
    for strike in list(all_options):
        #just one strike of the ticker and of  
        b = []
        
        #put one row in yahoo option table, the price of the underlying and the date into b
        for child in list(strike.children):
            b.append(child.get_text())
        b.append(adj_close)
        b.append(date_of_info)
        b.append(maturity)
        
        #Is option put or call?
        regexp = re.compile('\d\d\d\d\d\dP')
        regexp.search(b[0])
        if regexp.search(b[0]) is not None:
            b.append("Put")
        else:
            b.append("Call")
        
        #add strike to full list
        all_options_of_tick.append(b)
    
    return all_options_of_tick

#call the main function and get the option chain
option_chain = option_chain("AAPL")

########
NOW the varaible option_chain needs to somehow be entered into the DataBase