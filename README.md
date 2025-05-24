# Stock Market Data Scraper

A simple Python-based web scraper that extracts comprehensive stock market data from Yahoo Finance and presents it in both Excel and interactive HTML formats.

## Features

- **Comprehensive Data Collection**:
  - Stock Summary
  - Company Overview
  - Financial Statistics
  - Latest News
  - Major & Institutional Holders
  - Executive Information
  - Financial Statements
  - Analyst Insights
  - Historical Price Data with OHLC Charts

- **Data Export**:
  - .csv Format Summary
  - Interactive HTML Pages
  - OHLC (Open-High-Low-Close) Charts
  - Mobile-Responsive Dark Theme UI

## Prerequisites

- Python 3.x
- Chrome Browser
- Required Python packages:
  ```
  selenium
  pandas
  plotly
  ```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/stockmarket_scraper.git
   cd stockmarket_scraper
   ```

2. Install required packages:
   ```bash
   pip install selenium pandas plotly
   ```

3. Install Chrome WebDriver if you haven't already.

## Usage

1. Modify the tickers list in `utils.py` to include your desired stock symbols:
   ```python
   tickers = ["TSLA", "INTC", "NVDA", "MSFT", "AAPL"]
   ```

2. Run the scraper:
   ```bash
   python main.py
   ```

3. Access the data:
   - Excel files will be created for each ticker
   - Interactive HTML pages will be served at `http://localhost:8000`
   - Raw HTML files will be stored in the `exported_data` directory

## Project Structure

- `main.py`: Main script that orchestrates the scraping process
- `functions.py`: Contains all scraping functions for different data sections
- `utils.py`: Utility functions for data export and HTML generation
- `style.css`: Styling for the HTML output
- HTML templates:
  - `main_index_template.html`
  - `ticker_index_template.html`
  - `news_template.html`

## Features in Detail

### Data Collection
- **Summary**: Key statistics and quick overview
- **Statistics**: Detailed financial ratios and metrics
- **News**: Latest company news with images
- **Holders**: Major shareholders and institutional investors
- **Executives**: Company management information
- **Financials**: Quarterly financial statements
- **Analysis**: Earnings estimates and analyst recommendations
- **History**: Historical price data with interactive charts

### Data Presentation
- **Excel Export**: Organized spreadsheets with multiple sheets
- **Interactive Web Interface**: 
  - Dark theme
  - Mobile-responsive design
  - Easy navigation between stocks
  - Interactive OHLC charts
  - Organized data tables
  - Direct links to news articles

## Error Handling

- Robust error handling for network issues
- Automatic retry mechanism for failed requests
- Detailed error logging
- Graceful degradation when data is unavailable

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This tool is for educational purposes only. Make sure to comply with Yahoo Finance's terms of service when using this scraper.
