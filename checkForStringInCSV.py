import pandas
import sys
import os 

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
	try:
		arg1 = sys.argv[1]
		checkIfStringExistsInCSV(arg1)

	except IndexError:
		sys.exit()