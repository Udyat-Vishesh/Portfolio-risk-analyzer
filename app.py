import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date

# Title
st.title("AI-Based Portfolio Risk Analyzer")

# Custom stock search
user_input = st.text_input("Enter stock names (e.g., Tesla, Apple, TCS, Nifty, BTC)")

# Fetch ticker suggestions using yfinance
if user_input:
    search_result = yf.Ticker(user_input).info
    st.write(f"**Showing results for:** {search_result.get('longName', 'Unknown')} ({user_input.upper()})")
    selected_tickers = [user_input.upper()]
else:
    selected_tickers = []

# Custom date range selection
start_date = st.date_input("Select Start Date", date(2023, 1, 1))
end_date = st.date_input("Select End Date", date.today())

# Optional: Custom weights
use_custom_weights = st.checkbox("Use Custom Weights")
weights = []
if use_custom_weights and selected_tickers:
    for ticker in selected_tickers:
        w = st.number_input(f"Weight for {ticker} (in %)", min_value=0.0, max_value=100.0, value=100.0/len(selected_tickers))
        weights.append(w / 100)
    weights = np.array(weights)
    weights /= weights.sum()

# Fetch price data
if selected_tickers:
    price_data = yf.download(selected_tickers, start=start_date, end=end_date)['Adj Close']
    price_data = price_data.dropna()

    # Normalize for graph
    normalized = price_data / price_data.iloc[0] * 100

    # Portfolio returns
    daily_returns = price_data.pct_change().dropna()
    portfolio_returns = (daily_returns * weights).sum(axis=1) if use_custom_weights else daily_returns.mean(axis=1)

    # Risk Metrics
    avg_return = portfolio_returns.mean()
    std_dev = portfolio_returns.std()
    sharpe_ratio = avg_return / std_dev if std_dev != 0 else 0

    risk_metrics = pd.DataFrame({
        "Metric": ["Average Daily Return", "Standard Deviation", "Sharpe Ratio"],
        "Value": [avg_return, std_dev, sharpe_ratio]
    })

    st.subheader("Risk Metrics")
    st.dataframe(risk_metrics.style.format("{:.5f}").highlight_max(axis=0, color='lightgreen'))

    # Graph options
    st.subheader("Portfolio Graphs")
    graph_options = st.multiselect("Select Graphs to Display", ["Normalized Performance", "Portfolio Value Over Time", "Individual Stock Comparison"], default=["Normalized Performance"])

    if "Normalized Performance" in graph_options:
        fig1 = px.line(normalized, title="Normalized Stock Performance")
        st.plotly_chart(fig1)

    if "Portfolio Value Over Time" in graph_options:
        portfolio_value = (price_data * weights).sum(axis=1) if use_custom_weights else price_data.mean(axis=1)
        fig2 = px.line(x=portfolio_value.index, y=portfolio_value.values, labels={'x': 'Date', 'y': 'Portfolio Value'}, title="Portfolio Value")
        st.plotly_chart(fig2)

    if "Individual Stock Comparison" in graph_options:
        fig3 = px.line(price_data, title="Individual Stock Price Comparison")
        st.plotly_chart(fig3)

st.markdown("---")
st.caption("Built with love for finance and tech. Future AI analysis and reporting coming soon!")
