function initResourcesPopup() {
    $('#resources-popup').on('show.bs.modal', function () {
        $('input[id^="check-"]').prop('checked', false);
        $('#check-all').prop('indeterminate', false);
        $('#no-results').addClass('visually-hidden');

        const providerId = $('#provider_id').val();
        if (providerId) {
            $('#resource_provider_id').val(providerId);
        }
    });
}

function fetchResources() {
    /* Fetch resource records from the app server and populate the modal. */
    const providerId = $('#resource_provider_id').val();
    const includePackaged = $('#include_packaged').is(':checked');
    const url = `${rootPath}/packages/fetch-resources/${providerId}?${includePackaged ? 'include_packaged=1' : ''}`;

    $.getJSON(url)
        .done(function (result) {
            const tbody = $('<tbody id="resources-table-body">');
            if (result.total > 0) {
                for (let i = 0; i < result.items.length; i++) {
                    let row = $('<tr>');
                    let resource = result.items[i];
                    let resourceCheck = $(`<input class="form-check-input" type="checkbox" value=""
                                            id="check-item-${resource.id}" onchange="checkItem();">`);
                    resourceCheck.data(resource);
                    row.append($('<td>').append(resourceCheck));
                    row.append($('<td>').text(resource.title));
                    row.append($('<td>').text(resource.filename));
                    row.append($('<td>').text(resource.size));
                    row.append($('<td>').text(resource.mimetype));
                    row.append($('<td>').text(Object.keys(resource.archive_paths)));
                    tbody.append(row);
                }
                $('#no-results').addClass('visually-hidden');
            } else {
                $('#no-results').removeClass('visually-hidden');
            }
            $('#resources-table-body').replaceWith(tbody);
        })
        .fail(function (jqxhr, textStatus, error) {
            alert(`${textStatus}: ${error}`)
        })
}

function addResources() {
    /* Add checked resources in the modal to the resources multiselect form control. */
    const checkedResources = $('input:checked[id^="check-item-"]');
    if (checkedResources.length > 0) {
        const resourceSelect = $('#resource_ids');
        checkedResources.each(function () {
            let resource = $(this).data();
            // only add if not already present in the multiselect
            if ($(`input[value="${resource.id}"]`).length === 0) {
                let li = $('<li>');
                let checkbox = $(`<input type="checkbox" checked name="resource_ids" id="${resource.id}" value="${resource.id}">`);
                let label = $(`<label for="${resource.id}">`);
                label.text(`${resource.title} [${resource.filename} | ${resource.size} | ${resource.mimetype}]`);
                li.append(checkbox);
                li.append(' ');
                li.append(label);
                resourceSelect.append(li);
            }
        });
        flashTooltip('add-resources-btn', 'Added!');
    } else {
        flashTooltip('add-resources-btn', 'No resources selected');
    }
}

function toggleContribAuthor() {
    const isAuthor = $('#is_author').is(':checked');
    if (isAuthor) {
        $('#author_role_grp').removeClass('visually-hidden');
        $('#author_role').prop('required', true);
        $('#author_role').prop('disabled', false);
        $('#contributor_role_grp').addClass('visually-hidden');
        $('#contributor_role').prop('required', false);
        $('#contributor_role').prop('disabled', true);
    } else {
        $('#author_role_grp').addClass('visually-hidden');
        $('#author_role').prop('required', false);
        $('#author_role').prop('disabled', true);
        $('#contributor_role_grp').removeClass('visually-hidden');
        $('#contributor_role').prop('required', true);
        $('#contributor_role').prop('disabled', false);
    }
    selectContribRole();
}

function selectContribRole() {
    const isAuthor = $('#is_author').is(':checked');
    const isContactPerson = $('#contributor_role option:selected').val() == 'pointOfContact';
    if (!isAuthor && isContactPerson) {
        $('#contact_info_grp').removeClass('visually-hidden');
        $('#contact_info').prop('required', true);
        $('#contact_info').prop('disabled', false);
    } else {
        $('#contact_info_grp').addClass('visually-hidden');
        $('#contact_info').prop('required', false);
        $('#contact_info').prop('disabled', true);
    }
}

