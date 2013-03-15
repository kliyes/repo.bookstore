/*
* 验证模块插件
* lvy
* 2012年11月12日
* 功能:Js验证区域模块化代码
* 返回数据：消息码 + 消息内容	//code暂时木有
* 基于Jquery
* tig:	bl代表绑定项，需要将提示显示在哪一个id上
*/

/*
 * 加载方法
 */
function lyu_load(){
	//绑定方法
	$("[lyu]").bind("blur",function(){
		//todo
		lyu_main(this)
	});
	$("[lyu]").bind("focus",function(){
		//todo
		var obj_bl = "#" + $(this).attr("bl");
		$(obj_bl).html("");
	});
}
/*
 * 入口
 */
function lyu_main(obj){
	//获取lyu 根据lyu分配方法
	switch($(obj).attr("lyu")){
		case"Email":
			check_email_lyu(obj);
		break;
		case"Password":
			check_password_lyu(obj);
		break;
		case"PasswordConfirm":
			check_passwordConfirm_lyu(obj);
		break;
		case"OldPassword":
			check_oldPassword_lyu(obj);
		break;
		case"NewPassword":
			check_newPassword_lyu(obj);
		break;
		case"NewPasswordConfirm":
			check_newPasswordConfirm_lyu(obj);
		break;
		case"NickName":
			check_nickName_lyu(obj);
		break;
		case"ActivityTitle":
			check_activityTitle_lyu(obj);
		break;
		case"ActivityAddress":
			check_activityAddress_lyu(obj);
		break;
		case"Money":
			check_money_lyu(obj);
		break;
		case"ActivityDesc":
			check_activityDesc_lyu(obj);
		break;
		case"ProfilesDesc":
			check_profilesDesc_lyu(obj);
		break;
		case"ProfilesWebSite":
			check_profilesWebSite_lyu(obj);
		break;
		case"ActivityStartDate":
			check_activityStartDate_lyu(obj);
		break;
		case"ActivityEndDate":
			check_activityEndDate_lyu(obj);
		break;
	}
}
/*
 * -公共方法-
 * -剔除空格-
 */
function trim(str){
	return str.replace(/(^\s*)|(\s*$)/g,"");
}
//检查字符串是否为空 true表示为空 false表示不为空
function isNull(value){
    if(trim(value)==""){
		 return true;
	}else{
		return false;
	}
}
//检查中英文个数
function ZE_len(obj) {
	var len = 0;
	var a = obj.split("");
	for (var i = 0; i < a.length; i++) {
		if (a[i].charCodeAt(0) < 299) {
			len++;
		} else {
			len += 2;
		}
	}
	return len;
}
// 检查字符串是否合法，不允许输入某些非法字符
function isValidString(value,pattern) {
    var str = trim(value);
    if(str == '') return false;
    //var pattern=/^[\u4E00-\u9FA5A-Za-z0-9_]+$/; //只允许输入中文，英文字母或数字
    var matchArray=str.match(pattern);
    if(matchArray != null) {
        return true;
    }
    return false;
}
/*
 * var pattern=/^\S+$/gi;  判断是否含有空格。
 */
//检查字符串中是否含有空格
function isValidKG(value){
	if(value.indexOf(" ")!=-1){
		//alert("密码不能包含空格");
        return false;
    }
    return true;
}
/*
 * -私有属性-
 * -正则表达-
 */
//Email
var Email_RegExp = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,4}$/;
var Email_minLen = 5;
var Email_maxLen = 30;
//Password
var password_minLen = 6;
var password_maxLen = 20;
//OldPassword
var oldPassword_minLen = 6;
var oldPassword_maxLen = 20;
//NewPassword
var newPassword_minLen = 6;
var newPassword_maxLen = 20;
//NewPasswordConfirm

//NickName	要区分中英文长度  汉字2字节 英文1字节
var nickName_RegExp = /^[\u4E00-\u9FA5A-Za-z0-9_]+$/;	//只允许 中文 英文 数字
var nickName_minLen = 6;
var nickName_maxLen = 15;
//activityTitle
var activityTitle_RegExp = /^[\u4E00-\u9FA5A-Za-z0-9_]+$/;	//只允许 中文 英文 数字
var activityTitle_minLen = 6;
var activityTitle_maxLen = 30;
//activityAddress
var activityAddress_RegExp = /^[\u4E00-\u9FA5A-Za-z0-9_]+$/;	//只允许 中文 英文 数字
var activityAddress_minLen = 10;
var activityAddress_maxLen = 30;
//money
var money_RegExp = /^[0-9_]+$/;	//只允许 数字
var money_minNum = 0;
var money_maxNum = 10000;
//activityDesc
var activityDesc_RegExp = "";
var activityDesc_minLen = 50;
var activityDesc_maxLen = 200;
//profilesDesc
var profilesDesc_RegExp = "";
var profilesDesc_minLen = 20;
var profilesDesc_maxLen = 200;
//profilesWebSite
var profilesWebSite_RegExp = /^[A-Za-z0-9]+$/;	//只允许  英文 数字
var profilesWebSite_minLen = 3;
var profilesWebSite_maxLen = 20;
//ActivityStartTime
//ActivityEndTime

