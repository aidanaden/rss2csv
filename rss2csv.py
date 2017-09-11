import os
import sys
import feedparser
import csv
import datetime
import pytz
import dateutil.parser
from dateutil import parser
from dateutil import tz
from time import mktime

def parseTimeConverter(parsed_time):
	dt = datetime.fromtimestamp(mktime(parsed_time))
	return dt


def utc2sgt(time):
	date = dateutil.parser.parse(time)
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()

	utc = date.replace(tzinfo=from_zone)
	local = utc.astimezone(to_zone)

	return local

def EDT2SGConverter(time):

	if time.endswith('EDT'):
		new_time = time[:-4]

		original_fmt = "%a, %d %b %Y %H:%M:%S"

		date = datetime.datetime.strptime(new_time, original_fmt)
		dateLocalized = date + datetime.timedelta(days=1/2)
		date_sg_timezone = str(dateLocalized) + " SGT"
	
		return date_sg_timezone

def timeDifferenceFromLastModified(feed_UTC):

	#convert both datetimes to utc to do calculation, 
	#if possible would be better to do calculation with sgt
	exitCode = ""
	#sample = "2017-04-27 13:31:00+08:00"
	dateutil_converted = dateutil.parser.parse(str(feed_UTC))
	#utcSample = sgt2utc(sample)
	cwd = os.path.getmtime('output_feeds.csv')
	converted = datetime.datetime.utcfromtimestamp(cwd)
	converted_tz = datetime.datetime(year=converted.year,month=converted.month,day=converted.day,
		hour=converted.hour,minute=converted.minute,second=converted.second,tzinfo=pytz.utc)
	try:
		if converted_tz < dateutil_converted:
			exitCode = "last modified is older than rss feed, download that shit"
		else:
			exitCode = "last modified is newer than rss feed, ignore that shit"
	except:
		if converted < dateutil_converted:
			exitCode = "last modified is older than rss feed, download that shit"
		else:
			exitCode = "last modified is newer than rss feed, ignore that shit"

	return(exitCode)

def convert2utc(feed_date):

	utc = tz.tzutc()
	feed_date.astimezone(tz=utc)
	return feed_date

def rss2csv(url):

	rss_url = url

	#parse feed using feedparser
	
	feed = feedparser.parse(rss_url)
	print(feed.feed.title)

	#create special char table to be removed
	special_char_table = str.maketrans(dict.fromkeys('?./='))

	#remove http and https from url
	filename = rss_url.replace('http://', '').replace('https://', '')

	#remove special characters
	cleaned_filename = filename.translate(special_char_table)

	final_filename = "outputGarbage.csv"
	
	#toCSVKeys = feed['entries'][0].keys()
	fieldname1 = 'article_published'
	fieldname2 = 'article_title'
	fieldname3 = 'article_description'
	fieldname4 = 'aricle_url'
	fieldname5 = 'category'

	fieldNames = [fieldname1, fieldname2, fieldname3, fieldname4, fieldname5]

	converted_sg_time = "NA"
	categoryValue = ""

	gay = "NOTHING HAPPNEED"
	dateFields = ['published','pubDate','date','updated']
	with open(final_filename, "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, fieldNames)
		dict_writer.writeheader()
		for entry in feed['entries']:

			print(entry)
			categoryValue = ""
			#dt = parser.parse(entry['published'])
			#print(dt)
			#print(dt.astimezone(tz=None))
			#print(dt.astimezone(tz=tz.tzutc()))
			for tag in entry['tags']:
				categoryValue += str(tag['term']) + ', '


			for dateField in dateFields:
				
				try:
					gay = timeDifferenceFromLastModified(entry[dateField])
					converted_sg_time = utc2sgt(entry[dateField])
					
				except:
					continue

			dict_writer.writerow({fieldname1:converted_sg_time,fieldname2:entry['title'],fieldname3:entry['summary'],fieldname4:entry['link'], fieldname5:categoryValue})
		print(gay)
		pass



if __name__ == "__main__":
	try:
		arg1 = sys.argv[1]
	except IndexError:
		print("Usage: rss2csv.py <url of RSS feed>")
		sys.exit()

	rss2csv(arg1)

	



