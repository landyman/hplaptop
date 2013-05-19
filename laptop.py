__author__ = 'landyman'

import urllib2
import lxml.html

__LAPTOP_URL__ = "http://h71016.www7.hp.com/html/hpremarketing/daily.asp"

class Laptop(object):
    def __init__(self, part_number, condition, description, outlet_price, sale_price):
        self.part_number = part_number
        self.condition = condition
        self.description = description
        self.outlet_price = self.convertPrice(outlet_price)
        self.sale_price = self.convertPrice(sale_price)

    def convertPrice(self, price):
        if isinstance(price, float):
            return price
        if isinstance(price, str):
            if price.startswith('$'):
                return float(price[1:].replace(',',''))
            return float(price)
        return None

    def findMatch(self, features):
        if isinstance(features, str):
            features = [features]
        for feature in features:
            if self.description.find(feature) >= 0:
                return True
        return False

if __name__ == '__main__':
    dollars = 600.00
    while 1:
        new_dollars = raw_input("Please enter the maximum dollar amount. [$600] ")
        if new_dollars.strip() == "":
            break
        try:
            dollars = float(new_dollars.split('$')[0])
            break
        except Exception as ex:
            print "Please enter a valid dollar amount"
    features = ["FHD"]
    new_features = raw_input("Please enter any additional features to search for (Comma Separated). [FHD]")
    if new_features != "":
        features.extend([i.strip() for i in new_features.split(',')])

    print "Gathering today's laptop deals..."
    res = urllib2.urlopen(__LAPTOP_URL__)
    source = res.read()
    html = lxml.html.fromstring(source)
    table_rows = html.xpath('//table[@id="sortable_notebooks"]/tr[position()>1]')
    print "Searching through %d results..." % (len(table_rows))
    matched_items = []
    for row in table_rows:
        cells = row.xpath('./td')
        if len(cells) != 5:
            continue
        l = Laptop(cells[0].text_content(), cells[1].text_content(), cells[2].text_content(), cells[3].text_content(), cells[4].text_content())
        if l.findMatch(features):
            if l.outlet_price <= dollars or (l.sale_price is not None and l.sale_price < dollars):
                matched_items.append(l)
    print "Found %d results..." % (len(matched_items))
    matched_items.sort(key=lambda x: x.sale_price or x.outlet_price)
    max_len = max(map(lambda x: len(x.part_number), matched_items)) + 5
    for item in matched_items:
        price = item.outlet_price
        if item.sale_price is not None and item.sale_price < item.outlet_price:
            price = item.sale_price
        print "$%-10.2f%-*s%s" % (price, max_len, item.part_number, item.description)
    print "Done."

