from ..web import db

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)
    surname = db.Column(db.Text)
    shieldnum = db.Column(db.Integer)
    taxid = db.Column(db.Integer, unique=True)
    #Sgt, Lt, etc.
    title = db.Column(db.Text)
    location = db.Column(db.Text)
    precinct = db.Column(db.Text)
    borough = db.Column(db.Text)

class Docket(db.Model):
    id = db.Column(db.Text, primary_key=True)
    filed = db.Column(db.Text)
    url = db.Column(db.Text)
    nature = db.Column(db.Text)
    cause = db.Column(db.Text)
    county = db.Column(db.Text)
    office = db.Column(db.Text)
    court = db.Column(db.Text)

    judge = db.Column(db.Text)
    referring_judge = db.Column(db.Text)

    
    petitioner = db.Column(db.Text)
    respondent = db.Column(db.Text)
    
    claimant = db.Column(db.Text)
    cross_claimant = db.Column(db.Text)
    counter_claimant = db.Column(db.Text)
    
    amicus = db.Column(db.Text)
    intervenor = db.Column(db.Text)
    
    defendant = db.Column(db.Text)
    thirdparty_defendant = db.Column(db.Text)
    consolidated_defendant = db.Column(db.Text)
    counter_defendant = db.Column(db.Text)

    plaintiff = db.Column(db.Text)
    consolidated_plaintiff = db.Column(db.Text)
    cross_defendant = db.Column(db.Text)

    added = db.Column(db.DateTime)


    def __repr__(self):
        return '<Docket %r added on %r>' % (self.id, self.added)
   