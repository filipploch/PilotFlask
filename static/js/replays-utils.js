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


function replaysSelectReplay(element_id) {
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

    fetch('/select-replay', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(replayElementAttributes),
    }).then(response => {
        if (response.ok) {
            replayDescription.innerText = replayElement.textContent;
            replayData.setAttribute('data-replay-element-id', element_id);
            replayStartTimeLabel.innerText = formatTime(replayStartTime);
            replayEndTimeLabel.innerText = formatTime(replayEndTime);
            replaysElements.forEach((replaysElement) => {
                classListRemove(replaysElement.id, 'selected-replay');
            });
            classListAdd(element_id, 'selected-replay');
        } else {
            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
        }
    }) .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
    });
}

function formatTime(seconds) {
    let mins = Math.floor(seconds / 60);
    let secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

function replaysProcessReplay(replayElementId) {
    if (typeof replayElementId === 'undefined') {
        let replayDataElement = document.getElementById('selected-replay-data');
        replayElementId = replayDataElement.getAttribute('data-replay-element-id');
        console.log('replayElementId undefined');
    } else {
        console.log('replayElementId defined');
    }
}


function replaySetSource(element) {
    let buttons = Array.from(document.querySelectorAll('.replay-source-button'));
    let cameraPrefix = element.getAttribute('data-camera-prefix');
    let replaysElements = Array.from(document.querySelectorAll('.replay-element'));

    buttons.forEach((button) => {
        classListRemove(button.id, 'button-enable');
    });
    classListAdd(element.id, 'button-enable');

    if (cameraPrefix !== 'CX') {
        fetch(`/get-recorded-video-length/${cameraPrefix}`)
        .then(response => response.json())
        .then(data => {
            console.log('data:', data);
            replaysElements.forEach((element) => {
                let recordTime = element.getAttribute('data-record-time');
                console.log('recordTime:', recordTime);
                if(recordTime > data.video_length) {
                    classListAdd(element.id, 'element-disable');
                } else {
                    classListRemove(element.id, 'element-disable');
                }
            });
        })
        .catch(error => {
            console.error('Wystąpił błąd:', error);
        });
    }else{
        replaysElements.forEach((element) => {
            classListRemove(element.id, 'element-disable');
        });
    }
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