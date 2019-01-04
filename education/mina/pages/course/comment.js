//获取应用实例
var app = getApp();
Page({
    data: {
        "content": "",
        "score": 10,
        "course_id":0
    },
    onLoad: function (e) {    //上一页中 toComment函数带过来的course ID
        var that = this;
        that.setData({
            course_id:e.id
        });
    },

    scoreChange: function (e) {
        this.setData({
            "score": e.detail.value
        });
    },


    bindFormSubmit: function(e) {
        console.log(e.detail.value.textarea)
        this.setData({
            content: e.detail.value.textarea
        });
        this.doComment()
    },



    doComment: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/course/comment/add"),
            header: app.getRequestHeader(),
            method: "POST",
            data: {
                "content": that.data.content,
                "score": that.data.score,
                "course_id": that.data.course_id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                wx.redirectTo({
                    url:"/pages/course/info?id=" + that.data.course_id
                });
            }
        });
    }
});