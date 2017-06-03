import os
import json
import requests
from math import ceil
from datetime import datetime, timedelta
import numpy as np

all_values = 0
first_call = True
last_call__time = ''

# import certifi
# import urllib3
# http = urllib3.PoolManager(
#      cert_reqs='CERT_REQUIRED',
#      ca_certs=certifi.where()
# )


class Tree:
    def __init__(self, number_of_calls, data_split):
        self.root = TreeNode()
        self.number_of_calls = number_of_calls
        self.d = data_split
        self.generate_tree(self.root, 0)
        self.make_API_calls(self.root)

    def generate_tree(self, node, level):
        # print('START')
        # print(level)
        # print('node path', node.path)
        if (level < 4):
            for i in range(self.number_of_calls[level]):
                # print('START FOR LOOP')
                # print(level, i, self.number_of_calls[level])
                child = TreeNode()
                node.children.append(child)
                node.path = node.path[:level]
                # print('node', node)
                # print('node path', node.path)
                # print('child path', child.path)
                child.path = node.path
                child.path.append(i)
                # print('child path after', child.path)
                # print('----------------------')
                level += 1
                self.generate_tree(child, level)
                level -= 1

    def make_API_calls(self, node):
        if (len(node.children) == 0):
            path = node.path

            un = UNComtrade()

            global first_call
            if (first_call):
                global last_call_time
                last_call_time = datetime.now()
                first_call = False
            else:
                while (datetime.now() - last_call_time < timedelta(seconds=1)):
                    pass
                last_call_time = datetime.now()

            res = un.call_api(self.d['reporters'][path[0]], self.d['partners'][path[1]], self.d['time_period'][path[2]], self.d['trade_flows'],
                              self.d['type'], self.d['freq'], self.d['classification'], self.d['commodities'][path[3]], self.d['max_values'],
                              self.d['head'], self.d['format'])
            node.data = res
            return

        for i in range(len(node.children)):
            child = node.children[i]
            self.make_API_calls(child)

        node.join_children_data()
        # print('\nNODE COMBINED DATA')
        # print(len(node.data))


class TreeNode:
    def __init__(self):
        self.data = []
        self.children = []  # TreeNodes
        self.path = []

    def join_children_data(self):
        # print('\nJOIN')
        for child in self.children:
            self.data += child.data
        # print(len(self.data))


class UNComtrade:

    def years(self):
        years = [year for year in range(2016, 1961, -1)]
        years.insert(0, 'All')
        return years

    def reporters(self):
        path = os.path.join(os.path.dirname(__file__), 'data/reporters.json')
        return read_json(path)

    def partners(self):
        path = os.path.join(os.path.dirname(__file__), 'data/partners.json')
        return read_json(path)

    def commodities_HS(self):
        path = os.path.join(os.path.dirname(__file__), 'data/commodities_HS.json')
        return read_json(path)

    def commodities_HS_all(self):
        path = os.path.join(os.path.dirname(__file__), 'data/commodities_HS_tree.json')
        return read_json_all(path)

    def commodities_ST(self):
        path = os.path.join(os.path.dirname(__file__), 'data/commodities_ST.json')
        return read_json(path)

    def commodities_BEC(self):
        path = os.path.join(os.path.dirname(__file__), 'data/commodities_BEC.json')
        return read_json(path)

    def services(self):
        path = os.path.join(os.path.dirname(__file__), 'data/services.json')
        return read_json(path)

    def services_all(self):
        path = os.path.join(os.path.dirname(__file__), 'data/services_tree.json')
        return read_json_all(path)

    def trade_flows(self):
        path = os.path.join(os.path.dirname(__file__), 'data/trade_flows.json')
        return read_json(path)

    def call_api (self, reporters, partners, time_period, trade_flows, type='C', freq='A', classification='HS',
                  commodities='AG2 - All 2-digit HS commodities', max_values=10, head='H', format='json'):

        # print_all_parameters(reporters, partners, time_period, trade_flows, type, freq, classification, commodities, max_values, head, format)

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
            # največ eden od prvih treh je lahko all
            if ((r == 'all' and p == 'all') or (r == 'all' and ps == 'all') or (p == 'all' and ps == 'all')):
                print("Only one of reporters, partners and time_period can be set to all.")
                return 2
            else:
                base_URL = 'http://comtrade.un.org/api/get?'
                URL_parameters = 'type='+type+'&freq='+freq+'&r='+r+'&p='+p+'&ps='+ps+'&px='+classification+'&rg='\
                                 +rg+'&cc='+cc+'&fmt='+format+'&head='+head+'&max='+str(max_values)
                URL = base_URL + URL_parameters

                print(URL)

                req = requests.get(URL, verify=False)
                # req = http.request('GET', URL)

                if (req.status_code == 200):
                    if (format == 'json'):
                        req_json = req.json()

                        print_API_call_info(req_json, URL, max_values)

                        return req_json['dataset']

                    elif (format == 'csv'):
                        req_csv = req.content
                        print(req_csv)
                        return req_csv
                else:
                    print(req.status_code, req.text)
        else:
            print('\nOne of the parameters is not valid.\n')
            return 3


    def get_data(self, reporters, partners, time_period, trade_flows, type='C', freq='A', classification='HS',
                  commodities='AG2 - All 2-digit HS commodities', max_values=100000, head='H', format='json'):

        if (isinstance(time_period, list)):
            time_period = sorted(set(time_period))

        data_split = {
            'reporters': ([reporters[x:x+5] for x in range(0, len(reporters), 5)] if isinstance(reporters, list) and len(reporters) > 5 else [reporters]),
            'partners': ([partners[x:x+5] for x in range(0, len(partners), 5)] if isinstance(partners, list) and len(partners) > 5 else [partners]),
            'time_period': ([time_period[x:x+5] for x in range(0, len(time_period), 5)] if isinstance(time_period, list) and len(time_period) > 5 else [time_period]),
            'commodities': ([commodities[x:x+20] for x in range(0, len(commodities), 20)] if isinstance(commodities, list) and len(commodities) > 20 else [commodities]),
            'trade_flows': trade_flows,
            'type': type,
            'freq': freq,
            'classification': classification,
            'max_values': max_values,
            'head': head,
            'format': format,
        }

        number_of_calls = []
        number_of_calls = how_many_calls(reporters, number_of_calls, 5)
        number_of_calls = how_many_calls(partners, number_of_calls, 5)
        number_of_calls = how_many_calls(time_period, number_of_calls, 5)
        number_of_calls = how_many_calls(commodities, number_of_calls, 20)

        # print(number_of_calls)
        # print(data_split)

        tree = Tree(number_of_calls, data_split)
        # print(len(tree.root.data))
        # print(tree.root.data)

        return tree.root.data


