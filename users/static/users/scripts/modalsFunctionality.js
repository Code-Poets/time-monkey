$(function() {
    let customModal = jQuery(".custom-modal")
    let modalDialog = jQuery(".modal-dialog")

    $(".bs-modal").each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url')
        });
    });

    modalDialog.draggable();

    modalDialog.on("dragstop", function() {
        customModal.css({
            top:  ' calc( ' + customModal.css("top") + ' + ' +  modalDialog.css("top") + ')',
            left: ' calc( ' + customModal.css("left") + ' + ' +  modalDialog.css("left") + ')'
        });
        modalDialog.css({
            top:  '0px',
            left: '0px'
        });
    });

    $("#modal").on('shown.bs.modal', function () {
        $("body").removeClass("modal-open");
        customModal.removeClass("modal");
    });
});
