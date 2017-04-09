import datetime
import json
import requests


class UNComtrade:

    def years(self):
        years = [year for year in range(1962, 2017)]
        years.append('all')
        return years

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

    # partners, time_period, trade_flows,
    def call_api (self, reporters, partners, time_period, trade_flows, type='C', freq='A', classification='HS', commodities='AG2', max_values=500, head='H', format='json'):
        r = check_form(reporters)
        p = check_form(partners)
        ps = check_form(time_period)
        rg = check_form(trade_flows)

        if (r is not None and p is not None and ps is not None and rg is not None):
            # print(r,p,ps,rg)

            # TODO - največ en all, razen rg je vseeno lahko

            pass






def read_json(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return [country['text'] for country in data['results']]


def json2object(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        data_object = {}
        for country in data['results']:
            data_object[country['text']] = country['id']
        return data_object


def check_form(parameter):
    s = ''
    if (isinstance(parameter, str) or isinstance(parameter, int)):
        s = str(parameter)
    elif (isinstance(parameter, list)):
        if (len(parameter) > 5):
            print("You can choose max 5 values.")
            return None
        for i in range(len(parameter)):
            s += str(parameter[i])

            if (str(parameter[i]).lower()[:3] == 'all'):
                s = 'all'
                break
            elif (str(parameter[i]).lower()[:5] == 'total'):
                s = 'total'

            if (i < len(parameter) - 1):
                s += '%2C'
    else:
        print("Parameter must be a string or a list.")
        return None

    return s




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
    unc.call_api(['Albania', 'all'], 'Croatia', ['all', 2010, 2012, 2013], ['Alll cdsubufs', 'import'])



print_all()

# req = requests.get('https://comtrade.un.org/api/get?ps=all&p=0&px=HS&r=4&rg=all&cc=AG4&max=1000&head=M')
# print(req.json())


