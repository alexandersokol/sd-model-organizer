function moJsonDelivery(json) {
    console.log('json delivery: ' + json)
    const textArea = gradioApp().getElementById('mo_json_box').querySelector('textarea')
    const event = new Event('input', {'bubbles': true, "composed": true});
    textArea.value = json
    gradioApp().getElementById('mo_json_box').querySelector('textarea').dispatchEvent(event);
    console.log('json event dispatched')
}

function progressBuddy(value) {
    // var progressBar = gradioApp().getElementById('html-progress-buddy');
    // html-progress-buddy
    console.log(value)
    gradioApp().getElementById('progress-moid-x').style.width = value + '%';
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

