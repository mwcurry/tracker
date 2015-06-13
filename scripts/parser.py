import os
import re
import nltk
from nltk.tag.stanford import NERTagger
from nameparser import HumanName

data_dir ='../data/'

def read_files():
	for filename in os.listdir(data_dir):
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

	#our beautiful regex
	defendant_semi_re = ';(?![^()]*\))'
	defendant_comma_re = ', (?![^()]*\))'

	if re.search(defendant_semi_re, string):
		for item in string.split(';'):
			parse_defendant(item)
	else:
		for item in re.split(defendant_comma_re, string):
			parse_defendant(item)


def parse_defendant(defendant):
	'''
	Take a defendant (a single line comprised of many components)
	and break down those components to bucket them
	'''
	shield_re ='((Shield|SHIELD|shield).*[0-9]{4})'
	tax_re ='((tax|Tax|TAX).*[0-9]{6})'
	rank =''
	position =''
	name =''
	shield =''
	taxid =''

	#Remove non-humans and unidentified umans
	if (re.search('CITY OF NEW YORK', defendant)
	or re.search('UNIDENTIFIED', defendant)
	or re.search('JANE DOE', defendant)
	or re.search('JOHN DOE', defendant)):
		return


	#let's make our components and clean them up
	components = re.split('[,|;|\(|\)]', defendant)
	components = filter(None, components)
	components = map(str.strip, components)

	print components

	for c in components:
		#check for shield #
		if re.search('shield|SHIELD|Shield', c):
			shield = re.findall('[0-9]{2,5}', c)
		
		#check for tax ID #
		if re.search('tax|TAX|Tax', c):
			taxid = re.findall('[0-9]{6}', c)
		
		#check for position
		if lookup_position(c):
			#lookup_posittion returns a tuple: 
			#(standard position, position in value that matched)
			position = lookup_position(c)[0]
			match = lookup_position(c)[1]
			remainder = re.sub(match.lower(), '', c.lower()).lstrip().rstrip()
			
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
		'Sergeant': ['Sergeant'],
		'Supervising Chief Surgeon': ['Supervising Chief Surgeon']
	}

	for key in abb2pos:
		for abb in abb2pos[key]:
			if abb.lower() in defendant.lower():
				return key, abb
	return None

def nameTagger(component):
	name = HumanName(component)
	print name

'''def classify_names(name):
	st = NERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
	text = """YOUR TEXT GOES HERE"""

	for sent in nltk.sent_tokenize(text):
	    tokens = nltk.tokenize.word_tokenize(sent)
	    tags = st.tag(tokens)
	    for tag in tags:
	        if tag[1]=='PERSON': print tag'''

if __name__ =='__main__':
    #read_files()
    #lookup_position('NYPD OFFICER JOHN MARTINEZ')
    nameTagger('JOHN MARTINEZ')

