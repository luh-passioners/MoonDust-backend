import yfinance as yf
import pandas as pd
from datetime import datetime

def read_data(spreadsheet):
    try:
        # Attempt to read the data using pandas.read_excel
        df = pd.read_excel(spreadsheet)
        rows = []

        for index, row in df[['Name', 'Org', 'Amount', 'Date']].iterrows():
            rows.append({'Name': row['Name'],
                    'Org': row['Org'],
                    'Amount': row['Amount'],
                    'Date': row['Date'],
                    })
        
        return rows
            
    except FileNotFoundError:

        # Handle case where file doesn't exist
        print(f"Error: File '{spreadsheet}' not found.")
        return None  # Return None to indicate an error

    except pd.errors.ParserError:

        # Handle case where file format is unsupported
        print(f"Error: Unable to parse '{spreadsheet}'. Invalid format?")
        return None  # Return None to indicate an error

def get_stock_data(symbol, start_date, end_date):
    # Get historical data for the specified stock
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    return data

def get_stock_prices(symbol, start_date):
    end_date = datetime.now().strftime('%Y-%m-%d')
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
            prices.append({ "date": date, "price": price })
    return prices

def get_company_name(ticker):
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info['longName']
        return company_name
    except:
        return ticker

# def main():
#     symbol = input("Enter stock symbol: ")
#     start_date = input("Enter start date (YYYY-MM-DD): ")
#     end_date = datetime.now().strftime('%Y-%m-%d')

#     prices = get_stock_prices(symbol, start_date, end_date)
#     for point in prices:
#         print(point)

# if __name__ == "__main__":
#     main()