import streamlit as st
from datetime import date
import yfinance as yf

from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

st.title('The Magnificent 7 Stock Predictor')

stocks = {
    'Meta (META)': 'META',
    'Apple (AAPL)': 'AAPL',
    'Google (GOOG)': 'GOOG',
    'Amazon (AMZN)': 'AMZN',
    'Microsoft (MSFT)': 'MSFT',
    'Nvidia (NVDA)': 'NVDA',
    'Tesla (TSLA)': 'TSLA'
}

selected_stock_label = st.selectbox(
    'Select MAG7 stock:',
    list(stocks.keys())
)
selected_stock = stocks[selected_stock_label]

START = "2000-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
forecast_years = st.slider('Years from now:', 1, 5)
forecast_days = forecast_years * 365

@st.cache_data
def get_historical_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.columns = data.columns.get_level_values(0)  # Flatten MultiIndex
    data.reset_index(inplace=True)
    return data

@st.cache_data
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info

data = get_historical_data(selected_stock)
info = get_stock_info(selected_stock)

latest_price = data.iloc[-1]["Close"] if not data.empty else "N/A"

fundamentals = {
    "Company Name": info.get("shortName", "N/A"),
    "Sector": info.get("sector", "N/A"),
    "Industry": info.get("industry", "N/A"),
    "Current Stock Price ($)": f"{latest_price:.2f}" if latest_price != "N/A" else "N/A",
    "Market Cap ($)": f"{info.get('marketCap', 'N/A'):,}",
    "P/E Ratio (TTM)": info.get("trailingPE", "N/A"),
    "Dividend Yield": info.get("dividendYield", "N/A"),
    "52-Week High ($)": f"{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}",
    "52-Week Low ($)": f"{info.get('fiftyTwoWeekLow', 'N/A'):.2f}",
    "Beta (Volatility)": info.get("beta", "N/A"),
}

st.subheader(f"{selected_stock_label} Fundamentals")
df_fundamentals = pd.DataFrame(fundamentals.items())
st.markdown(df_fundamentals.to_html(index=False, header=False), unsafe_allow_html=True)

def plot_historical_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="Stock Open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Stock Close"))
    fig.layout.update(title_text=f'{selected_stock_label} Stock Price', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_historical_data()

forecast_data = data[['Date', 'Close']].copy()
forecast_data.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

forecast_data.dropna(subset=['y'], inplace=True)
forecast_data['y'] = pd.to_numeric(forecast_data['y'], errors='coerce')

prophet_model = Prophet()
prophet_model.fit(forecast_data)

future_dates = prophet_model.make_future_dataframe(periods=forecast_days)
forecast_result = prophet_model.predict(future_dates)

st.subheader(f'Forecast Plot for {forecast_years} Years')
forecast_plot = plot_plotly(prophet_model, forecast_result)
st.plotly_chart(forecast_plot)
