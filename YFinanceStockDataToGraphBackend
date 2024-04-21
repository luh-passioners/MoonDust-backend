import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol, start_date, end_date):
    # Get historical data for the specified stock
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    return data

def get_stock_prices(symbol, start_date, end_date):
    data = get_stock_data(symbol, start_date, end_date)
    prices = []
    for date in pd.date_range(start_date, end_date):
        date = date.strftime('%Y-%m-%d')
        if date in data.index:
            if date == end_date:
                today = datetime.now()
                if today.hour >= 16:
                    price = round(data.loc[date]['Close'], 2)
                else:
                    price = round(data.loc[date]['Open'], 2)
            else:
                price = round(data.loc[date, 'Open'], 2)
            prices.append((date, price))
    return prices

# def main():
#     symbol = input("Enter stock symbol: ")
#     start_date = input("Enter start date (YYYY-MM-DD): ")
#     end_date = datetime.now().strftime('%Y-%m-%d')

#     prices = get_stock_prices(symbol, start_date, end_date)
#     for point in prices:
#         print(point)

# if __name__ == "__main__":
#     main()
