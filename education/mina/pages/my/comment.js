//获取应用实例
var app = getApp();
Page({
    data: {
        "content": "",
        "score": 10,
        "instructor_comment_id":0 //论坛里帖子的id instructor_comment_id
    },
    onLoad: function (e) {    //上一页中 toComment函数带过来的course ID
        var that = this;
        that.setData({
            instructor_comment_id:e.id
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
            url: app.buildUrl("/my/comment/add"),
            header: app.getRequestHeader(),
            method: "POST",
            data: {
                "content": that.data.content,
                "score": that.data.score,
                "instructor_comment_id": that.data.instructor_comment_id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                wx.redirectTo({
                    url:"/pages/my/info?id=" + that.data.instructor_comment_id
                });
            }
        });
    }
});