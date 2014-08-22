from app import app
from flask import render_template, json, jsonify, request, Response

## DATABASE CONNECTION ##
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import BSON
from bson import json_util
client = MongoClient()
db = client.worldGenDB
questionColl = db.questions
tokenColl = db.tokens

#-------------------BROWSER NAVIGATION ROUTES-------------------#

@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Miguel' }
    posts = [
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template("index.html",
        title = 'Home',
        user = user,
        posts = posts)

### Creating a community
@app.route('/gen')
def gen():
	return render_template("gen.html")
	
### Submission screen
@app.route('/submit')
def submit():
	return render_template("submit.html")
	
### Admin ##########
@app.route('/admin')
def admin():
	questions = questionColl.find()
	tokens = tokenColl.find().sort("position", -1)
	return render_template("admin.html", title = 'Administration', questions = list(questions), tokens = list(tokens))
	
#-------------------FUNCTIONAL ROUTES-------------------#

### GET Return all QUESTIONS JSON ############
@app.route('/api/questions', methods=['GET'])
def questions():
	data = questionColl.find()
	return Response(json.dumps(list(data), indent=4, default=json_util.default),  mimetype='application/json')

### GET a single QUESTION ###############################
@app.route('/api/question/<questionid>', methods=['GET'])
def getQuestion(questionid):
	data = questionColl.find_one({"_id" : ObjectId(questionid)})
	return Response(json.dumps(data, indent=4, default=json_util.default),  mimetype='application/json')

### POST Add a new QUESTION ################
@app.route('/newQuestion', methods=['POST'])
def newQuestion():
	content = request.get_json(force=True)
	newPosition = questionColl.count()
	content['position'] = newPosition
	print "content ---"
	print type(content)
	print content
	print "--- content"
	newTokenID = questionColl.insert(content)
	return 'Inserted question ID: ' + str(newTokenID)
	
### GET Return all TOKENS JSON ############
@app.route('/api/tokens', methods=['GET'])
def tokens():
	data = tokenColl.find()
	return Response(json.dumps(list(data), indent=4, default=json_util.default),  mimetype='application/json')


### POST Add a new TOKEN ################
@app.route('/newToken', methods=['POST'])
def newToken():
	content = request.get_json(force=True)
	newPosition = tokenColl.count()
	content['position'] = newPosition
	print "content ---"
	print type(content)
	print content
	print "--- content"
	newTokenID = tokenColl.insert(content)
	return 'Inserted: ' + str(newTokenID)


### DELETE a QUESTION or TOKEN ################################
@app.route('/api/<resourceType>/<tokenid>', methods=['DELETE'])
def removeToken(resourceType,tokenid):
	dropID = tokenid
	if (resourceType == "token"):
		remove = db.tokens.remove({"_id" : ObjectId(dropID)}, True)
		return 'Attempting to remove token ' + dropID
		
	else:
		if (resourceType == "question"):
			remove = db.questions.remove({"_id" : ObjectId(dropID)}, True)
			return 'Attempting to remove question ' + dropID
			print remove
		else:
			return 'DELETE received with wrong resource type.'


