
$(document).ready(function() {
    $("#recommend").click(function () {
      if($('input:checkbox[name=recommend]').is(':checked')&&document.getElementById('message').value.indexOf("[Recommend]")<0) 
        document.getElementById('message').value = '[Recommend] '+document.getElementById('message').value;
      if(!$('input:checkbox[name=recommend]').is(':checked')&&document.getElementById('message').value.indexOf("[Recommend]")>-1) 
        document.getElementById('message').value = document.getElementById('message').value.substring(12);
    });  


      onClickMehthod = function(send_hour,send_min,send_sec){  
    
//calculate the time to start to watch video
  var click_time = new Date();
  var click_hour = click_time.getHours();
  var click_minute = click_time.getMinutes(); 
  var click_second = click_time.getTime() % 60000;//returns the number of milliseconds
  //change to seconds
  click_second= (click_second - (click_second % 1000))/1000;  
  
  var video_duration = parseInt(player.getCurrentTime());
  // player.seekTo(video_duration, true); 
  
  // var send_hour = document.getElementById("send_hour").value;
  // var send_min = document.getElementById("send_min").value;
  // var send_sec = document.getElementById("send_sec").value;

  console.log(send_hour);
  console.log(send_min);
  console.log(send_sec);

  console.log(click_hour);
  console.log(click_minute);
  console.log(click_second);
  console.log(video_duration);
  
      
  var watch_time = video_duration - (3600*parseInt(click_hour) +60*parseInt(click_minute) + parseInt(click_second) - 3600*parseInt(send_hour) - 60*parseInt(send_min) - parseInt(send_sec)); //（）里还要减去comment时间！
  console.log(watch_time);
  
  /*alert(click_time);*/
  player.seekTo(watch_time, true); 
    
    }; 
  /*Google Channel Api default start*/
  var chat_token = document.getElementById("token").value;
  var content = document.getElementById("content").value;

  $('#main').append(content);

  var channel = new goog.appengine.Channel(chat_token);
  var socket = channel.open();
  socket.onopen = function() {};


  /*update chat room msg from Channel Api*/
  socket.onmessage = function(m) {
    var data = $.parseJSON(m.data);
    console.log(data['html']);
    $('#main').append(data['html']);
    
  
  //control to watch video from recommended time 
    
    document.getElementById('container').scrollTop = document.getElementById('container').scrollHeight;
	
  };

  /*Google Channel Api default error msg*/
  socket.onerror = function(err) {
    alert("Error:" + err.description);
  };

  /*Google Channel Api default end*/
  socket.onclose = function() {};

  $("#clearBtn").on("click", clearbtn);


  /*Send chat message*/
  $("#target").submit(function(event) {
    event.preventDefault();
    $("#recommend").attr("checked",false);
    var success = validateData();
    if (success)
      sendData();
    return false;
  });
});

/*escape string prevent XSS*/

function validateData() {
  var escapemessage = encodeURI(document.getElementById("message").value);
  var tmpmsg;
  if(escapemessage=="") return false;
  else{
  tmpmsg=escapemessage.replace(/%20/g, " ");
  tmpmsg=tmpmsg.replace(/%25/g, "%");
  //tmpmsg=tmpmsg.replace(/%E2/%80/%A6/g, "");
  tmpmsg=tmpmsg.replace(/%5E/g, "^");
  tmpmsg=tmpmsg.replace(/%7C/g, "|");
  tmpmsg=tmpmsg.replace(/%5B/g, "[");
  tmpmsg=tmpmsg.replace(/%5D/g, "]");
  tmpmsg=tmpmsg.replace(/%7B/g, "{");
  tmpmsg=tmpmsg.replace(/%7D/g, "}");
  //tmpmsg=tmpmsg.replace(/%3C/g, "<");
  //tmpmsg=tmpmsg.replace(/%3E/g, ">");
  tmpmsg=tmpmsg.replace(/%22/g, '"');
  document.getElementById("message").value = tmpmsg;
  console.log(document.getElementById("message").value);
  return true;
  }
}

function sendData() {
  /*send chat message using ajax*/
  $.ajax({
    type: "POST",
    dataType: "html",
    url: "/post/",
    data: $("#target").serialize(),
    success: function(data) {
      var strresult = data;
    },
    error: function(data) {
      alert("error:" + data.responseText);
    }
  });
  /*clear up text box after send message*/
  document.getElementById("message").value = null;
  document.getElementById("message").placeHolder = "Enter to send";
}

/*clear chat room msg*/
function clearbtn() {
  document.getElementById('main').innerHTML = '';
}



