//获取应用实例
var app = getApp();
Page({
    data: {},
    onLoad() {

    },



    onShow() {
        this.getInstructorCommentInfo();
    },

    ////not works!
    onPullDownRefresh:function(){
        app.console('test');
        wx.setNavigationBarTitle({
             title: ''
        });
        wx.showNavigationBarLoading();
    },


    getInstructorCommentInfo:function(){
        var list = this.data.list;
        var that = this;
        wx.request({
            url:app.buildUrl('/my/index'),
            header:app.getRequestHeader(),
            method:"POST",
            success:function(res){
                var resp = res.data;
                if(resp.code != 200){
                    app.alert({'content':resp.msg});
                    return;
                }
                that.setData({
                     list:resp.data.list
                });
            }

        });
    },


     //点击跳转到comment Info 页面
    TabCommentInfo: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/my/info?id=" + e.currentTarget.dataset.id
            });
        }
    },



});