def read_json(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return [country['text'] for country in data['results']]


def read_json_all(filename):
    with open(filename, encoding='utf-8') as data_file:
        return json.loads(data_file.read())



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


def how_many_calls(data, number_of_calls, limit):
    if (isinstance(data, list) and len(data) > limit):
        number_of_calls.append(ceil(len(data) / limit))
    else:
        number_of_calls.append(1)
    return number_of_calls


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


def print_all_parameters(reporters, partners, time_period, trade_flows, type, freq,
                             classification, commodities, max_values, head, format):
    print('Reporters: ', reporters)
    print('Partners: ', partners)
    print('Time period: ', time_period)
    print('Trade flows: ', trade_flows)
    print('Type: ', type)
    print('Frequency: ', freq)
    print('Classification: ', classification)
    print('Commodities: ', commodities)
    print('Max values: ', max_values)
    print('Head: ', head)
    print('Format: ', format)


def print_API_call_info(req_json, URL, max_values):
    print('\n')
    print(URL)
    print('Message:', req_json['validation']['message'])
    print('Total values:', req_json['validation']['count']['value'])
    returned_values = req_json['validation']['count']['value'] if max_values > req_json['validation']['count']['value'] else max_values
    global all_values
    all_values += returned_values
    print('Returned values:', returned_values)
    if (req_json['validation']['datasetTimer'] is not None):
        duration = req_json['validation']['datasetTimer']['durationSeconds']
        print('API call took ' + "{0:.2f}".format(duration) + ' seconds')
    print('\n')

    # for record in req_json['dataset']:
    #     print(record)


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

# print_all()


def table_profiles(res, selected_years):
    header_row = ['REPORTER', 'PARTNER', 'TRADE FLOW', 'COMMODITY / SERVICE']
    [header_row.append(year) for year in selected_years]

    matrix = np.matrix([header_row])

    for r in res:
        reporter = r['rtTitle']
        partner = r['ptTitle']
        trade_flow = r['rgDesc']
        comm_service = r['cmdDescE'][0] + r['cmdDescE'][1:].lower()
        year = r['period']
        trade_value = r['TradeValue']

        sliced_matrix = matrix[:, 0:4]
        row = np.array([reporter, partner, trade_flow, comm_service])

        column_index = header_row.index(year)

        # print(row)
        # print(sliced_matrix)

        if (any((row == x).all() for x in sliced_matrix)):
            itemindex = np.where(sliced_matrix == row)
            index = np.bincount(itemindex[0]).argmax()

            matrix[index, column_index] = trade_value
        else:
            for y in selected_years:
                row = np.append(row, -1)

            row[column_index] = trade_value

            matrix = np.vstack([matrix, row])

        # print(matrix)
        # print('\n')

    return matrix


def table_time_series(res):
    header_row = ['REPORTER', 'PARTNER', 'TRADE FLOW', 'COMMODITY / SERVICE', 'YEAR', 'TRADE VALUE']

    matrix = np.matrix([header_row])

    for r in res:
        reporter = r['rtTitle']
        partner = r['ptTitle']
        trade_flow = r['rgDesc']
        comm_service = r['cmdDescE'][0] + r['cmdDescE'][1:].lower()
        year = r['period']
        trade_value = r['TradeValue']

        row = np.array([reporter, partner, trade_flow, comm_service, year, trade_value])

        matrix = np.vstack([matrix, row])

    return matrix



unc = UNComtrade()


if __name__ == "__main__":
    res = unc.get_data(['Slovenia'], 'Croatia', 2011, 'Import', commodities='ALL - All HS commodities')

    if (all_values == len(res)):
        print('Number of values is OK.\n')
    else:
        print('Number of values doesn\'t match.\n')



    selected_years = [2005, 2006, 2007, 2008, 2009, 2010, 2011]

    # profiles = table_profiles(res, selected_years)
    # for p in profiles:
    #     print(p)

    time_series = table_time_series(res)
    for ts in time_series:
        print(ts)



    '''
    for i in range(len(res)):
        for key, value in res[i].items():
            print(str(key) + ": " + str(value))
        print('\n\n')
    '''