import yfinance as yf

def get_company_name(ticker):
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info['longName']
        return company_name
    except Exception as e:
        return str(e)

# Example usage
# ticker = "AAPL"  # Example stock ticker
# company_name = get_company_name(ticker)
# print(f"The company for ticker {ticker} is: {company_name}")
