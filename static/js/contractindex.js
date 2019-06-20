function CreateContract() {
    var content = [];
    for (var i = 1; i < count; i++) {
        let res = {};
        res['Obligor'] = $("#Obligor"+i).val();
        res['creditor'] = $("#creditor"+i).val();
        res['premise'] = $("#premise"+i).val();
        res['res'] = $("#res"+i).val();
        res['tc_act'] = $("#tc_act"+i).val();
        res['tc_bas'] = $("#tc_bas"+i).val();
        content.push(res)
    }
    var data = {
        "contract_name":$("#contract_name").val(),
        "Obligor":$("#Obligor").val(),
        "creditor":$("#creditor").val(),
        "content":content
    }

    $.ajax({
        type:"POST",
        url:"/saveContract",
        contentType:'application/json; charset=utf-8',
        data: JSON.stringify(data),
        success:function(data) {   
            alert("submit success!");
            window.location.href="/";
        }
    });
}
