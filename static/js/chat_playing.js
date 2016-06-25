

$(document).ready(function() {
	$("#publish").on("click", save1);
	$("#closechat").on("click", save1);
	$("#closedia").on("click", closedialog);
});


// Check
function check(){
	
	var nameCheck = true;
	var urlCheck = true;
	var deCheck = true;
	
	var nameV = document.getElementById("chat_name").value.length;
	if(nameV == 0){		
		nameCheck = false;
	}
	
    var urlV = document.getElementById("url").value.length;
	if(urlV == 0){		
		urlCheck = false;
	}
	
	var deV = document.getElementById("description").value.length;
	if(deV == 0){		
		deCheck = false;
	}  
	     
    if(nameCheck && urlCheck && deCheck){
	   return true;	
	   
	}else{
	   return false;	
	   
	}
}

// Publish 
 function save1(){	
	if(check()){
		document.getElementById("DivLocker").style.display="block";
        document.getElementById("upcontainer").style.display="block";	
		
	}	
}


// Closedialog
function closedialog(){
	document.getElementById("DivLocker").style.display="none";
	document.getElementById("upcontainer").style.display="none";
	window.location.reload();	
  }
  

