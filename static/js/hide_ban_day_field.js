'use strict';

window.onload = function () {
    $('.checkbox-field').change(function (event) {
        let is_pressed = event.target.checked
        if (is_pressed) {
            $.ajax({
                success: function (data) {
                    $('#id_num_days, label[for="id_num_days"]').hide();
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
    });}