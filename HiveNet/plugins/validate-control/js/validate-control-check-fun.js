/*-----------------------
JQuery-UITool v1.0.0
完成时间：2011-
作者：黎慧剑
联系方式:snakeclub@163.com
程序说明：基于JQuery框架的Web界面便捷工具,基于该工具，可以通过简单的函数调用实现各类Web界面效果，简化Web开发

当前控件：BaseValidateFun
说明：基础校验函数（针对字符串）
文件：BaseValidateFun.js
依赖文件：PowerString.js
-----------------------*/

/*-----------------------
==BaseValidateFun==
基础校验函数（针对字符串）
-----------------------*/
/*---------------
--checkNotNull--
校验是否为空
--------------- */
String.prototype.checkNotNull=function()
{
    if(this == null || this == "")
    {
        return  false; 
    }
    else
    {
        return true;
    }
};

/*---------------
--checkLen--
校验长度是否满足要求，包含两端的值（该函数汉字认为长度为1）。
--------------- */
String.prototype.checkLen=function(minlen,maxlen)
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //转换长度
    var min = parseFloat(minlen);
    var max = parseFloat(maxlen);
    if(isNaN(min)){
        min = -1;
    }
    if(isNaN(max)){
        max = -1;
    }
    
    var len = this.length;
    if(len < min || (max== -1 ? false : (len > max)))
    {
        return false;
    }
    else
    {
        return true;
    }
};

/*---------------
--checkLenB--
校验长度是否满足要求，包含两端的值（该函数汉字认为长度为2）。
--------------- */
String.prototype.checkLenB=function(minlen,maxlen)
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //转换长度
    var min = parseFloat(minlen);
    var max = parseFloat(maxlen);
    if(isNaN(min)){
        min = -1;
    }
    if(isNaN(max)){
        max = -1;
    }
    
    var len = this.getRealLength();
    if(len < min || (max== -1 ? false : (len > max)))
    {
        return false;
    }
    else
    {
        return true;
    }
};

/*---------------
--isInt--
校验是否整数
--------------- */
String.prototype.isInt=function()
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //+-在首位(0次或1次)，后面的数字出现1次或多次
    var rep = new RegExp("^[+-]{0,1}\\d{1,}$");
		
	if(rep.test(this))
	{
	    return true;
    }
    else
    {
        return false;
    }
};

/*---------------
--isFloat--
校验是否浮点数
--------------- */
String.prototype.isFloat=function()
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //+-在首位(0次或1次)，整数位数字出现1次或多次，小数点出现0次或1次，小数位数字出现0次或多次
    var rep = new RegExp("^[+-]{0,1}\\d{1,}\\.{0,1}\\d{0,}$");
		
	if(rep.test(this))
	{
	    return true;
    }
    else
    {
        return false;
    }
};

/*---------------
--isEmail--
校验是否Email
--------------- */
String.prototype.isEmail=function()
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    var rep = new RegExp("^[^@.]+@[^@]+$");
	
	if(rep.test(this))
	{
	    return true;
    }
    else
    {
        return false;
    }
};

/*---------------
--isDateTime--
校验是否符合指定格式的日期时间
--------------- */
String.prototype.isDateTime=function()
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    //获得日期格式参数
    var format = "yyyy-MM-dd";
    if(arguments.length > 0){
        format = arguments[0];
    }
    //生成格式的正则表达式，用于判断格式是否正确,由于有d的替换，注意不能用\\d，而是用[0-9]
    var regstr = format.replace(/\\/g,'\\\\'); //将\替换为转义后的\\
    regstr = regstr.replace(/[\$\(\)\*\+\.\[\]\?\/\^\{\}\|]/g,'\\$&'); //转义字符
    regstr = regstr.replace(/yyyy/g,'[0-9]{4,4}'); //四位年份
    regstr = regstr.replace(/yyy/g,'[0-9]{3,3}'); //三位年份
    regstr = regstr.replace(/yy/g,'[0-9]{2,2}'); //两位年份
    regstr = regstr.replace(/MM/g,'((0[0-9])|(1[012]))'); //两位月份，0－9月前面需补0
    regstr = regstr.replace(/M/g,'([0-9]|(1[012]))'); //一位月份，0-9月不能补0
    regstr = regstr.replace(/dd/g,'(([012][0-9])|(3[01]))'); //两位日期，这里限制到不能超过31
    regstr = regstr.replace(/d/g,'(([12]{0,1}[0-9])|(3[01]))'); //一位日期，这里限制到不能超过31
    regstr = regstr.replace(/hh/g,'(([01][0-9])|(2[0-3]))'); //两位小时，这里限制到不能超过23
    regstr = regstr.replace(/hh/g,'((1{0,1}[0-9])|(2[0-3]))'); //一位小时，这里限制到不能超过23
    regstr = regstr.replace(/mm|ss/g,'(([0-5][0-9])|60)'); //两位分钟，这里限制到不能超过60
    regstr = regstr.replace(/m|s/g,'(([1-5]{0,1}[0-9])|60)'); //一位分钟，这里限制到不能超过60
        
    //加上开始和结束
    regstr = "^"+regstr+"$";
    
    var rep = new RegExp(regstr);
	
	if(rep.test(this))
	{
	    return true;
    }
    else
    {
        return false;
    }
};

