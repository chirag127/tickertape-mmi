import requests
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# Configuration
API_URL = "https://api.tickertape.in/mmi/now"
DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
CHART_FILE = "mmi_chart.png"
README_FILE = "README.md"

# Headers and Cookies from the user request
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "accept-version": "8.14.0",
    "dnt": "1",
    "origin": "https://www.tickertape.in",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}

COOKIES = {
    "AMP_d9d4ec74fa": "JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjIwZGExNDExZS02MTk1LTQ5OTAtOGIzYy03MGEwNjNmYmMwMWElMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzcxMjU0NjgxNTEyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc3MTI1NTY0MTI1NiUyQyUyMmxhc3RFdmVudElkJTIyJTNBNDI3JTdE"
}

def fetch_mmi_data():
    """Fetches the current MMI data from Ticker Tape API."""
    try:
        response = requests.get(API_URL, headers=HEADERS, cookies=COOKIES, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data["data"]
        else:
            print(f"API returned success=False: {data}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_mood_label(mmi_value):
    """Returns the mood label based on MMI value."""
    # MMI Zones:
    # Extreme Fear: < 30
    # Fear: 30 - 50
    # Greed: 50 - 70
    # Extreme Greed: > 70
    # (Approximate values based on common knowledge of MMI, adjusting if strict mapping needed)
    if mmi_value < 30:
        return "Extreme Fear"
    elif mmi_value < 50:
        return "Fear"
    elif mmi_value < 70:
        return "Greed"
    else:
        return "Extreme Greed"

def update_history(current_data):
    """Updates the history.json file with the new data point."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            print("Error reading history.json, starting with empty list.")

    # Extract relevant data
    # The API returns 'date' in the 'daily' array or 'date' field.
    # We use the 'date' from the data object which seems to be the update time.
    timestamp = current_data.get("date")
    value = current_data.get("currentValue")

    # Check if we already have this timestamp to avoid duplicates (optional but good)
    # Simple check: if last entry has same timestamp, skip or update.
    # The user wants hourly runs, so exact timestamp might differ slightly if it's capture time vs data time.
    # "date": "2026-02-16T14:20:00.086Z" <- this looks like data update time.
    # If the API doesn't update, we might get duplicate entries for the same data time.
    # Let's append anyway, or check the last entry's "date" field from the data.

    new_entry = {
        "timestamp": timestamp,
        "value": value,
        "mood": get_mood_label(value),
        "raw_data": { # Optional: store some other fields if useful
            "nifty": current_data.get("nifty"),
            "fma": current_data.get("fma"),
            "sma": current_data.get("sma")
        }
    }

    # Avoid duplicate data points based on timestamp from source
    if history and history[-1]["timestamp"] == timestamp:
        print("Data for this timestamp already exists. Skipping append.")
    else:
        history.append(new_entry)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
        print(f"Appended new data point: {value} ({new_entry['mood']}) at {timestamp}")

    return history

def generate_chart(history):
    """Generates a line chart for the last 180 days with Nifty overlay."""
    if not history:
        print("No history to plot.")
        return

    # Create DataFrame
    data_list = []
    for entry in history:
        timestamp = entry.get('timestamp')
        mmi_val = entry.get('value')

        # Extract Nifty value safely
        nifty_val = None
        if 'raw_data' in entry and 'nifty' in entry['raw_data']:
            nifty_val = entry['raw_data']['nifty']

        data_list.append({
            'timestamp': timestamp,
            'mmi': mmi_val,
            'nifty': nifty_val
        })

    df = pd.DataFrame(data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filter last 180 days (6 months)
    cutoff_date = pd.Timestamp.now(tz=df['timestamp'].dt.tz) - pd.Timedelta(days=180)
    df = df[df['timestamp'] > cutoff_date]

    if df.empty:
        print("No data in the last 180 days to plot.")
        return

    # Sort by date to ensure line plot is correct
    df = df.sort_values('timestamp')

    # Create figure and primary axis (MMI)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot MMI on ax1 (Left Axis)
    color = 'purple'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('MMI Value', color=color)
    line1, = ax1.plot(df['timestamp'], df['mmi'], marker='o', linestyle='-', color=color, markersize=4, label='MMI')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, 100)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Add colored zones background to ax1
    ax1.axhspan(0, 30, color='green', alpha=0.1, label='Extreme Fear')
    ax1.axhspan(30, 50, color='lime', alpha=0.1, label='Fear')
    ax1.axhspan(50, 70, color='orange', alpha=0.1, label='Greed')
    ax1.axhspan(70, 100, color='red', alpha=0.1, label='Extreme Greed')

    # Create secondary axis (Nifty) sharing the same x-axis
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Nifty Index', color=color)
    # Filter out None values for Nifty plotting
    mask = df['nifty'].notna()
    line2, = ax2.plot(df.loc[mask, 'timestamp'], df.loc[mask, 'nifty'], linestyle='--', color=color, alpha=0.7, label='Nifty')
    ax2.tick_params(axis='y', labelcolor=color)

    # Combine legends
    # We want legends from both axes.
    # Use lines from ax1 (only the MMI line, ignoring zones for cleaner legend?)
    # or just let matplotlib handle it.
    # To mimic previous simple legend + zones, we can just add a custom legend or handle it simply.

    # Simple combined legend
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.title("Market Mood Index (MMI) vs Nifty - Last 6 Months")

    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"Chart saved to {CHART_FILE}")
    plt.close()

def update_readme(latest_entry):
    """Updates the README.md with the latest MMI value and chart."""
    if not latest_entry:
        return

    mmi_value = latest_entry['value']
    mood = latest_entry['mood']
    timestamp = latest_entry['timestamp']

    # Convert timestamp to readable format
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        readable_time = dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        readable_time = timestamp

    content = f"""# Ticker Tape MMI Git Scraper

![Ticker Tape MMI Logo](logo.png)

A daily/hourly scraper for the Ticker Tape Market Mood Index (MMI).
This repository automatically fetches the MMI value, stores the history, and generates a chart.

## Latest MMI Value

**{mmi_value:.2f}** - **{mood}**
<small>Last Updated: {readable_time}</small>

## MMI Trend (Last 30 Days)

![MMI Chart](mmi_chart.png)

## Data

The historical data is available in [data/history.json](data/history.json).

### Zones Reference
- **Extreme Fear:** < 30
- **Fear:** 30 - 50
- **Greed:** 50 - 70
- **Extreme Greed:** > 70

## API Access

You can access the historical data via GitHub Pages:
[https://chirag127.github.io/tickertape-mmi/data/history.json](https://chirag127.github.io/tickertape-mmi/data/history.json)

Raw JSON File:
[https://raw.githubusercontent.com/chirag127/tickertape-mmi/main/data/history.json](https://raw.githubusercontent.com/chirag127/tickertape-mmi/main/data/history.json)
"""

    with open(README_FILE, "w") as f:
        f.write(content)
    print("README.md updated.")

def main():
    print("Starting MMI Scraper...")
    data = fetch_mmi_data()
    if data:
        history = update_history(data)
        generate_chart(history)
        if history:
            update_readme(history[-1])
    else:
        print("Failed to fetch data, skipping update.")

if __name__ == "__main__":
    main()
