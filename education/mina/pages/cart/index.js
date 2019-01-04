//index.js
var app = getApp();
Page({
    data: {
        editMode:true,
        number:1,   //
        duration: 1000,
        p:1,
        processing:false,
        list:[],
        currentTab: 0,
    },

    onLoad: function () {

    },
    onShow:function(){

        this.getCartList();
    },
    //每项前面的选中框
    selectTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (index !== "" && index != null) {
            list[ parseInt(index) ].active = !list[ parseInt(index) ].active;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //计算是否全选了
    allSelect: function () {
        var list = this.data.list;
        var allSelect = false;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (curItem.active) {
                allSelect = true;
            } else {
                allSelect = false;
                break;
            }
        }
        return allSelect;
    },
    //计算是否都没有选
    noSelect: function () {
        var list = this.data.list;
        var noSelect = 0;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (!curItem.active) {
                noSelect++;
            }
        }
        if (noSelect == list.length) {
            return true;
        } else {
            return false;
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        var currentAllSelect = this.data.allSelect;
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            list[i].active = !currentAllSelect;
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
    },
    //加数量
    jiaBtnTap: function (e) {
        var that = this;
        var index = e.currentTarget.dataset.index;
        var list = that.data.list;
        list[parseInt(index)].number++;
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
    },
    //减数量
    jianBtnTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (list[parseInt(index)].number > 1) {
            list[parseInt(index)].number--;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //编辑默认全不选
    editTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = false;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        this.setData({
             editMode:true,
        })
    },
    //选中完成默认全选
    saveTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = true;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        this.setData({
             editMode:false,
        })
    },
    getSaveHide: function () {
        return this.data.saveHidden;
    },
    totalPrice: function () {
        var list = this.data.list;
        var totalPrice = 0.00;
        for (var i = 0; i < list.length; i++) {
            if ( !list[i].active) {
                continue;
            }
            totalPrice = totalPrice + parseFloat( list[i].price );
        }
        return totalPrice;
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        this.setData({
            list: list,
            saveHidden: saveHidden,
            totalPrice: total,
            allSelect: allSelect,
            noSelect: noSelect,
        });
    },
    //去结算
    toPayOrder: function () {
        wx.navigateTo({
            url: "/pages/order/index"
        });
    },
    //如果没有显示去光光按钮事件
    toIndexPage: function () {
        wx.switchTab({
            url: "/pages/course/index"
        });
    },
    //选中删除的数据
    deleteSelected: function () {
        var list = this.data.list;
        var goods = [];
        list = list.filter(function ( item ) {
            if( item.active ){
                goods.push({
                     "id":item.course_id
                });
            }
            return !item.active;
        });
        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        //发送请求到后台删除数据
         wx.request({
            url:app.buildUrl('/cart/del'),
            header:app.getRequestHeader(),
            method:"POST",
            data:{
                   goods:JSON.stringify(goods)
            },
            success:function(res){
                var resp = res.data;
                if(resp.code != 200){
                    app.alert({'content':resp.msg});
                    return;
                }
            }
         });
    },

    //点击跳转到Course Info 页面
    TabCourseInfo: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/course/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
  //报名信息提取
    getCartList: function () {
        var that = this
        if( that.data.processing ){
           return;
        }

        that.setData({
            processing:true
        });


        wx.request({
            url:app.buildUrl('/cart/index'),
            header:app.getRequestHeader(),
            method:"POST",
            success:function(res){

                var resp = res.data;
                app.console(resp);
                if(resp.code != 200){
                    app.alert({'content':resp.msg});
                    return;
                }
                var list = resp.data.list;
                that.setData({
                     list:list,
                     processing:false,
                     saveHidden: true,
                     totalPrice: "00.00",
                     allSelect: false,
                     noSelect: false,
                });

                that.setPageData( that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list);

            }

        });
    },

  //分选框
  swiperTab: function (e) {
    var that = this;
    that.setData({
      currentTab: e.detail.current
    });
  },
  //点击切换
  clickTab: function (e) {
    var that = this;
    if (this.data.currentTab === e.target.dataset.current) {
      return false;
    } else {
      that.setData({
        currentTab: e.target.dataset.current
      })
    }
  },



});