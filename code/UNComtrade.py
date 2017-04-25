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
    def call_api (self, reporters, partners, time_period, trade_flows, type='C', freq='A', classification='HS',
                  commodities='AG2 - All 2-digit HS commodities', max_values=10, head='H', format='json'):
        r = check_form(reporters, 'r')
        p = check_form(partners, 'p')
        ps = check_form(time_period, 'ps')
        rg = check_form(trade_flows, 'rg')
        cc = check_form(commodities, 'cc')

        if (r is not None and p is not None and ps is not None and rg is not None and cc is not None):     # če so vsi veljavni
            # print(r,p,ps,rg)

            # največ en od prvih treh je lahko all
            if ((r == 'all' and p == 'all') or (r == 'all' and ps == 'all') or (p == 'all' and ps == 'all')):
                print("Only one of reporters, partners and time_period can be set to all")
            else:
                base_URL = 'http://comtrade.un.org/api/get?'

                # TODO
                # commodities?


                URL_parameters = 'type='+type+'&freq='+freq+'&r='+r+'&p='+p+'&ps='+ps+'&px='+classification+'&rg='\
                                 +rg+'&cc='+cc+'&fmt='+format+'&head='+head+'&max='+str(max_values)

                URL = base_URL + URL_parameters

                print(URL)

                req = requests.get(URL)
                req_json = req.json()

                print('Message:', req_json['validation']['message'])
                print('Total values:', req_json['validation']['count']['value'])
                print('Returned values:', req_json['validation']['count']['value'] if max_values > req_json['validation']['count']['value'] else max_values)
                print('API call took ' + str(req_json['validation']['datasetTimer']['durationSeconds']) + ' seconds')

                for record in req_json['dataset']:
                    print(record)

        else:
            print('\nOne of the parameters is not valid.\n')



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


def check_form(parameter, p):
    need_id = True

    if (p == 'r'):
        dict = json2object('data/reporters.json')
    elif (p == 'p'):
        dict = json2object('data/partners.json')
    elif (p == 'rg'):
        dict = json2object('data/trade_flows.json')
    elif (p == 'cc'):
        dict = json2object('data/commodities_HS.json')
    else:
        need_id = False

    s = ''
    if (isinstance(parameter, str)):
        if (need_id and parameter != 'all'):
            if (parameter in dict):
                s = dict[str(parameter)]
            else:
                print('\nParameter is not valid (not in the dictionary).\n')
                return None
        else:
            s = str(parameter)
    elif (isinstance(parameter, int)):
        s = str(parameter)
    elif (isinstance(parameter, list)):
        if (len(parameter) > 5):
            print("You can choose max 5 values.")
            return None
        for i in range(len(parameter)):
            if (need_id and parameter[i] != 'all' and parameter[i] in dict):
                s += str(dict[str(parameter[i])])
            else:
                s += str(parameter[i])

            if (str(parameter[i]).lower()[:3] == 'all'):
                s = 'all'
                break
            elif (str(parameter[i]).lower()[:5] == 'total'):
                s = 'total'

            if (i < len(parameter) - 1):
                s += '%2C'
    else:
        print("Parameter must be a string, integer or a list.")
        return None

    return s


def print_all():
    unc = UNComtrade()
    # print(unc.years())
    # print(unc.reporters())
    # print(unc.partners())
    # print(unc.commodities_HS())
    # print(unc.commodities_ST())
    # print(unc.commodities_BEC())
    # print(unc.services())
    # print(unc.trade_flows())
    unc.call_api('All', 'Slovenia', 2006, 'Export', commodities='TOTAL - Total of all HS commodities')


print_all()




