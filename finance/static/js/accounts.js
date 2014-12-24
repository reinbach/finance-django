$(function() {
    var acctForm = $("#account-form");
    acctForm.submit(function() {
        $.ajax({
            type: acctForm.attr("method"),
            url: acctForm.attr("action"),
            data: acctForm.serialize(),
            success: function(data) {
                updateAccountOptions(data.result);
                $("#accountAddModal").modal("hide");
                // update all debit/credit with same summary value
            },
            error: function(data) {
                $("#accountAddModalBody").html(data.result);
            }
        });
        return false;
    });
});

function updateAccountOptions(options) {
    $("select").each(function() {
        var cur_value = $(this).val();
        console.log("cur: " + cur_value);
        $(this).html(options);
        $(this).val(cur_value);
    });
}
