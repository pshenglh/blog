$(function () {
    var $more = $("#more");
    $more.click(function () {
        var page = $(this).attr("value");
        $.get($SCRIPT_ROOT + '/more', {
            page : page
        }, function (data, textStatus) {
                $(".article:last").after(data);
                var $next_page = parseInt(page)+1;
                $more.attr("value", parseInt(page)+1);
        });
    });
    $more.mouseover(function () {
        $(this).css("background-color", "#E0E0E0")
    });
    $more.mouseout(function () {
        $(this).css("background-color", "white")
    });
});
