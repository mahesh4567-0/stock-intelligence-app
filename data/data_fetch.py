import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol="INFY.NS", period="1y"):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)

    if df.empty:
        raise ValueError(f"No data found for {symbol}")

    df.reset_index(inplace=True)
    return df

def clean_data(df):
    # Ensure Date column exists
    if 'Date' not in df.columns:
        raise KeyError("Date column not found")

    # Convert Date format
    df['Date'] = pd.to_datetime(df['Date'])

    # Remove duplicate rows
    df = df.drop_duplicates(subset=['Date'])

    # Sort by Date (rolling calculations)
    df = df.sort_values(by='Date')

    # Handle missing values
    df = df.ffill().dropna()

    return df

def add_metrics(df):
    df = df[df['Open'] != 0]

    df['Daily Return'] = (df['Close'] - df['Open']) / df['Open']

    df['MA_7'] = df['Close'].rolling(window=7, min_periods=1).mean()

    df['52W High'] = df['High'].rolling(window=252, min_periods=1).max()
    df['52W Low'] = df['Low'].rolling(window=252, min_periods=1).min()

    # Improved Volatility
    df['Volatility'] = df['Daily Return'].rolling(window=7, min_periods=2).std()
    df['Volatility'] = df['Volatility'].fillna(0)

    # Round only numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].round(4)

    return df

def save_data(df, symbol):
    # Save cleaned data
    filename = f"data/{symbol}_clean.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def process_stock(symbol):
    df = fetch_stock_data(symbol)
    df = clean_data(df)
    df = add_metrics(df)
    # Save file
    save_data(df, symbol)

    return df


if __name__ == "__main__":
    df = process_stock("INFY.NS")

    print(df.head())
    print(df.tail())