function classListRemove(elementId, className) {
    var element = document.getElementById(elementId);
    if (element && element.classList.contains(className)) {
        element.classList.remove(className);
    }
}

function classListAdd(elementId, className) {
    var element = document.getElementById(elementId);
    if (element && !element.classList.contains(className)) {
        element.classList.add(className);
    }
}

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function getAttributes(element) {
    let attributes = {};
    for (let attr of element.attributes) {
        attributes[attr.name] = attr.value;
    }
    return attributes;
}