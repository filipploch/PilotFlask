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

function setAttributes(element, attributes) {
    for (const key in attributes) {
        if (attributes.hasOwnProperty(key)) {
            if (key.startsWith('data-')) {
                element.setAttribute(key, attributes[key]);
            }
        }
    }
}

function setClassOnlyForElement(elementId, elementsClass, className) {
    let elements = Array.from(document.querySelectorAll(elementsClass));

    elements.forEach((element) => {
        classListRemove(element.id, className);
    });
    classListAdd(elementId, className)
}

function elementsContainsClassName(elementsClass, checkedClass) {
    let elements = Array.from(document.querySelectorAll(elementsClass));

    elements.forEach((element) => {
        if (element.classList.contains(checkedClass)) {
            return true;
        }
    });
    return false;
}

function fetchGet(_url) {
    let url = new URL(_url);
    let selectElement = document.getElementById('competitions');
    let selectedValue = selectElement.value;
    url.searchParams.append('competition_id', selectedValue);
    location.href = url;
}