let current_status = $('#js-data').data('importlog-status');
if (['running', 'created'].includes(current_status)){
    getData();
}

function getData() {
    let pk = $('#js-data').data('importlog-pk');
    $.ajax({
        url : $('#js-data').data('import-log-get'),
        dataType: "json",
        success : function(data) {
            status = data['status'];
            if (current_status != status)
                location.reload();
            if (current_status == 'created'){
                setTimeout(getData, 1000);
            } else if (current_status == 'running'){
                setTimeout(getData, 10000);
            }
        }
    });
}