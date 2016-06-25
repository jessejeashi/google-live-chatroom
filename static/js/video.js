
$(document).ready(function(){
    console.log("ready!");

// JavaScript Document
var id = document.getElementById("url").value;


$.getJSON('https://www.googleapis.com/youtube/v3/videos?id='+id+'&key=AIzaSyDkIF8D2RE_msM5W1AVi4hxl8dju1BKesk&&part=snippet,contentDetails,statistics,status',function(data){
     
 if (typeof(data.items[0]) != "undefined") {
/*   console.log('video exists');
     console.log('title: '+ data.items[0].snippet.title);
     console.log('description: '+ data.items[0].snippet.description);
     console.log('duration: '+ data.items[0].contentDetails.duration);*/
	 document.getElementById("title").innerHTML = data.items[0].snippet.title ;
	 document.getElementById("video_description").innerHTML = data.items[0].snippet.description;
 }   
});



    
});


