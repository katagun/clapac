import os, sys, time, csv
import requests
import random
from scrapy.selector import Selector
import traceback 
import hashlib
from time import sleep
from random import randint
import logging
from xpath_patterns import CraigsListApaXpathPatterns
from apartment import CraigslistApartmentListing
import zipcodes


log = logging.getLogger(__name__)


class CraigslistApaCrawler:


    def __init__(self, config=None):
        if not config:
            log.error('Please, provide a configuration file, i.e. config.py')
            sys.exit(1)
        try:
            self.city = config['city'] 
            self.base_url = 'https://{}.craigslist.org'.format(self.city.lower())
            self.state = config['state'] 
            self.zipcodes = zipcodes.codes[config['zipcodes']] 
            self.bedrooms = config['bedrooms']
            self.bathrooms = config['bathrooms']
            self.output_dir = config['output_dir']
            self.user_agent  = config['user_agent']
            self.headers= { 'User-Agent': self.user_agent }
            self.xpath_patterns = CraigsListApaXpathPatterns().patterns
            self.parsed_apartments = []
            self.pages = []
        except KeyError as e:
            log.error('Error reading config.py')
            log.error(e)
            sys.exit(1)


    def bedrooms_bathrooms(self, bedrooms, bathrooms):
        if bedrooms and bathrooms:
            return bedrooms, bathrooms
        if not bedrooms and not bathrooms:
            return self.bedrooms, self.bathrooms
        else: return bedrooms, bathrooms


    def query_pars(self, zipcode=80111, bedrooms=None, bathrooms=None):
        query_pars  = "?sort=date&bundleDuplicates=1&hasPic=1"
        query_pars += "&laundry=1&laundry=4&parking=1&parking=2&parking=3&parking=4"
        "&postal={}&search_distance=1".format(zipcode)
        query_pars += "&max_bathrooms={}&min_bathrooms={}".format(bathrooms, bathrooms)
        query_pars += "&max_bedrooms={}&min_bedrooms={}".format(bedrooms, bedrooms)
        return query_pars


    def crawl_zipcodes(self, bedrooms=None, bathrooms=None):
        bedrooms, bathrooms = self.bedrooms_bathrooms(bedrooms, bathrooms)
        dirname = os.path.join(self.output_dir, time.strftime('%B-%d-%Y'))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(os.path.join(dirname, self.city + '.csv'), 'w') as fout:
            csv_fieldnames = CraigslistApartmentListing().properties.keys()
            writer = csv.DictWriter(fout, fieldnames=csv_fieldnames)
            writer.writeheader()
            for i, zipcode in enumerate(self.zipcodes):
                url = self.base_url + '/search/apa/'
                url += self.query_pars(zipcode=zipcode, bedrooms=bedrooms, bathrooms=bathrooms)
                tm = randint(0, i)
                log.debug("loop iteration: {}, zipcode: {}, timeout in sec: {}, url: {}".format(
                i, zipcode, tm, url))
                result = self.crawl_one_pagination(url=url, zipcode=zipcode, timeout=tm,
                        bedrooms=bedrooms, bathrooms=bathrooms)
                self.pages += result
                for r in result:
                    parsed_apartments = self.parse_one_page(page=r, zipcode=zipcode, bedrooms=bedrooms,
                            bathrooms=bathrooms)
                    self.parsed_apartments += parsed_apartments
                    for a in parsed_apartments: 
                        writer.writerow(a.properties)
                        log.debug(a)
            return self.parsed_apartments, self.pages


    def crawl_one_pagination(self, url=None, zipcode=None, timeout=0, bedrooms=None, bathrooms=None):
        results = []
        sleep(timeout)
        try:
            r = requests.get(url, headers=self.headers)
            log.info('Reguesting URL {}'.format(url))
            if r.status_code == 200:
                log.info('Got status code {}'.format(r.status_code))
                results.append(r.text)
                dirname = os.path.join(self.output_dir, time.strftime('%B-%d-%Y'))
                if not os.path.exists(dirname):
                    log.info('Creating directory {}'.format(dirname))
                    os.makedirs(dirname)
                digest = str(hashlib.md5(r.text.encode('utf-8')).hexdigest())
                fname = zipcode + '-' + digest + '.html'
                log.info('Creating file {}'.format(fname))
                with open(os.path.join(dirname,fname), 'w', encoding='utf-8') as f:
                    f.write(r.text)
                hxs  = Selector(text=r.text)
                next_url = hxs.xpath(self.xpath_patterns['next_url'])
                if len(next_url) != 0:
                    next_url = self.base_url + next_url.extract()[0]
                    self.crawl_one_pagination(url=next_url, zipcode=zipcode, timeout=2, 
                            bedrooms=bedrooms, bathrooms=bathrooms)
            else:
                log.error('something went wrong: HTTP status code {}'.format(r.status_code))
        except:
            log.error('something went wrong')
            traceback.print_exc(file=sys.stdout)
        return results


    def parse_one_page(self, page=None, zipcode=None, bedrooms=None, bathrooms=None):
        parsed_apartments = []
        hxs  = Selector(text=page)
        rows = hxs.xpath(self.xpath_patterns['rows'])
        if len(rows) == 0:
            log.warning("no results rows found for zipcode: {}".format(zipcode))
        else:
            log.info("found {} rows for zipcode {}".format(len(rows), zipcode))
        log.info('starting the loop over rows for zipcode: {}'.format(zipcode))
        for i, row in enumerate(rows):
            try:
                parsed_apartment = self.parse_one_apartment_row(row=row, zipcode=zipcode, 
                        bedrooms=bedrooms, bathrooms=bathrooms)
                parsed_apartments.append(parsed_apartment)
                log.debug(parsed_apartment)
            except:
                traceback.print_exc(file=sys.stdout)
                continue
        log.info('done with the loop over rows for zipcode: {}'.format(zipcode))
        return parsed_apartments

    
    def parse_one_apartment_row(self, row=None, zipcode=None, bedrooms=None, bathrooms=None):
        log.debug("creating an instance of CraigslistApartmentListing()")
        apartment = CraigslistApartmentListing()
        log.debug("starting the loop over xpath patterns")
        for p in self.xpath_patterns.keys():
            log.debug(p)
            if p == 'rows' or p == 'next_url':
                continue
            try:
                apartment[p] = row.xpath(self.xpath_patterns[p]).extract()[0].replace('\n','')
                log.debug("{} {}".format(p, row.xpath(self.xpath_patterns[p]).extract()[0]))
            except:
                traceback.print_exc(file=sys.stdout)
                log.error("{} {}".format(
                    p, row.xpath(self.xpath_patterns[p]).extract()))
                apartment[p] = None
        log.debug("finished the loop over xpath patterns")
        apartment["zipcode"] = zipcode 
        apartment["bathrooms"] =bathrooms 
        apartment["bedrooms"] = bedrooms
        try:
            housing = apartment['housing']
            housing = housing.lstrip().rstrip().replace(' ', '')
            ft = housing.split('-')[1].split('ft')[0].strip()
            apartment['ft'] = ft
            apartment['housing'] = housing 
        except:
            apartment['ft'] = None
        try:
            apartment["ad_url"] = 'https://denver.craigslist.org{}'.format(''.join(apartment['ad_url']))
        except:
            apartment["ad_url"] = None
        if not apartment['ft']:
            apartment['ft'] = None 
        if apartment['price']: 
            apartment['price']= apartment['price'].replace('$','')
        return apartment
