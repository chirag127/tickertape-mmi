# Ticker Tape MMI Git Scraper

A daily/hourly scraper for the Ticker Tape Market Mood Index (MMI).
This repository automatically fetches the MMI value, stores the history, and generates a chart.

## Latest MMI Value

**52.23** - **Greed**
<small>Last Updated: 2026-02-16 14:20 UTC</small>

## MMI Trend (Last 30 Days)

![MMI Chart](mmi_chart.png)

## Data

The historical data is available in [data/history.json](data/history.json).

### Zones Reference
- **Extreme Fear:** < 30
- **Fear:** 30 - 50
- **Greed:** 50 - 70
- **Extreme Greed:** > 70
