//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    regFlag:true //用于首页判断是显示注册还是已经注册完了显示跳转的按钮（两者为同一个按钮）
  },

  goToIndex:function(){
    wx.switchTab({
      url: '/pages/course/index',
    });
  },
  onLoad:function(){
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });

    this.checkLogin(); //查询是否已经注册，方法在👇

  },
  onShow:function(){

  },
  onReady: function(){
    var that = this;
    setTimeout(function(){
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function(res) {
      var angle = -(res.x*30).toFixed(1);
      if(angle>14){ angle=14; }
      else if(angle<-14){ angle=-14; }
      if(that.data.angle !== angle){
        that.setData({
          angle: angle
        });
      }
    });
  },

  //查询是否注册过
  checkLogin:function(){
        var that = this;
        wx.login({                      //wx.login 函数就是用来提取code的，换言之，就是找🔑
            success:function(res){
                if (!res.code){
                    app.alert({'content':'登陆失败,请再次点击~~'});
                    return;
                }
                wx.request({
                  url:app.buildUrl('/member/check-reg'), //地址统一在app.js里面改
                  header:app.getRequestHeader(),
                  method:'POST',
                  data:{code:res.code},
                  success:function(res){
                      if (res.data.code != 200){
                          that.setData({
                              regFlag:false
                          });
                          return;
                      }
                  app.setCache("token",res.data.data.token);
                  that.goToIndex        //去到首页
                  }

                });

            }
        });
  },


  //点击前端页面按钮
  login:function(e){
        var that = this;
        if(!e.detail.userInfo){
             app.alert({'content':'登陆失败,请再次点击~~'});
             return;

        }
        var data = e.detail.userInfo;
        wx.login({
            success:function(res){
                if (!res.code){
                    app.alert({'content':'登陆失败,请再次点击~~'});
                    return;
                }
                data['code'] =res.code;
                wx.request({
                  url:app.buildUrl('/member/login'),
                  header:app.getRequestHeader(),
                  method:'POST',
                  data:data,
                  success:function(res){
                        if(res.data.code !=200){
                           app.alert({ 'content':res.msg});
                           return;
                        }
                        app.setCache("token",res.data.data.token);
                        that.goToIndex();
                  }
                });
            }


        });
  }

});