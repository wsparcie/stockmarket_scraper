import os
import time
import pandas as pd
import plotly.graph_objects as go
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor

def wait(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def getgainerslosers(driver):
    try:
        def extractdata(url_type, url):
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="btn secondary reject-all"]')))
                try:
                    rejectionbutton = driver.find_element(By.XPATH, '//button[@class="btn secondary reject-all"]')
                    action = ActionChains(driver)
                    action.click(on_element=rejectionbutton)
                    action.perform()
                    time.sleep(2)
                except NoSuchElementException:
                    print("Reject button not found.")
            except:
                print("No cookie consent popup found.")
            table = None
            for _ in range(3):
                try:
                    table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.yf-1570k0a"))
                    )
                    break
                except:
                    time.sleep(2)
                    continue
            if not table:
                raise Exception("Table not found after retries")
            data = []
            headers = []
            for _ in range(3):
                try:
                    header_elements = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "thead tr th"))
                    )
                    for header in header_elements:
                        header_text = WebDriverWait(header, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".colCont"))
                        ).text.strip()
                        if header_text:
                            headers.append(header_text)
                    break
                except:
                    time.sleep(1)
                    continue
            for _ in range(3):
                try:
                    rows = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr.row"))
                    )
                    for row in rows:
                        try:
                            row_data = {}
                            symbol_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:first-child .symbol"))
                            )
                            row_data['Symbol'] = symbol_element.text.strip()
                            name_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(2) div"))
                            )
                            row_data['Name'] = name_element.get_attribute("title") or name_element.text.strip()
                            price_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(4) fin-streamer"))
                            )
                            row_data['Price'] = price_element.get_attribute("data-value")
                            change_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(5) fin-streamer"))
                            )
                            row_data['Change'] = change_element.get_attribute("data-value")
                            change_pct_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(6) fin-streamer"))
                            )
                            row_data['Change %'] = change_pct_element.get_attribute("data-value")
                            volume_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(7) fin-streamer"))
                            )
                            row_data['Volume'] = volume_element.text.strip()
                            avg_vol_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(8)"))
                            )
                            row_data['Avg Vol (3m)'] = avg_vol_element.text.strip()
                            market_cap_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(9) fin-streamer"))
                            )
                            row_data['Market Cap'] = market_cap_element.text.strip()
                            pe_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(10)"))
                            )
                            row_data['P/E (TTM)'] = pe_element.text.strip()
                            wk52_change_element = WebDriverWait(row, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(11) fin-streamer"))
                            )
                            row_data['52 Wk Change %'] = wk52_change_element.get_attribute("data-value")
                            data.append(row_data)
                        except Exception as row_error:
                            print(f"Error processing row: {row_error}")
                            continue
                    break
                except Exception as rows_error:
                    print(f"Error getting rows: {rows_error}")
                    time.sleep(1)
                    continue
            df = pd.DataFrame(data)
            numeric_columns = ['Price', 'Change', 'Change %', '52 Wk Change %']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            if 'Change %' in df.columns:
                df['Change %'] = df['Change %'].round(2)
            if '52 Wk Change %' in df.columns:
                df['52 Wk Change %'] = df['52 Wk Change %'].round(2)
            os.makedirs('./exported_data', exist_ok=True)
            df.to_html(f"./exported_data/{url_type}.html", 
                    index=False, 
                    classes="table table-dark table-striped", 
                    border=0)
            return url_type, df

        urls = {
            "gainers": "https://finance.yahoo.com/gainers",
            "losers": "https://finance.yahoo.com/losers"
        }
        results = {}
        for url_type, url in urls.items():
            try:
                type_result, df = extractdata(url_type, url)
                results[type_result] = df
            except Exception as e:
                print(f"Error processing {url_type}: {e}")
                results[url_type] = None
        gainersdf = results.get("gainers")
        losersdf = results.get("losers")
        if gainersdf is not None:
            print('\n_____GAINERS_____')
            print(gainersdf)
        if losersdf is not None:
            print('\n_____LOSERS_____')
            print(losersdf)
        return gainersdf, losersdf
    except Exception as e:
        print(f"Error in getgainerslosers: {e}")
        return None, None

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
                # Try multiple date format parsing approaches
                try:
                    # First try automatic parsing
                    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
                except (ValueError, TypeError):
                    try:
                        # Try specific format
                        df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
                    except (ValueError, TypeError):
                        # If all else fails, try forcing parsing
                        df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
            
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
