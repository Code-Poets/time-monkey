$(function() {
    $(".bs-modal").each(function () {
        $(this).modalForm({
            formURL: $(this).data("form-url")
        });
    });

    $("#opener_create").each(function (){
        $(this).modalForm({
            formURL: $(this).data("form-url")
        });
    });

    $('.modal-dialog').draggable();

    $(".modal-dialog" ).on("dragstop", function(event, ui) {
        $(".custom-modal").css({
            top:  ' calc( ' + $(".custom-modal").css("top") + ' + ' +  $(".modal-dialog").css("top") + ')',
            left: ' calc( ' + $(".custom-modal").css("left") + ' + ' +  $(".modal-dialog").css("left") + ')'
        });
        $(".modal-dialog").css({
            top:  '0px',
            left: '0px'
        });
    });

    $("#modal").on('shown.bs.modal', function() {
        $("body").removeClass("modal-open");
        $(".custom-modal").removeClass("modal");
    });
});
