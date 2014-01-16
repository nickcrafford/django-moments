/** Moments Admin JS customizations. */
(function($) {
    $(document).ready(function($) {
    	// "Upload zip" button on moments list page
        $(".object-tools").append('<li><a href="/admin/base/moment/upload-zip/" class="addlink">Upload Zip</a></li>');

        // "Save Changes" button on moments list page
        $(".paginator").append('<input style="float:right" id="save_changes" type="button" value="Save Changes" />');

        // Click handler for "Save Changes" button on moment list page
        $("#save_changes").click(function() {
        	window.confirm = function(message) { console.log(message)};
        	$("#action-toggle").click().click();
        	$('select[name="action"]').val('save_inlines_action');
        	$('button[name="index"]').click();
        });

        // Fix image paths for moments on moment detail page
        var image_link = $('.file-upload a');
        image_link.attr("href", "/static/assets/" + image_link.attr("href"));
    });
})(django.jQuery);
