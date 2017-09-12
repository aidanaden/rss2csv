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
#from datetime import datetime

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

def LastModifiedDateTimeIsOlder(dtObj):

	#convert both datetimes to utc to do calculation, 
	#if possible would be better to do calculation with sgt
	
	#converted version of feed's data time: expected to be in utc else will fk up
	
	cwd = os.path.getmtime('outputGarbage.csv')
	
	converted = datetime.datetime.utcfromtimestamp(cwd)
	#convert timestamp of last modified to utc + add tzone awareness
	converted_tz = datetime.datetime(year=converted.year,month=converted.month,day=converted.day,
		hour=converted.hour,minute=converted.minute,second=converted.second,tzinfo=tz.tzutc())
	print('last modified time: ', converted_tz)
	print('entry published time', dtObj)
	#try:
		#compare if feed date time is tz aware
	if converted_tz < dtObj:
		return True
	else:
		return False
	#except:
		#compare if feed date time is tz naive
		#if converted < feed_converted:
		#	return True
		#else:
		#	return False

def convert2utc(feed_date):

	utc = tz.tzutc()
	feed_date.astimezone(tz=utc)
	return feed_date

def rss2csv(url):

	rss_url = url

	#parse feed using feedparser
	
	feed = feedparser.parse(rss_url)
	#print(feed.feed.title)

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
	dateFields = ['published_parsed','updated_parsed']
	with open(final_filename, "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, fieldNames)
		dict_writer.writeheader()
		for entry in feed['entries']:

			print(entry)
			#dt = parser.parse(entry['published'])
			#print(dt)
			#print(dt.astimezone(tz=None))
			#print(entry['published_parsed'])

			for dateField in dateFields:
				try:
					dt2 = datetime.datetime.fromtimestamp(mktime(entry[dateField]))
					time_aware_dt2_for_comparison = dt2.replace(tzinfo=tz.tzutc())
					shouldDownload = LastModifiedDateTimeIsOlder(time_aware_dt2_for_comparison)
					converted_sg_time = utc2sgt(str(dt2))
					print(converted_sg_time)
				except:
					pass
			
			categoryValue = ""

			#dt = parser.parse(entry['published'])
			#print(dt)
			#print(dt.astimezone(tz=None))
			#print(dt.astimezone(tz=tz.tzutc()))
			#for tag in entry['tags']:
				#categoryValue += str(tag['term']) + ', '


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

	



