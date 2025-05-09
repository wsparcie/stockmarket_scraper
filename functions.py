import os
import time
import pandas as pd
import plotly.graph_objects as go
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor

def wait(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def getgainerslosers():
    def extractdata(url):
        driver = webdriver.Chrome()
        try:
            driver.get(url)
            try:
                rejectionbutton = driver.find_element(By.XPATH, '//button[@class="btn secondary reject-all"]')
                action = ActionChains(driver)
                action.click(on_element=rejectionbutton)
                action.perform()
                time.sleep(2)
            except NoSuchElementException:
                print("Reject button not found.")
            
            headers = []
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table[data-testid='table-container']")))
            headeritems = table.find_elements(By.CSS_SELECTOR, "th")
            for header in headeritems:
                headertext = header.text.strip()
                if headertext:
                    headers.append(headertext)
                else:
                    headers.append('Chart')
            rowsdata = []
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in rows:
                rowdata = []
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                for cell in cells:
                    streamers = cell.find_elements(By.TAG_NAME, "fin-streamer")
                    if streamers:
                        cell_text = streamers[0].text.strip()
                    else:
                        cell_text = cell.text.strip()
                    rowdata.append(cell_text)
                if rowdata:
                    if len(rowdata) > len(headers):
                        rowdata = rowdata[:len(headers)]
                    elif len(rowdata) < len(headers):
                        rowdata.extend([''] * (len(headers) - len(rowdata)))
                    rowsdata.append(rowdata)
            df = pd.DataFrame(rowsdata, columns=headers)
            return df
        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return pd.DataFrame()
        finally:
            driver.quit()

    urls = {
        "gainers": "https://finance.yahoo.com/gainers",
        "losers": "https://finance.yahoo.com/losers"
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(extractdata, urls.values()))
    gainersdf, losersdf = results
    print('\n_____GAINERS_____')
    print(gainersdf)
    print('\n_____LOSERS_____')
    print(losersdf)
    return gainersdf, losersdf

def getsummary(driver, ticker):
    print('\n_____SUMMARY_____')
    try:
        section = wait(driver, (By.CSS_SELECTOR, "[data-testid='quote-statistics']"))
        items = section.find_elements(By.TAG_NAME, "li")
        summary = {}
        for item in items:
            labelelement = item.find_element(By.CLASS_NAME, "label")
            valueelement = item.find_element(By.CLASS_NAME, "value")
            label = labelelement.get_attribute("title").strip()
            try:
                valuefin = valueelement.find_element(By.TAG_NAME, "fin-streamer")
                value = valuefin.get_attribute("data-value").strip()
            except NoSuchElementException:
                value = valueelement.text
            if value != "--":
                summary[label] = value
                
        summarydf = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
        print(summarydf)
        summarydf.to_html(f"./exported_data/{ticker}_summary.html", index=False, classes="table table-dark table-striped", border=0)
    except Exception as e:
        print(f"Error in getsummary for {ticker}: {e}")

    print('\n_____OVERVIEW_____')
    try:
        expandbutton = driver.find_element(By.CLASS_NAME, 'headerBtn')
        action = ActionChains(driver)
        action.click(on_element=expandbutton)
        action.perform()
        time.sleep(2)

        description = driver.find_element(By.CSS_SELECTOR, "div.description p").text
        websiteurl = driver.find_element(By.CSS_SELECTOR, "div.description a.subtle-link").get_attribute("href")
        infosection = driver.find_elements(By.CSS_SELECTOR, "div.right div.infoSection")
        companyinfo = {}
        for section in infosection:
            title = section.find_element(By.CSS_SELECTOR, "h3").text.strip()
            try:
                value = section.find_element(By.CSS_SELECTOR, "p a").text
                companyinfo[title] = value
            except NoSuchElementException:
                value = section.find_element(By.CSS_SELECTOR, "p").get_attribute("title")
                companyinfo[title] = value

        overviewdf = pd.DataFrame(list(companyinfo.items()), columns=['Metric', 'Value'])
        infodf = pd.DataFrame(list(companyinfo.items()), columns=['Metric', 'Value'])
        print(infodf, description, overviewdf, websiteurl)
        return summarydf, infodf, overviewdf, description, websiteurl
    except Exception as e:
        print(f"Error in getoverview for {ticker}: {e}")

def getstatistics(driver, ticker):
    print('\n_____STATISTICS_____')
    try:
        valuation = {}
        profitability = {}
        balance = {}
        valuationtable = driver.find_element(By.XPATH, "//section[@data-testid='valuation-measures']")
        valuationitems = valuationtable.find_elements(By.TAG_NAME, "li")
        for item in valuationitems:
            label = item.find_element(By.CLASS_NAME, "label").text.strip()
            value = item.find_element(By.CLASS_NAME, "value").text.strip()
            valuation[label] = value
    
        financialtable = driver.find_element(By.XPATH, "//section[@data-testid='financial-highlights']")
        profitabilitydiv = financialtable.find_elements(By.CLASS_NAME, "highlights")[0]
        profitabilityitems = profitabilitydiv.find_elements(By.TAG_NAME, "li")
        for item in profitabilityitems:
            label = item.find_element(By.CLASS_NAME, "label").text.strip()
            value = item.find_element(By.CLASS_NAME, "value").text.strip()
            profitability[label] = value
        balancediv = financialtable.find_elements(By.CLASS_NAME, "highlights")[1]
        balanceitems = balancediv.find_elements(By.TAG_NAME, "li")
        for item in balanceitems:
            label = item.find_element(By.CLASS_NAME, "label").text.strip()
            value = item.find_element(By.CLASS_NAME, "value").text.strip()
            balance[label] = value
        
        dfvaluation = pd.DataFrame(list(valuation.items()), columns=['Metric', 'Value'])
        dfprofitability = pd.DataFrame(list(profitability.items()), columns=['Metric', 'Value'])
        dfbalance = pd.DataFrame(list(balance.items()), columns=['Metric', 'Value'])
        print(dfvaluation, dfprofitability, dfbalance)
        htmlcontent = f"""
        {dfvaluation.to_html(index=False, classes="table table-dark table-striped", border=0)}
        {dfprofitability.to_html(index=False, classes="table table-dark table-striped", border=0)}
        {dfbalance.to_html(index=False, classes="table table-dark table-striped", border=0)}
        """
        with open(f"./exported_data/{ticker}_statistics.html", "w") as file:
            file.write(htmlcontent)
        return dfvaluation, dfprofitability, dfbalance
    except Exception as e:
        print(f"Error in getstatistics for {ticker}: {e}")

def getnews(driver, ticker):
    print('\n_____NEWS_____')
    try:
        button = wait(driver, (By.XPATH, '/html/body/div[2]/main/section/section/aside/section/nav/ul/li[2]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.stream-item")))
        headlines = []
        publishers = []
        publishtimes = []
        links = []
        imageurls = []
        table = driver.find_elements(By.CSS_SELECTOR, "li.stream-item.story-item")
        for item in table:
            linkelements = item.find_elements(By.TAG_NAME, "a")
            headlinelink = None
            for link in linkelements:
                if "titles" in link.get_attribute("class"):
                    headlinelink = link
                    break
            if headlinelink:
                headline = headlinelink.text.strip()
                link = headlinelink.get_attribute("href")
                try:
                    imageelement = item.find_element(By.TAG_NAME, "img")
                    imageurl = imageelement.get_attribute("data-src") or imageelement.get_attribute("src")
                    imageurls.append(imageurl)
                except:
                    imageurls.append("")
                try:
                    footer = item.find_element(By.CLASS_NAME, "publishing")
                    footertext = footer.text.strip()
                    if "•" in footertext:
                        parts = footertext.split("•")
                        publisher = parts[0].strip()
                        publishtime = parts[1].strip()
                    else:
                        publisher = footertext
                        publishtime = "--"
                    headlines.append(headline)
                    publishers.append(publisher)
                    publishtimes.append(publishtime)
                    links.append(link)
                except:
                    print("Couldn't find publisher information")
        # Build news items HTML
        newsitems = ""
        for headline, publisher, publishtime, link, imageurl in zip(headlines, publishers, publishtimes, links, imageurls):
            newsitems += f'''
                <div class="news-card">
                    <div class="card">
                        <div class="row g-0">
                            <div class="col-md-3">
                                <div class="img-container">
                                    <img src="{imageurl}" class="square-img" alt="News Image">
                                </div>
                            </div>
                            <div class="col-md-9">
                                <div class="card-body">
                                    <h5 class="card-title">{headline}</h5>
                                    <p class="card-text"><small class="text-secondary">{publisher} - {publishtime}</small></p>
                                    <a href="{link}" class="btn btn-primary" target="_blank">Read More</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            '''
        # Load style if present
        style = ''
        if os.path.exists('style.css'):
            with open('style.css', 'r') as f:
                style = f'<style>\n{f.read()}\n</style>'
        # Load template
        with open('news_template.html', 'r') as tpl:
            template = tpl.read()
        html_content = template.replace('{{ticker}}', ticker)
        html_content = html_content.replace('{{newsitems}}', newsitems)
        html_content = html_content.replace('{{style}}', style)
        with open(f"./exported_data/{ticker}_news.html", "w") as file:
            file.write(html_content)
        newsdata = {
                'Headline': headlines,
                'Publisher': publishers,
                'Time': publishtimes,
                'Link': links,
                'Image URL': imageurls
            }
        df = pd.DataFrame(newsdata)
        print(df)
        return df
    except Exception as e:
        print(f"Error in getnews for {ticker}: {e}")

def getholders(driver, ticker):
    print('\n_____HOLDERS_____')
    try:
        button = wait(driver, (By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[11]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr.majorHolders")))

        major = []
        institutional = []
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.majorHolders")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                value = cells[0].text.strip()
                description = cells[1].text.strip()
                major.append({"Value": value, "Description": description})
        headers = driver.find_elements(By.CSS_SELECTOR, "thead th.yf-idy1mk")
        headertexts = [header.text.strip() for header in headers]
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.yf-idy1mk")
        institutional = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td.yf-idy1mk")
            rowdata = [cell.text.strip() for cell in cells]
            institutional.append(rowdata)
        if institutional and len(institutional[0]) != len(headertexts):
            headertexts = headertexts[:len(institutional[0])] if len(headertexts) > len(institutional[0]) else headertexts
            headertexts = headertexts + [f"Column{i+1}" for i in range(len(headertexts), len(institutional[0]))]

        dfmajor = pd.DataFrame(major, columns=["Value", "Description"])
        dfinstitutional = pd.DataFrame(institutional, columns=headertexts)
        print(dfmajor, dfinstitutional)
        htmlcontent = f"""
            {dfmajor.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dfinstitutional.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
        """
        with open(f"./exported_data/{ticker}_holders.html", "w") as file:
            file.write(htmlcontent)
        return dfmajor, dfinstitutional
    except Exception as e:
        print(f"Error in getholders for {ticker}: {e}")

def getexecutives(driver, ticker):
    print('\n_____EXECUTIVES_____')
    try:
        button = wait(driver, (By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[7]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
        
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        executives = []
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                executives.append(row_data)
            except StaleElementReferenceException:
                print("Stale element encountered. Retrying...")
                rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                continue

        df = pd.DataFrame(executives, columns=["Name", "Title", "Pay", "Exercised", "Year Born"])
        print(df)
        df.to_html(f"./exported_data/{ticker}_executives.html", index=False, classes="table table-dark table-striped", border=0)
        return df
    except Exception as e:
        print(f"Error in getexecutives for {ticker}: {e}")

def getfinancials(driver, ticker):
    print('\n_____FINANCIALS_____')
    try:
        button = wait(driver, (By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[8]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tab-quarterly')))
        quarterlybutton = driver.find_element(By.ID, 'tab-quarterly')
        quarterlybutton.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tableHeader div.column")))

        headers = ["Breakdown"]
        headerelements = driver.find_elements(By.CSS_SELECTOR, "div.tableHeader div.column")
        for header in headerelements:
            text = header.text.strip()
            if text and text != "Breakdown":
                headers.append(text)
        data = []
        rows = driver.find_elements(By.CSS_SELECTOR, "div.tableBody div.row")
        for row in rows:
            rowdata = []
            titleelement = row.find_element(By.CSS_SELECTOR, "div.rowTitle")
            title = titleelement.text.strip()
            rowdata.append(title)
            valueelements = row.find_elements(By.CSS_SELECTOR, "div.column:not(.sticky)")
            for valueelement in valueelements:
                value = valueelement.text.strip()
                rowdata.append(value)
            data.append(rowdata)
        maxcolumns = max(len(row) for row in data)
        if len(headers) < maxcolumns:
            headers.extend([f"Column {i}" for i in range(len(headers), maxcolumns)])

        df = pd.DataFrame(data, columns=headers[:maxcolumns])
        print(df)
        df.to_html(f"./exported_data/{ticker}_financials.html", index=False, classes="table table-dark table-striped", border=0)
        return df
    except Exception as e:
        print(f"Error in getfinancials for {ticker}: {e}")

def getanalysis(driver, ticker):
    print('\n_____ANALYSIS_____')
    try:
        button = wait(driver, (By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[9]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//section[@data-testid='earningsEstimate']")))

        def extractdata(sectionxpath):
            section = driver.find_element(By.XPATH, sectionxpath)
            headerrow = section.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr")
            headers = [header.text for header in headerrow.find_elements(By.TAG_NAME, "th")]
            datarows = section.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
            data = {}
            for row in datarows:
                cells = row.find_elements(By.TAG_NAME, "td")
                rowlabel = cells[0].text.strip()
                rowvalues = [cell.text.strip() for cell in cells[1:]]
                data[rowlabel] = rowvalues

            df = pd.DataFrame.from_dict(data, orient='index', columns=headers[1:])
            print(df)
            return df

        dfearnings = extractdata("//section[@data-testid='earningsEstimate']")
        dfrevenue = extractdata("//section[@data-testid='revenueEstimate']")
        dfhistory = extractdata("//section[@data-testid='earningsHistory']")
        dftrends = extractdata("//section[@data-testid='epsTrend']")
        dfrevisions = extractdata("//section[@data-testid='epsRevisions']")
        dfgrowth = extractdata("//section[@data-testid='growthEstimate']")
        htmlcontent = f"""
            {dfearnings.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dfrevenue.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dfhistory.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dftrends.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dfrevisions.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
            {dfgrowth.to_html(index=False, classes="table table-dark table-striped", border=0)}\n\n
        """
        with open(f'./exported_data/{ticker}_analysis.html', 'w') as file:
            file.write(htmlcontent)
        return dfearnings, dfrevenue, dfhistory, dftrends, dfrevisions, dfgrowth
    except Exception as e:
        print(f"Error in getanalysis: {e}")

def gethistory(driver, ticker):
    print('\n_____HISTORY_____')
    try:
        button = wait(driver, (By.XPATH, '//*[@id="nimbus-app"]/section/section/aside/section/nav/ul/li[6]/a'))
        button.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        retrycount = 5
        while retrycount > 0:
            try:
                tables = driver.find_elements(By.TAG_NAME, "table")
                table = tables[0]
                headers = []
                thead = table.find_elements(By.TAG_NAME, "thead")
                if thead:
                    headerrow = thead[0].find_elements(By.TAG_NAME, "tr")
                    if headerrow:
                        headercols = headerrow[0].find_elements(By.TAG_NAME, "th")
                        for col in headercols:
                            headers.append(col.text.strip())
                data = []
                tbody = table.find_elements(By.TAG_NAME, "tbody")
                if tbody:
                    rows = tbody[0].find_elements(By.TAG_NAME, "tr")
                else:
                    rows = table.find_elements(By.TAG_NAME, "tr")[1:]
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) != len(headers) and len(headers) > 0:
                        continue
                    rowdata = []
                    for col in cols:
                        rowdata.append(col.text.strip())
                    if rowdata:
                        data.append(rowdata)
                break
            except StaleElementReferenceException:
                retrycount -= 1
                if retrycount == 0:
                    raise

        df = pd.DataFrame(data, columns=headers)
        print(df)
        df.to_html(f"./exported_data/{ticker}_history.html", index=False, classes="table table-dark table-striped", border=0)
        
        try:
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            pricecolumns = [col for col in df.columns if any(priceterm in col.lower() for priceterm in ['price', 'close', 'open', 'high', 'low', 'adj'])]
            if pricecolumns and 'Date' in df.columns:
                ohlccolumns = ['Open', 'High', 'Low', 'Close']
                if all(col in df.columns for col in ohlccolumns):
                    figurecandle = go.Figure(data=[go.Candlestick(
                        x=df['Date'],
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='OHLC'
                    )])
                    figurecandle.update_layout(
                        title=f'{ticker} OHLC Chart',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        template='plotly_white'
                    )
                    figurecandle.write_html(f"./exported_data/{ticker}_ohlcchart.html")
        except Exception as e:
            print(f"Error generating chart for {ticker}: {e}")
        return df
    except Exception as e:
        print(f"Error in gethistory for {ticker}: {e}")
