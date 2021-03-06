/*---------------------------
modal-control.js
说明：遮罩及弹出窗口控件
作者：黎慧剑
版本：v1.0.0
时间：2018.6.8
邮件：snakeclub@163.com

---------------------------*/


;
(function ($) {

	/*---------------
  	定义插件的调用名字，避免不同插件互相干扰
  --------------- */
	$.modalControl = new Object();

	/*---------------
  	$.modalControl.debug : 标记是否debug
  --------------- */
	$.modalControl.debug = false;

	/*---------------
  	$.modalControl.pageLoading.templateHtml : 页面装载提示的HTML代码，如果需要自定义模板样式，可以修改该变量
  --------------- */
	$.modalControl.pageLoading = new Object();
	$.modalControl.pageLoading.opts = new Object();
	$.modalControl.pageLoading.templateHtml = '<div class="modal bg-transparent" id="{$id$}">' +
		'<div class="modal-dialog rounded border border-dark modal-page-loading-div">' +
		'<img src="{$src$}" class="modal-page-loading-img">' +
		'<br>' +
		'<a class="modal-page-loading-text">{$loadingText$}</a>' +
		'</div>' +
		'</div>';

	/*---------------
  	$.modalControl.pageLoading.defaults : pageLoading的默认处理参数
  --------------- */
	$.modalControl.pageLoading.defaults = {
		modalType: "pageLoading", //遮罩类型
		id: "$PageLoadingID$", //遮罩的ID，用于进行标识和处理
		showOnCreate: false, //在创建遮罩时直接显示遮罩
		rebuildOnShow: false, //显示时是否重建（如果ID已存在的情况下，删除原遮罩并重新建立）
		destroyOnHide: false, //隐藏时是否销毁遮罩对象
		fade: true, //是否要过度动画效果，有动画效果的情况下，show/hide等操作需注意不能在一个函数内执行（JS单线程会阻塞渲染，导致同一个函数内执行的操作没有效果）
		backdrop: "static", //bootstrap的modal参数，static代表点击空白处不关闭，true代表点击空白处关闭
		keyboard: false, //bootstrap的modal参数，当按退出按钮（ESC）时是否关闭
		focus: true, //bootstrap的modal参数，当启动时是否将焦点放到遮罩中
		// 以下为非公共的参数
		src: "../pic/loading-middle.gif", //loading的gif图像地址
		loadingText: "loading" //提示文字
	};

	/*---------------
  	$.modalControl.messageBox.templateHtml : messageBox提示的HTML代码，如果需要自定义模板样式，可以修改该变量
  --------------- */
	$.modalControl.messageBox = new Object();
	$.modalControl.messageBox.opts = new Object();
	$.modalControl.messageBox.templateHtml = '<div class="modal" id="{$id$}" tabindex="-1" role="dialog" aria-labelledby="hivenet-plugin-modal" aria-hidden="true">' +
		'<div class="modal-dialog modal-dialog-centered" role="document">' +
		'<div class="modal-content">' +
		'<div class="modal-header">' +
		'<a class="modal-title modal-title-compact" id="{$id$}_Title">{$titleText$}</a>' +
		'<button type="button" class="close modal-close-compact" data-dismiss="modal" aria-label="Close">' +
		'<span aria-hidden="true">&times;</span>' +
		'</button>' +
		'</div>' +
		'<div class="modal-body">' +
		'<a class="modal-content-text">{$contentText$}</a>' +
		'</div>' +
		'<div class="modal-footer">' +
		'<button id="{$id$}_CloseBtn" type="button" class="btn btn-primary modal-btn-close" data-dismiss="modal">{$closeBtnText$}</button>' +
		'<button id="{$id$}_YesBtn" type="button" class="btn btn-primary modal-btn-yes">{$yesBtnText$}</button>' +
		'</div>' +
		'</div>' +
		'</div>' +
		'</div>';

	/*---------------
  	$.modalControl.messageBox.defaults : pageLoading的默认处理参数
  --------------- */
	$.modalControl.messageBox.defaults = {
		modalType: "messageBox", //遮罩类型
		id: "$MessageBoxID$", //遮罩的ID，用于进行标识和处理
		showOnCreate: false, //在创建遮罩时直接显示遮罩
		rebuildOnShow: false, //显示时是否重建（如果ID已存在的情况下，删除原遮罩并重新建立）
		destroyOnHide: false, //隐藏时是否销毁遮罩对象
		fade: true, //是否要过度动画效果，有动画效果的情况下，show/hide等操作需注意不能在一个函数内执行（JS单线程会阻塞渲染，导致同一个函数内执行的操作没有效果）
		backdrop: "static", //bootstrap的modal参数，static代表点击空白处不关闭，true代表点击空白处关闭
		keyboard: false, //bootstrap的modal参数，当按退出按钮（ESC）时是否关闭
		focus: true, //bootstrap的modal参数，当启动时是否将焦点放到遮罩中
		// 以下为非公共的参数
		boxType: 'alert', //消息框类型，alert - 单按钮消息框，yesno - 双按钮消息框
		sizes: "md", //消息框大小，lg 大， md 中等, sm 小
		titleText: "MessageBox", //消息框标题文字
		contentText: "", //消息框提示文字，也可以传入html代码和jquery对象，当为jquery对象时，会将该对象移入模板中（置为显示），当发生变更或销毁时时会将对象移出到原来的位置（并隐藏）
		closeBtnText: "close", //关闭按钮文字
		hideCloseIcon: false, //隐藏右上角的关闭窗口图标
		disableDefaultCloseEvent: false, //是否屏蔽关闭按钮的默认关闭提示框事件，如果需要自行实现方法可设置该参数
		CloseEvent: null, //自定义关闭按钮事件，参数为function (event){alert(event.data.modalObj);alert(event.data.modalType);alert(event.data.eventName);}
		yesBtnText: "OK", //确认按钮文本
		yesBtnEvent: null //自定义关闭按钮事件，参数为function (event){alert(event.data.modalObj);alert(event.data.modalType);alert(event.data.eventName);}
	};

	/*---------------
  	$("#object").modalControlCreate(opts) : 创建遮罩及弹出框（不显示）
  		opts : 不同类型的遮罩参数参考各个defaults参数设置
  	注意：
  	1、对象为要创建遮罩所在的对象，如果是全屏对象，可以使用$("body").modalControlCreate({modalType : "PageLoading", id : "$PageLoadingID$"})
  	2、如果筛选器有多个对象，只处理第1个
  --------------- */
	$.fn.modalControlCreate = function (opts) {
		try {

			for (var i = 0; i < 1; i++) {
				//处理默认参数
				templateHtml = "";
				try {
					eval("opts = $.extend({}, $.modalControl." + opts.modalType + ".defaults, opts || {});");
				} catch (e) {
					debug("modalControlCreate : match opts: " + e.toString());
					return []; //无法识别的modalType，返回一个空的对象数组
				}

				//处理创建类型
				var modalObj = $("#" + opts.id);
				var useHisModal = true; //标记是否使用原有对象
				if (opts.rebuildOnShow && opts.showOnCreate && modalObj.length > 0) {
					// 删除原对象
					useHisModal = false;
					modalObj.modalControlDestroy();
				}

				if (modalObj.length == 0 || !useHisModal) {
					//历史遮罩不存在，或已被删除，创建遮罩
					var obj = $(this.get(i));
					templateHtml = GetTemplateHtml(opts);
					if (templateHtml == "") {
						return []; //获取不到模板HTML代码
					}
					obj.append(templateHtml);

					//重新获取对象,设置控件标签
					modalObj = $("#" + opts.id);
					if (modalObj.length != 1) {
						return []; //未能正常获取到对象
					}

					modalObj.attr("hivenet-plugin-name", "modal-control");
					modalObj.attr("modal-control-type", opts.modalType);

					//是否需要动态效果
					if (opts.fade) {
						modalObj.addClass("fade");
					} else {
						modalObj.removeClass("fade");
					}

					//遮罩的bootstrap参数
					modalObj.attr("data-backdrop", opts.backdrop.toString());
					modalObj.attr("data-keyboard", opts.keyboard.toString());
					modalObj.attr("data-focus", opts.focus.toString());

					//区分类型绑定参数
					ShowOptsDeal(modalObj, opts.modalType, opts)

					//重新登记opts
					eval("$.modalControl." + opts.modalType + ".opts." + opts.id + " = opts;");
				}

				//判断是否需要显示
				if (opts.showOnCreate) {
					modalObj.modalControlShow(undefined, true);
				}

				return modalObj;
			}
		} catch (e) {
			debug("modalControlCreate : outer : " + e.toString());
			return [];
		}
	};

	/*---------------
  	$("#modal_id").modalControlShow() : 显示遮罩及弹出框
  		opts : 显示的参数数组，按不同类型内容可改变显示的内容，参考各类遮罩中的defaults参数自定义部分
  		isCallByCreate : 是否在modalControlCreate中调用，如果是则不重新创建遮罩
  --------------- */
	$.fn.modalControlShow = function (opts, isCallByCreate) {
		try {
			for (var i = 0; i < 1; i++) {
				var modalObj = $(this.get(i));
				var modalType = modalObj.attr("modal-control-type");
				var id = modalObj.attr("id");
				var init_opts = eval("$.modalControl." + modalType + ".opts." + id);

				if ((isCallByCreate === undefined || !isCallByCreate) && init_opts.rebuildOnShow) {
					//每次显示时重建
					modalObj.parent().modalControlCreate(init_opts);
				}

				//自定义参数

				if (opts !== undefined) {

					ShowOptsDeal(modalObj, modalType, opts);
				}

				//显示遮罩
				modalObj.modal("show");
			}
		} catch (e) {
			debug("modalControlShow : outer : " + e.toString());
		}
	};

	/*---------------
  	$("#modal_id").modalControlHide() : 隐藏遮罩及弹出框
  --------------- */
	$.fn.modalControlHide = function () {
		try {
			for (var i = 0; i < 1; i++) {
				var modalObj = $(this.get(i));
				var modalType = modalObj.attr("modal-control-type");
				var id = modalObj.attr("id");
				var opts = eval("$.modalControl." + modalType + ".opts." + id + ";");

				//根据参数判断是否要销毁
				if (opts.destroyOnHide) {
					modalObj.removeClass("fade"); //屏蔽动画
					//隐藏遮罩
					modalObj.modal("hide");
					//销毁对象
					modalObj.modalControlDestroy();
				} else {
					//隐藏遮罩
					modalObj.modal("hide");
				}
			}
		} catch (e) {
			debug("modalControlHide : outer : " + e.toString());
		}
	};

	/*---------------
  	$("#modal_id").modalControlToggle() : 切换遮罩及弹出框显示和隐藏状态
  --------------- */
	$.fn.modalControlToggle = function () {
		try {
			for (var i = 0; i < 1; i++) {
				var modalObj = $(this.get(i));
				var modalType = modalObj.attr("modal-control-type");
				modalObj.modal('toggle');
			}
		} catch (e) {
			debug("modalControlToggle : outer : " + e.toString());
		}
	};

	/*---------------
  	$("#modal_id").modalControlDestroy() : 销毁遮罩及弹出框
  --------------- */
	$.fn.modalControlDestroy = function () {
		try {
			for (var i = 0; i < 1; i++) {
				var modalObj = $(this.get(i));
				modalObj.remove();
			}
		} catch (e) {
			debug("modalControlDestroy : outer : " + e.toString());
		}
	};


	//以下为私有函数
	/*---------------
		  GetTemplateHtml : 获取遮罩模板的HTML代码
			  opts : 参数
			  返回值 : 替换参数后的模板
	--------------- */
	function GetTemplateHtml(opts) {
		templateHtml = "";
		try {
			switch (opts.modalType) {
				case "pageLoading":
					templateHtml = $.modalControl.pageLoading.templateHtml;
					templateHtml = templateHtml.replace(/\{\$id\$\}/g, opts.id);
					break;
				case "messageBox":
					templateHtml = $.modalControl.messageBox.templateHtml;
					templateHtml = templateHtml.replace(/\{\$id\$\}/g, opts.id);
					break;
				default:
					break; //无法识别的modalType
			}
		} catch (e) {
			debug("GetTemplateHtml : outer : " + e.toString());
		}
		return templateHtml;
	};

	/*---------------
		  ShowOptsDeal : 显示参数处理
			  opts : 参数
	--------------- */
	function ShowOptsDeal(modalObj, modalType, opts) {
		try {
			switch (modalType) {
				case "pageLoading":
					if (opts.src !== undefined) {
						modalObj.find("img.modal-page-loading-img").attr("src", opts.src);
					}
					if (opts.loadingText !== undefined) {
						modalObj.find("a.modal-page-loading-text").html(opts.loadingText);
					}
					break;
				case "messageBox":
					if (opts.boxType !== undefined) {
						var yesBtnObj = modalObj.find("button.modal-btn-yes");
						var closeBtnObj = modalObj.find("button.modal-btn-close");
						if (opts.boxType == "yesno") {
							//双按钮确认窗口
							yesBtnObj.removeClass("sr-only");
							closeBtnObj.removeClass("btn-primary");
							closeBtnObj.addClass("btn-secondary");
						} else {
							yesBtnObj.addClass("sr-only");
							closeBtnObj.removeClass("btn-secondary");
							closeBtnObj.addClass("btn-primary");
						}
					}
					if (opts.sizes !== undefined) {
						//移除类
						var dialogObj = modalObj.find("div.modal-dialog");
						dialogObj.removeClass("modal-lg modal-sm");
						switch (opts.sizes) {
							case "lg":
								dialogObj.addClass("modal-lg");
								break;
							case "sm":
								dialogObj.addClass("modal-sm");
								break;
							default:
								break;
						}
					}
					if (opts.titleText !== undefined) {
						modalObj.find("a.modal-title").html(opts.titleText);
					}
					if (opts.contentText !== undefined) {
						MessageBoxChangeContentObj(modalObj, opts.contentText)
					}
					if (opts.closeBtnText !== undefined) {
						modalObj.find("button.modal-btn-close").html(opts.closeBtnText);
					}
					if (opts.hideCloseIcon !== undefined) {
						if (opts.hideCloseIcon) {
							modalObj.find("button.modal-close-compact").addClass("invisible");
						} else {
							modalObj.find("button.modal-close-compact").removeClass("invisible");
						}
					}
					if (opts.disableDefaultCloseEvent !== undefined) {
						if (opts.disableDefaultCloseEvent) {
							modalObj.find("button.modal-btn-close,button.modal-close-compact").removeAttr("data-dismiss");
						} else {
							modalObj.find("button.modal-btn-close,button.modal-close-compact").attr("data-dismiss", "modal");
						}
					}
					if (opts.CloseEvent !== undefined) {
						//移除所有事件
						modalObj.find("button.modal-btn-close,button.modal-close-compact").off("click");
						if (opts.CloseEvent != null) {
							modalObj.find("button.modal-btn-close,button.modal-close-compact").on("click", {
								modalObj: modalObj,
								modalType: "messageBox",
								eventName: "CloseEvent"
							}, opts.CloseEvent);
						}
					}
					if (opts.yesBtnText !== undefined) {
						modalObj.find("button.modal-btn-yes").html(opts.yesBtnText);
					}
					if (opts.yesBtnEvent !== undefined) {
						//移除所有事件
						modalObj.find("button.modal-btn-yes").off("click");
						if (opts.yesBtnEvent != null) {
							modalObj.find("button.modal-btn-yes").on("click", {
								modalObj: modalObj,
								modalType: "messageBox",
								eventName: "YesEvent"
							}, opts.yesBtnEvent);
						}
					}
					break;
				default:
					break; //无法识别的modalType
			}
		} catch (e) {
			debug("ShowOptsDeal : outer : " + e.toString());
		}
	};

	/*---------------
		  MessageBoxChangeContentObj : 将对象加到消息提示框内容中
	--------------- */
	function MessageBoxChangeContentObj(modalObj, contentObj) {
		try {
			//先检查是否要将现有对象移出
			var modalContentObj = modalObj.find("a.modal-content-text");
			if ($.modalControl.messageBox.contentParent !== undefined) {
				var lastObj = modalContentObj.children();
				lastObj.addClass("invisible sr-only");
				lastObj.appendTo($.modalControl.messageBox.contentParent);
				$.modalControl.messageBox.contentParent = undefined;
			}

			if (typeof (contentObj) == "string") {
				modalContentObj.html(contentObj);
			} else if (contentObj instanceof jQuery) {
				//删除原来的内容
				modalContentObj.html("");
				//登记父节点位置
				$.modalControl.messageBox.contentParent = contentObj.parent();
				contentObj.appendTo(modalContentObj);
				contentObj.removeClass("invisible sr-only");
			}
		} catch (e) {
			debug("MessageBoxChangeContentObj : outer : " + e.toString());
		}
	};

	/*---------------
		  debug : 通过alert弹出debug的信息
	--------------- */
	function debug(str) {
		if ($.debug === true) {
			alert("debug：" + str);
		}
	};

})(jQuery);