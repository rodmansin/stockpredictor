import streamlit as st
from datetime import date
import yfinance as yf

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