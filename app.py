import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Set layout and title
st.set_page_config(layout="wide", page_title="Portfolio Risk Analyzer")
st.title("AI-Based Portfolio Risk Analyzer")

# Stock options
stock_options = {
    "TCS": "TCS.NS",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Reliance": "RELIANCE.NS"
}

# User selects stocks
selected_stocks = st.multiselect("Select Stocks", list(stock_options.keys()), default=["TCS", "Apple"])

# Time period selection
time_period = st.selectbox("Select Time Period", ['1 Week', '6 Months', '1 Year'])
period_days = {'1 Week': 7, '6 Months': 182, '1 Year': 365}
days = period_days[time_period]

# Fetching and calculating
@st.cache_data
def fetch_data(tickers, days):
    data = yf.download([stock_options[t] for t in tickers], period=f"{days}d")["Close"]
    returns = data.pct_change().dropna()
    return data, returns

if selected_stocks:
    data, returns = fetch_data(selected_stocks, days)

    weights = [1 / len(selected_stocks)] * len(selected_stocks)
    portfolio_return = (returns * weights).sum(axis=1)

    def risk_metrics(returns):
        volatility = returns.std()
        sharpe_ratio = returns.mean() / volatility
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        return volatility, sharpe_ratio, max_drawdown

    vol, sharpe, dd = risk_metrics(portfolio_return)

    st.subheader("Risk Metrics")
    metrics_df = pd.DataFrame({
        "Volatility": [vol],
        "Sharpe Ratio": [sharpe],
        "Max Drawdown": [dd]
    }, index=[time_period])

    st.dataframe(metrics_df.style.background_gradient(cmap="coolwarm"))

    st.subheader("Portfolio Return Over Time")
    fig, ax = plt.subplots()
    portfolio_return.cumsum().plot(ax=ax, linewidth=2)
    ax.set_title("Cumulative Portfolio Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Returns")
    st.pyplot(fig)

else:
    st.warning("Please select at least one stock.")
