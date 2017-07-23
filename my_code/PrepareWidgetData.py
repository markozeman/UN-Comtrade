import json


def read_and_save_new_json(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        data = data['results']

        new_data = {}

        for record in data:
            if (record['parent'] == '#'):
                new_data[record['id']] = record
                new_data[record['id']]['children'] = {}
            else:
                id = record['id']
                if (len(id) == 2):
                    new_data['TOTAL']['children'][id] = record
                    new_data['TOTAL']['children'][id]['children'] = {}
                elif (len(id) == 4):
                    first_two = id[:2]
                    new_data['TOTAL']['children'][first_two]['children'][id] = record
                    new_data['TOTAL']['children'][first_two]['children'][id]['children'] = {}
                elif (len(id) == 6):
                    first_two = id[:2]
                    second_two = id[:4]
                    new_data['TOTAL']['children'][first_two]['children'][second_two]['children'][id] = record
                    new_data['TOTAL']['children'][first_two]['children'][second_two]['children'][id]['children'] = {}

        with open('commodities_HS_tree.json', 'w') as outfile:
            json.dump(new_data, outfile, indent=4, sort_keys=True)




def read_and_save_new_json_service(filename):
    with open(filename, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        data = data['results']

        new_data = {}

        manual_ids = [950, 960, 961, 970, 972, 973, 974, 975, 976, 977]
        manual_data = {}

        for record in data:
            if (record['parent'] == '#'):
                new_data[record['id']] = record
                new_data[record['id']]['children'] = {}
            else:
                num = record['text'].split(' ')[0].split('.')
                num = list(filter(None, num))

                if (len(num) == 1):
                    new_data['200']['children'][num[0]] = record
                    new_data['200']['children'][num[0]]['children'] = {}
                elif (len(num) == 2):
                    new_data['200']['children'][num[0]]['children'][num[1]] = record
                    new_data['200']['children'][num[0]]['children'][num[1]]['children'] = {}
                elif (len(num) == 3):
                    new_data['200']['children'][num[0]]['children'][num[1]]['children'][num[2]] = record
                    new_data['200']['children'][num[0]]['children'][num[1]]['children'][num[2]]['children'] = {}
                elif (len(num) == 4):
                    new_data['200']['children'][num[0]]['children'][num[1]]['children'][num[2]]['children'][num[3]] = record
                    new_data['200']['children'][num[0]]['children'][num[1]]['children'][num[2]]['children'][num[3]]['children'] = {}

            if (record['id'].isdigit() and int(record['id']) in manual_ids):
                manual_data[record['id']] = record

        # add manual data
        new_data = add_manual_data(new_data, manual_data)

        with open('services_tree.json', 'w') as outfile:
            json.dump(new_data, outfile, indent=4, sort_keys=True)



def add_manual_data(new_data, manual_data):
    first_level = ['950', '960', '961', '970']
    for year in first_level:
        new_data['200']['children']['Memorandum']['children'][year] = manual_data[year]
        new_data['200']['children']['Memorandum']['children'][year]['children'] = {}

    second_level_1 = ['972', '974', '976']
    for year in second_level_1:
        new_data['200']['children']['Memorandum']['children']['960']['children'][year] = manual_data[year]
        new_data['200']['children']['Memorandum']['children']['960']['children'][year]['children'] = {}

    second_level_2 = ['973', '975', '976']
    for year in second_level_2:
        new_data['200']['children']['Memorandum']['children']['961']['children'][year] = manual_data[year]
        new_data['200']['children']['Memorandum']['children']['961']['children'][year]['children'] = {}

    return new_data



if __name__ == "__main__":
    read_and_save_new_json_service('data/services.json')