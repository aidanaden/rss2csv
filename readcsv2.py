import os
import sys
import feedparser
import csv
import pandas
import datetime
import pytz
import webbrowser
from dateutil import tz
from dateutil import parser
from time import mktime

def utc2sgt(time):
	date = parser.parse(time)
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()

	utc = date.replace(tzinfo=from_zone)
	local = utc.astimezone(to_zone)

	return local

def downloadFile(entry,dict_writer,publisher_description_entry,feed_title):

	dateFields = ['published_parsed','updated_parsed']
	titleFields = ['title']
	summaryFields = ['summary','description']
	categoryFields = ['category']
	
	converted_sg_time = ""
	summaryEntry = ""
	titleEntry = ""
	categoryEntry = ""

	titleEntry = entry['title']

	for dateField in dateFields:
		try:
			dt2 = datetime.datetime.fromtimestamp(mktime(entry[dateField]))
			time_aware_dt2_for_comparison = dt2.replace(tzinfo=tz.tzutc())
			#shouldDownload = LastModifiedDateTimeIsOlder(time_aware_dt2_for_comparison)
			converted_sg_time = utc2sgt(str(dt2))
			#print(converted_sg_time)
		except:
			pass

	for summaryField in summaryFields:
		if summaryField in entry:
			summaryEntry = entry[summaryField]
		else:
			pass

	try:
		for tag in entry['tags']:
			categoryEntry += tag['term'] + ','
	except:
		pass

	print("downloaded " + titleEntry)
	dict_writer.writerow({date_time:converted_sg_time,
				title:titleEntry,
				publisher:feed_title,
				description:summaryEntry,
				link:entry['link'],
				category:categoryEntry,
				publisher_description:publisher_description_entry})

def checkIfFileExists():
	try:
		with open(output_filename, 'rt', encoding='utf-8') as ifile:
			return True			
	except:
		return False

def checkIfContainsString(string,df):
	if df[title].str.contains(str(string)).any():
		print("article exists in file!")
		return True
	else:
		return False

def rss2csv(url, dict_writer):

	feed = feedparser.parse(url)

	try:
		publisher_description_entry = feed.feed.description
	except:
		publisher_description_entry = ""

	with open(output_filename, 'rt', encoding='utf-8') as input_file: 
		dfX = pandas.read_csv(input_file)
		for entry in feed['entries']:
			if (dfX[title] == entry['title']).any():
				print('file exists')
			else:
				print('file does not exists') 
				downloadFile(entry,dict_writer,publisher_description_entry,feed.feed.title)
		

def rss2csvNOCHECK(url, dict_writer):

	feed = feedparser.parse(url)

	try:
		publisher_description_entry = feed.feed.description
	except:
		publisher_description_entry = ""

	for entry in feed['entries']:
		downloadFile(entry,dict_writer,publisher_description_entry,feed.feed.title)
		


def firstDownload():
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "wt", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			dict_writer.writeheader()
			for column in df:
				for row in df[column]:
					rss2csvNOCHECK(str(row), dict_writer)

def update():
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "at", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			for column in df:
				for row in df[column]:
					rss2csv(str(row), dict_writer)


def checkIfStringExistsInCSV(string):
	index = 1
	results = []
	results_exists = 0
	with open(output_filename, 'rt', encoding='utf-8') as input_file:
		df = pandas.read_csv(input_file)
		searchList = [category,description,publisher_description] # list of columns to search from
		for column in searchList:

			lowercaseDf = df[column].str.lower()
			selectedDf = df[lowercaseDf.str.contains(string.lower(),na = False)]
			
			for title, publisher, entryUrl in zip(selectedDf['article_title'], selectedDf['article_publisher'], selectedDf['article_url']):

				if title == "":
					pass
				else:
					results_exists += 1

					print(index, ") Publisher: ",publisher)
					print("Title: ", title, '\n')

					results.append(entryUrl)

				index += 1

		if results_exists == 0:
			print('unable to find any articles')

		else:
			varInput = input("Enter article number: ")
			if varInput == "N":
				sys.exit()
			else:
				varInput = int(varInput)
				try:
					webbrowser.get(chrome_path).open(results[varInput - 1])
				except:
					print('Index does not exist!')


if __name__ == "__main__":
	
	news_feed_file = "News Feeds.csv"
	output_filename = "output_feeds.csv"
	chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
	
	date_time = 'article_published'
	title = 'article_title'
	publisher = 'article_publisher'
	description = 'article_description'
	link = 'article_url'
	category = 'article_category'
	publisher_description = 'publisher_description'

	fieldNames = [date_time, title, publisher, description, link, category, publisher_description]

	usageMessage = "\nUsage: python readcsv2.py <command>\nExample: python readcsv2.py download\n\nOptions:\n1) download : download all rss feeds\n2) update : update rss feeds\n3) search : search for keyword in csv"
	try:
		arg1 = sys.argv[1]
		if arg1 == 'download':
			if checkIfFileExists() == False:
				firstDownload()
			else:
				update()
		elif arg1 == 'search':
			arg2 = sys.argv[2]
			checkIfStringExistsInCSV(arg2)
		else:
			print(usageMessage)

	except IndexError:
		print(usageMessage)
		sys.exit()

		




