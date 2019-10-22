$("#id_project").change(function () {
    var url = $("#reportForm").attr("data-activities-url");
    var projectId = $(this).val();
    $.ajax({
        url: url,
        data: {
            'project': projectId
        },
        success: function (data) {
            $("#id_activities").html(data);
        }
    });
});
