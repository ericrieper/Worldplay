from app import app
from flask import render_template, json, jsonify, request, Response
import pprint
pp = pprint.PrettyPrinter(indent=4)

## DATABASE CONNECTION ##
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import BSON, json_util
client = MongoClient()
db = client.worldGenDB
questionColl = db.questions
tokenColl = db.tokens
cityColl = db.cities

#-------------------FUNCTIONS-------------------#

def makeJSON(data):
	return Response(json.dumps(data, indent=4, default=json_util.default),  mimetype='application/json')
	
def getScores(cityID):
	cityData = cityColl.find_one({"_id" : ObjectId(cityID)})
	answerCount = len(cityData['answers'])
	scores = []
	

	# FOR EACH ANSWER
	for answer in cityData['answers']:
		tokenScore = 0
		questionID = answer['question']
		response = answer['response'];
		questionData = questionColl.find_one({"_id" : ObjectId(questionID)})

		# FOR EACH TOKEN LINKED TO ANSWER
		for token in questionData['questionTokens']:
			currentTokenID = token['tokenID']
			tokenName = tokenColl.find_one({'_id' : ObjectId(currentTokenID)})['name']
			
			if (response == 0):
				scoreChange = int(token['tokenValueNo'])
			elif (response == 1):
				scoreChange = int(token['tokenValueYes'])

			for s in scores:
			    if s['scoreTokenID'] == currentTokenID:
			        s['score'] += scoreChange
			        s['percent'] = getPercent(s['score'],answerCount)
			        break
			else:
			    scores.append({'scoreTokenID' : currentTokenID, 'name' : tokenName, 'score' : scoreChange, 'percent' : getPercent(scoreChange,answerCount)})
	#print "SCORES:\n"
	#pp.pprint(scores)
	return scores

def getPercent(s,totalAnswers):
	maxScore = totalAnswers * 5
	scorePercent = ( (s+maxScore) / float((maxScore*2)) )*100
	return scorePercent
	
def getRounds():
	rounds = db.settings.find_one({"setting": "rounds"})['value'];
	return rounds


#-------------------BROWSER NAVIGATION ROUTES-------------------#

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title = 'Home')

### Creating a community
@app.route('/gen')
def gen():
	return render_template("gen.html")
	
### View City
@app.route('/city/<cityid>', methods=['GET'])
def cityView(cityid):
	data = cityColl.find_one({"_id" : ObjectId(cityid)})
	return render_template("city.html", title = 'City View', city = data)
	
### Admin ##########
@app.route('/admin')
def admin():
	questions = questionColl.find()
	tokens = tokenColl.find().sort("position", -1)
	cities = cityColl.find()
	return render_template("admin.html", title = 'Administration', questions = list(questions), tokens = list(tokens), cities = list(cities), rounds = getRounds())
	
#-------------------FUNCTIONAL ROUTES-------------------#
	
### GET return all CITIES JSON #######
@app.route('/api/cities', methods=['GET'])
def getCities():
	data = cityColl.find()
	return makeJSON(list(data))

### POST Add a new CITY ################
@app.route('/api/city', methods=['POST'])
def newCity():
	content = request.get_json(force=True)
	newTokenID = cityColl.insert(content)
	return str(newTokenID)
	
### GET return a single CITY JSON #######
@app.route('/api/city/<cityid>', methods=['GET'])
def getCity(cityid):
	data = cityColl.find_one({"_id" : ObjectId(cityid)})
	return makeJSON(data)

### GET Return all QUESTIONS JSON ############
@app.route('/api/questions', methods=['GET'])
def questions():
	data = questionColl.find().limit(getRounds())
	return makeJSON(list(data))
	
### GET a single QUESTION ###############################
@app.route('/api/question/<questionid>', methods=['GET'])
def getQuestion(questionid):
	data = questionColl.find_one({"_id" : ObjectId(questionid)})
	return makeJSON(data)

### POST Add a new QUESTION ################
@app.route('/newQuestion', methods=['POST'])
def newQuestion():
	content = request.get_json(force=True)
	newPosition = questionColl.count()
	content['position'] = newPosition
	newTokenID = questionColl.insert(content)
	return 'Inserted question ID: ' + str(newTokenID)
	
### GET Return all TOKENS JSON ############
@app.route('/api/tokens', methods=['GET'])
def tokens():
	data = tokenColl.find()
	return makeJSON(list(data))

### POST Add a new TOKEN ################
@app.route('/newToken', methods=['POST'])
def newToken():
	content = request.get_json(force=True)
	newPosition = tokenColl.count()
	content['position'] = newPosition
	newTokenID = tokenColl.insert(content)
	return 'Inserted: ' + str(newTokenID)

### DELETE a RESOURCE ################################
@app.route('/api/<resourceType>/<tokenid>', methods=['DELETE'])
def removeToken(resourceType,tokenid):
	dropID = tokenid
	if (resourceType == "token"):
		remove = db.tokens.remove({"_id" : ObjectId(dropID)}, True)
		return 'Attempting to remove token ' + dropID
	elif (resourceType == "city"):
		remove = db.cities.remove({"_id" : ObjectId(dropID)}, True)
		return 'Attempting to remove city ' + dropID
	else:
		if (resourceType == "question"):
			remove = db.questions.remove({"_id" : ObjectId(dropID)}, True)
			return 'Attempting to remove question ' + dropID
		else:
			return 'DELETE received with wrong resource type.'
			
### PUT Update total questions asked ############
@app.route('/totalQuestions', methods=['PUT'])
def totalQuestions():
	content = request.get_json(force=True)
	questionsAsked = content['questions']
	db.settings.update({"setting": "rounds"}, {"$set": {"value": int(questionsAsked)}})
	return str(getRounds())