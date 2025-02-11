#name: blake maas
#based off a ml/ai stock tracker i already wrote, and am having to rewrite due to a corruption issue which caused a loss of many many lines of code
#originally used alphaapi for this, modified to work with nasdaq and furfill hw requirements.
#rewritten in google colab since my IDE was not liking it. and i think i got it the way you wanted it.

import requests
from datetime import date
import statistics
import json

def get_stock_data(ticker: str) -> dict:
    """
    gets stock data for the given ticker from nasdaq.
    returns a list of closing prices if successful, else raises an exception.
    """
    # realised you gave us a beautiful thing to start so changed to fit this
    ticker = ticker.upper()  # make sure ticker is uppercase
    today = date.today()  # get today's date
    start = str(today.replace(year=today.year - 5))  # start date 5 years ago
    base_url = "https://api.nasdaq.com"  # setup base url and components for api request
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start}&limit=9999"
    request_url = base_url + path  # full api request url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.nasdaq.com"
    }  # changed header to work better because of error I had

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
            float(entry["close"].replace('$', '').replace(',', '').strip())  # clean and convert prices
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
        "average": sum(prices) / len(prices), 
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

    # protect file writing using try/except
    try:
        # write the result data to stocks.json
        with open("stocks.json", "w") as outfile:
            json.dump(result_data, outfile, indent=4)
        print("results successfully written to stocks.json")
    except IOError as e:
        print(f"file write error: {e}")
