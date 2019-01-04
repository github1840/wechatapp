//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
var utils = require('../../utils/util.js');

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax:1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount:2,
        mobileInput:'',
        nameInput:'',
        commentList:[],
        commentCount:0,
        course_id:0

    },
    onLoad: function (e) {
        var that = this;
        that.setData({        //从上一页获取ID 传到本页， setData， 下面的getInfo就会直接用到
                id:e.id
        });

    },
    onShow:function(){
        this.getInfo();
        this.getComment();
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    //报名
    addShopCar: function () {
        var that = this;
        var data = {
            //课程ID
            'id':this.data.info.id,
            'number':this.data.buyNumber
        };

        wx.request({
            url:app.buildUrl('/cart/set'),
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function(res){
                var resp =res.data;
                app.alert({'content':resp.msg});
                that.setData({
                     //隐藏报名登记弹出框
                     hideShopPopup:true
                });

            }
        });

        this.sendMobileServer();
        this.sendNameServer();
    },

    buyNow: function () {
        wx.navigateTo({
            url: "/pages/order/index"
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if( this.data.buyNumber <= this.data.buyNumMin){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if( this.data.buyNumber >= this.data.buyNumMax ){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    //获取详情数据
    getInfo:function(){
        var that = this;
        wx.request({
            url:app.buildUrl("/course/info"),
            header:app.getRequestHeader(),
            data:({
              id: that.data.id
            }),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    wx.navigateTo({
                        url: "/pages/course/index"
                    });
                    return;
                }

                that.setData({
                    info: resp.data.info,
                    buyNumMax: 5,
                    shopCarNum:resp.data.cart_number
                });

                WxParse.wxParse('article', 'html', resp.data.info.summary, that, 5);
            }
        });
    },

    //分享
    onShareAppMessage: function () {
        var that = this;
        return {
            title: that.data.info.name,
            path: '/pages/course/info?id=' + that.data.info.id,
            success: function (res) {
                // 转发成功
                wx.request({
                    url: app.buildUrl("/member/share"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        url: utils.getCurrentPageUrlWithArgs()
                    },
                    success: function (res) {

                    }
                });
            },
            fail: function (res) {
                // 转发失败
            }
        }
    },
   //报名时收取手机号码信息
    listenerMobileInput:function( e ){
        this.setData({
            mobileInput: e.detail.value
        });
    },

    sendMobileServer:function(e){
        var that = this
        wx.request({
            url:app.buildUrl("/member/mobile"),
            header:app.getRequestHeader(),
            data:({
              mobile: that.data.mobileInput
            }),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
            }
        });
    },

   //报名时收取用户姓名

    listenerNameInput:function( e ){
        this.setData({
            nameInput: e.detail.value
        });
    },

    sendNameServer:function(e){
        var that = this
        wx.request({
            url:app.buildUrl("/member/name"),
            header:app.getRequestHeader(),
            data:({
              name: that.data.nameInput
            }),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
            }
        });
    },




    //去评论页面
    toComment:function(e){
            var that = this;
            wx.navigateTo({
                url:'/pages/course/comment?id='+ e.currentTarget.dataset.id //两种带数据方法，一是currentTarget 数据从wxml中获取，而是that.data.info.id 数据直接从JS的data中取出

            });
    },
    //去课程动态
    toMyCourseActivity:function(e){
            var that = this;
            that.setData({        //从上一页获取ID 传到本页， setData， 下面的getInfo就会直接用到
                course_id:e.currentTarget.dataset.id
            });
            wx.request({
                url: app.buildUrl("/course/activity"),
                header: app.getRequestHeader(),
                data: {
                    course_id: that.data.course_id
                },
                success: function (res) {
                    var resp = res.data;
                    if (resp.code != 200) {
                        app.alert({"content": resp.msg});
                        return;
                    }
                    that.setData({
                        instructor_comment_id: resp.data.instructor_comment_id
                    });
                    wx.navigateTo({
                         url:'/pages/my/info?id='+ that.data.instructor_comment_id
                    });
                }
        });
    },


    //显示评论内容
    getComment:function(){
         var that = this;
        wx.request({
            url: app.buildUrl("/course/comments"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                    commentList: resp.data.list,
                    commentCount: resp.data.count,
                });
            }
        });
    },
});