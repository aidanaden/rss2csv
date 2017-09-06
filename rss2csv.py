import sys
import feedparser
import csv
import datetime
import pytz
import dateutil.parser
from dateutil import tz

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

def rss2csv(url):

	rss_url = url

	#parse feed using feedparser
	
	feed = feedparser.parse(rss_url)

	#create special char table to be removed
	special_char_table = str.maketrans(dict.fromkeys('?./='))

	#remove http and https from url
	filename = rss_url.replace('http://', '').replace('https://', '')

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
	with open(cleaned_filename + '.csv', "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, fieldNames)
		dict_writer.writeheader()
		for entry in feed['entries']:

			try:
				categoryValue = entry['category']
			except:
				categoryValue = "NIL"

			for dateField in dateFields:
				try:
					converted_sg_time = utc2sgt(entry[dateField])
				except:
					continue

			dict_writer.writerow({fieldname1:converted_sg_time,fieldname2:entry['title'],fieldname3:entry['summary'],fieldname4:entry['link'], fieldname5:categoryValue})

		pass

if __name__ == "__main__":
	try:
		arg1 = sys.argv[1]
	except IndexError:
		print("Usage: rss2csv.py <url of RSS feed>")
		sys.exit()

	rss2csv(arg1)

	



