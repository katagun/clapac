import logging, sys, timeit
from craigslist_apa_crawler import CraigslistApaCrawler
import os

try:
    from config import config
except ImportError:
    print('config.py not found')
    sys.exit(1)


def main():
    start_time = timeit.default_timer()
    # setup logging
    logging_format = '%(asctime)s [%(levelname)s] - %(funcName)s lineno: %(lineno)d %(message)s'
    logging.basicConfig(format=logging_format, level=logging.DEBUG)
    # start the crawler
    logging.info('State: '.format(config['state']))
    logging.info('City: '.format(config['city']))
    logging.info('Starting the loop over zipcodes')
    apa_crawler = CraigslistApaCrawler(config=config)
    apartments, _ = apa_crawler.crawl_zipcodes()
    # done
    elapsed = timeit.default_timer() - start_time
    logging.info('time elasped since start of program: {}'.format(elapsed))
    logging.info('Stage one finished, you can check preliminary results.')
    logging.info('===============================================')


if __name__ == "__main__":
    main()
