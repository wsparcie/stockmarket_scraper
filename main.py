import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
from functions import getsummary, getstatistics, getnews, getholders, getexecutives, getfinancials, getanalysis, gethistory
from utils import exportcsv, generateticketindex, generateindex, servehtml
from utils import tickers

os.makedirs('./exported_data', exist_ok=True)

def wait(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

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
        generateticketindex(ticker, summary, info, description, websiteurl)

    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
    finally:
        driver.quit()

with ThreadPoolExecutor(max_workers=len(tickers)) as executor:
    executor.map(parallelprocess, tickers)

generateindex()
servehtml()
