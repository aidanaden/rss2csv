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

def rss2csv(url, categoryValue):

	#parse feed using feedparser
	feed = feedparser.parse(url)

	#create special char table to be removed
	special_char_table = str.maketrans(dict.fromkeys('?./='))

	#remove http and https from url
	filename = url.replace('http://', '').replace('https://', '')

	#remove special characters
	cleaned_filename = filename.translate(special_char_table)
	
	#toCSVKeys = feed['entries'][0].keys()
	fieldname1 = 'article_published'
	fieldname2 = 'article_title'
	fieldname3 = 'article_description'
	fieldname4 = 'aricle_url'
	fieldname5 = 'category'

	fieldNames = [fieldname1, fieldname2, fieldname3, fieldname4, fieldname5]

	dateFields = ['published','pubDate','date','updated']
	titleFields = ['title','id']
	summaryFields = ['summary','description']

	with open(cleaned_filename + '.csv', "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, fieldNames)
		dict_writer.writeheader()
		for entry in feed['entries']:

			# commented try block for category
			#try:	
			#	categoryValue = entry['category']
			#except:
			#	categoryValue = "NIL"
			converted_sg_time = "NA"
			summaryEntry = "NA"
			titleEntry = "NA"

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

			for dateField in dateFields:
				try:
					converted_sg_time = utc2sgt(entry[dateField])
				except:
					continue

			dict_writer.writerow({fieldname1:converted_sg_time,fieldname2:titleEntry,fieldname3:summaryEntry,fieldname4:entry['link'], fieldname5:categoryValue})

		pass

news_feed_file = 'News Feeds.csv'
with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
	df = pandas.read_csv(input_file)
	for column in df:
		for row in df[column]:
			#print(row)
			#print(column)
			rss2csv(str(row), str(column))
			
		
		




