import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
from functions import getgainerslosers, getsummary, getstatistics, getnews, getholders, getexecutives, getfinancials, getanalysis, gethistory

import pandas as pd
from http.server import SimpleHTTPRequestHandler, HTTPServer


tickers = [
    "TSLA", "INTC", "NVDA", "MSFT", "AAPL",
    ]

os.makedirs('./exported_data', exist_ok=True)

def wait(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def exportcsv(ticker, data):
    try:
        os.makedirs(f"./{ticker}_data", exist_ok=True)
        for name, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.to_csv(f"./{ticker}_data/{name}.csv", index=False)
    except Exception as e:
        print(f"Error exporting {ticker} to csv: {e}")

def generatetickerindex(ticker, summary, info, description, websiteurl):
    try:
        summaryhtml = summary.to_html(index=False, classes="table table-dark table-striped", border=0)
        infohtml = info.to_html(index=False, classes="table table-dark table-striped", border=0)
        with open('ticker_index_template.html', 'r') as tpl:
            template = tpl.read()
        style = ''
        if os.path.exists('style.css'):
            with open('style.css', 'r') as f:
                style = f'<style>\n{f.read()}\n</style>'
        html = template.replace('{{ticker}}', ticker)
        html = html.replace('{{summaryhtml}}', summaryhtml)
        html = html.replace('{{infohtml}}', infohtml)
        html = html.replace('{{description}}', description)
        html = html.replace('{{websiteurl}}', websiteurl)
        html = html.replace('{{style}}', style)
        with open(f'./exported_data/{ticker}_index.html', 'w') as file:
            file.write(html)
    except Exception as e:
        print(f"Error generating {ticker}_index.html: {e}")

def parallelprocess(ticker):
    driver = webdriver.Chrome()
    try:
        url = f'https://finance.yahoo.com/quote/{ticker}'
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="btn secondary reject-all"]')))
        try:
            rejectionbutton = driver.find_element(By.XPATH, '//button[@class="btn secondary reject-all"]')
            action = ActionChains(driver)
            action.click(on_element=rejectionbutton)
            action.perform()
            time.sleep(2)
        except NoSuchElementException:
            print(f"Reject button not found for ticker {ticker}.")

        summary, overview, info, description, websiteurl = getsummary(driver, ticker)
        valuation, profitability, balance = getstatistics(driver, ticker)
        news = getnews(driver, ticker)
        majorholders, institutionalholders = getholders(driver, ticker)
        executives = getexecutives(driver, ticker)
        financials = getfinancials(driver, ticker)
        earnings, revenue, earningshistory, trends, revisions, growth = getanalysis(driver, ticker)
        history = gethistory(driver, ticker)
        
        data = {
            "Overview": overview,
            "Valuation": valuation,
            "Profitability": profitability,
            "Balance": balance,
            "News": news,
            "Major Holders": majorholders,
            "Institutional Holders": institutionalholders,
            "Executives": executives,
            "Financials": financials,
            "Earnings Estimate": earnings,
            "Revenue Estimate": revenue,
            "Earnings History": earningshistory,
            "EPS Trend": trends,
            "EPS Revisions": revisions,
            "Growth Estimate": growth,
            "Price History": history,
        }

        exportcsv(ticker, data)
        generatetickerindex(ticker, summary, info, description, websiteurl)

    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
    finally:
        driver.quit()

with ThreadPoolExecutor(max_workers=len(tickers)) as executor:
    executor.map(parallelprocess, tickers)

def generateindex():
    driver = webdriver.Chrome()
    try:
        options = "\n".join([f'<option value="{t}_index.html">{t}</option>' for t in tickers])
        gainers, losers = getgainerslosers(driver)
        gainershtml = gainers.head(15).to_html(index=False, classes="table table-dark table-striped", border=0)
        losershtml = losers.head(15).to_html(index=False, classes="table table-dark table-striped", border=0)
        with open('main_index_template.html', 'r') as tpl:
            template = tpl.read()
        style = ''
        if os.path.exists('style.css'):
            with open('style.css', 'r') as f:
                style = f'<style>\n{f.read()}\n</style>'
        html = template.replace('{{options}}', options)
        html = html.replace('{{gainershtml}}', gainershtml)
        html = html.replace('{{losershtml}}', losershtml)
        html = html.replace('{{style}}', style)
        with open('./exported_data/index.html', 'w') as file:
            file.write(html)
    except Exception as e:
        print(f"Error generating main index.html: {e}")

def servehtml():
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/favicon.ico':
                self.send_response(204)
                self.end_headers()
                return
            return super().do_GET()

    os.chdir('./exported_data')
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving at http://localhost:8000")
    httpd.serve_forever()

generateindex()
servehtml()
