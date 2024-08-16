function replaysShowInfo(element) {
    const info = document.getElementById('element-info');
    const action = element.getAttribute('data-action');
    const player = element.getAttribute('data-player');
    const team = element.getAttribute('data-team');
    info.innerText = `Action: ${action}\nPlayer: ${player}\nTeam: ${team}`;
}

function replaysClearInfo() {
    const info = document.getElementById('element-info');
    info.innerText = ''; // Clear the info div when mouse leaves a child div
}


function replaysSelectReplay(element_id, className) {
    let replayElement = document.getElementById(element_id);
    let replaysElements = Array.from(document.querySelectorAll('.replay-element'));
//    console.log(replayElement);
//    console.log(replayElement.getAttribute('data-replay-start-time'));
    let replayElementAttributes = getAttributes(replayElement);
    let replayStartTimeLabel = document.getElementById('replay-start-time');
    let replayEndTimeLabel = document.getElementById('replay-end-time');
    let replayStartTime = replayElement.getAttribute('data-replay-start-time');
    let replayEndTime = replayElement.getAttribute('data-replay-end-time');
    let replayData = document.getElementById('selected-replay-data');
    let replayDescription = document.getElementById('selected-replay-description');
    let replayEditor = document.getElementById('selected-replay');

    let buttons = Array.from(document.querySelectorAll('.replay-source-button'));

    buttons.forEach((button) => {
        classListRemove(button.id, 'element-disable');
    });

    if ((!elementsContainsClassName('.replay-source-button', 'button-enable')) && (className === 'actual-replay')) {
            setClassOnlyForElement('replay-source-button-stream', '.replay-source-button', 'button-enable');
        }

    replayDescription.innerText = replayElement.textContent;
    replayData.setAttribute('data-replay-id', replayElement.getAttribute('data-replay-id'));
    replayData.setAttribute('data-replay-element-id', element_id);
    console.log(getAttributes(replayElement));
    setAttributes(replayData, getAttributes(replayElement));
    replayStartTimeLabel.innerText = formatTime(replayStartTime);
    replayEndTimeLabel.innerText = formatTime(replayEndTime);
    replaysElements.forEach((replaysElement) => {
        classListRemove(replaysElement.id, className);
    });
    if (!replayElement.classList.contains('actual-replay')) {
        classListAdd(element_id, className);
        classListRemove(replayEditor.id, 'actual-replay');
        classListAdd(replayEditor.id, className);
    } else {
        classListRemove(replayEditor.id, className);
        classListAdd(replayEditor.id, 'actual-replay');
    }
}


function setActualReplay() {

}


//function replaysSelectReplay(element_id) {
//    let replayElement = document.getElementById(element_id);
//    let replaysElements = Array.from(document.querySelectorAll('.replay-element'));
////    console.log(replayElement);
////    console.log(replayElement.getAttribute('data-replay-start-time'));
//    let replayElementAttributes = getAttributes(replayElement);
//    let replayStartTimeLabel = document.getElementById('replay-start-time');
//    let replayEndTimeLabel = document.getElementById('replay-end-time');
//    let replayStartTime = replayElement.getAttribute('data-replay-start-time');
//    let replayEndTime = replayElement.getAttribute('data-replay-end-time');
//    let replayData = document.getElementById('selected-replay-data');
//    let replayDescription = document.getElementById('selected-replay-description');
//
//    fetch('/select-replay', {
//        method: 'POST',
//        headers: {
//        'Content-Type': 'application/json',
//        },
//        body: JSON.stringify(replayElementAttributes),
//    }).then(response => {
//        if (response.ok) {
//            replayDescription.innerText = replayElement.textContent;
//            replayData.setAttribute('data-replay-id', element_id);
//            replayStartTimeLabel.innerText = formatTime(replayStartTime);
//            replayEndTimeLabel.innerText = formatTime(replayEndTime);
//            replaysElements.forEach((replaysElement) => {
//                classListRemove(replaysElement.id, 'selected-replay');
//            });
//            classListAdd(element_id, 'selected-replay');
//        } else {
//            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
//        }
//    }) .catch(error => {
//        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
//    });
//}

