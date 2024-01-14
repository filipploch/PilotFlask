        function wsSetReplayFileNamePrefix() {
            const now = new Date();

            const year = now.getFullYear();
            const month = (now.getMonth() + 1).toString().padStart(2, '0');
            const day = now.getDate().toString().padStart(2, '0');

            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');

            return `${year}${month}${day}_${hours}${minutes}${seconds}`;
        }

        function wsChangeSide() {
			var selectTeams = document.querySelector("#ws-teams-buttons");
			var selectTeamAbtn = document.getElementById("select-team-a-btn");
			var selectTeamBbtn = document.getElementById("select-team-a-btn");

			var selectTeamsChildren = Array.from(selectTeams.children);
			selectTeamsChildren.reverse();

			selectTeamsChildren.forEach(function (child) {
				selectTeams.appendChild(child);
			});
		}

        function wsCheckScoreboardReverse() {
            var selectTeams = document.querySelector("#ws-teams-buttons");
			var selectTeamAbtn = document.getElementById("select-team-a-btn");
			var selectTeamBbtn = document.getElementById("select-team-b-btn");
			var selectTeamsChildren = [];
            fetch('/get-is-scoreboard-reversed')
            .then(response => response.json())
            .then(data => {
                var isReversed = data['data'];
                    if (isReversed == 0) {
                        selectTeamsChildren.push(selectTeamAbtn, selectTeamBbtn);
                    } else if (isReversed == 1) {
                        selectTeamsChildren.push(selectTeamBbtn, selectTeamAbtn);
                    }
                selectTeamsChildren.forEach(function (child) {
                    console.log(child);
                    selectTeams.appendChild(child);
                });
            }).catch(function (error) {
                console.error(error);
            });
        }

        function hideEditFrame() {
            classListAdd('ws-edit-frame', 'invisible')
        }

        function getValueOrNone(value) {
        console.log('getValueOrNone(value):', value);
            if (value === 'NULL') {
                return null;
            } else if (!isNaN(value)) {
                // Sprawdzamy, czy wartość jest liczbą
                return parseInt(value);
            } else {
                // Jeśli nie jest 'null' ani liczbą, zwracamy jako string
                return String(value);
            }
        }

        function setNoneToWsElements() {
            document.getElementById('ws-action-id').innerText = 'NULL';
            document.getElementById('ws-player-id').innerText = 'NULL';
            document.getElementById('ws-team').innerText = 'NULL';
            document.getElementById('ws-team-id').innerText = 'NULL';
            document.getElementById('ws-current-date').innerText = 'NULL';
            document.getElementById('ws-current-second').innerText = 'NULL';
        }

        function setValuesToWsElements(element) {
            console.log(element);
            document.getElementById('ws-player-id').innerText = element['id'];
            document.getElementById('ws-team-id').innerText = element['team-id'];
        }

        function setTeam(team) {
            var teamElement = document.getElementById('ws-team');
            var actionId = parseInt(document.getElementById('ws-action-id').textContent);
            var typeOfGoalButtons = document.getElementById('ws-type-of-goal-buttons');
            teamElement.innerText = team;
            console.log('typeof(actionId):', typeof(actionId));
            console.log('actionId:', actionId);
            if (actionId == 1) {
                classListAdd('ws-teams-buttons', 'invisible');
                classListRemove('ws-type-of-goal-buttons', 'invisible');
            }
            else {
                getSquad(team, actionId);
            }

        }

        function setSquadToGet(actionId) {
            var typeOfGoalButtons = document.getElementById('ws-type-of-goal-buttons');
            var actionIdElement = document.getElementById('ws-action-id');
            var teamElement = document.getElementById('ws-team');
            var team = teamElement.textContent;
            classListAdd('ws-type-of-goal-buttons', 'invisible');
            if (actionId == 1) {
                actionIdElement.innerText = actionId;
                getSquad(team, 1)
                }
            else if (actionId == 4) {
                actionIdElement.innerText = actionId;
                if (team == 'teama') {
                    teamElement.innerText = 'teamb';
                    team = 'teamb';
                } else if (team == 'teamb') {
                    teamElement.innerText = 'teama';
                    team = 'teama';
                }
                getSquad(team, 4);
            }
        }


        function saveReplay(typeOfAction) {
            fetch('/drop_replay');
            fetch('/matchdata')
                .then(response => response.json())
                .then(data => {
                    checkScoreboardReverse();
                    var editFrame = document.getElementById('ws-edit-frame');
                    var actionId = document.getElementById('ws-action-id');
                    var currentDate = document.getElementById('ws-current-date');
                    var currentSecond = document.getElementById('ws-current-second');
                    actionId.innerHTML = typeOfAction;
                    currentDate.innerHTML = wsSetReplayFileNamePrefix();
                    currentSecond.innerHTML = data.match.seconds;
                    classListRemove('ws-edit-frame', 'invisible');
//                    classListRemove('ws-');
                    renderEditFrameContent(typeOfAction);

                })
        }

        function renderEditFrameContent(typeOfAction) {
            if (typeOfAction == '0' || typeOfAction == '1') {
                renderEditFrameGoalContent(typeOfAction);
            }
            else if (typeOfAction == '6' || typeOfAction == '10' || typeOfAction == '11') {
                renderEditFrameNoTeamContent();
            }
            else {
                renderEditFrameElseContent();
            }
        }

        function renderEditFrameGoalContent(typeOfAction) {
            var editFrameTitle = document.getElementById('ws-edit-frame-title');
            editFrameTitle.innerHTML = 'Gol dla...';
            var selectTeamAbtn = document.getElementById('ws-select-team-a-btn');
            var selectTeamBbtn = document.getElementById('ws-select-team-b-btn');
            selectTeamAbtn.setAttribute('onclick', 'setTeam("teama"); updateValue(1, "display-score-a");');
            selectTeamBbtn.setAttribute('onclick', 'setTeam("teamb"); updateValue(1, "display-score-b");');
            classListRemove('ws-teams-buttons', 'invisible');
            if (typeOfAction == 0) {
                sleep(2000).then(() => {
                    fetch('/goal-sequence');
                });
                document.getElementById('ws-action-id').innerText = '1';
            }
        }

        function renderEditFrameNoTeamContent() {
            var playerId = document.getElementById('ws-player-id');
            var teamId = document.getElementById('ws-team-id');
            playerId.innerHTML = 'NULL';
            teamId.innerHTML = 'NULL';
            classListAdd('ws-teams-buttons', 'invisible');
            classListAdd('ws-edit-frame-title', 'invisible');
            classListAdd('ws-edit-frame', 'invisible');
            classListRemove('ws-teams-buttons', 'invisible');
            saveElement();
        }

        function renderEditFrameElseContent() {
            var editFrameTitle = document.getElementById('ws-edit-frame-title');
            var selectTeamAbtn = document.getElementById('ws-select-team-a-btn');
            var selectTeamBbtn = document.getElementById('ws-select-team-b-btn');
            editFrameTitle.innerHTML = 'Kto strzelał/faulował?';
            selectTeamAbtn.setAttribute('onclick', 'setTeam("teama");');
            selectTeamBbtn.setAttribute('onclick', 'setTeam("teamb");');
            classListRemove('ws-teams-buttons', 'invisible');
        }

        async function fetchDataAndRender(statsContent) {
            try {
                // Wykonanie żądania do endpointu Flask
                const response = await fetch(`/render-statistics/${statsContent}`);

            } catch (error) {
                console.error('Error:', error);
            }
        }

    function setStreamButtonOn() {
        var streamButton = document.getElementById('ws-btn-stream');
        var newImage = `<img src="{{ url_for('static', filename='images/ws-controller/stream-on.png') }}" alt="STREAM">`;
        streamButton.removeAttribute('ondblclick');
        streamButton.setAttribute('ondblclick', 'stopStream()');
        classListAdd('ws-btn-stream', 'backlight-red');
        streamButton.innerHTML = newImage;
    }

    function setStreamButtonOff() {
        var streamButton = document.getElementById('ws-btn-stream');
        var newImage = `<img src="{{ url_for('static', filename='images/ws-controller/stream-off.png') }}" alt="OFF">`;
        streamButton.removeAttribute('ondblclick');
        streamButton.setAttribute('ondblclick', 'startStream()');
        classListRemove('ws-btn-stream', 'backlight-red');
        streamButton.innerHTML = newImage;
    }

    function startStream() {
            fetch('/start-stream')
                .then(response => response.json())
                .then(data => {
                    if (data.outputActive === true) {
                        setStreamButtonOn();
                    } else {
                        console.error('Błąd: Stream nie został uruchomiony.');
                    }
                })
                .catch(error => console.error('Błąd podczas rozpoczynania streamu:', error));
    }

    function stopStream() {
        fetch('/stop-stream')
        .then(setStreamButtonOff())
        .catch(error => console.error('Błąd podczas zatrzymania streamu:', error));
    }

//    window.onload = function () {
//        fetch('/get-stream-status')
//        .then(response => response.json())
//        .then(data => {
//            console.log(data.outputActive);
//            if (data.outputActive === true) {
//                setStreamButtonOn();
//            } else if (data.outputActive === false) {
//                setStreamButtonOff();
//            } else {
//                console.error('Błąd: Nie udało się pobrać statusu streamu.');
//            }
//        })
//        .catch(error => console.error('Błąd:', error));
//    };