import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
import numpy as np
import requests

# ---------- Mapping Full Indian Company Names to NSE Tickers ----------
indian_stock_map = {
    "reliance industries": "RELIANCE.NS",
    "tata consultancy services": "TCS.NS",
    "infosys": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "state bank of india": "SBIN.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "larsen & toubro": "LT.NS",
    "asian paints": "ASIANPAINT.NS"
}

# ---------- Technical Indicators ----------
def add_technical_indicators(df):
    length = len(df)
    window_20 = min(20, length)
    window_50 = min(50, length)
    rsi_period = min(14, length)

    df['SMA_20'] = df['Close'].rolling(window=window_20).mean()
    df['SMA_50'] = df['Close'].rolling(window=window_50).mean()

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2    
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    return df

# ---------- Prediction ----------
def add_predictions(df, days=10):
    df = df.dropna().copy()
    if len(df) < 10:
        return [], []
    df.loc[:, 'Days'] = np.arange(len(df))
    X = df[['Days']]
    y = df['Close']
    model = LinearRegression().fit(X, y)

    future_days = np.arange(len(df), len(df) + days)
    future_df = pd.DataFrame(future_days, columns=['Days'])
    future_prices = model.predict(future_df)

    future_dates = pd.date_range(df.index[-1], periods=days + 1, freq='B')[1:]
    return future_dates, future_prices

# ---------- Fetch and Plot ----------
def fetch_and_plot():
    input_name = stock_entry.get().strip().lower()
    ticker = indian_stock_map.get(input_name)

    if not ticker:
        messagebox.showwarning("Input Error", f"Company '{input_name}' not recognized.\nPlease select a valid Indian company.")
        return

    period = period_var.get()

    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty:
            messagebox.showinfo("No Data", f"No data found for '{ticker}'.")
            return

        if len(data) < 10:
            messagebox.showinfo("Insufficient Data", "Not enough data to analyze. Try selecting a longer period.")
            return

        data = add_technical_indicators(data)

        fig.clear()
        ax1 = fig.add_subplot(311)
        ax2 = fig.add_subplot(312)
        ax3 = fig.add_subplot(313)

        # Price and SMA
        ax1.plot(data.index, data['Close'], label='Close', color='blue')
        ax1.plot(data.index, data['SMA_20'], label='SMA 20', linestyle='--')
        ax1.plot(data.index, data['SMA_50'], label='SMA 50', linestyle='--')

        # Predictions
        future_dates, future_prices = add_predictions(data)
        if len(future_dates) > 0:
            ax1.plot(future_dates, future_prices, label='Prediction', linestyle='dashdot', color='magenta')

        ax1.set_title(f"{input_name.title()} Price + SMA + Prediction")
        ax1.legend()
        ax1.grid(True)

        # RSI
        ax2.plot(data.index, data['RSI'], label='RSI', color='green')
        ax2.axhline(70, color='red', linestyle='--')
        ax2.axhline(30, color='blue', linestyle='--')
        ax2.set_title("RSI")
        ax2.legend()
        ax2.grid(True)

        # MACD
        ax3.plot(data.index, data['MACD'], label='MACD', color='black')
        ax3.plot(data.index, data['Signal'], label='Signal', linestyle='--', color='orange')
        ax3.set_title("MACD")
        ax3.legend()
        ax3.grid(True)

        canvas.draw()

        show_news(input_name)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------- News API ----------
def show_news(company_name):
    try:
        api_key = "your_api_key"  # Replace with your key
        query = company_name
        url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}&language=en&category=business"

        response = requests.get(url)
        articles = response.json().get('results', [])

        news_box.delete("1.0", tk.END)
        if not articles:
            news_box.insert(tk.END, "No news found.\n")
            return

        news_box.insert(tk.END, f"Latest News for {company_name.title()}:\n\n")
        for article in articles[:5]:
            title = article['title']
            link = article['link']
            news_box.insert(tk.END, f"• {title}\n  {link}\n\n")

    except Exception as e:
        news_box.insert(tk.END, f"News fetch error: {e}\n")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("📊 AI-Powered Stock Market Analyzer (India)")
root.geometry("1024x800")

frame = ttk.Frame(root, padding=10)
frame.pack(side=tk.TOP, fill=tk.X)

ttk.Label(frame, text="Company Name:").pack(side=tk.LEFT)

# Combobox for company selection
company_names = list(indian_stock_map.keys())
stock_entry = ttk.Combobox(frame, values=company_names, width=40)
stock_entry.pack(side=tk.LEFT, padx=5)

ttk.Label(frame, text="Period:").pack(side=tk.LEFT)
period_var = tk.StringVar(value='6mo')
ttk.Combobox(frame, textvariable=period_var, values=['1mo', '3mo', '6mo', '1y', '2y', '5y'], width=8).pack(side=tk.LEFT, padx=5)

ttk.Button(frame, text="Analyze", command=fetch_and_plot).pack(side=tk.LEFT, padx=10)

fig = Figure(figsize=(10, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

news_frame = ttk.LabelFrame(root, text="📰 Financial News", padding=10)
news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
news_box = tk.Text(news_frame, height=10, wrap=tk.WORD)
news_box.pack(fill=tk.BOTH, expand=True)

root.mainloop()