//comment
var comment_RegExp = "";
var comment_minLen = 5;
var comment_maxLen = 200;
/*
 * Email 验证
 */
function check_email_lyu(obj){
	//1.
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	//2.
	if(isNull(obj_val)){
		$(obj_bl).html("邮箱不能为空");
		return false;
	}
    if(obj_val.length < Email_minLen){
    	$(obj_bl).html("邮箱字段不足" + Email_minLen + "位！");
    	return false;
    }
    if(obj_val.length > Email_maxLen){
    	$(obj_bl).html("邮箱字段大于" + Email_maxLen + "位！");
    	return false;
    }
    if(!isValidString(obj_val,Email_RegExp)){
		$(obj_bl).html("邮箱格式错误！");
		return false;
	}
    if(!isValidKG(obj_val)){
    	$(obj_bl).html("邮箱字段中不能包含空格！");
    	return false;
    }
    $(obj_bl).html("");
    return true;	
}
/*
 * Password 验证
 */
function check_password_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("密码不能为空");
		return false;
	}
	if(obj_val.length < password_minLen){
    	$(obj_bl).html("密码字段不足" + password_minLen + "位！");
    	return false;
    }
    if(obj_val.length > password_maxLen){
    	$(obj_bl).html("密码字段大于" + password_maxLen + "位！");
    	return false;
    }
    if(!isValidKG(obj_val)){
    	$(obj_bl).html("密码字段中不能包含空格！");
    	return false;
    }
    $(obj_bl).html("");
    return true;
}
/*
 * PasswordConfirm 验证
 */
function check_passwordConfirm_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("确认密码不能为空");
		return false;
	}
	if(obj_val != $("[lyu='Password']").val()){
		$(obj_bl).html("两次密码不同！");
		return false;
	}
	if(!isValidKG(obj_val)){
    	$(obj_bl).html("密码字段中不能包含空格！");
    	return false;
    }
	$(obj_bl).html("");
    return true;
}

/*
 * OldPassword 验证	作用于修改密码模块 输入老密码
 */
function check_oldPassword_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("旧密码不能为空");
		return false;
	}
	if(obj_val.length < oldPassword_minLen){
    	$(obj_bl).html("旧密码字段不足" + oldPassword_minLen + "位！");
    	return false;
    }
    if(obj_val.length > oldPassword_maxLen){
    	$(obj_bl).html("旧密码字段大于" + oldPassword_maxLen + "位！");
    	return false;
    }
    if(!isValidKG(obj_val)){
    	$(obj_bl).html("密码字段中不能包含空格！");
    	return false;
    }
    $(obj_bl).html("");
    return true;
}
/*
 * NewPassword 验证
 */
function check_newPassword_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("新密码不能为空");
		return false;
	}
	if(obj_val.length < newPassword_minLen){
    	$(obj_bl).html("新密码字段不足" + newPassword_minLen + "位！");
    	return false;
    }
    if(obj_val.length > newPassword_maxLen){
    	$(obj_bl).html("新密码字段大于" + newPassword_maxLen + "位！");
    	return false;
    }
    if(obj_val == $("[lyu='OldPassword']").val()){
    	$(obj_bl).html("新密码不能与旧密码相同！");
    	return false;
    }
    if(!isValidKG(obj_val)){
    	$(obj_bl).html("密码字段中不能包含空格！");
    	return false;
    }
    $(obj_bl).html("");
    return true;
}
/*
 * NewPasswordConfirm 新密码确认
 */
function check_newPasswordConfirm_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("密码确认项不能为空");
		return false;
	}
	if(obj_val != $("[lyu='NewPassword']").val()){
    	$(obj_bl).html("确认密码应与新密码保持一致");
    	return false;
    }
    if(!isValidKG(obj_val)){
    	$(obj_bl).html("密码字段中不能包含空格！");
    	return false;
    }
    $(obj_bl).html("");
    return true;
}
/*
 * NickName 验证
 */
