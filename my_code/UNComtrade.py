import os
import json
import requests
from math import ceil
from datetime import datetime, timedelta
from collections import OrderedDict
import numpy as np
import Orange.data
from Orange.data import DiscreteVariable, ContinuousVariable

# all_values = 0
first_call = True
last_call__time = ''


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
                while (datetime.now() - last_call_time < timedelta(seconds=1.2)):
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
        path = os.path.join(os.path.dirname(__file__), 'data', 'reporters.json')
        return read_json(path)

    def partners(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'partners.json')
        return read_json(path)

    def commodities_HS(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'commodities_HS.json')
        return read_json(path)

    def commodities_HS_all(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'commodities_HS_tree.json')
        return read_json_all(path)

    def commodities_ST(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'commodities_ST.json')
        return read_json(path)

    def commodities_BEC(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'commodities_BEC.json')
        return read_json(path)

    def services(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'services.json')
        return read_json(path)

    def services_all(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'services_tree.json')
        return read_json_all(path)

    def trade_flows(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'trade_flows.json')
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
        ps = check_form(time_period, 'ps', freq=freq)
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

                # print(URL)

                res = self.return_response(format, URL)
                return res
        else:
            print('\nOne of the parameters is not valid.\n')
            return 3


    def return_response(self, format, URL):
        res = requests.get(URL)

        if (res.status_code == 200):
            if (format == 'json'):
                res_json = res.json()

                # print_API_call_info(req_json, URL, max_values)

                return res_json['dataset']

            elif (format == 'csv'):
                res_csv = res.content
                print(res_csv)
                return res_csv
        else:
            print('API returned error!')
            print(res.status_code, res.text)

        return None


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


    def table_profiles(self, res, selected_years):
        matrix = []

        for r in res:
            reporter = r['rtTitle']
            partner = r['ptTitle']
            trade_flow = r['rgDesc']
            comm_service = r['cmdDescE'][0] + r['cmdDescE'][1:].lower()
            year = str(r['period'])
            trade_value = int(r['TradeValue'])

            row = [reporter, partner, trade_flow, comm_service]

            column_index = selected_years.index(year)
            row_index = get_row_index(matrix, row, len(selected_years))

            if (row_index != -1):  # row already exists
                matrix[row_index][column_index] = trade_value
            else:
                # prepend years to row list
                row[:0] = ['?'] * len(selected_years)
                row[column_index] = trade_value
                matrix.append(row)

        if (len(matrix) == 0):
            return None

        obj = np.array(matrix, dtype=object)
        unique_reporters = np.unique(obj[:, len(selected_years)]) if len(matrix) > 0 else []
        unique_partners = np.unique(obj[:, len(selected_years) + 1]) if len(matrix) > 0 else []
        unique_trade_flows = np.unique(obj[:, len(selected_years) + 2]) if len(matrix) > 0 else []
        unique_comm_ser = np.unique(obj[:, len(selected_years) + 3]) if len(matrix) > 0 else []

        metas = []
        metas.append(DiscreteVariable('Reporter', unique_reporters))
        metas.append(DiscreteVariable('Partner', unique_partners))
        metas.append(DiscreteVariable('Trade Flow', unique_trade_flows))
        metas.append(DiscreteVariable('Commodity / Service', unique_comm_ser))
        attributes = []
        [attributes.append(ContinuousVariable(year)) for year in selected_years]
        attributes = tuple(attributes)

        orange_domain = Orange.data.Domain(attributes, metas=metas)

        orange_data_table = Orange.data.Table.from_list(orange_domain, matrix)

        return orange_data_table


    def table_time_series(self, res):
        matrix = []

        for r in res:
            reporter = r['rtTitle']
            partner = r['ptTitle']
            trade_flow = r['rgDesc']
            comm_service = r['cmdDescE'][0] + r['cmdDescE'][1:].lower()
            year = str(r['period'])
            trade_value = int(r['TradeValue'])

            row = [trade_value, reporter, partner, trade_flow, comm_service, year]
            matrix.append(row)

        if (len(matrix) == 0):
            return None

        matrix.sort(key=lambda x: x[4])

        obj = np.array(matrix, dtype=object)
        unique_reporters = np.unique(obj[:, 1]) if len(matrix) > 0 else []
        unique_partners = np.unique(obj[:, 2]) if len(matrix) > 0 else []
        unique_trade_flows = np.unique(obj[:, 3]) if len(matrix) > 0 else []
        unique_comm_ser = np.unique(obj[:, 4]) if len(matrix) > 0 else []
        unique_years = np.unique(obj[:, 5]) if len(matrix) > 0 else []

        metas = []
        metas.append(DiscreteVariable('Reporter', unique_reporters))
        metas.append(DiscreteVariable('Partner', unique_partners))
        metas.append(DiscreteVariable('Trade Flow', unique_trade_flows))
        metas.append(DiscreteVariable('Commodity / Service', unique_comm_ser))
        metas.append(DiscreteVariable('Year', unique_years))
        attributes = tuple([ContinuousVariable('Trade Value (US $)')])

        orange_domain = Orange.data.Domain(attributes, metas=metas)

        orange_data_table = Orange.data.Table.from_list(orange_domain, matrix)

        return orange_data_table


