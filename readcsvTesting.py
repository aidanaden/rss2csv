import os
import sys
import feedparser
import csv
import pandas
import datetime
import pytz
import dateutil.parser
from dateutil import tz
from dateutil import parser
from time import mktime

def shortcutConvertSG(date_time):
	dt = parser.parse(date_time)
	dt.astimezone(tzinfo=None)
	
	return dt

def utc2sgt(time):
	date = dateutil.parser.parse(time)
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()

	utc = date.replace(tzinfo=from_zone)
	local = utc.astimezone(to_zone)

	return local

def LastModifiedDateTimeIsOlder(dtObj):

	#convert both datetimes to utc to do calculation, 
	#if possible would be better to do calculation with sgt
	
	#converted version of feed's data time: expected to be in utc else will fk up
	feed_converted = dtObj.astimezone(tz=tz.tzutc())
	
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

def rss2csv(url, categoryValue, dict_writer, download):

	feed = feedparser.parse(url)

	dateFields = ['published_parsed','updated_parsed']
	titleFields = ['title']
	summaryFields = ['summary','description']
	categoryFields = ['category']
	shouldDownload = False

	for entry in feed['entries']:

		converted_sg_time = "NA"
		summaryEntry = "NA"
		titleEntry = "NA"
		categoryEntry = ""

		for dateField in dateFields:
			try:
				#dt = parser.parse(entry[dateField])
				dt2 = datetime.datetime.fromtimestamp(mktime(entry[dateField]))
	
				time_aware_dt2_for_comparison = dt2.replace(tzinfo=tz.tzutc())
				shouldDownload = LastModifiedDateTimeIsOlder(time_aware_dt2_for_comparison)
				converted_sg_time = utc2sgt(str(dt2))
			except:
				pass

		#print(utc2sgt(str(dt2)))
		#converted_sg_time = dt.astimezone(tz=None)
		#shouldDownload = LastModifiedDateTimeIsOlder(dt)
			#else:
				#pass

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

			try:
				for tag in entry['tags']:
					categoryEntry += tag['term'] + ','
			except:
				pass

			print("downloaded " + titleEntry)
			dict_writer.writerow({date_time:converted_sg_time,title:titleEntry,publisher:feed.feed.title,
				description:summaryEntry,link:entry['link'],category:categoryEntry})

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

def checkIfStringExistsInCSV(string):
	with open(output_filename, 'rt', encoding='utf-8') as input_file:
		df = pandas.read_csv(input_file)
		searchList = ['category','article_description'] # list of columns to search from
		for column in searchList:
			#try:
			lowercaseDf = df[column].str.lower()
			selectedDf = df[lowercaseDf.str.contains(string.lower(),na = False)]
			#except:
			#	pass
			#else:
			for title, publisher in zip(selectedDf['article_title'], selectedDf['article_publisher']):
				print("Publisher: ",publisher)
				print("Title: ", title, '\n')

if __name__ == "__main__":
	
	news_feed_file = "News Feeds.csv"
	output_filename = "output_feeds.csv"
	
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

		




