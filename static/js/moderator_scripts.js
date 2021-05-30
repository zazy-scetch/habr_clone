'use strict';

$('.checkbox-field').change(function (event) {
    let is_pressed = event.target.checked
    if (is_pressed) {
        $.ajax({
            success: function (data) {
                $('#id_num_days, label[for="id_num_days"]').hide();
                let day_field = $('#id_num_days')[0];
                day_field.value = 1;
            },
        });
    }else {
        $.ajax({
            success: function (data) {
                $('#id_num_days, label[for="id_num_days"]').show();
            },
        });
    };
    event.preventDefault();
});


//    $('.spam').on('click', '.btn-unlock', function (event) {
//        let user_id = event.target.href.split('/')[event.target.href.split('/').length - 2];
//        if (user_id) {
//            $.ajax({
//                url: "/moderator/remove_user_ban/" + user_id + "/",
//
//                success: function (data) {
//                    $('.spam').html(data.result);
//                    console.log('success');
//                },
//            });
//        }
//        event.preventDefault();
//    });
//};