def read_json(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return [country['text'] for country in data['results']]


def read_json_all(filename):
    with open(filename, encoding='utf-8') as data_file:
        return json.loads(data_file.read(), object_pairs_hook=OrderedDict)


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
        path = os.path.join(os.path.dirname(__file__), 'data/reporters.json')
        dict = json2object(path)
    elif (p == 'p'):
        path = os.path.join(os.path.dirname(__file__), 'data/partners.json')
        dict = json2object(path)
    elif (p == 'rg'):
        path = os.path.join(os.path.dirname(__file__), 'data/trade_flows.json')
        dict = json2object(path)
    elif (p == 'cc'):
        if (classified == 'HS'):
            path = os.path.join(os.path.dirname(__file__), 'data/commodities_HS.json')
            dict = json2object(path)
        elif (classified == 'ST'):
            path = os.path.join(os.path.dirname(__file__), 'data/commodities_ST.json')
            dict = json2object(path)
        elif (classified == 'BEC'):
            path = os.path.join(os.path.dirname(__file__), 'data/commodities_BEC.json')
            dict = json2object(path)
        elif (classified == 'EB02'):
            path = os.path.join(os.path.dirname(__file__), 'data/services.json')
            dict = json2object(path)
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
                        if (int(y) < 1962 or int(y) > 2050):
                            print('Year is not correct')
                            return None
            elif (isinstance(parameter, str)):
                if (parameter != 'all'):
                    print('Year is not correct')
                    return None
        need_id = False
    else:
        return None

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


def get_row_index(matrix, row_4, len_years):
    for i in range(len(matrix)-1, -1, -1):
        r = matrix[i]
        if (r[len_years] == row_4[0] and r[len_years+1] == row_4[1] and r[len_years+2] == row_4[2] and r[len_years+3] == row_4[3]):
            return i
    return -1


'''
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
    print('Returned values:', returned_values)
    if (req_json['validation']['datasetTimer'] is not None):
        duration = req_json['validation']['datasetTimer']['durationSeconds']
        print('API call took ' + "{0:.2f}".format(duration) + ' seconds')
    print('\n')


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
'''


if __name__ == "__main__":
    unc = UNComtrade()

    res = unc.return_response('csv', 'https://comtrade.un.org/api/get')

    print(res)
    print(len(res))

    # r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2014], 'Export', freq='A')
    # print(r)

    # if (all_values == len(res)):
    #     print('Number of values is OK.\n')
    # else:
    #     print('Number of values doesn\'t match.\n')

    # selected_years = [2005, 2006, 2007, 2008, 2009, 2010, 2011]
    #
    # profiles = unc.table_profiles(res, selected_years)
    # for p in profiles:
    #     print(p)
    #
    # time_series = unc.table_time_series(res)
    # for ts in time_series:
    #     print(ts)

