function showModal(modalId, reloadOnCancel = false) {
    const modal = new bootstrap.Modal(`#${modalId}`);
    if (reloadOnCancel) {
        $(`#${modalId}`).on('hide.bs.modal', function () {
            location.reload(true);
        })
    }
    modal.show();
}
