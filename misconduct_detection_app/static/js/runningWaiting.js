// Send selected file type and detection library
$("#detectionLibSelectionInput").val("Jplag");
let detectionLibSelectionSubmit = new FormData($('#detectionLibSelectionForm')[0]);
$.ajax({
    url: "/select/running/",
    type: 'POST',
    cache: false,
    data: detectionLibSelectionSubmit,
    processData: false,
    contentType: false,
    dataType:"json",
    beforeSend: function() {
        uploading = true;
    },
    success : function(data) {
        uploading = false;
    }
});

$(document).ready(function () {
    // Set name and other global variables, Django variables for this page
    $("#title").text("Please Wait...");

    // Clear body content
    $("body").empty();
    $("body").append("<br>");

    // Create first h1 element and attach it
    $("body").append("<h1 style='text-align: center'>Please wait, the detection is in progress.</h1>");
    $("body").append("<br>");

    // Crate second h1 element and attach it
    $("body").append("<h1 style='text-align: center'>This might take a few minutes.</h1>")
    $("body").append("<br>");

    // Crate the image and attach it
    $("body").append("<h1 style='text-align: center'><i class='fa fa-spinner fa-spin' style='font-size:68px'></i></h1>")

    // Redirect
    $(document).ajaxStop(function() {
        window.location.replace('/results/');
    });
});