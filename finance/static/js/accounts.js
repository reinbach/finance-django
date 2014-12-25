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
                // clear/reset modal values
            },
            error: function(data) {
                $("#accountAddModalBody").html(data.result);
            }
        });
        return false;
    });

    $("select[name!=account_type]").change(function() {
        var new_value = $(this).val();
        var row = $(this).parents("tr");
        var summary_value = $(":input[name$='summary']", row).val()
        $("tr ~ tr").each(function() {
            if ($(":input[name$='summary']", this).val() == summary_value) {
                $("select", this).each(function() {
                    if ($(this).val() == "") {
                        $(this).val(new_value);
                    }
                });
            }
        });
    });
});

function updateAccountOptions(options) {
    $("select[name!=account_type]").each(function() {
        var cur_value = $(this).val();
        $(this).html(options);
        $(this).val(cur_value);
    });
}
