import os
import sys
import feedparser
import csv
import pandas
import datetime
import pytz
import re
import webbrowser
from dateutil import tz
from dateutil import parser
from time import mktime
from OrderedSet import *


def utc2sgt(time):
	date = parser.parse(time)
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()

	utc = date.replace(tzinfo=from_zone)
	local = utc.astimezone(to_zone)

	return local

def LastModifiedDateTimeIsOlder(dtObj):
	
	cwd = os.path.getmtime(output_filename)
	converted = datetime.datetime.utcfromtimestamp(cwd)
	converted_tz = datetime.datetime(year=converted.year,month=converted.month,day=converted.day,
		hour=converted.hour,minute=converted.minute,second=converted.second,tzinfo=tz.tzutc())

	if converted_tz < dtObj:
		return True
	else:
		return False

def downloadFile(feed_title,entry,dict_writer,publisher_description_entry,categoryValue,justDownload):

	dateFields = ['updated_parsed']
	titleFields = ['title']
	summaryFields = ['summary','description']
	
	converted_sg_time = ""
	summaryEntry = ""
	titleEntry = ""
	shouldDownload = False

	for dateField in dateFields:
		try:
			dt2 = datetime.datetime.fromtimestamp(mktime(entry[dateField]))
			time_aware_dt2_for_comparison = dt2.replace(tzinfo=tz.tzutc())
			shouldDownload = LastModifiedDateTimeIsOlder(time_aware_dt2_for_comparison)
			converted_sg_time = utc2sgt(str(dt2))
			#print(converted_sg_time)
		except:
			pass

	if shouldDownload | justDownload:

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
		dict_writer.writerow({date_time:converted_sg_time,
					title:titleEntry,
					publisher:feed_title,
					description:summaryEntry,
					link:entry['link'],
					category:categoryValue,
					publisher_description:publisher_description_entry})

def rss2csv(url, dict_writer,categoryValue,justDownload):

	feed = feedparser.parse(url)

	try:
		publisher_description_entry = feed.feed.description
	except:
		publisher_description_entry = ""

	dateFields = ['published_parsed','updated_parsed']
	titleFields = ['title']
	summaryFields = ['summary','description']
	shouldDownload = False

	for entry in feed['entries']:

		downloadFile(feed.feed.title,entry,dict_writer,publisher_description_entry,categoryValue,justDownload)

	pass


def firstDownload():
	justDownload = True
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "wt", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			dict_writer.writeheader()
			for column in df:
				for row in df[column]:
					rss2csv(str(row), dict_writer,str(column),justDownload)

def update():
	justDownload = False
	with open(news_feed_file, 'rt', encoding = 'utf-8') as input_file:
		df = pandas.read_csv(input_file)
		with open(output_filename, "at", encoding = "utf-8") as output_file:
			dict_writer = csv.DictWriter(output_file, fieldNames)
			for column in df:
				for row in df[column]:
					rss2csv(str(row), dict_writer,str(column),justDownload)

def searchForString(string):
	index = 1
	results = []
	results_exists = 0
	with open(output_filename, 'rt', encoding='utf-8') as input_file:
		df = pandas.read_csv(input_file)
		searchList = [link,category,description,publisher_description] # list of columns to search from
		for column in searchList:

			lowercaseDf = df[column].str.lower()
			selectedDf = df[lowercaseDf.str.contains(string.lower(),na = False)]
			
			for title, publisher, entryUrl in zip(selectedDf['article_title'], selectedDf['article_publisher'], selectedDf['article_url']):

				if entryUrl in results:
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


def cleanHtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def checkIfStringExistsInCSV(string):
	index = 1
	results_title = []
	results_description = []
	results_cat = []

	with open(output_filename, 'rt', encoding='utf-8') as input_file:
		df = pandas.read_csv(input_file)
		searchField1 = 'article_url'
		searchField2 = 'article_description'
		searchField3 = 'article_category'
		searchList = [searchField1,searchField2,searchField3] # list of columns to search from
		for column in searchList:
			
			lowercaseDf = df[column].str.lower()
			selectedDf = df[lowercaseDf.str.contains(string.lower(),na = False)]
			
			for title, desc, cat in zip(selectedDf['article_title'], selectedDf[searchField2], selectedDf[searchField3]):

				if title in results_title and desc in results_description:
					pass

				else:

					cleaned_description = cleanHtml(desc)
					#paragraphed_description = ("""%s""" % cleaned_description)

					results_title.append(title)
					results_description.append(cleaned_description)
					results_cat.append(cat)

				index += 1

		return results_title,results_description,results_cat

def searchForMultipleWords(keyword_list,frontFileName):

	endFileName = "_output.txt"
	full_output_path = "".join((frontFileName, endFileName))

	titleList = []
	descList = []
	catList = []

	seen_titles = OrderedSet()
	seen_desc = OrderedSet()
	seen_cat = []

	for keyword in keyword_list:

		titleList_temp, descList_temp, catList_temp = checkIfStringExistsInCSV(keyword)
		titleList += titleList_temp
		descList += descList_temp
		catList += catList_temp

	unique_categories_list = OrderedSet(catList)

	for title1,description1,category1 in zip(titleList,descList,catList):
		if title1 not in seen_titles and description1 not in seen_desc:
			seen_titles.add(title1)
			seen_desc.add(description1)
			seen_cat.append(category1)


	with open(full_output_path,"at",encoding="utf-8") as text_file:
		for unique_category in unique_categories_list:
			text_file.write("\n%s:\n\n" % unique_category)
			for title,desc,cat in zip(seen_titles,seen_desc,seen_cat):
				if cat == unique_category:
					text_file.write("\n\nTitle: %s\n\nDescription: %s\n\n" % (title,desc))
				else:
					pass

def readConfig(filepath):
	with open(filepath, "rt", encoding='utf-8') as config_file:
		filename = re.split('[.]',filepath)
		outputFirstname = filename[0]
		content = config_file.readlines()
		content = [x.strip() for x in content]
		searchForMultipleWords(content,outputFirstname)


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

	usageMessage = "\nUsage: python aidantifier.py <command>\nExample: python aidantifier.py download\n\nOptions:\n1) download : download all rss feeds\n2) update : update rss feeds"
	try:
		arg1 = sys.argv[1]
		if arg1 == 'download':
			firstDownload()

		elif arg1 == 'update':
			update()

		elif arg1 == 'search':
			arg2 = sys.argv[2]
			searchForString(arg2)

		elif arg1 == 'cfg':
			try:
				arg2 = sys.argv[2]
			except:
				print("enter keywords file path, make sure in same directory")
			else:
				readConfig(arg2)

		else:
			print(usageMessage)

	except IndexError:
		print(usageMessage)
		sys.exit()

		




