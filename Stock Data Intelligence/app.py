from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Enable CORS (frontend can access backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder where CSV files exist
DATA_PATH = "data"

#  Companies list
COMPANIES = ["INFY.NS", "TCS.NS", "RELIANCE.NS"]


#  Helper function to load data
def load_stock(symbol: str):
    file_path = os.path.join(DATA_PATH, f"{symbol}_clean.csv")

    print("Looking for file:", file_path)  # 🔥 Debug log (important for Render)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} data not found. Expected: {file_path}"
        )

    df = pd.read_csv(file_path)

    # Convert Date properly
    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)

    return df


# Root (for testing)
@app.get("/")
def home():
    return {"message": "Stock API is running "}


# Get all companies
@app.get("/companies")
def get_companies():
    return {"companies": COMPANIES}


#  Get last 30 days stock data
@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    df = load_stock(symbol)

    df = df.tail(30)

    return df.to_dict(orient="records")


# Get summary
@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    df = load_stock(symbol)

    summary = {
        "symbol": symbol,
        "52W High": float(df["52W High"].max()),
        "52W Low": float(df["52W Low"].min()),
        "Average Close": float(df["Close"].mean())
    }

    return summary


# Compare two stocks
@app.get("/compare")
def compare_stocks(symbol1: str, symbol2: str):
    df1 = load_stock(symbol1)
    df2 = load_stock(symbol2)

    return {
        symbol1: {
            "avg_close": float(df1["Close"].mean()),
            "latest_price": float(df1["Close"].iloc[-1])
        },
        symbol2: {
            "avg_close": float(df2["Close"].mean()),
            "latest_price": float(df2["Close"].iloc[-1])
        }
    }