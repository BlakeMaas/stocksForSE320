#name: blake maas
#based off a ml/ai stock tracker i already wrote, and am having to rewrite due to a corruption issue which caused a loss of many many lines of code
#originally used alphaapi for this, modified to work with nasdaq and furfill hw requirements.

import requests
from datetime import date
import statistics
import json

def get_stock_data(ticker: str) -> dict:
    """
    gets stock data for the given ticker from nasdaq.
    returns a list of closing prices if successful, else raises an exception.
    """
    
    #realised you gave us a beautiful thing to start so changed to fit this: 
    ticker = ticker.upper()  # make sure ticker is uppercase
    current_date = date.today()  # get today's date
    start_period = str(current_date.replace(year=current_date.year - 5))  # start date 5 years ago
    base_url = "https://api.nasdaq.com" # setup base url and components for api request
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start_period}&limit=9999"
    request_url = base_url + path  # full api request url
    headers = {
        "User-Agent": "Mozilla/5.0"  # avoid request blocking
    }

    try:
        # send request and check for issues
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()  # check http errors
        response_data = response.json()  # get json response
        
        # verify data availability
        if "data" not in response_data or "tradesTable" not in response_data["data"]:
            raise ValueError(f"no historical data found for {ticker}.")

        # extract closing prices
        closing_prices = [
            float(entry["close"].replace(',', ''))  # clean and convert prices
            for entry in response_data["data"]["tradesTable"]["rows"]
        ]
        
        # check if data is valid
        if not closing_prices:
            raise ValueError(f"no valid closing prices found for {ticker}.")
        return closing_prices

    # handle network or request issues
    except requests.RequestException as e:
        raise RuntimeError(f"network or api error while fetching data for {ticker}: {e}")
    # handle data or key issues
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"data issue for {ticker}: {e}")

def process_stock_data(prices: list) -> dict:
    """
    calculate min, max, avg, and median prices.
    """
    return {
        "minimum": min(prices),
        "max": max(prices),
        "avgerage": sum(prices) / len(prices),
        "median": statistics.median(prices)
    }

if __name__ == "__main__":
    # list of stock tickers to process
    stock_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  
    result_data = []  # to store results
    
    # process each stock ticker
    for ticker in stock_tickers:
        try:
            print(f"fetching data for {ticker}...")
            closing_prices = get_stock_data(ticker)  # get prices
            print(f"successfully fetched {len(closing_prices)} data points for {ticker}.")
            
            # analyze the stock data
            stats = process_stock_data(closing_prices)
            stats["ticker"] = ticker  # include the ticker in the result
            result_data.append(stats)
        except RuntimeError as e:
            # print any errors encountered
            print(e)
