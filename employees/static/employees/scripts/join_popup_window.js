$(function () {
    $(dialog_id).dialog ({
        modal: true,
        autoOpen: false,
	    buttons : [
	        {
	            text: join_discard_text,
	            click: function () {
	                $(this).dialog('close');
	            }
	        }
	    ]
	}).prev().find(".ui-dialog-titlebar-close").hide ();

	$(opener_id).click(function () {
	    $(dialog_id).dialog('open');
	});
});