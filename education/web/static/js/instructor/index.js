;
var food_index_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        var that = this;
        $(".wrap_search .search").click( function(){
            $(".wrap_search").submit();
        });
    },
};

$(document).ready( function(){
    food_index_ops.init();
});