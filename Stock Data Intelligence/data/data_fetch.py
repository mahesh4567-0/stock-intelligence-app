import yfinance as yf
import pandas as pd
import os


# Ensure data folder exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


# Fetch stock data
def fetch_stock_data(symbol="INFY.NS", period="1y"):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)

        if df.empty:
            raise ValueError(f"No data found for {symbol}")

        df.reset_index(inplace=True)

        return df

    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")


# Clean data
def clean_data(df):
    if 'Date' not in df.columns:
        raise KeyError("Date column not found")

    # Convert Date properly (remove timezone issues)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

    # Remove duplicates
    df = df.drop_duplicates(subset=['Date'])

    # Sort before rolling
    df = df.sort_values(by='Date')

    # Handle missing values
    df = df.replace([float("inf"), float("-inf")], None)
    df = df.ffill().dropna()

    return df


# Add technical metrics
def add_metrics(df):
    df = df[df['Open'] != 0]

    # Daily Return
    df['Daily Return'] = (df['Close'] - df['Open']) / df['Open']

    # Moving Average
    df['MA_7'] = df['Close'].rolling(window=7, min_periods=1).mean()

    # 52 Week High/Low
    df['52W High'] = df['High'].rolling(window=252, min_periods=1).max()
    df['52W Low'] = df['Low'].rolling(window=252, min_periods=1).min()

    # Volatility
    df['Volatility'] = df['Daily Return'].rolling(window=7, min_periods=2).std()
    df['Volatility'] = df['Volatility'].fillna(0)

    # Round numeric columns only
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].round(4)

    return df


# Save CSV
def save_data(df, symbol):
    file_path = os.path.join(DATA_DIR, f"{symbol}_clean.csv")

    df.to_csv(file_path, index=False)

    print(f" Data saved to {file_path}")


# Main processing function
def process_stock(symbol):
    try:
        df = fetch_stock_data(symbol)
        df = clean_data(df)
        df = add_metrics(df)

        save_data(df, symbol)

        return df

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")
        raise


# Run manually (for testing)
if __name__ == "__main__":
    symbol = "INFY.NS"

    df = process_stock(symbol)

    print("\nHEAD:\n", df.head())
    print("\nTAIL:\n", df.tail())