function check_nickName_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("昵称不能为空");
		return false;
	}
	var len = ZE_len(obj_val);
	if(len < nickName_minLen){
		$(obj_bl).html("昵称字段小于" + nickName_minLen + "位！");
		return false;
	}
	if(len > nickName_maxLen){
		$(obj_bl).html("昵称字段大于" + nickName_maxLen + "位！");
		return false;
	}
	if(!isValidString(obj_val,nickName_RegExp)){
		$(obj_bl).html("昵称不能输入特殊字符");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ActivityTitle 验证
 */
function check_activityTitle_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动名称不能为空");
		return false;
	}
	if(obj_val.length < activityTitle_minLen){
		$(obj_bl).html("活动名称字段小于" + activityTitle_minLen + "位！");
		return false;
	}
	if(obj_val.length > activityTitle_maxLen){
		$(obj_bl).html("活动名称字段大于" + activityTitle_maxLen + "位！");
		return false;
	}
	if(!isValidString(obj_val,activityTitle_RegExp)){
		$(obj_bl).html("活动名称不能输入特殊字符");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ActivityAddress 验证
 */
function check_activityAddress_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动地址不能为空");
		return false;
	}
	if(obj_val.length < activityAddress_minLen){
		$(obj_bl).html("活动地址字段小于" + activityAddress_minLen + "位！");
		return false;
	}
	if(obj_val.length > activityAddress_maxLen){
		$(obj_bl).html("活动地址字段大于" + activityAddress_maxLen + "位！");
		return false;
	}
	if(!isValidString(obj_val,activityAddress_RegExp)){
		$(obj_bl).html("活动地址不能输入特殊字符");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * Money(Fee) 验证
 */
function check_money_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动费用不能为空");
		return false;
	}
	if(!isValidString(obj_val,money_RegExp)){
		$(obj_bl).html("活动费用只能输入正整数");
		return false;
	}
	if(obj_val < money_minNum){
		$(obj_bl).html("活动费用少于" + money_minNum + "元");
		return false;
	}
	if(obj_val > money_maxNum){
		$(obj_bl).html("活动费用大于" + money_maxNum + "元");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ActivityDesc 验证
 */
function check_activityDesc_lyu(obj){
	var obj_val = $(obj).val();
	//obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动描述不能为空");
		return false;
	}
	if(obj_val.length < activityDesc_minLen){
		$(obj_bl).html("活动描述字段小于" + activityDesc_minLen + "位！");
		return false;
	}
	if(obj_val.length > activityDesc_maxLen){
		$(obj_bl).html("活动描述字段大于" + activityDesc_maxLen + "位！");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ProfilesDesc 验证
 */
function check_profilesDesc_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("用户描述不能为空");
		return false;
	}
	if(obj_val.length < profilesDesc_minLen){
		$(obj_bl).html("用户描述字段小于" + profilesDesc_minLen + "位！");
		return false;
	}
	if(obj_val.length > profilesDesc_maxLen){
		$(obj_bl).html("用户描述字段大于" + profilesDesc_maxLen + "位！");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ProfilesWebSite 验证
 */
function check_profilesWebSite_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(obj_val.length < profilesWebSite_minLen && obj_val.length != 0){
		$(obj_bl).html("个性域名字段小于" + profilesWebSite_minLen + "位！");
		return false;
	}
	if(obj_val.length > profilesWebSite_maxLen && obj_val.length != 0){
		$(obj_bl).html("个性域名字段大于" + profilesWebSite_maxLen + "位！");
		return false;
	}
	if(!isValidString(obj_val,profilesWebSite_RegExp) && obj_val.length != 0 ){
		$(obj_bl).html("个性域名不能输入中文或特殊字符");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * ActivityStartDate 验证
 */
function check_activityStartDate_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动开始日期不能为空");
		return false;
	}
	$(obj_bl).html("");
	return true;
}

/*
 * ActivityEndDate 验证
 */
function check_activityEndDate_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("活动结束日期不能为空");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * Comment 验证
 */
function check_comment_lyu(obj){
	var obj_val = $(obj).val();
	obj_val = trim(obj_val);
	var obj_bl = "#" + $(obj).attr("bl");
	if(isNull(obj_val)){
		$(obj_bl).html("评论不能为空噢");
		return false;
	}
	if(obj_val.length < comment_minLen){
		$(obj_bl).html("评论字段小于" + comment_minLen + "位！");
		return false;
	}
	if(obj_val.length > comment_maxLen){
		$(obj_bl).html("评论字段大于" + comment_maxLen + "位！");
		return false;
	}
	$(obj_bl).html("");
	return true;
}
/*
 * 添加聚焦方法
 */
$(document).ready(function(){
	$("[select_focus='0']").bind("mouseover",function(){
		$(this).focus();
	});
});
