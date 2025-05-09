import os
import pandas as pd
from http.server import SimpleHTTPRequestHandler, HTTPServer
from main import tickers
from functions import getgainerslosers

def exportxlsx(ticker, data):
    try:
        with pd.ExcelWriter(f"./{ticker}_data.xlsx") as writer:
            for name, data in data.items():
                if isinstance(data, pd.DataFrame) and not data.empty:
                    data.to_excel(writer, sheet_name=name[:31], index=False)
    except Exception as e:
        print(f"Error exporting {ticker} to xlsx: {e}")


def generateticketindex(ticker, summary, info, description, websiteurl):
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

def generateindex():
    try:
        options = "\n".join([f'<option value="{t}_index.html">{t}</option>' for t in tickers])
        gainers, losers = getgainerslosers()
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
