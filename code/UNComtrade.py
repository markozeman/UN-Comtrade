import json
import requests


class UNComtrade:

    def years(self):
        years = [year for year in range(1962, 2017)]
        years.append('all')
        return years

    def reporters(self):
        return read_json('../code/data/reporters.json')

    def partners(self):
        return read_json('../code/data/partners.json')

    def commodities_HS(self):
        return read_json('../code/data/commodities_HS.json')

    def commodities_ST(self):
        return read_json('../code/data/commodities_ST.json')

    def commodities_BEC(self):
        return read_json('../code/data/commodities_BEC.json')

    def services(self):
        return read_json('../code/data/services.json')

    def trade_flows(self):
        return read_json('../code/data/trade_flows.json')

    # partners, time_period, trade_flows,
    def call_api (self, reporters, partners, time_period, trade_flows, type='C', freq='A', classification='HS',
                  commodities='AG2 - All 2-digit HS commodities', max_values=10, head='H', format='json'):

        # check if optional parameters are ok
        if (not check_optional_parameters(type, freq, classification, max_values, head, format)):
            return 1

        if (type == 'S'):
            classification = 'EB02'
            commodities = check_if_commodities_default(commodities, 'TOTAL - Total EBOPS 2002 Services')

        if (classification == 'ST'):
            commodities = check_if_commodities_default(commodities, 'AG2 - All 2-digit SITC commodities')
        elif (classification == 'BEC'):
            commodities = check_if_commodities_default(commodities, 'AG2 - All 2-digit BEC commodities')

        r = check_form(reporters, 'r')
        p = check_form(partners, 'p')
        ps = check_form(time_period, 'ps')
        rg = check_form(trade_flows, 'rg')
        cc = check_form(commodities, 'cc', classified=classification, freq=freq)

        if (r is not None and p is not None and ps is not None and rg is not None and cc is not None):     # če so vsi veljavni
            # največ en od prvih treh je lahko all
            if ((r == 'all' and p == 'all') or (r == 'all' and ps == 'all') or (p == 'all' and ps == 'all')):
                print("Only one of reporters, partners and time_period can be set to all.")
                return 2
            else:
                base_URL = 'http://comtrade.un.org/api/get?'
                URL_parameters = 'type='+type+'&freq='+freq+'&r='+r+'&p='+p+'&ps='+ps+'&px='+classification+'&rg='\
                                 +rg+'&cc='+cc+'&fmt='+format+'&head='+head+'&max='+str(max_values)
                URL = base_URL + URL_parameters

                req = requests.get(URL)

                if (format == 'json'):
                    print(req)
                    req_json = req.json()

                    print(URL)
                    print('Message:', req_json['validation']['message'])
                    print('Total values:', req_json['validation']['count']['value'])
                    print('Returned values:',
                          req_json['validation']['count']['value'] if max_values > req_json['validation']['count'][
                              'value'] else max_values)
                    print('API call took ' + "{0:.2f}".format(
                        req_json['validation']['datasetTimer']['durationSeconds']) + ' seconds')

                    for record in req_json['dataset']:
                        print(record)

                    return req_json['dataset']

                elif (format == 'csv'):
                    req_csv = req.content
                    print(req_csv)
                    return req_csv
        else:
            print('\nOne of the parameters is not valid.\n')
            return 3



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


def check_if_commodities_default(comm, new):
    if (comm == 'AG2 - All 2-digit HS commodities'):
        return new
    return comm


def check_optional_parameters(t, fr, c, mv, h, f):
    ok = True
    if (t != 'C' and t != 'S'):
        print('Type parameter is invalid.')
        ok = False
    if (fr != 'A' and fr != 'M'):
        print('Frequency parameter is invalid.')
        ok = False
    if (c != 'HS' and c != 'ST' and c != 'BEC' and c != 'EB02'):
        print('Classification parameter is invalid.')
        ok = False
    if (isinstance(mv, str) or (isinstance(mv, int) and mv < 0 or mv > 100000)):
        print('Max values parameter is invalid.')
        ok = False
    if (h != 'H' and h != 'M'):
        print('Head parameter is invalid.')
        ok = False
    if (f != 'json' and f != 'csv'):
        print('Format parameter is invalid.')
        ok = False
    return ok


def check_form(parameter, p, classified='', freq=''):
    need_id = True

    if (p == 'r'):
        dict = json2object('../code/data/reporters.json')
    elif (p == 'p'):
        dict = json2object('../code/data/partners.json')
    elif (p == 'rg'):
        dict = json2object('../code/data/trade_flows.json')
    elif (p == 'cc'):
        if (classified == 'HS'):
            dict = json2object('../code/data/commodities_HS.json')
        elif (classified == 'ST'):
            dict = json2object('../code/data/commodities_ST.json')
        elif (classified == 'BEC'):
            dict = json2object('../code/data/commodities_BEC.json')
        elif (classified == 'EB02'):
            dict = json2object('../code/data/services.json')
        else:
            print('Wrong classification.')
            return None
    elif (p == 'ps'):
        if (freq == 'A'):
            if (isinstance(parameter, int) and (parameter < 1962 or parameter > 2050)):
                print('Year is not correct')
                return None
            elif (isinstance(parameter, list)):
                if (parameter[0] != 'all'):
                    for y in parameter:
                        if (y < 1962 or y > 2050):
                            print('Year is not correct')
                            return None
            elif (isinstance(parameter, str)):
                if (parameter != 'all'):
                    print('Year is not correct')
                    return None
        need_id = False
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
        if (len(parameter) > 20 and p == 'cc'):
            print("You can choose max 20 commodities.")
            return None
        if (len(parameter) > 5 and p != 'cc'):
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
    r = unc.call_api('Norway', ['Finland', 'Denmark'], [2014, 2015], 'All', max_values=1000)
    # print(r)


# print_all()




