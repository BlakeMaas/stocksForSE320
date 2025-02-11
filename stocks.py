#name: blake maas
#based off a ml/ai stock tracker i already wrote parts of which I either borrowed or was inspired by other code on github
#and am having to rewrite due to a corruption issue which caused a loss of many many lines of code
#originally used alphaapi for this, modified to work with nasdaq.

import requests
from datetime import date

def get_stock_data(symbol: str) -> list:
    """
    gets stock data for the given symbol from nasdaq.
    returns a list of closing prices if successful, else raises an exception.
    """
    # setup base url and components for api request
    base_url = "https://api.nasdaq.com"
    symbol = symbol.upper()  # make sure symbol is uppercase
    current_date = date.today()  # get today's date
    start_period = str(current_date.replace(year=current_date.year - 5))  # start date 5 years ago
    endpoint = f"/api/quote/{symbol}/historical?assetclass=stocks&fromdate={start_period}&limit=9999"
    request_url = base_url + endpoint  # full api request url
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
            raise ValueError(f"no historical data found for {symbol}.")

        # extract closing prices
        closing_prices = [
            float(entry["close"].replace(',', ''))  # clean and convert prices
            for entry in response_data["data"]["tradesTable"]["rows"]
        ]
        
        # check if data is valid
        if not closing_prices:
            raise ValueError(f"no valid closing prices found for {symbol}.")
        return closing_prices

    # handle network or request issues
    except requests.RequestException as e:
        raise RuntimeError(f"network or api error while fetching data for {symbol}: {e}")
    # handle data or key issues
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"data issue for {symbol}: {e}")




if __name__ == "__main__":
    # list of stock symbols to process
    stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  
    
    # process each stock symbol
    for symbol in stock_symbols:
        try:
            print(f"fetching data for {symbol}...")
            closing_prices = get_stock_data(symbol)  # get prices
            print(f"successfully fetched {len(closing_prices)} data points for {symbol}.")
        except RuntimeError as e:
            # print any errors encountered
            print(e)
