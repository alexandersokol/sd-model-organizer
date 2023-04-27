function findElem(elementId) {
    return document.getElementById(elementId)
    // return gradioApp().getElementById(elementId)
}

function log(text) {
    console.log(text)
}

function updateDownloadBlockVisibility(id, tag, isVisible, visibleUnit) {
    const block = findElem(tag + '-' + id)
    const previewBlock = findElem(tag + '-preview-' + id)

    if (block) {
        block.style.display = isVisible ? visibleUnit : 'none'
        log(block.id + " display =" + block.style.display)
    }

    if (previewBlock) {
        previewBlock.style.display = isVisible ? visibleUnit : 'none'
        log(previewBlock.id + " display =" + previewBlock.style.display)
    }
}

function updateDownloadCardState(id, state) {
    let cardClass = ''
    let isUrlVisible = false
    let isDownloadProgressVisible = false
    let isResultBoxVisible = false

    if (state === 'Pending') {
        cardClass = 'mo-alert-secondary'
        isUrlVisible = true
    } else if (state === 'In Progress') {
        cardClass = 'mo-alert-primary'
        isUrlVisible = true
        isDownloadProgressVisible = true
    } else if (state === 'Completed') {
        cardClass = 'mo-alert-success'
        isResultBoxVisible = true
    } else if (state === 'Exists') {
        cardClass = 'mo-alert-info'
        isResultBoxVisible = true
    } else if (state === 'Error') {
        cardClass = 'mo-alert-danger'
        isResultBoxVisible = true
    } else if (state === 'Cancelled'){
        cardClass = 'mo-alert-warning'
    } else {
        return
    }
    log(cardClass)
    const className = 'mo-downloads-card ' + cardClass
    log(className)
    const cardElement = findElem('download-card-' + id)
    cardElement.className = className
    findElem('status-' + id).textContent = state

    updateDownloadBlockVisibility(id, 'url', isUrlVisible, 'block')
    updateDownloadBlockVisibility(id, 'info-bar', isDownloadProgressVisible, 'flex')
    updateDownloadBlockVisibility(id, 'progress', isDownloadProgressVisible, 'flex')
    updateDownloadBlockVisibility(id, 'result-box', isResultBoxVisible, 'block')

}

function updateResultText(id, title, text) {
    const elem = findElem('result-box-' + id)
    if (elem) {
        let resultContent = '<p>' + title + ':</p>'
        if (Array.isArray(text)) {
            text.forEach(function (txt) {
                resultContent += '<p style="margin-left: 1rem; padding: 0 !important; line-height: 1.4 !important;">'
                resultContent += txt
                resultContent += '</p>'
            });
        } else {
            resultContent += '<p style="margin-left: 1rem; padding: 0 !important; line-height: 1.4 !important;">'
            resultContent += text
            resultContent += '</p>'
        }
        elem.innerHTML = resultContent
    }
}

function updateText(id, tag, isPreview, value) {
    const p = isPreview ? '-preview-' : '-'
    const elem = findElem(tag + p + id)
    if (elem) {
        elem.textContent = value
    }
}

function updateProgressBar(id, tag, isPreview, value) {
    const p = isPreview ? '-preview-' : '-'
    const elem = findElem(tag + p + id)
    if (elem) {
        const val = value + '%'
        elem.style.width = val
        elem.textContent = val
    }
}

function handleProgressUpdates(value) {
    const data = JSON.parse(value);

    if (data.hasOwnProperty('records')) {
        data.records.forEach(function (item, index) {
            handleRecordUpdates(item)
        });
    }

    return []
}

function handleRecordUpdates(data) {
    const id = data.id;

    if (data.hasOwnProperty('status')) {
        updateDownloadCardState(id, data.status)
    }

    if (data.hasOwnProperty('result_text')) {
        let resultTitle = data.hasOwnProperty('result_title') ? data.result_title : 'Result'
        updateResultText(id, resultTitle, data.result_text)
    }

    if (data.hasOwnProperty('progress_info_left')) {
        updateText(id, 'progress-info-left', false, data.progress_info_left)
    }

    if (data.hasOwnProperty('progress_info_center')) {
        updateText(id, 'progress-info-center', false, data.progress_info_center)
    }

    if (data.hasOwnProperty('progress_info_right')) {
        updateText(id, 'progress-info-right', false, data.progress_info_right)
    }

    if (data.hasOwnProperty('progress_preview_info_left')) {
        updateText(id, 'progress-info-left', true, data.progress_preview_info_left)
    }

    if (data.hasOwnProperty('progress_preview_info_center')) {
        updateText(id, 'progress-info-center', true, data.progress_preview_info_center)
    }

    if (data.hasOwnProperty('progress_preview_info_right')) {
        updateText(id, 'progress-info-right', true, data.progress_preview_info_right)
    }

    if (data.hasOwnProperty('progress')) {
        updateProgressBar(id, 'progress-bar', false, data.progress)
    }

    if (data.hasOwnProperty('progress_preview')) {
        updateProgressBar(id, 'progress-bar', true, data.progress_preview)
    }
}

