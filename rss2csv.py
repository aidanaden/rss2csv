import sys
import feedparser
import csv

def rss2csv(url):

	horrible_subs_rss_url = sys.argv[1]

	#parse feed using feedparser
	feed = feedparser.parse(horrible_subs_rss_url)

	#create special char table to be removed
	special_char_table = str.maketrans(dict.fromkeys('?./='))

	#remove http and https from url
	filename = horrible_subs_rss_url.replace('http://', '').replace('https://', '')

	#remove special characters
	cleaned_filename = filename.translate(special_char_table)
	
	toCSVKeys = feed['entries'][0].keys()

	with open(cleaned_filename + '.csv', "wt", encoding = "utf-8") as output_file:
		dict_writer = csv.DictWriter(output_file, toCSVKeys)
		dict_writer.writeheader()
		dict_writer.writerows(feed['entries'])

		pass

if __name__ == "__main__":
	try:
		arg1 = sys.argv[1]
	except IndexError:
		print("Usage: rss2csv.py <url of RSS feed>")
		sys.exit()

	rss2csv(arg1)

	



