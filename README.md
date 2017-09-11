# rss2csv
Internship script for rss feed to csv from csv 

Parses urls of rss feed from a given csv file--in this case News Feeds.csv--and writes output in a csv file 
containing all the rss feeds, categorized by date time, publisher, description, url and category.

Usage: readcsvTesting.py [download, update, search]

download: downloads from urls and writes into a csv file named "output_feeds.csv"

update: downloads latest rss feeds posts since last modified time of output_feeds.csv

search: searches for the entered keyword in output_feeds.csv and returns title and publisher
