import os
import re
import nltk
import codecs
import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nltk.tag import StanfordNERTagger
import numpy as np
from sklearn.naive_bayes import GaussianNB
import random

import names

data_dir ='../data/police'

def read_files():
	for filename in os.listdir(data_dir):
		#ignore .ds_store & other files
		if not filename.startswith('.') and os.path.isfile(os.path.join(data_dir, filename)):
			#f = codecs.open(os.path.join(data_dir,filename),'r', 'utf-8')
			f = open(os.path.join(data_dir,filename),'r')
			string = f.read()
			string = re.sub('\n',' ', string)
			list_defendants(string)
	

def list_defendants(string):
	'''
	From small sample size, we know that defendants can be listed with
	commas or semi colons to split them.
	If a defendants list uses semi-colons, we do not want to split on commas
	since commas can be used as appositives, e.g. "New York City, a municipality"
	To solve this, we split by commas or semi colons
	'''

	#to do: apply positions to unique defendants when grammar dictacts they should have it
	## e.g. "Officers A, B, and C should be Officer A, Officer B, Officer C"

	#our beautiful regex
	defendant_semi_re = '; (?![^()]*\))'
	defendant_comma_re = ', (?![^()]*\))'

	if re.search(defendant_semi_re, string):
		for item in string.split('; '):
			parse_defendant(item)
			
	else:
		for item in re.split(defendant_comma_re, string):
			parse_defendant(item)


def parse_defendant(defendant):
	'''
	Take a defendant (a single line comprised of many components)
	and break down those components to bucket them
	'''
	#Regex to find shield & tax components, currently deprecated
	shield_re ='((Shield|SHIELD|shield).*[0-9]{4})'
	tax_re ='((tax|Tax|TAX).*[0-9]{6})'
	#Legal, Anti Terror, etc.
	org = ''
	#Lt., Sgt., etc.
	position = ''
	#precint or boro
	location = ''
	name = ''
	shield = ''
	taxid = ''
	remainder = ''
	precinct = ''

	#Remove non-humans and unidentified umans
	if (re.search('CITY OF NEW YORK', defendant)
	or re.search('UNIDENTIFIED', defendant)
	or re.search('JANE DOE', defendant)
	or re.search('JOHN DOE', defendant)
	or defendant.startswith("THE" or "the" or "The")):
		return


	#let's make our components and clean them up
	components = re.split('[,|;|\(|\)]', defendant)
	components = filter(None, components)
	components = map(str.strip, components)

	remainders = components[:]


	for c in components:
		#check for shield #
		if re.search('shield|SHIELD|Shield', c):
			shield = re.findall('[0-9]{2,5}', c)
			remainders.remove(c)
		
		#check for tax ID #
		if re.search('tax|TAX|Tax', c):
			taxid = re.findall('[0-9]{6}', c)
			remainders.remove(c)
		
		#check for position
		if lookup_position(c):
			#lookup_posittion returns a tuple: 
			#(standard position, position in value that matched)
			position = lookup_position(c)[0]
			match = lookup_position(c)[1]
			remainder = re.sub(match.lower(), '', c.lower()).lstrip().rstrip()
			remainders.remove(c)
			remainders.append(remainder.title())

		#lookup precinct
		if 'precinct' in c.lower():
			precinct = re.findall('[0-9]{1,4}[a-zA-Z]{2}', c)
			remainders.remove(c)

	check = nltk_ner(remainders)
	if check[0] == True:
		name = check[1]
		remainders.remove(check[2])

	

	print "Initial: ", components
	if name: print "\t name:", name
	if shield: print "\t shield:", shield
	if taxid: print "\t taxid:", taxid
	if position: print "\t position:", position
	if precinct: print "\t precinct:", precinct
	if remainders: print "Remainders:", remainders
	print "*"*10

			
def lookup_position(defendant=None):
	abb2pos = {
		'Assistant Chief': ['Assistant Chief'],
		'Assistant Chief Chaplain': ['Assistant Chief Chaplain'],
		'Assistant Chief Surgeon': ['Assistant Chief Surgeon'],
		'Bureau Chief': ['Bureau Chief'],
		'Cadet': ['Cadet'],
		'Captain': ['Captain'],
		'Chaplain': ['Chaplain'],
		'Chief of Department': ['Chief of Department'],
		'Commissioner': ['Commissioner'],
		'Deputy Chief': ['Deputy Chief'],
		'Deputy Chief Chaplain': ['Deputy Chief Chaplain'],
		'Deputy Commissioner': ['Deputy Commissioner'],
		'Deputy Inspector': ['Deputy Inspector'],
		'Detective': ['Detective'],
		'District Surgeon': ['District Surgeon'],
		'Inspector': ['Inspector'],
		'Lieutenant': ['Lieutenant', 'LT.', 'LT', 'LIEUT.', 'LIEUT'],
		'Police Officer': ['Police Officer', 'NYPD Officer'],
		'Police Surgeon': ['Police Surgeon'],
		'Recruit Officer': ['Recruit Officer'],
		'Sergeant': ['Sergeant', 'SGT.', 'NYPD Sergeant'],
		'Supervising Chief Surgeon': ['Supervising Chief Surgeon']
	}

	for key in abb2pos:
		for abb in abb2pos[key]:
			if abb.lower() in defendant.lower():
				return key, abb
	return None

def check_for_name(remainders):
	'''Functions tries to determine if a compnent is a name
	It needs to return '''

	engine = create_engine('sqlite:///names.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	for item in remainders:
		for word in re.split("[ ]*", item):
			instance = names.Names.checkName(session, word.title())
			#print word, instance #wow, wording
			if instance:
				return item, True
			else:
				return item, False

	session.commit()



def nltk_ner(remainders):
	st = StanfordNERTagger('../stanford-ner/english.all.3class.distsim.crf.ser.gz', '../stanford-ner/stanford-ner.jar') 
	for item in remainders:
		name = ""
		tagged = st.tag(item.split())
		for entity in tagged:
			if entity[1] == u'PERSON':
				name += (entity[0].title() + ' ')
		if name: 
			return True, name, item
		else:
			return False, name, item


def nb_names():
	#generate list of tuple names
	engine = create_engine('sqlite:///names.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	db_names = names.Names.getAllNames(session)
	names_list = [(x,'name') for x in db_names]
	words_list = generate_words()
	sample_names = [names_list[i] for i in sorted(random.sample(xrange(len(names_list)), len(words_list)))]

	data = sample_names + words_list
	shuffled_data = np.random.permutation(data)
	strings = []
	classification = []
	for item in shuffled_data:
		strings.append([item[0]])
		classification.append(str(item[1]))


	X = np.array(strings)
	Y = np.array(classification)

	print X,Y
	clf = GaussianNB()
	clf.fit(X, Y)
	


def generate_words():
	data_dir ='../data/words'
	words = []
	for filename in os.listdir(data_dir):
		#ignore .ds_store & other files
		if not filename.startswith('.') and os.path.isfile(os.path.join(data_dir, filename)):
			f = open(os.path.join(data_dir,filename),'r')
			string = f.read()
			for word in string.split():
				if word in words:
					continue
				words.append(word.strip(',').lower())
	words_list = [(x,'word') for x in words]
	return words_list



if __name__ =='__main__':
    #read_files()
    #nltk_ner('a')
    #lookup_position('NYPD OFFICER JOHN MARTINEZ')
    nb_names()
    

