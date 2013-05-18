$(document).ready(function(e) {
    addressInfoShow();
	addressInfoClose();
	passwordInfo();
	passwordInfoClose();
});

var addressInfoShow = function(){
	showSys("#edit_address","#old_address_info","#new_address_info",addressInfoCallBack);
}
var addressInfoCallBack = function(){
	$("#edit_address").fadeOut(300,function(){
		$("#edit_done_address").fadeIn(300);
	});
}
var addressInfoClose = function(){
	showSysClose("#edit_done_address","#old_address_info","#new_address_info",addressInfoCloseCallBack);
}
var addressInfoCloseCallBack = function(){
	$("#edit_done_address").fadeOut(300,function(){
		$("#edit_address").fadeIn(300);
	});
}
var passwordInfo = function(){
	showSys("#edit_passwod","#none_password","#new_password",passwordInfoCallBack);
}
var passwordInfoCallBack = function(){
	$("#edit_passwod").fadeOut(300,function(){
		$("#edit_done_password").fadeIn(300);
	});
}
var passwordInfoClose = function(){
	showSysClose("#edit_done_password","#none_password","#new_password",passwordInfoCloseCallBack);
}
var passwordInfoCloseCallBack = function(){
	console.log(12);
}

var showSys = function(o1,o2,o3,callback){
	$(o1).bind("click",function(){
		$(o2).slideUp(300,function(){
			$(o3).slideDown(300,callback);
		});
		return false;
	});
};

var showSysClose = function(o1,o2,o3,callback){
	$(o1).bind("click",function(){
		$(o3).slideUp(300,function(){
			$(o2).slideDown(300,callback);
		});
		return false;
	});
};