# Intro

Web crapping in a constantly moving target.
This is a quick and dirty attempt at scrapping Craigslist for
apartments data which could be useful to someone
looking for a place to call home (rent). If you fancy scrapy,
then this project is not using much of it. 
Part of the reason is because the goal was to scrape only relevant zipcodes,
and it was difficult to do with scrapy.

This code works with the Craigslist.org as of July 19 2017.
It may break and not work at any point in the future,
and it is not going to be carefully maintained.

Also, crawling is done sequentially with randomized delays,
and crawling Denver Metro, Colorado should take about an hour.
It is a lot, but if you don't want to get banned or throttled 
by Craigslist admins, it is advisable to be on the safe side.

# Python 2 or Python 3?

3, as csv.py is broken in Python 2.

# Installation and Usage

You may choose to use virtual env or conda if you wish.
Basic install should work:

```
pip3 install -r requirements.txt
```

Configuration is mostly defined in config.py:

```
config = {
    'state': 'CO',
    'city' : 'Denver',
    'zipcodes' : 'Denver',
    'bedrooms' : 2,
    'bathrooms' : 2,
    'user_agent' : 'MyAwesomeSauceCrawler',
    'output_dir' : 'output',
}
```
To run crawler stage one:

```
python3 stage1.py
```

By default the results will be written out to output/ dir.

To run stage two (remove duplicate entries and try to get the proper zipcode from the listing itself):

```
python3 stage2.py output/July-19-2017/Denver.csv output/July-19-2017/Denver-clean.csv
```

# TODO

 - Write a blog about this project
 - Analyze the data for personal use (Craiglist would go after anyone who 
 tries to commercialize this).
 - Cleanup stage2 code, i.e. fix broken logging, when running in standalone mode, etc.
 - Rewrite the whole thing in golang with better design (and hopefully lessons learned).

# DISCLAIMER

Some parts of the code are not very pretty, so be warned.
Better yet, some part of the code don't make much sense, 
and are probably not very correct. However, the data produced looks usable.
