import os
import sys
import feedparser
import csv
import pandas
import datetime
import pytz
import dateutil.parser
from dateutil import tz

def utc2sgt(time):

	if time is None:
		return "NA"

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

def LastModifiedDateTimeIsOlder(feed_UTC):

	#convert both datetimes to utc to do calculation, 
	#if possible would be better to do calculation with sgt
	exitCode = ""
	#sample = "2017-04-27 13:31:00+08:00"
	dateutil_converted = dateutil.parser.parse(str(feed_UTC))
	#utcSample = sgt2utc(sample)
	cwd = os.path.getmtime(news_feed_file)
	converted = datetime.datetime.utcfromtimestamp(cwd)
	converted_tz = datetime.datetime(year=converted.year,month=converted.month,day=converted.day,
		hour=converted.hour,minute=converted.minute,second=converted.second,tzinfo=pytz.utc)
	print(converted_tz)
	try:
		if converted_tz < dateutil_converted:
			return True
		else:
			return False
	except:
		if converted < dateutil_converted:
			return True
		else:
			return False


def getFileNameFromURL(url):
	#create special char table to be removed
	special_char_table = str.maketrans(dict.fromkeys('?./='))
	#remove http and https from url
	filename = url.replace('http://', '').replace('https://', '')
	#remove special characters
	cleaned_filename = filename.translate(special_char_table)

	return cleaned_filename

def rss2csv(url, categoryValue, dict_writer):

	#parse feed using feedparser
	feed = feedparser.parse(url)

	#filename = getFileNameFromURL(url)
	
	dateFields = ['published','pubDate','date','updated']
	titleFields = ['title','id']
	summaryFields = ['summary','description']

	for entry in feed['entries']:

		converted_sg_time = "NA"
		summaryEntry = "NA"
		titleEntry = "NA"

		for dateField in dateFields:
			try:
				shouldDownload = LastModifiedDateTimeIsOlder(entry[dateField])
				converted_sg_time = utc2sgt(entry[dateField])
			except:
				continue
		print(shouldDownload)		
		if shouldDownload | len(df.index) <= 2:

			for summaryField in summaryFields:
				try:
					summaryEntry = entry[summaryField]
				except:
					continue

			for titleField in titleFields:
				try:
					titleEntry = entry[titleField]
				except:
					continue

		

			dict_writer.writerow({fieldname1:converted_sg_time,fieldname2:titleEntry,fieldname3:summaryEntry,fieldname4:entry['link'], fieldname5:categoryValue})

	pass

news_feed_file = 'News Feeds.csv'
output_filename = "output_feeds.csv"

fieldname1 = 'article_published'
fieldname2 = 'article_title'
fieldname3 = 'article_description'
fieldname4 = 'aricle_url'
fieldname5 = 'category'

fieldNames = [fieldname1, fieldname2, fieldname3, fieldname4, fieldname5]

with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
	df = pandas.read_csv(input_file)
	with open(output_filename, "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, fieldNames)
		dict_writer.writeheader()
		print(len(df.index))
		for column in df:
			for row in df[column]:
				rss2csv(str(row), str(column), dict_writer)
			
		
		




