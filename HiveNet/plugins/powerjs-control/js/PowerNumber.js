/*-----------------------
JQuery-UITool v1.0.0
完成时间：2011-
作者：黎慧剑
联系方式:snakeclub@163.com
程序说明：基于JQuery框架的Web界面便捷工具,基于该工具，可以通过简单的函数调用实现各类Web界面效果，简化Web开发

当前控件：PowerNumber
说明：增强的数字处理
文件：PowerNumber.js
依赖文件：
-----------------------*/
/*-----------------------
==PowerNumber==
说明：增强的数字处理
-----------------------*/

/*---------------
--toFixed--
数值的四舍五入，修正js原四舍五入方法的bug
--------------- */
Number.prototype.toFixed = function(d){
      var s=this+"";
      if(!d)d=0;
      if(s.indexOf(".")==-1)s+=".";
      s+=new Array(d+1).join("0");
      if (new RegExp("^(-|\\+)?(\\d+(\\.\\d{0,"+ (d+1) +"})?)\\d*$").test(s)){
          var s="0"+ RegExp.$2, pm=RegExp.$1, a=RegExp.$3.length, b=true;
          if (a==d+2){a=s.match(/\d/g); if (parseInt(a[a.length-1])>4){
              for(var i=a.length-2; i>=0; i--) {a[i] = parseInt(a[i])+1;
              if(a[i]==10){a[i]=0; b=i!=1;} else break;}
          }
          s=a.join("").replace(new RegExp("(\\d+)(\\d{"+d+"})\\d$"),"$1.$2");
      }
      if(b)s=s.substr(1);return (pm+s).replace(/\.$/, "");} return this+"";
};


/*---------------
--floatAdd--
浮点数相加，修正原JS的浮点数相加出现的精度问题
支持任意浮点数相加，可传入string或number
--------------- */
function floatAdd(){
    //获得精度
    var fix = 0;
    for(var i = 0;i<arguments.length;i++){
        var r;
        var nstr = arguments[i].toString();
        try{r=nstr.split(".")[1].length;}catch(e){r=0;}
        fix = Math.max(r,fix);
    }
    //转为整型计算
    var m = Math.pow(10,fix);
    var ret = 0;
    for(var i = 0;i<arguments.length;i++){
        if(typeof(arguments[i]) != "number")
            ret += parseFloat(arguments[i])*m;
        else
            ret += arguments[i]*m;
    }
    
    return ret/m;
};

/*---------------
--floatSub--
浮点数相减，修正原JS的浮点数相加出现的精度问题
支持任意浮点数相减，可传入string或number，第1个参数值减去后面的所有参数值
--------------- */
function floatSub(){
    //获得精度
    var fix = 0;
    for(var i = 0;i<arguments.length;i++){
        var r;
        var nstr = arguments[i].toString();
        try{r=nstr.split(".")[1].length;}catch(e){r=0;}
        fix = Math.max(r,fix);
    }
    //转为整型计算
    var m = Math.pow(10,fix);
    var ret;
    if(typeof(arguments[0]) != "number")
        ret = parseFloat(arguments[0])*m;
    else
        ret = arguments[0]*m;
        
    for(var i = 1;i<arguments.length;i++){
        if(typeof(arguments[i]) != "number")
            ret -= parseFloat(arguments[i])*m;
        else
            ret -= arguments[i]*m;
    }
    
    return ret/m;
};


/*---------------
--floatMul--
浮点数相乘，修正原JS的浮点数出现的精度问题
支持任意浮点数相乘，可传入string或number
--------------- */
function floatMul(){
    //获得精度
    var fix = 0;
    for(var i = 0;i<arguments.length;i++){
        var nstr = arguments[i].toString();
        try{fix += nstr.split(".")[1].length;}catch(e){;}
    }
    //转为整型计算
    var ret = 1;
    for(var i = 0;i<arguments.length;i++){
        var nnum = arguments[i];
        if(typeof(nnum) != "number")
            nnum = parseFloat(nnum);
        //转为整型计算
        ret = ret * Number(nnum.toString().replace(".",""));
    }
    
    return ret/Math.pow(10,fix);
};

/*---------------
--floatDiv--
浮点数相除，修正原JS的浮点数出现的精度问题
支持“两个”浮点数相除，可传入string或number
--------------- */
function floatDiv(arg1,arg2){
  var t1=0,t2=0,r1,r2;
  if(typeof(arg1) != "number")
    arg1 = parseFloat(arg1);
  if(typeof(arg2) != "number")
    arg2 = parseFloat(arg2);
    
  try{t1=arg1.toString().split(".")[1].length}catch(e){}
  try{t2=arg2.toString().split(".")[1].length}catch(e){}
  with(Math){
      r1=Number(arg1.toString().replace(".",""));
      r2=Number(arg2.toString().replace(".",""));
      return (r1/r2)*pow(10,t2-t1);
  }
};


/*---------------
--Number.prototype.add--
浮点数相加，修正原JS的浮点数出现的精度问题
--------------- */
Number.prototype.add = function (arg){
    return floatAdd(arg,this);
};

/*---------------
--Number.prototype.sub--
浮点数相减，修正原JS的浮点数出现的精度问题
--------------- */
Number.prototype.sub = function (arg){
    return floatSub(this,arg);
};

/*---------------
--Number.prototype.mul--
浮点数相乘，修正原JS的浮点数出现的精度问题
--------------- */
Number.prototype.mul = function (arg){
    return floatMul(this,arg);
};

/*---------------
--Number.prototype.div--
浮点数相除，修正原JS的浮点数出现的精度问题
--------------- */
Number.prototype.div = function (arg){
    return floatDiv(this,arg);
};
