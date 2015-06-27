import os
import re
import codecs
from sqlalchemy import Column, Float, Text, ForeignKey
from sqlalchemy import exists, update, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, load_only
from sqlalchemy import create_engine


Base = declarative_base()

class Names(Base):
	__tablename__ = 'names'
	name = Column(Text, primary_key=True)
	occurances = Column(Float)

	@classmethod
	def addYear(class_, year):
		for name in year:
			instance = session.query(Names).filter(Names.name == name).first()
			if instance:
				Names.name.occurances += year[name]
			else:
				new_name = Names()
				new_name.name = name
				new_name.occurances = year[name]
				session.add(new_name)
		session.commit()


	@classmethod
	def getOccurances(class_, name):
		instance = session.query(Names).filter(Names.name == name).first()
		if instance:
			return instance.occurances

	@classmethod
	def getAllNames(class_, session):
		instance = session.query(Names).options(load_only("name")).all()
		names = []
		for name in instance:
			names.append(name.name)
		return names

	@classmethod
	def checkName(class_, session, name):
		instance = session.query(Names).filter(Names.name == name).first()
		if instance:
			return True
		else:
			return False

def generate_census_names():
	names = {}
	for filename in os.listdir(data_dir):
		f = open(os.path.join(data_dir,filename),'r')
		for line in f:
			name, gender, occurances = line.split(',')
			names[name] = occurances

	Names.addYear(names)
	


if __name__ =='__main__':
	data_dir ='../data/name/census/'
	engine = create_engine('sqlite:///names.db')
	Base.metadata.create_all(engine)
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	#generate_census_names()
	#Names.getOccurances('Mary')
	print Names.checkName(session, 'Raymond')