/*---------------
--checkDate--
校验日期是否为有效日期，注意日期格式必须为“年[分隔符]月[分隔符]日”。
--------------- */
String.prototype.checkDate=function()
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //获得分隔符
    var sp = "-";
    if(arguments.length > 0){
        sp = arguments[0];
    }
    //截取年月日
    var DayArray = this.split(sp,3);
    var year = parseInt(DayArray[0]);
    var month = parseInt(DayArray[1]);
    var day = parseInt(DayArray[2]);
    
    if   (isNaN(year)||isNaN(month)||isNaN(day))   return   false;
    if(year < 0) return false;
    if   ((month>12)||(month<=0))       return   false;
    var   loDay   =   [0,31,28,31,30,31,30,31,31,30,31,30,31];
    if   (year%4==0)   loDay[2]   =   29;   
    if(day > loDay[month]) return false;
    
    return   !isNaN(Date.UTC(year,month,day));   
};

/*---------------
--checkNumArea--
校验数字是否在取值范围内。
--------------- */
String.prototype.checkNumArea=function(min,max)
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //如果不是浮点数，则直接返回失败
    if(!this.isFloat()){
        return false;
    }
    
    //转换最大最小值
    var vmin = parseFloat(min);
    var vmax = parseFloat(max);
    if(isNaN(vmin)){
        vmin = null;
    }
    if(isNaN(vmax)){
        vmax = null;
    }
    
    //是否等于的参数
    var isEqMin = true;
    var isEqMax = true;
    if(arguments.length > 2){
        isEqMin = arguments[2];
    }
    if(arguments.length > 3){
        isEqMax = arguments[3];
    }
    
    var vthis = parseFloat(this);
    
    //比较最小值
    if(vmin != null && (vthis < vmin || (!isEqMin && vthis==vmin))){
        return false;
    }
    
    //比较最大值
    if(vmax != null && (vthis > vmax || (!isEqMax && vthis==vmax))){
        return false;
    }
    
    //通过比较
    return true;
};

/*---------------
--checkFloatSize--
校验数字的精度是否满足要求。
--------------- */
String.prototype.checkFloatSize=function(zs,xs)
{
    //只有非空才校验后面的
    if(!this.checkNotNull())
    {
    		return true;
    }
    
    //如果不是浮点数，则直接返回失败
    if(!this.isFloat()){
        return false;
    }
    
    //转换最大最小值
    var vzs = parseInt(zs);
    var vxs = parseInt(xs);
    if(isNaN(vzs)){
        return false;
    }
    if(isNaN(vxs)){
        return false;
    }
    
    var pos = this.indexOf(".");
    var z;
    var x;
    if(pos == -1)
    {
        //整个是整数
        z = this;
        x = "";
    }
    else
    {
        z = this.substring(0,pos);
        x = this.substring(pos+1);
    }
    if(z.substring(0,1) == "+" || z.substring(0,1) == "-")
    {
        z = z.substring(1);
    }
    
    //开始校验
    if(z.length > vzs || x.length > vxs)
    {
        return false;
    }
    return true;
};