function formatTime(seconds) {
    let mins = Math.floor(seconds / 60);
    let secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

//function replaysProcessReplay(replayElementId) {
//    if (typeof replayElementId === 'undefined') {
//        let replayDataElement = document.getElementById('selected-replay-data');
//        replayElementId = replayDataElement.getAttribute('data-replay-id');
//    }
//    let replayElement = document.getElementById(replayElementId);
//}

function replaysProcessReplay() {
    let replayDataElement = document.getElementById('selected-replay-data');
    let replayData = getAttributes(replayDataElement);
    let sourceButtonsContainer = document.getElementById('replay-source-buttons');
    let isSourceButtonSelected = sourceButtonsContainer.getAttribute('data-is-selected');
    let streamSourceButton = document.getElementById('replay-source-button-stream');
    let replayElement = document.getElementById(replayDataElement.getAttribute('data-replay-element-id'));
    let selectedReplay = document.getElementById('selected-replay');

    if (!elementsContainsClassName('.replay-source-button', 'button-enable')) {
        setClassOnlyForElement('replay-source-button-stream', '.replay-source-button', 'button-enable');
    }

    fetch('/process-replay', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'data': replayData }),
    })
        .then(response => {
        if ((response.ok) && (isSourceButtonSelected === '0')) {
            sourceButtonsContainer.setAttribute('data-is-selected', '1');
            classListRemove(replayElement.id, 'selected-replay');
            classListRemove(selectedReplay.id, 'selected-replay');
            classListAdd(selectedReplay.id, 'actual-replay');
            setClassOnlyForElement(replayElement.id, '.replay-element', 'actual-replay');
            classListAdd(streamSourceButton.id, 'button-enable');
        } else if (response.ok) {
            classListRemove(replayElement.id, 'selected-replay');
            classListRemove(selectedReplay.id, 'selected-replay');
            classListAdd(selectedReplay.id, 'actual-replay');
            setClassOnlyForElement(replayElement.id, '.replay-element', 'actual-replay');
        } else {
            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
        }
        })
        .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
        });
}

function replaySetSource(element) {
    let buttons = Array.from(document.querySelectorAll('.replay-source-button'));
    let cameraPrefix = element.getAttribute('data-camera-prefix');
    let replaysElements = Array.from(document.querySelectorAll('.replay-element'));

    buttons.forEach((button) => {
        classListRemove(button.id, 'button-enable');
    });
    classListAdd(element.id, 'button-enable');


    fetch(`/set-replay-file/${cameraPrefix}`)
    .then(response => response.json())
    .then(data => {
        console.log('data:', data);
        replaysElements.forEach((element) => {
            if (cameraPrefix !== 'C0') {
                let recordTime = element.getAttribute('data-record-time');
                console.log('recordTime:', recordTime);
                if(recordTime > data.video_length) {
                    classListAdd(element.id, 'element-disable');
                } else {
                    classListRemove(element.id, 'element-disable');
                }
            }else{
                replaysElements.forEach((element) => {
                    classListRemove(element.id, 'element-disable');
                });
            }
        });
    })
    .catch(error => {
        console.error('Wystąpił błąd:', error);
    });

}

function saveTime(elapsedTime) {
    fetch('/update-time', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'seconds': elapsedTime }),
    })
        .then(response => {
        if (response.ok) {
            console.log('Czas zapisany w bazie danych.');
        } else {
            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
        }
        })
        .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
        });
    }

function updateReplayTime(element, difference) {
    let valueType = element.getAttribute('data-value-type');
    let displayType = document.getElementById(valueType);
    let replayId = document.getElementById('selected-replay-data').getAttribute('data-replay-id');
    fetch('/update-replay-time', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({'valueType': valueType, 'difference': difference, 'replayId': replayId}),
    })
        .then(response => response.json())
        .then(data => {
        displayType.innerText = formatTime(data.seconds);
        console.log('data:', data);
        })
        .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
        });
    }

function replaysScrollToEnd(element_id) {
    const elements = document.getElementById(element_id);
    elements.scrollTop = elements.scrollHeight;
}