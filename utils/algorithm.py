import pandas as pd
from prophet import Prophet


def predict(stock_data, days):
    df = pd.DataFrame(stock_data, columns=["ds", "y"])  # Convert to DataFrame

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)  # Forecast 'n' days ahead
    forecast = model.predict(future)

    future_week = forecast.tail(days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]   # Get only the next 'n' days

    future_data = [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "yhat": round(row["yhat"], 2),
            "yhat_lower": round(row["yhat_lower"], 2),
            "yhat_upper": round(row["yhat_upper"], 2),
        }
        for _, row in future_week.iterrows()
    ]

    return future_data
