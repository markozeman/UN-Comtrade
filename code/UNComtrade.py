import datetime
import json
import requests


class UNComtrade:

    def years(self):
        return [year for year in range(1962, 2017)]

    def reporters(self):
        return read_json('data/reporters.json')

    def partners(self):
        return read_json('data/partners.json')

    def commodities_HS(self):
        return read_json('data/commodities_HS.json')

    def commodities_ST(self):
        return read_json('data/commodities_ST.json')

    def commodities_BEC(self):
        return read_json('data/commodities_BEC.json')

    def services(self):
        return read_json('data/services.json')

    def trade_flows(self):
        return read_json('data/trade_flows.json')


def read_json(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return [country['text'] for country in data['results']]


def print_all():
    unc = UNComtrade()
    print(unc.years())
    print(unc.reporters())
    print(unc.partners())
    print(unc.commodities_HS())
    print(unc.commodities_ST())
    print(unc.commodities_BEC())
    print(unc.services())
    print(unc.trade_flows())




req = requests.get('https://comtrade.un.org/api/get?r=4&px=HS&ps=all&p=0&rg=all&cc=AG4&max=1000&head=M')
print(req.json())