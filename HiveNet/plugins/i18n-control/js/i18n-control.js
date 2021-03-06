/*---------------------------
i18n-control.js
说明：支持多语言处理的页面控件JS代码
作者：黎慧剑
版本：v1.0.0
时间：2018.5.27
邮件：nakeclub@163.com

使用方法：
	1、在页面装载完成后，初始化多语言处理控件
		$(document).ready(function(){
			$.i18nControl.Init(true,'i18n/','nav','zh');
		});
	
	2、可以点击导航栏菜单切换语言，或通过以下js的执行在后台切换：
	$.i18nControl.ChangeLocale('zh', true);
	
	3、在其他地方如果需要使用多语言的字符处理，可以直接用原生的i18n方法：
	alert($.i18n( 'home' ));
	var message = '$1 and $2 together.';
	alert($.i18n( message, 'haha','oo' ));
		
---------------------------*/

;(function($) {
	
	/*---------------
  	定义插件的调用名字，避免不同插件互相干扰
  --------------- */
	$.i18nControl = new Object();
	
	/*---------------
  	currentLocale : 当前语言变量
    执行方法：$.i18nControl.currentLocale = 'zh'
  --------------- */
  $.i18nControl.currentLocale = undefined;
  
  /*---------------
  	loadedLocale : 已装载文件的语言
    执行方法：$.i18nControl.loadedLocale
  --------------- */
  $.i18nControl.loadedLocale = new Object();
  
  /*---------------
  	beforeTransFunc : 开始转换语言时执行的函数，可用该定义来打开loading遮罩
    执行方法：$.i18nControl.beforeTransFunc = function(){;};
  --------------- */
  $.i18nControl.beforeTransFunc = undefined;
  
  /*---------------
  	afterTransFunc : 结束转换语言时执行的函数，可用该定义来关闭loading遮罩
    执行方法：$.i18nControl.afterTransFunc = function(){;};
  --------------- */
  $.i18nControl.afterTransFunc = undefined;
  
  
  /*---------------
  	jsonFilePrefix : 多语言JSON定义文件前缀，例如pagename-zh.json
    执行方法：$.i18nControl.jsonFilePrefix = 'nav'
  --------------- */
  $.i18nControl.jsonFilePrefix = "nav";
  
  /*---------------
  	jsonFilePath : 多语言JSON定义文件的路径(与当前页面的相对路径)，注意最后要带'/'
    执行方法：$.i18nControl.jsonFilePath = 'i18n/'
  --------------- */
  $.i18nControl.jsonFilePath = "i18n/";
  
  /*---------------
  	Init : 初始化国际化控件
    执行方法：$.i18nControl.Init()
    	withNavMenu : 是否需初始化导航栏菜单样式
    	jsonFilePath : 多语言JSON定义文件的路径(与当前页面的相对路径)，注意最后要带'/'
    	jsonFilePrefix : 多语言JSON定义文件前缀，例如pagename-zh.json
    	locale : 初始化时指定语言
    	beforeTransFunc : 开始转换语言时执行的函数，可用该定义来打开loading遮罩
    	afterTransFunc : 结束转换语言时执行的函数，可用该定义来关闭loading遮罩
  --------------- */
  $.i18nControl.Init = function(withNavMenu, jsonFilePath, jsonFilePrefix, locale, beforeTransFunc, afterTransFunc){
  	//从cookie中获取默认的语言，如果获取不到，则从html标签中获取，否则以'en'为默认值
  	var vLocale = locale;
  	var defaultLocale = $("html").attr("lang");
  	if(vLocale === undefined){
	  	vLocale = Cookies.get("i18nControl-locale");
	  	if (vLocale === undefined) {
	  		vLocale = defaultLocale;
	  		if (vLocale === undefined)
	  			vLocale = "en";
	  	}
	  }
  	
  	//参数
  	if(jsonFilePath != undefined){
  		$.i18nControl.jsonFilePath = jsonFilePath;
  	}
  	
  	if(jsonFilePrefix != undefined){
  		$.i18nControl.jsonFilePrefix = jsonFilePrefix;
  	}
  	
  	if (beforeTransFunc != undefined) {
  		$.i18nControl.beforeTransFunc = beforeTransFunc;
  	}
  	
  	if (afterTransFunc != undefined) {
  		$.i18nControl.afterTransFunc = afterTransFunc;
  	}
  	 
	  //修改语言为指定值
	  if(defaultLocale == vLocale){
	  	//默认语言，只需装载语言文件
	  	$.i18n().locale = vLocale;
			$.i18n().load($.i18nControl.jsonFilePath + $.i18nControl.jsonFilePrefix + '-' + vLocale + '.json', $.i18n().locale).done(
			function() {
				//登记已装载的语言
				eval("$.i18nControl.loadedLocale." + $.i18n().locale + " = true;");
			} );
	  }else{
	  	//修改语言
		  $.i18nControl.ChangeLocale(vLocale, withNavMenu);
		}
  };
  
  /*---------------
  	ChangeLocale : 修改语言为指定值
  		locale ：要修改的语言
  		withNavMenu : 是否同步修改菜单栏的当前语言选项
    执行方法：$.i18nControl.ChangeLocale('zh')
  --------------- */
  $.i18nControl.ChangeLocale = function(locale, withNavMenu){
  	//检查是否有变化
  	if ($.i18nControl.currentLocale == locale)
  		return;
  	
  	//修改菜单栏语言选项
  	if(withNavMenu == true){
  		//需要初始化导航栏菜单，变更样式
	  	var menuObj = $("ul[hivenet-plugin-name='i18n-control']").find("div[i18n-control-locale='"+locale+"']")
	  	ChangeNavMenuStyle(menuObj);
  	}
  		
  	//装载语言文件并进行处理
		$.i18n().locale = locale;
		if(locale in $.i18nControl.loadedLocale){
			//已装载文件，无需重复装载，直接替换处理
			SearchAndUpdateLanguage();
		}else{
			$.i18n().load($.i18nControl.jsonFilePath + $.i18nControl.jsonFilePrefix + "-" + locale + ".json", locale).done(
			function() {
				//登记已装载的语言
				eval("$.i18nControl.loadedLocale." + $.i18n().locale + " = true;");
				
				//装载语言文件后，执行界面的多国语言替换处理
				SearchAndUpdateLanguage();
			});
		}
  	
  	//保存到cookie中
  	$.i18nControl.currentLocale = locale
  	Cookies.set('i18nControl-locale', locale);
  };
  
  /*---------------
  	MenuOnClick : 控件菜单项被点击时要绑定的执行函数
    执行方法：$.i18nControl.MenuOnClick()
  --------------- */
  $.i18nControl.MenuOnClick = function(){
  	//检查语言是否有变化
  	var locale = $(this).attr('i18n-control-locale');
  	if ($.i18nControl.currentLocale == locale)
  		return;
  		
  	//调整界面
  	ChangeNavMenuStyle(this);
  	
  	//修改语言为指定值
	  $.i18nControl.ChangeLocale(locale);
  };
  
  
  //以下为私有函数
  /*---------------
  	ChangeNavMenuStyle : 变更导航栏菜单样式
  		menuObj : 菜单对象
  --------------- */
  function ChangeNavMenuStyle(menuObj){
    $("img[i18n-control-type='MainImg']").attr('src',$(menuObj).find('img').attr('src'));
  	$("ul[hivenet-plugin-name='i18n-control']").find("div[i18n-control-locale]").removeClass("active");
  	$(menuObj).addClass("active");
  };
  
  /*---------------
  	SearchAndUpdateLanguage : 遍历更新对象的显示语言
  --------------- */
  function SearchAndUpdateLanguage(){
  	//转换开始
  	if($.i18nControl.beforeTransFunc != undefined){
  		$.i18nControl.beforeTransFunc();
  	}
  	
  	//找到所有具有i18n-control属性的对象
  	$('[i18n-control]').each(function (){
  			UpdateObjLanguage(this);
  		});
  	
  	//转换结束
  	if($.i18nControl.afterTransFunc != undefined){
  		$.i18nControl.afterTransFunc();
  	}
  };
  
  /*---------------
  	UpdateObjLanguage : 更新指定对象的显示语言
  		dealObj : 要处理的对象
  --------------- */
  function UpdateObjLanguage(dealObj){
  	var obj = $(dealObj);
  	var paraType = obj.attr("i18n-control");
  	var paraStr = obj.attr("i18n-control-para");
  	var paraArray = new Array();

  	if(paraType == "var"){
  		//通过数组变量获取参数值
  		eval("paraArray = " + paraStr + ";");
  	}
  	else{
  		//通过字符串获取参数值
  		paraArray = paraStr.toStringArray(2,"~",";",":");
  	}
  	
  	//根据参数执行替换处理
  	for(var i= 0;i<paraArray.length;i++){
  		var tranStr = "";
  		//通过判断paraArray长度来支持带变量的情况
  		var evalTranStr = "tranStr = $.i18n(paraArray[i][2]";
  		for(j=3;j<paraArray[i].length;j++){
  			evalTranStr = evalTranStr + ",paraArray[i][" + j.toString() + "]";
  		}
  		evalTranStr = evalTranStr + ");";
  		eval(evalTranStr);
  		
  		switch(paraArray[i][0]){
  			case "text":
  				obj.text(tranStr);
  				break;
  			case "html":
  				obj.html(tranStr);
  				break;
  			case "val":
  				obj.val(tranStr);
  				break;
  			case "attr":
  				obj.attr(paraArray[i][1], tranStr);
  				break;
  			case "prop":
  				obj.prop(paraArray[i][1], tranStr);
  				break;
  			default:
  				break;
  		}
  	}
  };
  
})(jQuery);

/*---------------
页面加载完成后执行初始化
----------------*/
$(document).ready(function(){
	//绑定菜单语句
	$("ul[hivenet-plugin-name='i18n-control']").find("div[i18n-control-locale]").on("click", $.i18nControl.MenuOnClick);
});
