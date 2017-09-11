import os
import sys
import feedparser
import csv
import pandas
import datetime
import pytz
import dateutil.parser
from dateutil import tz

def convert2sgt(time,url):

	if time is None:
		return "NA"

	to_zone = tz.tzlocal()
	date = dateutil.parser.parse(time)

	if url in EDTURL:
		from_zone = tz.gettz('US/Eastern')
		edt = date.replace(tzinfo=from_zone)
		local = edt.astimezone(to_zone)

	elif url in PDTURL:
		from_zone = tz.gettz('US/Pacific')
		pdt = date.replace(tzinfo=from_zone)
		local = pdt.astimezone(to_zone)

	else:
		from_zone = tz.tzutc()
		utc = date.replace(tzinfo=from_zone)
		local = utc.astimezone(to_zone)

	return local

def LastModifiedDateTimeIsOlder(feed_UTC,url):

	#convert both datetimes to utc to do calculation, 
	#if possible would be better to do calculation with sgt
	
	#converted version of feed's data time: expected to be in utc else will fk up
	feed_converted = convert2utc(feed_UTC,url)
	
	cwd = os.path.getmtime(output_filename)
	converted = datetime.datetime.utcfromtimestamp(cwd)
	#convert timestamp of last modified to utc + add tzone awareness
	converted_tz = datetime.datetime(year=converted.year,month=converted.month,day=converted.day,
		hour=converted.hour,minute=converted.minute,second=converted.second,tzinfo=tz.tzutc())
	try:
		#compare if feed date time is tz aware
		if converted_tz < feed_converted:
			return True
		else:
			return False
	except:
		#compare if feed date time is tz naive
		if converted < feed_converted:
			return True
		else:
			return False

def convert2utc(feed_date,url):

	feed_converted = dateutil.parser.parse(str(feed_date))
	utc = tz.tzutc()
	if url in EDTURL:
		from_zone = tz.gettz('US/Eastern')
		edt = feed_converted.replace(tzinfo=from_zone)
		local = edt.astimezone(utc)
		local_dt = dateutil.parser.parse(str(local))
		return local_dt

	elif url in PDTURL:
		from_zone = tz.gettz('US/Pacific')
		pdt = feed_converted.replace(tzinfo=from_zone)
		local = pdt.astimezone(utc)
		local_dt = dateutil.parser.parse(str(local))
		return local_dt

	else:
		local = feed_converted
		return local

def rss2csv(url, categoryValue, dict_writer, download):

	feed = feedparser.parse(url)

	dateFields = ['published','pubDate','date','updated']
	titleFields = ['title']
	summaryFields = ['summary','description']
	shouldDownload = False

	for entry in feed['entries']:

		converted_sg_time = "NA"
		summaryEntry = "NA"
		titleEntry = "NA"

		for dateField in dateFields:
			if dateField in entry:
				dateOfEntry = entry[dateField]
				shouldDownload = LastModifiedDateTimeIsOlder(dateOfEntry,url)
				converted_sg_time = convert2sgt(dateOfEntry,url)
			else:
				pass

		if shouldDownload | download:

			for summaryField in summaryFields:
				if summaryField in entry:
					summaryEntry = entry[summaryField]
				else:
					pass

			for titleField in titleFields:
				if titleField in entry:
					titleEntry = entry[titleField]
				else:
					pass

			print("downloaded " + titleEntry)
			dict_writer.writerow({date_time:converted_sg_time,title:titleEntry,publisher:feed.feed.title,
				description:summaryEntry,link:entry['link'],category:categoryValue})

	pass


def firstDownload():
	shouldDownload = True
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "wt", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			dict_writer.writeheader()
			for column in df:
				for row in df[column]:
					rss2csv(str(row), str(column), dict_writer,True)

def update():
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "at", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			for column in df:
				for row in df[column]:
					rss2csv(str(row), str(column), dict_writer,False)

#def sortCSVByDate():
def loadConfig():
	import imp
	f = open("config.cfg")
	global data
	data = imp.load_source('data', '', f)
	f.close()

def checkIfStringExistsInCSV(string):
	with open('output_feeds.csv', 'rt', encoding='utf-8') as input_file:
		df = pandas.read_csv(input_file)
		for column in df:
			try:
				selectedDf = df[df[column].str.contains(string)]
				for title, publisher in zip(selectedDf['article_title'], selectedDf['article_publisher']):
					print("Publisher: ",publisher)
					print("Title: ", title, '\n')
			except:
				pass

if __name__ == "__main__":
	
	# init config
	loadConfig()
	EDTURL = data.EDTURL
	PDTURL = data.PDTURL
	news_feed_file = data.news_feed_file
	output_filename = data.output_filename
	
	date_time = 'article_published'
	title = 'article_title'
	publisher = 'article_publisher'
	description = 'article_description'
	link = 'article_url'
	category = 'category'

	fieldNames = [date_time, title, publisher, description, link, category]

	usageMessage = "\nUsage: python aidantifier.py <command>\nExample: python aidantifier.py download\n\nOptions:\n1) download : download all rss feeds\n2) update : update rss feeds"
	try:
		arg1 = sys.argv[1]
		if arg1 == 'download':
			firstDownload()
		elif arg1 == 'update':
			update()
		elif arg1 == 'search':
			arg2 = sys.argv[2]
			checkIfStringExistsInCSV(arg2)
		else:
			print(usageMessage)

	except IndexError:
		print(usageMessage)
		sys.exit()

		




