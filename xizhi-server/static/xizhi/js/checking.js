
//这里存放所有验证的脚本处理

//剔除空格
function trim(str){
	return str.replace(/(^\s*)|(\s*$)/g,"");
}
//消除提示
function clearMsg(obj){
    try{
        obj.empty();   
    }
    catch(err) {}
}
//检查字符串是为为空 true表示为空 false表示不为空
function isNull(IdValue){
    if(trim(IdValue)==""){
		 return true;
	}else{
		return false;
	}
}
//检查信息长度完整性，参数1为需要检查的参数，参数2为不能小于的长度
function CheckMessageLength(checkValue, length){
	if(checkValue.length < length){
		return false;
	} else {
		return true;
	}
}

//检查邮箱格式是否正确，正确返回true,否者返回false
function isEmailFormatRight(checkvalue){
	var emailStr = trim(checkvalue);   
    var emailPattern=/^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,4}$/;
    var matchArray=emailStr.match(emailPattern);
    if(matchArray==null) {
        return false;
    }
    return true;
}
// 检查字符串是否合法，不允许输入某些非法字符
function isValidString(value) {
    var str = trim(value);
    if(str == '') return false;
    
    var pattern=/^[\u4E00-\u9FA5A-Za-z0-9_]+$/; //只允许输入中文，英文字母或数字
    var matchArray=str.match(pattern);
    if(matchArray != null) {
        return true;
    }
    return false;
}