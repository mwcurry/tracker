"""
Script to convert the wikipedia list of 
NYPD positions to a dictionary for later use
"""

import pprint

s = '''	Chief of Department	
	Bureau Chief
	Supervising Chief Surgeon	
	Assistant Chief
	Assistant Chief Chaplain
	Assistant Chief Surgeon	
	Deputy Chief
	Deputy Chief Chaplain
	District Surgeon	
	Inspector
	Chaplain
	Police Surgeon	
	Deputy Inspector	
	Captain	
	Lieutenant	
	Sergeant	
	Detective
	Police Officer	
	Recruit Officer
	Cadet'''

d = {}

for position in s.split('\n'):
	position = position.strip()
	d[position] = [position]

pprint.pprint(d)
