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

#def EDT2SGConverter(time):

	#if time.endswith('EDT'):
		#new_time = time[:-4]

		#original_fmt = "%a, %d %b %Y %H:%M:%S"

		#date = datetime.datetime.strptime(new_time, original_fmt)
		#dateLocalized = date + datetime.timedelta(days=1/2)
		#date_sg_timezone = str(dateLocalized) + " SGT"
	
		#return date_sg_timezone

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


#def getFileNameFromURL(url):
	##create special char table to be removed
	#special_char_table = str.maketrans(dict.fromkeys('?./='))
	##remove http and https from url
	#filename = url.replace('http://', '').replace('https://', '')
	##remove special characters
	#cleaned_filename = filename.translate(special_char_table)

	#return cleaned_filename

def rss2csv(url, categoryValue, dict_writer, download):

	#parse feed using feedparser
	feed = feedparser.parse(url)

	#filename = getFileNameFromURL(url)
	
	#create fields arrays to check
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
			#try:
				#shouldDownload = LastModifiedDateTimeIsOlder(entry[dateField],url)
			else:
				pass
			#except:
			#	pass
			#else:
			#	converted_sg_time = convert2sgt(entry[dateField],url)

		if shouldDownload | download:

			for summaryField in summaryFields:
				if summaryField in entry:
					summaryEntry = entry[summaryField]
				else:
					pass
				#try:
				#	summaryEntry = entry[summaryField]
				#except:
				#	pass

			for titleField in titleFields:
				if titleField in entry:
					titleEntry = entry[titleField]
				else:
					pass
				#try:
				#	titleEntry = entry[titleField]
				#except:
				#	pass

			print("downloaded " + titleEntry)
			dict_writer.writerow({fieldname1:converted_sg_time,fieldname2:titleEntry,
				fieldname3:summaryEntry,fieldname4:entry['link'],fieldname5:categoryValue})

	pass


#with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
	#df = pandas.read_csv(input_file)
	#with open(output_filename, "wt", encoding = "utf-8") as output_file:
		#dict_writer = csv.DictWriter(output_file, fieldNames)
		#dict_writer.writeheader()
		#try:
			#with open(output_filename, 'rt', encoding = 'utf-8') as input_output_file:
				#output_df = pandas.read_csv(input_output_file)
				#print(len(output_df.index))
		#except:
			#print('unable to read output file')
			

		#for column in df:
			#for row in df[column]:
				#rss2csv(str(row), str(column), dict_writer)


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


if __name__ == "__main__":

	# time zones for urls : update these dictionaries 
	# for future urls that use data times that aren't in utc
	
	EDTURL = ["https://phys.org/rss-feed/technology-news/security/","http://www.darkreading.com/rss_simple.asp",
			  "https://phys.org/rss-feed/technology-news/security/","http://feeds.reuters.com/reuters/technologyNews"]
	PDTURL = ["http://feeds.feedburner.com/feedburner/Talos?format=xml","http://feeds.feedburner.com/TheHackersNews"]

	news_feed_file = 'News Feeds.csv'
	output_filename = "output_feeds.csv"

	fieldname1 = 'article_published'
	fieldname2 = 'article_title'
	fieldname3 = 'article_description'
	fieldname4 = 'aricle_url'
	fieldname5 = 'category'

	fieldNames = [fieldname1, fieldname2, fieldname3, fieldname4, fieldname5]

	usageMessage = "\nUsage: python aidantifier.py <command>\nExample: python aidantifier.py download\n\nOptions:\n1) download : download all rss feeds\n2) update : update rss feeds"
	try:
		arg1 = sys.argv[1]
		if arg1 == 'download':
			firstDownload()
		elif arg1 == 'update':
			update()
		else:
			print(usageMessage)

	except IndexError:
		print(usageMessage)
		sys.exit()

		




