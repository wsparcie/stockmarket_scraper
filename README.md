# Stock Market Data Scraper

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.29.0-green.svg)](https://www.selenium.dev/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2.3-red.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-6.0.1-orange.svg)](https://plotly.com/)
[![Status](https://img.shields.io/badge/Status-Alpha-yellow.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-May%202025-brightgreen.svg)](https://github.com/yourusername/stockmarket_scraper)

A simple Python-based web scraper that extracts comprehensive stock market data from Yahoo Finance and presents it in both .csv format and interactive HTML formats.

## Features in Detail

### Data Collection
- **Stock Summary**: Key statistics and quick overview
- **Company Overview**: Detailed company information
- **Latest News**: Recent company updates and articles
- **Financial Statistics**: Comprehensive financial metrics
- **Financial Statements**: Quarterly reports
- **Analyst Insights**: Market analysis and recommendations
- **Major & Institutional Holders**: Ownership information
- **Executive Information**: Management details
- **Historical Price Data**: Daily statistics
- **Historical Price Data**: Latest OHLC Chart

### Data Export Features
- **.csv Format Export**:
  - Organized spreadsheets
  - Multiple data sheets
  - Formatted tables
  
- **Interactive Web Interface**:
  - Dark theme UI
  - Mobile-responsive design
  - OHLC charts
  - Data tables
  - News integration

### Technical Features
- **Error Handling**:
  - Network issue management
  - Automatic retry system
  - Detailed error logging
  - Graceful data fallbacks

## Prerequisites

- Python 3.x
- Chrome Browser
- Required Python packages:
  ```
  selenium>=4.29.0
  pandas>=2.2.3
  plotly>=6.0.1
  ```

## Installation and Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Chrome WebDriver if not already present

## Usage

1. Configure stock tickers in `utils.py`:
   ```python
   tickers = ["TSLA", "INTC", "NVDA", "MSFT", "AAPL"]
   ```

2. Run the scraper:
   ```bash
   python main.py
   ```

3. Access your data:
   - .csv files: Generated per ticker
   - Web Interface: `http://localhost:x`
   - Raw HTML: Check `exported_data` directory

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This tool is for educational purposes only. Please comply with Yahoo Finance's terms of service when using this scraper.
