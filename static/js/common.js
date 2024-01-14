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
    console.log('poszlo sleep()');
    return new Promise((resolve) => setTimeout(resolve, time));
}