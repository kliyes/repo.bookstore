/*!
 * Book Store v1.0
 *
 * Copyright 2013 YANG.LYU, Inc
 * http:www.yanduren.com
 *
 * NOTICE!! DO NOT USE ANY OF THIS CODE
 * IT'S ALL JUST JUNK FOR OUR ITEM!
 * 
 */

// REGISTER EVENT
$(document).ready(function(){
	
	// 展开或伸缩书籍类型列表
	$("#extend_type").bind("click",function(){
		extend_type(this);
	});
	
	// 推荐列表聚焦
	$(".books-recommend-ul").bind("mouseenter",function(){
		recommend_focus(this);
		pause_auto_loop(this);
	});
	$(".books-recommend-ul").bind("mouseleave",function(){
		continue_auto_loop();
	});
	
	recommend_auto_loop();
});

// 展开或伸缩书籍类型列表
var extend_type_static = 0;
var extend_type = function(o){
	//检测 动画状态
	if(extend_type_static!=0)
	return;
	extend_type_static = 1;
	//检测 .booktype-other 状态
	if($(".booktype-other").css('display')=="none"){
		//展开
		$(".booktype-other").show("slow",function(){
			//更改状态
			extend_type_static = 0;
			$(o).removeClass("box-next").addClass("box-next-close");
		});
	}else{
		//回收
		$(".booktype-other").hide("slow",function(){
			$(o).removeClass("box-next-close").addClass("box-next");
			extend_type_static = 0;
		});
	}
}

// 推荐列表聚焦
var recommend_focus = function(o){
	//获取当前书籍信息
	var bookuid = $(o).attr("data-bookuid");
	response_book_info(bookuid);
	//改变当前选中项的状态
	$(o).addClass("active").siblings().removeClass('active');
}
//获取当前书籍信息
var response_book_info = function(o){
	$("#book_name").html($("#name_"+o).html());
	$("#book_author").html($("#author_"+o).html());
	$("#book_desc").html($("#desc_"+o).html());
	$("#book_pic").attr("src", ($("#pic_"+o).attr("src")));
}
//推荐聚焦自动轮询
var recommend_auto_loop = function(){
	//获取 .books-recommend-ul 数量
	var count = $(".books-recommend-ul").size();
	for(var j = 0; j <= count; j++){
		$($(".books-recommend-ul")[j]).attr("data-auto-loop",j);
	}
	$($(".books-recommend-ul")[0]).addClass('active').siblings().removeClass('active');
	auto_loop_base('s');
}
//暂停轮询	-- 鼠标移上其中一个推荐项时 停止轮询
var correct_loop = null;
var pause_auto_loop = function(o){
	correct_loop =$(o).attr('data-auto-loop');
	clearInterval(auto_loop);
}
//继续轮询  -- 鼠标移开后从记录的位置继续开始轮询
var continue_auto_loop = function(){
	auto_loop_base('c');
}
var auto_loop = null;
var auto_i = 0;
var auto_loop_base = function(o){
	//获取 .books-recommend-ul 数量
	var count = $(".books-recommend-ul").size();
	//为第i添加 .active 样式
	if(o=='c'){
		auto_i = correct_loop;
		correct_loop = null;
	}else if(o=='s'){
		auto_i = parseInt(auto_i);
		var uid = $($(".books-recommend-ul")[auto_i]).attr("data-bookuid");
		response_book_info(uid);
		auto_i += 1;
	}
	auto_loop = setInterval(function(){
		$($(".books-recommend-ul")[auto_i]).addClass('active').siblings().removeClass('active');
		var uid = $($(".books-recommend-ul")[auto_i]).attr("data-bookuid");
		response_book_info(uid);
		auto_i = parseInt(auto_i);
		auto_i += 1;
		if(auto_i>=count){
			auto_i = 0;
		}
	},3000);
}
