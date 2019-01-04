;
var upload = {                             // Upload.py 中的函数 uploadPic()相关
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        if (!file_key) {
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'                          //buildPicUrl与python的URLManager一样在 static/js/common.js中
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>'; //本段代码是用于 封面图的预览代码，封面图上传后出现上传按钮右侧的预览图

        if ($(".upload_pic_wrap .pic-each").size() > 0) {
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        food_set_ops.delete_img();
    }
};                         // upload 不在主函数中是因为他并不是需要文件读完后就作用的，而是点击出发的，下面的两个很是 eventBind 和initEditor都是要页面刷完后直接现实的


var food_set_ops = {                                     //1.定义一个主函数 函数中有很多小函数
    init: function () {
        this.ue = null;
        this.eventBind();
        this.initEditor();
        this.delete_img();
    },
    eventBind: function () {                             //2.主函数中的小函数
        var that = this;

        $(".wrap_food_set .upload_pic_wrap input[name=pic]").change(function () {
            $(".wrap_food_set .upload_pic_wrap").submit();
        });

        $(".wrap_food_set select[name=cat_id]").select2({
            language: "zh-CN",
            width: '100%'
        });

        $(".wrap_food_set input[name=tags]").tagsInput({
            width: 'auto',
            height: 40,
            onAddTag: function (tag) {
            },
            onRemoveTag: function (tag) {
            }
        });

        $(".wrap_food_set .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }

            var cat_id_target = $(".wrap_food_set select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".wrap_food_set input[name=name]");
            var name = name_target.val();

            var instructor_id_target = $(".wrap_food_set input[name=instructor_id]");
            var instructor_id = instructor_id_target.val();

            var course_date_target = $(".wrap_food_set input[name=course_date]");
            var course_date = course_date_target.val();

            var location_target = $(".wrap_food_set input[name=location]");
            var location = location_target.val();

            var price_target = $(".wrap_food_set input[name=price]");
            var price = price_target.val();

            var summary = $.trim(that.ue.getContent());

            var stock_target = $(".wrap_food_set input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".wrap_food_set input[name=tags]");
            var tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }

            if (name.length < 1) {
                common_ops.alert("请输入符合规范的名称~~");
                return;
            }

            if (course_date.length < 1) {
                common_ops.alert("请输入开课日期~~");
                return;
            }

            if (location.length < 1) {
                common_ops.alert("请输入开课地点~~");
                return;
            }

            if (parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            if ($(".wrap_food_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }

            if (summary.length < 10) {
                common_ops.tip("请输入描述，并不能少于10个字符~~", price_target);
                return;
            }

            if (parseInt(stock) < 1) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }

            if (tags.length < 1) {
                common_ops.alert("请输入标签，便于搜索~~");
                return;
            }

            btn_target.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                instructor_id:instructor_id,
                course_date:course_date,
                location:location,
                price: price,
                main_image: $(".wrap_food_set .pic-each .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                id: $(".wrap_food_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("/course/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/course/index");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });

        });


    },
    initEditor: function () {
        var that = this;
        that.ue = UE.getEditor('editor', {
            toolbars: [
                ['undo', 'redo', '|',
                    'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', '|', 'rowspacingtop', 'rowspacingbottom', 'lineheight'],
                ['customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                    'directionalityltr', 'directionalityrtl', 'indent', '|',
                    'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                    'link', 'unlink'],
                ['imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
                    'insertimage', 'insertvideo', '|',
                    'horizontal', 'spechars', '|', 'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols']

            ],
            enableAutoSave: true,
            saveInterval: 60000,
            elementPathEnabled: false,
            zIndex: 4,
            serverUrl: common_ops.buildUrl('/upload/ueditor')
        });
    },
    delete_img: function () {
        $(".wrap_food_set .del_image").unbind().click(function () {
            $(this).parent().remove();
        });
    }
};

$(document).ready(function () {
    food_set_ops.init();
});