function updateORCID() {
    const orcid_url = 'https://orcid.org/' + $('#orcid').val();
    $('#orcid-description').text(orcid_url);
}

function updateROR() {
    const ror_url = 'https://ror.org/' + $('#ror').val();
    $('#ror-description').text(ror_url);
}

function selectGeoShape() {
    const isPoint = $('input[type="radio"][value="point"]').is(':checked');
    const isRegion = $('input[type="radio"][value="box"]').is(':checked');
    if (!isPoint && !isRegion) {
        $('input[type="radio"][value="point"]').prop('checked', true);
    }
    if (isRegion) {
        $('#geo_region_grp').removeClass('visually-hidden');
        $('#west').prop('required', true);
        $('#south').prop('required', true);
        $('#west').prop('disabled', false);
        $('#south').prop('disabled', false);
    } else {
        $('#geo_region_grp').addClass('visually-hidden');
        $('#west').prop('required', false);
        $('#south').prop('required', false);
        $('#west').prop('disabled', true);
        $('#south').prop('disabled', true);
    }
}


async function fileSelected(zip = false) {
    /* Update file/zip upload form with file size, content type
     * and SHA-256 hash computed from the selected input file.
     *
     * Adapted from https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API/Non-cryptographic_uses_of_subtle_crypto
     */
    zip = zip ? 'zip_' : '';
    const file = $(`#${zip}file`).prop('files')[0];
    const arrayBuffer = await file.arrayBuffer();
    const hashAsArrayBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
    const uint8ViewOfHash = new Uint8Array(hashAsArrayBuffer);
    const hashAsString = Array.from(uint8ViewOfHash)
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");

    $(`#${zip}size`).val(file.size);
    $(`#${zip}mimetype`).val(file.type);
    $(`#${zip}sha256`).val(hashAsString);
}


let sdgVocab;

function loadSDGVocabulary() {
    $.getJSON("/vocabulary/SDG")
        .done(function (data) {
            sdgVocab = data;
            populateSDGs();
        })
        .fail(function (jqxhr, textStatus, error) {
            alert(`${textStatus}: ${error}`);
        });
}


function populateSDGs() {
    const goalDropdown = $('#goal');
    $.each(sdgVocab.keywords, function (i, sdg) {
        goalDropdown.append(
            $(`<option value="${sdg.key}">${sdg.key} ${sdg.title}</option>`)
        );
    });
    populateSDGTargets();
}


function populateSDGTargets() {
    const goal = $('#goal').val();
    const targetDropdown = $('#target');
    targetDropdown.empty();
    targetDropdown.append(
        $(`<option value="">All</option>`)
    );
    $.each(sdgVocab.keywords, function (i, sdg) {
        if (sdg.key == goal) {
            $.each(sdg.keywords, function (j, sdgTarget) {
                targetDropdown.append(
                    $(`<option value="${sdgTarget.key}">${sdgTarget.key} ${sdgTarget.target}</option>`)
                );
            });
        }
    });
    populateSDGIndicators();
}


function populateSDGIndicators() {
    const goal = $('#goal').val();
    const target = $('#target').val();
    const indicatorDropdown = $('#indicator');
    indicatorDropdown.empty();
    indicatorDropdown.append(
        $(`<option value="">All</option>`)
    );
    $.each(sdgVocab.keywords, function (i, sdg) {
        if (sdg.key == goal) {
            $.each(sdg.keywords, function (j, sdgTarget) {
                if (sdgTarget.key == target) {
                    $.each(sdgTarget.keywords, function (k, sdgIndicator) {
                        indicatorDropdown.append(
                            $(`<option value="${sdgIndicator.key}">${sdgIndicator.key} ${sdgIndicator.indicator}</option>`)
                        );
                    });
                }
            });
        }
    });
}