function generateUUID() {
    let d = new Date().getTime();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

function populateBackstack() {
    const textArea = findElem('mo_json_nav_box').querySelector('textarea')
    const currentNavigationJson = textArea.value
    const backstack = []
    if (Boolean(currentNavigationJson)) {

        const currentNavigation = JSON.parse(currentNavigationJson);
        log('Current Navigation: ' + currentNavigation)

        if (currentNavigation.hasOwnProperty('backstack')) {
            currentNavigation.backstack.forEach(function (item, index) {
                backstack.push(item);
            });
            delete currentNavigation.backstack;
        }

        if (currentNavigation.hasOwnProperty('token')) {
            delete currentNavigation.token;
        }
        log('previous backstack: ' + backstack)

        backstack.unshift(currentNavigation);
        log('new backstack: ' + backstack)
    }
    return backstack
}

function navigateHome() {
    log('Navigate home screen')
    const navObj = {};
    deliverNavObject(navObj)
    return []
}

function navigateBack() {
    const textArea = findElem('mo_json_nav_box').querySelector('textarea')
    const currentNavigationJson = textArea.value
    let backNav = {}
    if (Boolean(currentNavigationJson)) {
        const currentNavigation = JSON.parse(currentNavigationJson);
        log('Current Navigation: ' + currentNavigation)

        if (currentNavigation.hasOwnProperty('backstack') && currentNavigation.backstack.length !== 0) {
            backNav = currentNavigation.backstack.shift()

            if (currentNavigation.backstack.length !== 0) {
                backNav.backstack = currentNavigation.backstack
            }
        }
    }
    deliverNavObject(backNav)
    return []
}

function navigateDetails(id) {
    log('Navigate details screen for id: ' + id)
    const navObj = {
        screen: "details",
        record_id: id,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateAdd() {
    log('Navigate add screen')
    const navObj = {
        screen: "edit",
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateEdit(id) {
    log('Navigate edit screen for id: ' + id)
    const navObj = {
        screen: "edit",
        record_id: id,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateDownloadRecord(id) {
    log('Navigate download screen for id: ' + id)
    const navObj = {
        screen: "download",
        record_id: id,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateDownloadRecordList(ids_json) {
    const ids = JSON.parse(JSON.parse(ids_json))
    log('Navigate download screen for records: ' + ids)
    const navObj = {
        screen: "download",
        record_ids: ids,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateDownloadGroup(groupName) {
    log('Navigate download screen for group: ' + groupName)
    const navObj = {
        screen: "download",
        group: groupName,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function navigateRemove(id) {
    log('Navigate removal screen for id: ' + id)
    const navObj = {
        screen: "remove",
        record_id: id,
        token: generateUUID(),
        backstack: populateBackstack()
    };
    deliverNavObject(navObj)
    return []
}

function deliverNavObject(navObj) {
    const navJson = JSON.stringify(navObj);
    const textArea = findElem('mo_json_nav_box').querySelector('textarea')
    const event = new Event('input', {'bubbles': true, "composed": true});
    textArea.value = navJson
    findElem('mo_json_nav_box').querySelector('textarea').dispatchEvent(event);
    console.log('JSON Nav dispatched: ' + navJson)
}

/*
onUiLoaded(() => {
    const inputElement = document.querySelector("#mo-groups-widget input");

    inputElement.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            const inputValue = inputElement.value;
            console.log(inputValue);

            const textArea = document.getElementById('mo-add-groups-box').querySelector('textarea')
            const event = new Event('input', {'bubbles': true, "composed": true});
            textArea.value = inputValue
            document.getElementById('mo-add-groups-box').querySelector('textarea').dispatchEvent(event);

            inputElement.value = ''
            const event2 = new Event('input', {'bubbles': true, "composed": true});
            document.getElementById('mo-groups-widget').querySelector('input').dispatchEvent(event2);
        }
    });
})
*/

