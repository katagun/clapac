from apartment import CraigslistApartmentListing
import sys
import csv
import time, timeit 
from time import sleep
from random import randint
import requests
import hashlib
from scrapy.selector import Selector
import zipcodes
import traceback
import os
import logging
try:
    from config import config
except ImportError:
    print('config.py not found')
    sys.exit(1)


def apa_listings(csv_rows):
    apartments = []
    for row in csv_rows:
        apa = CraigslistApartmentListing()
        for k in apa.properties.keys():
            try:
                apa[k] = row[k] 
            except KeyError:
                continue
        apartments.append(apa)
    return apartments


def unique_apa_listings(csv_rows):
    apartments = apa_listings(csv_rows)
    apartments_seen_ids = set()
    unique_apartments = []
    for apa in apartments:
        if apa['datapid'] in apartments_seen_ids:
            continue
        else:
            apartments_seen_ids.add(apa['datapid']) 
            unique_apartments.append(apa)
    return unique_apartments


def loop_thru_apartments(apartments=[], func=None, output_file=None):
    logging.info('starting the loop over apartments')
    for i, apa in enumerate(apartments):
        logging.debug("{} apartments left to process".format(len(apartments) - i))
        func(i, apa, output_file)
    return apartments


def sleep_and_get_url(tm, url):
    logging.debug('sleeping for {} seconds, then checking url {}'.format(tm, url))
    sleep(tm)
    print('done sleeping')
    try:
        r = requests.get(url)
    except:
        logging.error('something went wrong')
        traceback.print_exc(file=sys.stdout)
        return None
    return r


def ammend_apa(i, apa, fout):
    tm = randint(1, i + 2)
    try:
        r = sleep_and_get_url(tm, apa['ad_url'])
        if r.status_code != 200:
            logging.error('something went wrong, got HTTP status code: {}'.format(r.status_code))
            fout.write(str(apa) + '\n')
            return apa
        digest = str(hashlib.md5(r.text.encode('utf-8')).hexdigest())
        with open('output/' + digest + '.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
    except:
        logging.error('something went wrong')
        traceback.print_exc(file=sys.stdout)
        return apa
    hxs  = Selector(text=r.text)
    try:
        map_location = hxs.xpath("//div[@class='mapbox']/p[@class='mapaddress']/small/a/@href").extract()[0]
        apa['map_location'] = map_location 
    except:
        traceback.print_exc(file=sys.stdout)
        apa['map_location'] = None 
    try:
        html = hxs.xpath("//html").extract()[0]
    except:
        traceback.print_exc(file=sys.stdout)
        fout.write(str(apa) + '\n')
        return apa
    for zipcode in zipcodes.codes[config['zipcodes']]:
        if zipcode in html:
            apa['zipcode'] = zipcode
        break
    fout.write(str(apa) + '\n')
    return apa


def run(input_filename, output_filename):
    with open(input_filename, 'r') as fin, open(output_filename, 'w') as fout:
        csv_rows = csv.DictReader(fin)
        apartments = unique_apa_listings(csv_rows)
        ammended_apartments = loop_thru_apartments(
            apartments=apartments, 
            func=ammend_apa, 
            output_file=fout
        )

if __name__ == "__main__":
    start_time = timeit.default_timer()
    # setup logging
    logging_format = '%(asctime)s [%(levelname)s] - %(funcName)s lineno: %(lineno)d %(message)s'
    logging.basicConfig(format=logging_format, level=logging.DEBUG)
    # start the crawler
    logging.info('State: '.format(config['state']))
    logging.info('City: '.format(config['city']))
    input_file, output_file = sys.argv[1], sys.argv[2] 
    run(input_file, output_file)
    elapsed = timeit.default_timer() - start_time
    logging.info('time elasped since start of program: {}'.format(elapsed))
    logging.info('Stage two finished, you can check the results.')
    logging.info('===============================================')
