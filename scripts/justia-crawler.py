from bs4 import BeautifulSoup
import urllib2
import datetime
import json
import ast

import sys
import os
sys.path.append(os.path.abspath('../web'))

import models

def get_listings():
	#440 = Civil Rights - Other Civil Rights
	#Cout - NY SD
	for page in xrange(1, 932):
		url = "https://dockets.justia.com/search?court=nyedce&nos=440&cases=mostrecent&page="
		f = open("crawled.txt", "a")
		f.write("*"*10 + "\n")
		f.write(str(url+str(page)))
		f.write("\n" + "*"*10 + "\n")
		f.close()
		listing_page = urllib2.urlopen(url + str(page))
		soup = BeautifulSoup(listing_page)
		docket_urls = soup.find_all("a", {"class":"case-name"})

		for link in docket_urls:
			#to do - check if listing is in database
			crawl_docket(link["href"])


def crawl_docket(url):
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page)
	case_table = soup.find(id="case-info-table")
	keys = case_table.find_all("th")
	values = case_table.find_all("td")
	case = {}
	case["url"] = url
	for i in xrange(0, len(keys) - 1):
		case[keys[i].string] = values[i].string

	print case
	f = open("dockets.txt", "a")
	f.write(str(case))
	f.write("\n")
	f.close()

	return


def reduce_keys(filename):
	json_rows = map(ast.literal_eval, open(filename))
	sets = map(set, json_rows)
	keys = []
	for s in sets:
		#print s
		for key in s:
			if key in keys:
				continue
			else:
				keys.append(key)
	print keys

	'''['url', u'Filed:', u'Presiding Judge:', u'Case Number:', u'Plaintiff:', u'Defendant:', u'Nature of Suit:', u'Cause of Action:', u'County:', u'Office:', u'Court:', u'Referring Judge:', u'Cross_defendant:', u'Cross_claimant:', u'Petitioner:', u'Respondent:', u'Claimant:', u'Counter_claimant:', u'Counter_defendant:', u'Amicus:', u'Intervenor:', u'Thirdparty_defendant:', u'Consolidated_defendant:', u'Consolidated_plaintiff:']'''

def list_defendants(filename):
	defs = []
	json_rows = map(ast.literal_eval, open(filename))
	for docket in json_rows:
		try:
			defs.append(docket['Defendant:'])
		except:
			print "No defendant", docket['Case Number:']

	for d in defs:
		print d

def import_dockets(filename):
	json_rows = map(ast.literal_eval, open(filename))
	for docket in json_rows:
		s = ''
		for key in docket.keys():
			s += d2d(key) + " = '" + docket[key] + "', "
		d = Session.Docket(s[:-1])


def d2d(key):
	"""
	Function converts the Justia docket names to database names
	"""
	converter = {'url': 'url',
		'Filed:': 'filed',
		'Presiding Judge:': 'judge',
		'Case Number:': 'id',
		'Plaintiff:': 'plaintiff',
		'Defendant:': 'defendant',
		'Nature of Suit:': 'nature',
		'Cause of Action:': 'cause',
		'County:': 'county',
		'Office:': 'office',
		'Court:': 'court',
		'Referring Judge:': 'referring_judge',
		'Cross_defendant:': 'cross_defendant',
		'Cross_claimant:': 'cross_claimant',
		'Petitioner:': 'petitioner',
		'Respondent:': 'respondent',
		'Claimant:': 'claimant',
		'Counter_claimant:': 'counter_claimant',
		'Counter_defendant:': 'counter_defendant',
		'Amicus:': 'amicus',
		'Intervenor:': 'intervenor',
		'Thirdparty_defendant:': 'thirdparty_defendant',
		'Consolidated_defendant:': 'consolidated_defendant',
		'Consolidated_plaintiff:': 'consolidated_plaintiff'
		}

	try:
		if converter[key]:
			return converter[key]
	except:
		return "Value Error"

if __name__ =="__main__":
	import_dockets("dockets.txt")
    