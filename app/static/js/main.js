// On page ready
Zepto(function($){
	$('.preFolded').hide();
	getQuestions();
	getTokens();
	$('#beginButton').on('click',function(e){
		begin();
	});
	$('#noButton').on('click',function(e){answerQuestion(0)});
	$('#yesButton').on('click',function(e){answerQuestion(1)});
	
	$('#cityName').keyup(function(e){
    if(e.keyCode == 13)
    {
        begin();
		e.preventDefault();
    }
	})
})

function begin(){
	genName = $('#cityName').val();
	if (genName == ""){genName = "My City";}
	navigate('/gen')
}

// Ajax GET for dynamic content container
function navigate(route){
	dip('#mainContainer',0);
	$('#mainContainer').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
		$.get(route, function(response){
			$('#activeContainer').html(response);
			if(route == "/gen"){
				$('#cityVis h3').html(genName);
				for(i = 0; i < totalTokens; i++){
					var tokenName = tokens[i].name;
					var tokenID = tokens[i]._id.$oid;
					var tokenHTML = '<li id="bar-'+tokenID+'"><span>'+tokenName+'</span></li>';
					$('#cityVis ul').append(tokenHTML);
				}
				displayQuestion();
				$('#bottomFunctions').addClass('animated fadeIn');
				$('#bottomFunctions').removeClass('hidden');
			}
			else {updateContent(response)}
			dip('#mainContainer',1);
		})
	})
}

// Fade element in / out
function dip(el,dir){
	
	if (dir == 0){
		$(el).removeClass('fadeIn');
		$(el).addClass('animated fadeOut');
	}
	else if (dir == 1){
		$(el).removeClass('fadeOut');
		$(el).addClass('animated fadeIn junks');
	}
}

function updateContent(data){
	
}




/*-------------------GENERATION VIEW-------------------*/

var tokens;
var totalTokens = 0;
var clientQuestions = [];
var currQuestion = 0;
var totalQuestions = 0;
var clientAnswers = [];
var genName = "New City";
var scores = [];


function getQuestions(){
	$.getJSON('/api/questions', function(data){
		clientQuestions = data;
		totalQuestions = clientQuestions.length;
	})
}

function getTokens(){
	$.getJSON('/api/tokens', function(data){
		tokens = data;
		totalTokens = tokens.length;
	})
}

function debugClient(){
	$('#debug').html(JSON.stringify(clientAnswers));
}

function displayQuestion() {
	var q = $('#questionDisplay');
	q.addClass('animated fadeOut');
	q.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
		q.html(clientQuestions[currQuestion].questionText);
		q.removeClass('animated fadeOut');
		q.addClass('animated fadeIn');		
	});
}

function answerQuestion(response){
	data = {'question' : clientQuestions[currQuestion]._id.$oid, 'response' : response};
	clientAnswers.push(data);
	debugClient();
	updateBars();
	currQuestion++;
	if (currQuestion < totalQuestions){displayQuestion()}
	else {displaySubmit()}
}

function updateBars(){
	scores = [];
	for (i = 0; i < totalTokens; i++){ // CREATE SCORE OBJECTS
		scores.push({
		'tID' : tokens[i]._id.$oid,
			'name' : tokens[i].name,
			'percent' : 0,
			'score' : 0
		});
	}
	
	for (i = 0; i < clientAnswers.length; i++){ // FOR EACH ANSWERED QUESTION
		for (t = 0; t < totalTokens; t++) { // FOR EACH TOKEN

			if (clientAnswers[i].response == 0){ // ANSWER WAS NO
				var tokenNoVal = parseInt(clientQuestions[i].questionTokens[t].tokenValueNo);
				scores[t].score += tokenNoVal;
			}
			else {
				var tokenYesVal = parseInt(clientQuestions[i].questionTokens[t].tokenValueYes);
				scores[t].score += tokenYesVal;
			}
		}
	}
	// DONE TABULATING, UPDATE BARS
	for (i = 0; i < scores.length; i++){ // FOR EACH SCORE
		var maxScore = totalQuestions * 5;
		var scorePercent = ((scores[i].score+maxScore) / (maxScore*2))*100;
		scores[i].percent = scorePercent;
		$('#bar-'+scores[i].tID + " span").width(scorePercent+'%')
	}
} // END of updateBars()


function displaySubmit(){
		
		dip('#bottomFunctions',0);
		$('#bottomFunctions').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
			submitGen();	
		})

}

/*-------------------SUBMISSION VIEW-------------------*/

function submitGen(){
	var data = {'cityName' : genName, 'answers' : clientAnswers, 'scores' : scores};
	$.post('/api/city', JSON.stringify(data), function(response){
		var newLoc = "/city/"+response;
		window.location.assign(newLoc);
	})
	
}

/*-------------------ADMIN VIEW-------------------*/

// Display toggler
function display(eid){
	$('#'+eid).toggle();
}

$('.qView').on('click',function(e){
	eid = $(this).attr('id').slice(3);
	console.log('eid: ' + eid);
	display('qD-'+eid);
})

// Update slider box
$('.tokenValueInput').change(function(e){
	var yn = $(this).attr('name').slice(0,1);
	var sliderID = $(this).attr('name').slice(2);
	$('#'+yn+'Val-'+sliderID).html($(this).val());
})

$('#qSlider').change(function(e){
	var newAmount = $(this).val();
	var data = JSON.stringify({'questions' : newAmount});
	$('#qSliderDisp').html($(this).val());
	
	$.ajax({
		url: '/totalQuestions',
		type: 'PUT',
		data: data,
		success: function(data) {
			$('#qSliderDisp').addClass('animated flash');			
			$('#qSliderDisp').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
				$('#qSliderDisp').removeClass('flash');
			})
		}
	});

})

//////////// QUESTIONS ///////////////////

// Save a new QUESTION to the DB
$('#newQuestionForm').submit(function(e){
	e.preventDefault();
	var questionText = $('#tokenTextInput').val();
	var questionTokens = [];
	$('.tokenValueInput').each(function(index,item){
		var itemID = $(item).attr('name').slice(2);
		var itemValueNo = $(item).val();
		var itemValueYes = $('#ySlider-'+itemID).val();
		var newItem = {'tokenID' : itemID , 'tokenValueNo' : itemValueNo,  'tokenValueYes' : itemValueYes}
		questionTokens.push(newItem);
	})
	
	var data = {'questionText' : questionText, 'questionTokens' : questionTokens};
	
	$.post('/newQuestion', JSON.stringify(data), function(response){
		//alert(JSON.stringify(response));
		location.reload();
	})
})


//////////// TOKENS ///////////////////

// Save a new TOKEN to the DB
$('#newTokenForm').submit(function(e){
	e.preventDefault();
	var data = getFormData($('#newTokenForm'));
	var formData = JSON.stringify(data);
	
	$.post('/newToken', formData, function(response){
		//alert(JSON.stringify(response));
		location.reload();
	})

})

// Remove existing TOKEN from DB
$('.remover').on('click',function(e){
	var dropID;
	dropID = $(this).attr("id");
	dropID = dropID.slice(5);
	var resourceType;
	if ($(this).hasClass("tokenDel")){resourceType = "token"}
	else if ($(this).hasClass("questionDel")){ resourceType = "question"}
	else if ($(this).hasClass("cityDel")){ resourceType = "city"}
	$.ajax({
	    url: '/api/'+resourceType+'/'+dropID,
	    type: 'DELETE',
	    success: function(result) {
	        //alert('Response: ' +result);
	        location.reload();
	    }
	});
})


/*------------------- HELPER FUNCTIONS -------------------*/
function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });
    return indexed_array;
}