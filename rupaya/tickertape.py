import requests
from bs4 import BeautifulSoup
import pandas as pd
from rupaya_utils import extract_num, parse_num

def get_stock_price(tt_name):
    res = requests.get("https://www.tickertape.in/stocks/{}".format(tt_name))
    soup = BeautifulSoup(res.content, "html.parser")
    qb_div = soup.find("div", {"class":"quote-box-root"})
    current_price = qb_div.find("span", {"class":"current-price"}).text
    return extract_num(current_price)

def get_financial_df(tt_name, stmt_type):
    res = requests.get(
        "https://www.tickertape.in/stocks/{}/financials?statement={}&view=normal".format(
            tt_name,
            stmt_type
        )
    )
    soup = BeautifulSoup(res.content, "html.parser")
    fin_div = soup.find("div", {"data-statement-type":"{}".format(stmt_type)})
    left_col = fin_div.find("div", {"class":"text-left"})
    left_divs = left_col.find_all("div", {"class":"field-label"})
    
    data_labels = ["Financial Year"]
    for div in left_divs:
        data_labels.append(div.text)
        
    right_divs = fin_div.find_all("div", {"class":"text-right"})
    values = []
    for div in right_divs:
        cells = div.find_all("div", {"class":"cell"})
        col_vals = []
        for cell in cells:
            val = cell.text.replace("—", "0.0")
            col_vals.append(parse_num(val))
        values.append(col_vals)
    
    fin_df = pd.DataFrame(values, columns=data_labels)
    return fin_df

def get_income_statement(tt_name):
    return get_financial_df(tt_name, "income")

def get_balance_sheet(tt_name):
    return get_financial_df(tt_name, "balancesheet")

def get_cashflow_statement(tt_name):
    return get_financial_df(tt_name, "cashflow")

def get_market_cap(stock_price, bs_df):
    total_shares = extract_num(
            bs_df["Total Common Shares Outstanding"].tolist()[-1]) + extract_num(
            bs_df["Total Preferred Shares Outstanding"][-1:].tolist()[-1])
    return stock_price * total_shares
    
def get_top_companies():
    res = requests.get("https://www.tickertape.in/stocks?filter=top")
    soup = BeautifulSoup(res.content, "html.parser")
    
    page_div = soup.find("div", {"class":"page"})
    lis = page_div.find_all("li")
    
    top_companies = []
    for li in lis:
        name = li.text
        tt_name = li.find("a").get("href").split("/stocks/")[-1]
        tt_link = "www.tickertape.in/stocks/{}".format(tt_name)
        top_companies.append([name, tt_name, tt_link])
        top_companies = sorted(top_companies, key=lambda x : x[0])
    return top_companies

def  get_all_companies():
    res = requests.get("https://www.tickertape.in/stocks")
    soup = BeautifulSoup(res.content, "html.parser")
    
    links_div = soup.find("div", {"class":"link-list"})
    alinks = links_div.find_all("a")
    
    all_companies = []
    temp_names = []
    for alink in alinks:
        ares = requests.get("https://www.tickertape.in/stocks?filter={}".format(alink.text))
        asoup = BeautifulSoup(ares.content, "html.parser")
        
        page_div = asoup.find("div", {"class":"page"})
        lis = page_div.find_all("li")
    
        for li in lis:
            name = li.text
            tt_name = li.find("a").get("href").split("/stocks/")[-1]
            tt_link = "www.tickertape.in/stocks/{}".format(tt_name)
            if not name in temp_names:
                temp_names.append(name)
                all_companies.append([name, tt_name, tt_link])
    all_companies = sorted(all_companies, key=lambda x : x[0])
    return all_companies