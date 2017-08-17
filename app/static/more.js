$(function () {
    $("#more").click(function () {
        $.get('/static/more.html', function (data, textStatus) {
            $(".article:last").after(data)
        });

    })
});