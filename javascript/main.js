function moJsonDelivery(json) {
    console.log('json delivery: ' + json)
    const textArea = gradioApp().getElementById('mo_json_box').querySelector('textarea')
    const event = new Event('input', {'bubbles': true, "composed": true});
    textArea.value = json
    gradioApp().getElementById('mo_json_box').querySelector('textarea').dispatchEvent(event);
    console.log('json event dispatched')
}