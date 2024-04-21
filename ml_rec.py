from fms_machinelearning.IBD50_Tickers import get_tickers
from fms_machinelearning.Finviz_Scraper import analyze_news, NewsParser, NewsScraper
from fms_machinelearning.Social_Media_Scraper import Calculate_Score, scrape_investorhub_board
from fms_machinelearning.YFinanceStockInformationScraper import get_fundamental_score, get_technical_score

def recommend_positions():
  tickers = get_tickers()

  # news score
  scraper = NewsScraper(tickers)
  scraper.scrape_news()
  parser = NewsParser(scraper.news_data)
  sorted_news_data, ticker_links = parser.parse_news_links()
  news_sentiment_scores = analyze_news(ticker_links) # list of -1 through 1

  # forum score
  forum_sentiment_scores = {}
  for ticker in tickers:
    forum_sentiment_scores[ticker] = Calculate_Score(scrape_investorhub_board(ticker))

  print("forum scores!", forum_sentiment_scores)

  # fundamental score
  fundamental_scores = {}
  for ticker in tickers:
    fundamental_scores[ticker] = get_fundamental_score(ticker)

  # technical score
  technical_scores = {}
  for ticker in tickers:
    technical_scores[ticker] = get_technical_score(ticker)

  # consolidate scores:
  recommendations = []

  for ticker in tickers:
    aggregate_score = (0.3 * 0) + (0.3 * fundamental_scores[tickers]) + (0.2 * technical_scores[ticker]) + (0.2 * forum_sentiment_scores[ticker])

    recommendations.append({ "ticker": ticker, "score": aggregate_score })

  sorted(recommendations, key=lambda x: x["score"], reverse=True)

  return recommendations
  