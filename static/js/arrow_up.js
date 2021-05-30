$(document).ready(function () {
    let content_position = 0
    $(function () {
        $('.scrollup').click(function () {
            content_position = $(window).scrollTop()
            $("html, body").animate({scrollTop: 0}, 100);
        })
    })
    $(function () {
        $('.scrolldown').click(function () {
            $("html, body").animate({scrollTop: content_position}, 100);
        })
    })
    $(window).scroll(function () {
        if ($(this).scrollTop() > 500) {
            $('.scrollup').fadeIn();
            $('.scrolldown').fadeOut();
        } else {
            $('.scrollup').fadeOut();
            if (content_position > 0) {
                $('.scrolldown').fadeIn();
            }
        }
    });
});