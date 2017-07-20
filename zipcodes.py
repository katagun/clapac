import csv


def zipcodes(filename='zipcodes.csv', cities=['Denver'], state='CO'):
    with open(filename, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        zipcodes = []
        for row in csvreader:
            for city in cities:
                if row['city'] == city and row['state'] == state:
                    zipcodes.append(row['zip'])
    return zipcodes

denver_metro = zipcodes(filename='zipcodes.csv', 
        cities=['Denver', 'Aurora', 'Englewood', 'Littleton', 'Castle Rock', 'Lone Tree' ], 
        state='CO')

codes = {} 
codes['Denver Metro'] = denver_metro 

for z in ['Denver', 'Aurora', 'Englewood', 'Littleton', 'Castle Rock', 'Lone Tree' ]:
    codes[z] = zipcodes(cities=[z], state='CO')

