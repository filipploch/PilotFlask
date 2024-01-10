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
        console.log(value);
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
            var actionId = document.getElementById('ws-action-id').textContent;
            var teamsButtons = document.getElementById('ws-teams-buttons');
            var typeOfGoalButtons = document.getElementById('ws-type-of-goal-buttons');
            teamElement.innerText = team;
            if (actionId == 1) {
                teamsButtons.classList.add('invisible');
                typeOfGoalButtons.classList.remove('invisible');
            }
            else {
                getSquad(team, actionId);
            }

        }



//        function showTeamLineup(actionId, teamsIdsDict) {
//            var teamId = document.getElementById('ws-team-id').textContent;
//            var actionIdElement = document.getElementById('ws-action-id');
//            var teamAlineup = document.getElementById('ws-teama-lineup');
//            var teamBlineup = document.getElementById('ws-teamb-lineup');
//            actionIdElement.innerHTML = actionId;
//            if (actionId == '1') {
//                if (teamId == teamsIdsDict['teamAid']) {
//                    getSquad('teama', parseInt(actionId));
//                } else if (teamId == teamsIdsDict['teamBid']) {
//                    getSquad('teamb', parseInt(actionId));
//                }
//            } else if (actionId == '4') {
//                if (teamId == teamsIdsDict['teamAid']) {
//                    getSquad('teamb', parseInt(actionId));
//                } else if (teamId == teamsIdsDict['teamBid']) {
//                    getSquad('teama', parseInt(actionId));
//                }
//            }
//        }
//
//        function prepareSquad(elementId, elements) {
//			const tbl = document.getElementById(elementId);
//			// Wyczyść listę przed dodaniem nowych elementów
//			tbl.innerHTML = '';
//			// Wygeneruj elementy listy
//			elements.forEach(element => {
//				const row = document.createElement('tr');
//				const playerId= document.createElement('td');
//				const playerNr= document.createElement('td');
//				const playerName = document.createElement('td');
//				const playerPosition = document.createElement('td');
//				const playerIsCaptain = document.createElement('td');
//				const teamId = document.createElement('td');
//				row.setAttribute('class', 'li-element')
//				playerId.textContent = element['id'];
//				playerId.style.color = 'rgba(0,0,0,0)';
//				playerId.style.display = 'none';
//				playerNr.textContent = element['nr'];
//				playerName.textContent = element['first-name'] + ' ' + element['last-name'];
//				playerPosition.textContent = element['is-gk'];
//				playerIsCaptain.textContent = element['is-captain'];
//				teamId.textContent = element['team-id'];
//				teamId.style.display = 'none';
//
//
//
//				// style! captain: bold, goalkeeper: underline
//
//				if (element['is-captain']) {
//					row.style.fontWeight = 700;
//				}
//
//				if (element['is-gk']) {
//					row.style.textDecoration = 'underline';
//				}
//
//				// Dodaj obsługę zdarzenia kliknięcia elementu
//				row.addEventListener('click', () => {
//					saveElement(element);
//					clearSidebar();
//				});
//					row.appendChild(playerId);
//					row.appendChild(playerNr);
//					row.appendChild(playerName);
//					row.appendChild(teamId);
//					tbl.appendChild(row);
//				});
//		}

        function setSquadToGet(actionId) {
            var typeOfGoalButtons = document.getElementById('ws-type-of-goal-buttons');
            var actionIdElement = document.getElementById('ws-action-id');
            var teamElement = document.getElementById('ws-team');
            var team = teamElement.textContent;
            typeOfGoalButtons.classList.add('invisible');
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

//        function saveElement() {
//			let actionId = document.getElementById('ws-action-id').textContent;
//			let teamId = document.getElementById('ws-team-id').textContent;
//			let playerId = document.getElementById('ws-player-id').textContent;
//			let seconds = document.getElementById('ws-current-second').textContent;
//			let currentDate = document.getElementById('ws-current-date').textContent;
//				if(parseInt(actionId) !== 0){
//					action_data = {
//						'seconds': getValueOrNone(seconds),
//						'action_id': getValueOrNone(actionId),
//						'player_id': getValueOrNone(playerId),
//						'team_id': getValueOrNone(teamId),
//						'current_date': currentDate
//					}
//					fetch(`/insert-match-action`, {
//						method: 'POST',
//						headers: { 'Content-Type': 'application/json' },
//						body: JSON.stringify(action_data)					})
//						// .then(response => response.json())
//						.then(action_data => {
//							console.log('Element został zapisany:', action_data);
//						})
//						.catch(error => {
//							console.error('Wystąpił błąd podczas zapisywania elementu:', error);
//						})
//						;
//					}
//        }


        function saveReplay(typeOfAction) {
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
                    editFrame.classList.remove('invisible');
                    renderEditFrameContent(typeOfAction);

                })
        }

        function renderEditFrameContent(typeOfAction) {
            if (typeOfAction == '1') {
                renderEditFrameGoalContent();
            }
            else if (typeOfAction == '6' || typeOfAction == '10' || typeOfAction == '11') {
                renderEditFrameNoTeamContent();
            }
            else {
                renderEditFrameElseContent();
            }
        }

        function renderEditFrameGoalContent() {
            var editFrameTitle = document.getElementById('ws-edit-frame-title');
            editFrameTitle.innerHTML = 'Gol dla...';
            selectTeamAbtn = document.getElementById('ws-select-team-a-btn');
            selectTeamBbtn = document.getElementById('ws-select-team-b-btn');
            selectTeamAbtn.setAttribute('onclick', 'setTeam("teama"); updateValue(1, "display-score-a");')
            selectTeamBbtn.setAttribute('onclick', 'setTeam("teamb"); updateValue(1, "display-score-b");')
            classListRemove('ws-teams-buttons', 'invisible');
        }

        function renderEditFrameNoTeamContent() {
            var editFrame = document.getElementById('ws-edit-frame');
            var playerId = document.getElementById('ws-player-id');
            var teamId = document.getElementById('ws-team-id');
            playerId.innerHTML = 'NULL';
            teamId.innerHTML = 'NULL';
            var teamsButtons = document.getElementById('ws-teams-buttons');
            var editFrameTitle = document.getElementById('ws-edit-frame-title');
            teamsButtons.classList.add('invisible');
            editFrameTitle.classList.add('invisible');
            editFrame.classList.add('invisible');
            saveElement();
        }

        function renderEditFrameElseContent() {
            var editFrameTitle = document.getElementById('ws-edit-frame-title');
            editFrameTitle.innerHTML = 'Kto strzelał/faulował?';
            selectTeamAbtn.setAttribute('onclick', 'setTeam("teama");')
            selectTeamBbtn.setAttribute('onclick', 'setTeam("teamb");')
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
        streamButton.classList.add('backlight-red');
        streamButton.innerHTML = newImage;
    }

    function setStreamButtonOff() {
        var streamButton = document.getElementById('ws-btn-stream');
        var newImage = `<img src="{{ url_for('static', filename='images/ws-controller/stream-off.png') }}" alt="OFF">`;
        streamButton.removeAttribute('ondblclick');
        streamButton.setAttribute('ondblclick', 'startStream()');
        streamButton.classList.remove('backlight-red');
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