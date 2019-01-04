//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 5000,
        duration: 1500,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        p:1,
        processing:false,
        // 3D 轮播图用的参数
        swiperH:'',//swiper高度
        nowIdx:0,//当前swiper索引
    },
    onLoad: function () {
        var that = this;
        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });
    },
    //解决切换不刷新维内托，每次展示都会调用这个方法
    onShow:function(){
        this.getBannerAndCat();
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },

    //搜索框
    listenerSearchInput:function( e ){
        this.setData({
            searchInput: e.detail.value,
        });
    },
    toSearch:function( e ){
        this.setData({
            p:1,
            goods:[],
            loadingMoreHidden:true,
            inputShowed: true
        });
        this.getCourseList();
        this.setData({
        });
	},

    //**********搜索框

    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/course/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/course/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/course/index"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    banners: resp.data.banner_list,
                    categories: resp.data.cat_list
                });
                that.getCourseList();
            }
        });
    },
    catClick: function (e) {
        this.setData({
            activeCategoryId: e.currentTarget.id,
            searchInput:''
        });
        this.setData({
            loadingMoreHidden: true,
            p:1,
            goods:[]
        });
        this.getCourseList();
    },


    onReachBottom: function () {
        var that = this;
        setTimeout(function () {
            that.getCourseList();
        }, 500);
    },

    getCourseList: function () {
        var that = this;
        if( that.data.processing ){
            return;
        }
        if( !that.data.loadingMoreHidden ){
            return;
        }
        that.setData({
            processing:true
        });

        wx.request({
            url: app.buildUrl("/course/search"),
            header: app.getRequestHeader(),
            data: {
                cat_id: that.data.activeCategoryId,
                mix_kw: that.data.searchInput,
                p: that.data.p,
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                var goods = resp.data.list;
                that.setData({
                    goods: that.data.goods.concat( goods ),
                    p: that.data.p + 1,
                    processing:false
                });

                if( resp.data.has_more == 0 ){
                    that.setData({
                        loadingMoreHidden: false
                    });
                }

            }
        });
    },


//3D 轮播图

    //获取swiper高度
    getHeight:function(e){
    var winWid = wx.getSystemInfoSync().windowWidth - 2*50;//获取当前屏幕的宽度
    var imgh = e.detail.height;//图片高度
    var imgw = e.detail.width;
    var sH = winWid * imgh / imgw + "px"
    this.setData({
        swiperH: sH//设置高度
    })
},
    //swiper滑动事件
    swiperChange:function(e){
        this.setData({
            nowIdx: e.detail.current,
            swiperCurrent: e.detail.current
        })
    },

});
