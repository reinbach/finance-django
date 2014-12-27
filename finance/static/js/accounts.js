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
                $(":input[type!='hidden']", acctForm).val("");
                $(":input", acctForm).attr("checked", false);
                $("#id_parent", acctForm).html(data.parent);
            },
            error: function(data) {
                $("#accountAddModalBody").html(data.result);
            }
        });
        return false;
    });
});

function updateAccountOptions(options) {
    $("select[name!=account_type]").each(function() {
        var cur_value = $(this).val();
        $(this).html(options);
        $(this).val(cur_value);
    });
}
