import pandas
import sys
import os 
import re
from OrderedSet import *

def cleanHtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def checkIfStringExistsInCSV(string):
	index = 1
	results_title = []
	results_description = []
	results_cat = []

	with open('output_feeds.csv', 'rt', encoding='utf-8') as input_file:
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

					print(index,") Title: ", title, '\n')

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

#LOGIC OF OUTPUT
#for category in categoryFields:
#	text_file.write(category)
#	if cat == category:
#		text_file.write(title + stuff)

def readConfig(filepath):
	with open(filepath, "rt", encoding='utf-8') as config_file:
		filename = re.split('[.]',filepath)
		outputFirstname = filename[0]
		content = config_file.readlines()
		content = [x.strip() for x in content]
		searchForMultipleWords(content,outputFirstname)


if __name__ == "__main__":

	try:
		arg1 = sys.argv[1]
		readConfig(arg1)
	except:
		print('error!')
		sys.exit()
