import argparse
import os
from bs4 import BeautifulSoup
import requests
import re


def parse_ebay(ebay_link, page_num=1):
    r = requests.get(ebay_link)
    price_title = {}
    next_page_link = ''
    for _ in range(page_num):
        if next_page_link:
            r = requests.get(next_page_link)
        data = r.text
        soup = BeautifulSoup(data)
        for elem in soup.find_all('li', attrs={'class': 'sresult lvresult clearfix li shic'}):
            title = elem.find('h3', attrs={'class': 'lvtitle'}).text.encode('utf-8')
            price = elem.find('li', attrs={'class': 'lvprice prc'}).text
            link = elem.find('h3', attrs={'class': 'lvtitle'}).find('a').get('href')
            # print link
            price = re.findall("\d+\.\d+", price)
            price_link = []
            if len(price) != 1:
                price_link.append(price[1])
                price_link.append(link)
            else:
                price_link.append(price[0])
                price_link.append(link)
            price_title[title] = price_link
        next_page_link = soup.find('a', attrs={'class': 'gspr next'}).get('href')
    return price_title


def parse_amazon(titles_prices):
    if not os.path.exists('./output/'):
        os.makedirs('./output/')
    else:
        open('./output/results.txt', 'w')
    for title, e_price in titles_prices.iteritems():
        title = title.strip()
        r = requests.get('http://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords='+title.replace("\"", ""))
        data = r.text
        soup = BeautifulSoup(data)
        if soup.find('li', attrs={'class': 's-result-item celwidget'}) is not None:
            if soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}) is not None:
                a_link = soup.find('a', attrs={'class': 'a-link-normal s-access-detail-page  a-text-normal'}).get('href')
                a_price = soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}).text
                a_price = re.findall("\d+\.\d+", a_price)
                print a_price[0]
                print e_price[0]
                if float(a_price[0]) > float(e_price[0]):
                    with open('./output/results.txt', 'a') as outfile:
                        outfile.write("Ebay price: {}, {}, Amazon price: {}, product name: {}, {}\n\n".format(str(e_price[0]), str(e_price[1]), str(a_price[0]), str(title), a_link))
                    # print a_price

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run parser')
    parser.add_argument("--ebay_link", dest="ebay_link", required=True,
                        help="Summary page of Ebay with buy it now and new lots ", metavar="")
    parser.add_argument("--page_num", dest="page_num", required=True,
                        help="Page numbers to parse", metavar="")
    args = parser.parse_args()
    ebay_results = parse_ebay(args.ebay_link, page_num=int(args.page_num))
    parse_amazon(ebay_results)