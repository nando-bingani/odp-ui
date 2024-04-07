function initCheckAll() {
    $('#check-all').prop('indeterminate', false);

    let checkedAll = false;
    const checkedCount = $('input:checked[id^="check-item-"]').length;

    if (checkedCount > 0) {
        const itemCount = $('input[id^="check-item-"]').length;
        if (checkedCount < itemCount) {
            $('#check-all').prop('indeterminate', true);
        } else {
            checkedAll = true;
        }
    }

    $('#check-all').prop('checked', checkedAll);
    $('label[for="check-all"]').text(`Select ${checkedAll ? 'none' : 'all'}`);
}

function checkAll() {
    const checked = $('#check-all').is(':checked');
    $('input[id^="check-item-"]').prop('checked', checked);
    $('label[for="check-all"]').text(`Select ${checked ? 'none' : 'all'}`);
}

function checkItem() {
    initCheckAll();
}

function flashTooltip(elementId, text) {
    const tooltip = new bootstrap.Tooltip($(`#${elementId}`), {
        title: text,
        trigger: 'manual'
    });
    tooltip.show();
    setTimeout(function () {
        tooltip.hide();
    }, 3000);
}
