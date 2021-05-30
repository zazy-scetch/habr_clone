$(document).ready(function () {
// 	$('#main-magnifier').click(function () {
// 		$('.form-search').fadeIn();
// 		$('#main-magnifier').css({
// 			'display':'none',
// 		})
// 		return false;
// 	})
    // $('.magnifier-in-input').click(function(){
    // 	$('#search-articles-form').submit();
    // });
    $('.page-link').click(function () {
        let num_page = $(this).attr('class');
        num_page = num_page.split('-')
        num_page = num_page[num_page.length - 1]
        $('#search-articles-form').attr("action", "/search/" + num_page)
        $('#search-articles-form').submit();
    });
})

var focusOnInput = function(){
    $('.input-search').focus();
}