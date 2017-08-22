$(function () {
    var $more = $("#more");
    var $pages = $more.attr("pages");
    $more.bind("click", function () {
        var page = $(this).attr("value");
        $.get($SCRIPT_ROOT + '/more', {
            page : page
        }, function (data, textStatus) {
                $(".article:last").after(data);
                var $next_page = parseInt(page)+1;
                if ($next_page > $pages){
                    $more.text("已显示所有内容");
                    $more.unbind("click")
                    $more.unbind("mouseover")
                }
                $more.attr("value", parseInt(page)+1);
        });
    });
    $more.bind("mouseover", function () {
        $(this).css("background-color", "#E0E0E0")
    });
    $more.bind("mouseout", function () {
        $(this).css("background-color", "white")
    });
});
