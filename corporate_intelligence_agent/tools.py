import yfinance as yf
import numpy as np
import logging
from google.adk.tools import google_search

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_fundamentals(ticker: str) -> str:
    """Fetches financial fundamentals for a given ticker using yfinance."""
    logger.info(f"get_fundamentals called for: {ticker}")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key metrics with error handling
        revenue_growth = info.get('revenueGrowth', 'N/A')
        operating_margins = info.get('operatingMargins', 'N/A')
        total_cash = info.get('totalCash', 'N/A')
        total_debt = info.get('totalDebt', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        
        # Format the data
        data = (
            f"Market Cap: {market_cap}\n"
            f"Revenue Growth: {revenue_growth}\n"
            f"Operating Margins: {operating_margins}\n"
            f"Total Cash: {total_cash}\n"
            f"Total Debt: {total_debt}\n"
            f"P/E Ratio: {pe_ratio}"
        )
    except Exception as e:
        data = f"Error fetching data: {str(e)}"
        
    logger.info(f"get_fundamentals returning: {data}")
    return data

def get_outlook(ticker: str, days: int = 30, sims: int = 5000) -> str:
    """
    Monte-Carlo experimental outlook using log-return simulation.

    Returns:
        A textual forecast containing:
        - probability of positive return
        - expected return
        - expected volatility
        - Sharpe ratio
        - qualitative classification
    """
    logger.info(f"get_outlook called for: {ticker}")

    try:
        # Download prices
        data = yf.download(ticker, period="3y", auto_adjust=True, progress=False)

        # Validate download
        if data is None or data.empty:
            raise ValueError(f"No price data found for {ticker}")

        close_prices = data["Close"].dropna()

        if close_prices.empty:
            raise ValueError("Close price series is empty")

        if len(close_prices) < 60:
            raise ValueError("Not enough historical data for simulation")

        # Daily log returns
        log_returns = np.log(close_prices / close_prices.shift(1)).dropna()

        if log_returns.empty:
            raise ValueError("Log returns are empty")

        # Convert to SAFE SCALARS
        # mu = float(log_returns.mean()) # commented to remove warnings, used for fool proofing
        # sigma = float(log_returns.std())
        # last_price = float(close_prices.iloc[-1])
        mu = log_returns.mean().item() # might break, if it does return to the above code.
        sigma = log_returns.std().item()
        last_price = close_prices.iloc[-1].item() if hasattr(close_prices.iloc[-1], "item") else float(close_prices.iloc[-1])


        if np.isnan(mu) or np.isnan(sigma):
            raise ValueError("mu or sigma is NaN (invalid)")

        if sigma == 0:
            raise ValueError("Standard deviation is zero (flat price series)")

        # Monte-Carlo simulation
        noise_matrix = np.random.normal(mu, sigma, size=(sims, days))
        price_paths = last_price * np.exp(noise_matrix.cumsum(axis=1))
        final_prices = price_paths[:, -1]

        final_returns = (final_prices - last_price) / last_price

        prob_up = float((final_returns > 0).mean())
        expected_return = float(final_returns.mean())
        volatility = float(final_returns.std())

        sharpe = float((mu / sigma) * np.sqrt(252)) if sigma > 0 else 0.0

        # Interpretation
        if prob_up > 0.65:
            outlook_label = "Bullish"
        elif prob_up > 0.55:
            outlook_label = "Moderately Bullish"
        elif prob_up > 0.45:
            outlook_label = "Neutral / Uncertain"
        else:
            outlook_label = "Bearish"

        summary = (
            f"Monte-Carlo Outlook for {ticker} ({days}-day horizon):\n"
            f"- Outlook: {outlook_label}\n"
            f"- Probability stock ends higher: {prob_up:.2%}\n"
            f"- Expected return: {expected_return:.2%}\n"
            f"- Expected volatility: {volatility:.2%}\n"
            f"- Sharpe ratio (est.): {sharpe:.2f}\n"
            f"*This forecast is experimental and based on Monte-Carlo simulation.*"
        )

    except Exception as e:
        summary = f"Error generating outlook: {str(e)}"

    logger.info(f"get_outlook returning: {summary}")
    return summary

def parse_sec_filing(ticker: str) -> str:
    """Parses the latest SEC filing for risks (Mock)."""
    logger.info(f"parse_sec_filing called for: {ticker}")
    # Mock data for MVP
    data = f"Latest 10-K for {ticker} highlights risks in: Supply chain disruptions, Antitrust litigation, and Foreign exchange fluctuations."
    logger.info(f"parse_sec_filing returning: {data}")
    return data

# Used used now but may use in future to analys sentiments based on social media sites
# def score_sentiment(text: str) -> str:
#     """Scores the sentiment of a given text (Mock)."""
#     logger.info(f"score_sentiment called.")
#     # Mock logic
#     score = 75
#     label = "Positive"
#     return f"Sentiment Score: {score} ({label})"
