$(function() {
    $("#delete-report").each(function (){
            $(this).modalForm({
                formURL: $(this).data("form-url")
            });
    });

    $("#opener_join").each(function (){
        $(this).modalForm({
            formURL: $(this).data("form-url")
        });
    });
});
