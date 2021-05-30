'use strict';
$('.modal').on('click', '.btn-secondary, .close', function (event) {
        let target_href = event.target;
        if (target_href) {
            $.ajax({
                success: function (data) {
                    $('.modal').modal('hide');
                    console.log('close all modals');
                },
            });
        };
        event.preventDefault();
    });
