/*---------------------------
validate-control.js
说明：表单校验控件
作者：黎慧剑
版本：v1.0.0
时间：2018.6.11
邮件：nakeclub@163.com

使用方法：
	
		
---------------------------*/

;(function($) {
	
	/*---------------
  	定义插件的调用名字，避免不同插件互相干扰
  --------------- */
	$.validateControl = new Object();
	
	/*---------------
  	$.validateControl.debug : 标记是否debug
  --------------- */
  $.validateControl.debug = false;
  
  /*---------------
  	$.validateControl.opts.defaults : 默认参数值
  --------------- */
  $.validateControl.defaultInfo = {
  	"NotNull" : " is required!",
  	"$.validateControl.Len" : "'s length must between $1 and $2!",
  	"$.validateControl.LenB" : "'s bit length must between $1 and $2!",
  	"$.validateControl.Int" : " must be int!",
  	"$.validateControl.Float" : " must be float with $1 Integer bit and $2 decimal place!",
  	"$.validateControl.NumArea" : " must be number >$1 and <$2!",
  	"$.validateControl.DateTime" : " must be datetime format like $1!",
  	"$.validateControl.NString" : " must be digital character!",
  	"$.validateControl.Email" : " is not a email format!",
  	"$.validateControl.Equal" : " must equal $1 !"
  };
  
  /*---------------
  	$.validateControl.opts.defaults : 默认参数值
  --------------- */
  $.validateControl.opts = new Object();
  $.validateControl.opts.defaults = {
  	isBindSubmit : false, //是否监听submit方法，在submit的时候执行检查
  	isCheckWhenEdit : true,  //是否在编辑过程中校验单个元素
  	invalidateInfoWithShowname : true, //验证失败信息是否含显示名
  	isAlertWhenFailed : false,  //是否在验证失败时进行告警提示
  	modalControlID : "",  //要提示的modal-control模块ID（要求外部要先建立好控件实例）
  	alertInfo : "Validate Failed!",  //验证失败时的告警信息
  	alertInfoPara : []  //执行告警时传入的i18n参数清单数组（可以为字符串，也可以为JS变量-在外部改变JS变量值以达到动态效果），格式如[["string","name"], ["var", "varname"] ](通过二维数组的第1个字符串标记是变量名还是一般类型)
  };
  
  /*---------------
  	$.validateControl.opts.current : 当前参数值
  --------------- */
  $.validateControl.opts.current = undefined;
  
  /*---------------
  	Init : 初始化验证控件
    执行方法：$.validateControl.Init()
    	opts : 
  --------------- */
  $.validateControl.Init = function(opts){
  	try{
	  	//合并参数
	  	opts = $.extend({}, $.validateControl.opts.defaults, opts || {});
	  	$.validateControl.opts.current = opts;
	  	
	  	//绑定Submit监听事件
	  	if(opts.isBindSubmit === true){
	  		$("form.needs-validation").on("submit", function(event) {
	  			try{
		  			if($(this).validateControlCheck(true,$.validateControl.opts.current.isAlertWhenFailed) === true){
		  				//验证通过
		  				;
		  			}
		  			else{
		  				//验证不通过，禁止submit
						  event.preventDefault();
		          event.stopPropagation();
		        }
		      }catch(err){
		      	debug("onsubmit : outer : "+err.toString());
		      }
				});
	  	}
	  	
	  	//绑定元素检查事件
	  	if(opts.isCheckWhenEdit === true){
	  		//正常绑定的对象
	  		var objs = $("[required],[validate-control]");
	  		objs.validateControlBindEditEvent();
	  	}
	  	
  	}catch(e){
			debug("Init : outer : "+e.toString());
		}
  };
  
  /*---------------
  	$("#object").validateControlCheck() : 对指定元素及子元素执行校验
  		setValidatedTag : 是否设置已校验的标签，true-对对象增加一个is-validated的标签，fasle-不进行任何处理
  		isAlertWhenFailed : 是否在验证失败时进行告警提示
  		返回值：true-校验通过，false-校验失败
  --------------- */
	$.fn.validateControlCheck = function(setValidatedTag, isAlertWhenFailed) {
		var isValidate = true;
		try{
			for(var i = 0;i < this.length;i++){
				var obj = $(this.get(i));
				//对子元素执行同样的处理，具有required和validate-control属性的对象，子对象检查不告警
				var subValidate = obj.find("[required],[validate-control]").validateControlCheck(setValidatedTag, false);
				
				//对自己进行校验
				if(setValidatedTag){
					obj.attr("is-validated","");
				}
				var selfValidate = ValidateJQueryObj(obj);
				
				//返回全部接口结果的合集，只要有一个失败就是失败
				isValidate = (isValidate && subValidate && selfValidate);
			}
		}catch(e){
			debug("validateControlCheck : outer : "+e.toString());
			isValidate = false;
		}
		//进行提示
		if(!isValidate && isAlertWhenFailed === true){
			AlertFailedFun();
		}
		return isValidate;
	};
	
	/*---------------
  	$("#object").validateControlReset() : 对指定元素及子元素重新设置样式为默认样式，并去除is-validated标签
  --------------- */
	$.fn.validateControlReset = function(){
		try{
			for(var i = 0;i < this.length;i++){
				var obj = $(this.get(i));
				//对子元素执行同样的处理
				obj.find("[required],[validate-control]").validateControlReset();
				
				//处理自己
				obj.removeAttr("is-validated");
				obj.removeClass("is-invalid is-valid");
			}
		}catch(e){
			debug("validateControlReset : outer : "+e.toString());
		}	
	};
	
	/*---------------
  	$("#object").validateControlBindEditEvent() : 对指定元素及子元素绑定编辑校验事件
  --------------- */
	$.fn.validateControlBindEditEvent = function(){
		try{
			//先绑定自己
			var selfobjs = $(this).filter("[required],[validate-control]");
			BindEditEventFun(selfobjs);
			for(var i = 0;i < this.length;i++){
				var obj = $(this.get(i));
				//对子元素执行同样的处理
				var objs = obj.find("[required],[validate-control]");
				BindEditEventFun(objs);
			}
		}catch(e){
			debug("validateControlBindEditEvent : outer : "+e.toString());
		}	
	};
	
	/*---------------
  	BindEditEvent : 验证控件需绑定的处理事件，用于判断输入内容及改变样式
    执行方法：$.validateControl.BindEditEvent
  --------------- */
	$.validateControl.BindEditEvent = function(){
		var obj = $(this);
		obj.validateControlCheck(false,false);
	};
	
	//以下为控件自带的基础校验函数
	/*---------------
  	$.validateControl.Len:长度应在$1和$2之间:最小长度:最大长度 ：限制不能录入超过指定长度的字符，例如"$.validateControl.Len::0:10"，长度为0-10则满足校验条件
  	注意：对于一个汉字认为是1
  --------------- */
	$.validateControl.Len = function(objValue,minlen,maxlen){
		try{
			return objValue.toString().checkLen(minlen,maxlen);
		}catch(e){
			debug("$.validateControl.Len : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
  	$.validateControl.LenB:长度应在$1和$2之间:最小长度:最大长度 ：限制不能录入超过指定长度的字符，例如"$.validateControl.LenB::0:10"，长度为0-10则满足校验条件
  	注意：对于一个汉字认为是2
  --------------- */
	$.validateControl.LenB = function(objValue,minlen,maxlen){
		try{
			return objValue.toString().checkLenB(minlen,maxlen);
		}catch(e){
			debug("$.validateControl.LenB : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		Int:只能录入整数 ：限制只能录入整数，例如"Int:"
  --------------- */
	$.validateControl.Int = function(objValue){
		try{
			return objValue.toString().isInt();
		}catch(e){
			debug("$.validateControl.Int : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		Float:整数位不大于$1位,小数位不大于$2位:整数位:小数位：限制录入的浮点数，例如"Float::3:6"
  --------------- */
	$.validateControl.Float = function(objValue,zs,xs){
		try{
			return objValue.toString().checkFloatSize(zs,xs);
		}catch(e){
			debug("$.validateControl.Float : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		NumArea:数值应在$1和$2之间:[=]最小值:[=]最大值：限制录入的数值范围,数值前面加=代表等于也在范围内，例如"NumArea::=-1000:23.3"
  --------------- */
	$.validateControl.NumArea = function(objValue,minValue,maxValue){
		try{
			var isEqMin = (minValue.charAt(0)=="=");
			var isEqMax = (maxValue.charAt(0)=="=");
	    var minStr = (isEqMin?minValue.substring(1):minValue);
	    var maxStr = (isEqMax?maxValue.substring(1):maxValue);
	  	return objValue.toString().checkNumArea(minStr,maxStr,isEqMin,isEqMax);
  	}catch(e){
			debug("$.validateControl.NumArea : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		DateTime:格式应为$1:格式：限制录入的日期时间（注意，格式中不能带,），例如"DateTime::yyyy-MM-dd hh:mm:ss"
  --------------- */
	$.validateControl.DateTime = function(objValue,formatStr){
		try{
			return objValue.toString().isDateTime(formatStr);
		}catch(e){
			debug("$.validateControl.DateTime : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		NString:只能录入数字 ：限制只能录入数字
  --------------- */
	$.validateControl.NString = function(objValue){
		try{
			var NumReg = new RegExp("^[0-9]{0,}$");
	  	return NumReg.test(objValue.toString());
  	}catch(e){
			debug("$.validateControl.NString : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		Equal:相等 ：限制取值与指定的值一致
  --------------- */
	$.validateControl.Equal = function(objValue,matchValue){
		try{
  		return (matchValue.toString() == objValue.toString());
  	}catch(e){
			debug("$.validateControl.Equal : outer : "+e.toString());
			return false;
		}
	};
	
	/*---------------
		Email:Email地址格式错误 ：限制录入的只能是Email地址
  --------------- */
	$.validateControl.Email = function(objValue){
		try{
			return objValue.toString().isEmail();
		}catch(e){
			debug("$.validateControl.Equal : outer : "+e.toString());
			return false;
		}
	};
	
	//以下为私有函数
  /*---------------
  	ValidateJQueryObj : 对JQuery对象进行验证
  		obj : 需要验证的JQuery对象
  		返回值：true-校验通过，false-校验失败
  --------------- */
  function ValidateJQueryObj(obj){
  	try{
	  	//看看是否属于可以验证的类型
	  	var hasRequired = (obj.attr("required") !== undefined);
	  	var validateControl = obj.attr("validate-control");
	  	if(!(hasRequired || validateControl !== undefined)){
	  		//没有校验参数，无需校验
	  		return true;
	  	}
	  	
	  	//通过函数获取对象值
	  	var objValue = GetInputValue(obj);
	  	if(objValue === null && obj.attr("is-validated") === undefined){
	  		//对象值为空时，且对象未标记为is-validated状态，将对象恢复为正常的样式并直接返回true
	  		SetObjValidateStyle(obj, true, "")
	  		return true;
	  	}
	  	
	  	//开始进行校验处理
	  	vReslut = ValidateJQueryObjOnly(obj,objValue);
	  	
	  	//根据校验结果设置对象样式
	  	SetObjValidateStyle(obj, vReslut[0], vReslut[1]);
	  	
	  	return vReslut[0];
		}catch(e){
			debug("ValidateJQueryObj : outer : "+e.toString());
			return false;
		}
  };
  
  /*---------------
  	ValidateJQueryObjOnly : 只进行校验，不处理状态变更
  		obj : 需要获取值的JQuery对象
  		objValue : 对象取值
  		返回值：[isValidate,showInfo]
  --------------- */
  function ValidateJQueryObjOnly(obj,objValue){
  	try{
  		var hasRequired = (obj.attr("required") !== undefined);
	  	var validateControl = obj.attr("validate-control");
	  	
	  	var isValidate = true;
	  	var showInfo = "";
	  	if(objValue === null){
	  		if(hasRequired){
	  			//必填
	  			isValidate = false;
	  			showInfo = $.validateControl.defaultInfo['NotNull'];
	  		}
	  	}
	  	else{
	  		//有值的情况，校验任务清单
	  		if(validateControl !== undefined){
		  		var paraStr = obj.attr("validate-control-para");
		  		var paraArray = new Array();
		  		if(validateControl == "var"){
		  			//通过数组变量获取参数值
  					eval("paraArray = " + paraStr + ";");
		  		}
		  		else{
		  			//通过字符串获取参数值
		  			paraArray = paraStr.toStringArray(2,"~",";",":");
		  		}
		  		
		  		//逐个参数执行校验判断
		  		for(var i= 0;i<paraArray.length;i++){
		  			isValidate = CheckValueValidate(objValue,paraArray[i]);
		  			if(!isValidate){
		  				//没有通过校验，获得显示提示
		  				showInfo = GetInvalidateShowInfo(paraArray[i]);
		  				break; //退出循环
		  			}
		  		}
		  	}
	  	}
	  	
	  	return [isValidate, showInfo];
  	}catch(e){
			debug("ValidateJQueryObjOnly : outer : "+e.toString());
			return [false,"ValidateJQueryObjOnly error:"+e.toString()];
		}
  };
  
  /*---------------
  	GetInputValue : 获取JQuery对象的编辑值
  		obj : 需要获取值的JQuery对象
  		返回值：根据对象类型不同返回不同的值，但每个类型如果没有输入的情况将统一转换为null返回，避免外围判断的差异
  --------------- */
  function GetInputValue(obj){
  	var inputValue = null;
  	try{
  		jObj = $(obj);
	  	var tagName = jObj.get(0).tagName.toLowerCase();
	  	switch(tagName){
	  		case "input":
	  			var typeStr = jObj.attr("type");
	  			if(typeStr == "checkbox"){
	  				inputValue = jObj.is(':checked').toString();
	  			}
	  			else if(typeStr == "radio"){
	  				inputValue = $("body").find("input[name='"+jObj.attr("name")+"']:checked").val();
	  			}
	  			else{
		  			inputValue = jObj.val();
		  		}
	  			break;
	  		case "textarea":
	  			inputValue = jObj.val();
	  			break;
	  		case "select":
	  			inputValue = jObj.val();
	  			break;
	  		default:
	  			break;
	  	}
	  	if(inputValue === undefined || inputValue == ""){
	  		inputValue = null;
	  	}
  	}catch(e){
			debug("GetInputValue : outer : "+e.toString());
		}
		
  	return inputValue;
  };
  
  /*---------------
  	CheckValueValidate : 校验值是否符合指定的校验参数
  		inputValue : 校验值
  		paraList : 校验参数数组
  		返回值：true-校验通过，false-校验失败
  --------------- */
  function CheckValueValidate(inputValue, paraList){
  	try{
  		//执行函数
  		var checkResult = false;
  		var evalStr = "checkResult = " + paraList[0] + "(inputValue";
  		for(var i = 2;i<paraList.length;i++){
  			evalStr = evalStr + ",paraList["+i.toString()+"]";
  		}
  		evalStr = evalStr + ");";
  		eval(evalStr);
  		return checkResult;
  	}catch(e){
			debug("CheckValueValidate : outer : "+e.toString()+inputValue.toString());
			return false;
		}
  };
  
  /*---------------
  	GetInvalidateShowInfo : 获取校验失败的提示信息
  		para : 校验参数
  		返回值：经过组织及国际化转换后的提示信息
  --------------- */
  function GetInvalidateShowInfo(para){
  	try{
	  	var showInfo = para[1];
	  	if(showInfo === undefined || showInfo == ""){
	  		eval("showInfo = $.validateControl.defaultInfo['"+para[0]+"'];");
	  		if(showInfo === undefined){
	  			showInfo = "";
	  		}
	  		else{
	  			//组成参数字符串
	  			var paraStr = "";
	  			for(var i = 2; i < para.length; i++){
	  				if(para[i] == "true"){
	  					//将true 转换为0
	  					paraStr = paraStr + ",'0'";
	  				}
	  				else if(para[i] == "false"){
	  					//将false 转换为1
	  					paraStr = paraStr + ",'1'";
	  				}
	  				else{
	  					paraStr = paraStr + ",para["+i.toString()+"]";
	  				}	
	  			}
	  			//执行国际化处理
	  			eval("showInfo = $.i18n(showInfo" + paraStr + ")");
	  		}
	  	}
	  	return showInfo;
	  }catch(e){
			debug("GetInvalidateShowInfo : outer : "+e.toString());
			return "";
		}
  };
  
  /*---------------
  	AlertFailedFun : 通过modal-control模块提示校验失败
  --------------- */
  function AlertFailedFun(){
  	try{
  		if($.validateControl.opts.current.isAlertWhenFailed == true){
  			//先组织提示内容
  			var showInfo = $.validateControl.opts.current.alertInfo;
  			var para = $.validateControl.opts.current.alertInfoPara;
  			var paraStr = "";
  			for(var i = 0; i<para.length;i++){
  				if(para[i][0] == "var"){
  					//变量名形式
  					paraStr = paraStr + "," + para[i][1];
  				}else{
  					paraStr = paraStr + ",para["+i.toString()+"][1]";
  				}
  			}
  			//执行国际化处理
  			eval("showInfo = $.i18n(showInfo" + paraStr + ")");
  			
  			//调用modal-control模块
  			if($.validateControl.opts.current.modalControlID !== undefined && $.validateControl.opts.current.modalControlID != ""){
  				$("#"+$.validateControl.opts.current.modalControlID).modalControlShow({
  					titleText : $.i18n("Warning"),
  					contentText : showInfo
  				});
  			}
  			else{
  				//直接用alert
  				alert(showInfo);
  			}
  		}
  	}catch(e){
			debug("AlertFailedFun : outer : "+e.toString());
		}
  };
  
  /*---------------
  	SetObjValidateStyle : 设置对象的验证样式
  		inObj : 要设置的对象
  		isValidate : 是否验证通过
  		showInfo : 验证不通过的信息
  --------------- */
  function SetObjValidateStyle(inObj, isValidate, showInfo){
  	try{
  		//对于radio要特殊处理
  		var obj = inObj;
  		if(obj.is("input[type='radio']")){
  			obj = $("body").find("input[name='"+inObj.attr("name")+"']");
  		}
  		if(isValidate){
  			//验证通过，设置通过的样式
  			if(obj.attr("is-validated") !== undefined){
	  			obj.removeClass("is-invalid");
	  			obj.addClass("is-valid");
	  		}
	  		else{
	  			obj.removeClass("is-invalid is-valid");
	  		}
  		}
  		else{
  			//验证不通过
	  		var showName = "";
	  		if($.validateControl.opts.current.invalidateInfoWithShowname === true){
	  			showName = GetShowName(inObj);
  			}
  			//在feedback中提示
  			var feedbackObj = $();
  			if(inObj.is("input[type='radio']")){
  				feedbackObj = $("div.invalid-feedback[for='"+inObj.attr("name")+"']");
  			}
  			else{
	  			feedbackObj = obj.nextAll("div.invalid-feedback[for='"+obj.attr("id")+"']");
	  		}
  			if(feedbackObj.length == 1){
  				feedbackObj.html(showName+showInfo);
  			}
  			obj.removeClass("is-valid");
  			obj.addClass("is-invalid");
  		}
  	}catch(e){
			debug("SetObjValidateStyle : outer : "+e.toString());
		}
  };
  
  /*---------------
  	GetShowName : 获取对象的显示名
  		obj : 要获取的对象
  		返回值： 获取到到的显示名
  --------------- */
  function GetShowName(obj){
  	try{
  		//先从当前的属性获取
	  	var tempShowName = obj.attr("show-name");
	  	if(tempShowName !== undefined){
	  		return $.i18n(tempShowName);
	  	}
	  	//获取不到，尝试从本对象的label中获取
	  	var labelObj = $();
	  	if(obj.is("input[type='radio']")){
	  		labelObj = $("#"+obj.attr("name"));
	  	}
	  	else if(obj.is("input[type='file']")){
	  		labelObj = obj.parent().prev("label[for='"+obj.attr("id")+"']");
	  	}
	  	else{
		  	labelObj = obj.prev("label[for='"+obj.attr("id")+"']");
		  }
	  	if(labelObj.length == 1){
	  		return labelObj.text();
	  	}
	  	return "";
  	}catch(e){
			debug("GetShowName : outer : "+e.toString());
			return "";
		}
  };
  
  /*---------------
  	BindEditEventFun : 通用的绑定操作
  		objs : 要获取的对象集合
  --------------- */
  function BindEditEventFun(objs){
  	objs.on("keyup",$.validateControl.BindEditEvent); //失去焦点时执行，通用
		objs.filter("input:not([type='checkbox'],[type='radio'],[type='file'])").on("blur",$.validateControl.BindEditEvent); //每输入一个字符
		objs.filter("select,input[type='file']").on("change",$.validateControl.BindEditEvent);//变更了选项
		//jquery 对checkbox的事件中取值存在bug，要用JS原生方法处理
		var checkboxObjs = objs.filter("input[type='checkbox'],input[type='radio']");
		for(var i = 0;i< checkboxObjs.length; i++){
			$(checkboxObjs.get(i)).get(0).onclick = $.validateControl.BindEditEvent;
		}
  };
  
  /*---------------
  	debug : 通过alert弹出debug的信息
  --------------- */
  function debug(str){
  	if($.debug === true){
  		alert("debug：" + str);
  	}
  };
  
})(jQuery);

