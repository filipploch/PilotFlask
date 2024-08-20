var matchdata = JSON.parse(document.getElementById('matchdata').getAttribute('data-matchdata'));
var timeData = JSON.parse(document.getElementById('time-data').getAttribute('data-time-data'));

		function fetchDataFromAPI() {
			var url = 'matchdata';

			return new Promise(function (resolve, reject) {
				fetch(url)
					.then(function (response) {
						if (response.ok) {
							return response.json();
						} else {
							throw new Error('Net error');
						}
					})
					.then(function (data) {
						resolve(data);
					})
					.catch(function (error) {
						reject(error);
					});
			});
		}

		// Wywołanie funkcji i przypisanie danych do zmiennej przed uruchomieniem innych skryptów
		fetchDataFromAPI().then(function (data) {
			var myData = data;
			elapsedTime = myData.match.seconds;
			timeLimit = myData.match.period_length;

		}).catch(function (error) {
			console.error(error);
		});

function updateValueById(value, divId){
    document.getElementById(divId).innerHTML = value;
}


		function setSourceIndex(sceneName, sourceName, sourceIndex) {
		    if (typeof sourceIndex == 'undefined') {
                sourceIndex = -1;
                // Tutaj możesz dostosować zachowanie funkcji w zależności od optionalArg
            }

            // Wyślij żądanie na serwer Flask po kliknięciu przycisku
            fetch(`/set_source_index/${sceneName}/${sourceName}/${sourceIndex}`);
		}


		function changeSide() {
		    changeSideScoreboard()
            changeSideSubstitutions()
		}

		function changeSideScoreboard() {
			var scoreboard = document.querySelector("#scoreboard");
			var teams = document.querySelector("#teams");
			var a = document.getElementById("fouls-a-group");
			var b = document.getElementById("score-a-group");
			var c = document.getElementById("score-b-group");
			var d = document.getElementById("fouls-b-group");
			var teamA = document.getElementById("team-a-group");
			var teamB = document.getElementById("team-b-group");

			var scoreboardChildren = Array.from(scoreboard.children);
			scoreboardChildren.reverse();

			scoreboardChildren.forEach(function (child) {
				scoreboard.appendChild(child);
			});

			var teamChildren = Array.from(teams.children);
			teamChildren.reverse();

			teamChildren.forEach(function (child) {
				teams.appendChild(child);
			});
		}

        function changeSideSubstitutions() {
            if (document.querySelector('#substitution-buttons') !== 'undefined') {
                let substitution = document.querySelector('#substitution-buttons');
                let substitutionButtonA = document.getElementById('substitution-button-teama');
                let substitutionButtonB = document.getElementById('substitution-button-teamb');


                let substitutionChildren = Array.from(substitution.children);
                substitutionChildren.reverse();

                substitutionChildren.forEach(function (child) {
                    substitution.appendChild(child);
                });
            }
		}

		function pressChangeSideBtn() {
			changeSide();
			fetch('/change-scoreboard-side', {
				method: 'PUT'
			});
		}

		function updateValue(difference, divId) {
			var divElement = document.getElementById(divId);
			var actualValue = parseInt(divElement.innerText); // Pobierz aktualną wartość liczbową z diva

			var newValue = actualValue + difference; // Dodaj lub odejmij wartość liczby

			var data = {
				'value': newValue,
				'divId': divId
			};


			// Wywołaj żądanie POST do skryptu Python
			fetch('http://127.0.0.1:5555/update-value', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(data)
			})

		}

		function fetchSquad(team, elements, header) {
			fetch(`/controller-lineup/${team}`)
				.then(response => response.json())
				.then(data => {
					// Po otrzymaniu danych, wygeneruj listę elementów
					document.getElementById(header).innerHTML = data[0]['team-full-name'];
					prepareSquad(data);
				})
				.catch(error => {
					console.error('Wystąpił błąd:', error);
				});
		}

		function getSquad(team, actionId) {
			clearSidebar();
			fetchSquad(team, 'elements', 'sidebar-head');
			document.getElementById('action-id').innerHTML = actionId;
			document.getElementById('ws-action-id').innerHTML = actionId;
			const sidebarBody = document.getElementById('sidebar-body');
			const cancelButton = document.createElement('button');
			cancelButton.textContent = 'Zamknij';
			cancelButton.addEventListener('click', () => {
					clearSidebar();
				});
			sidebarFooter = document.getElementById('sidebar-footer');
			cancelButton.setAttribute('id', 'sidebar-cancel-button')
			sidebarFooter.appendChild(cancelButton);
		}

		function prepareSquad(elements) {
			const tbl = document.getElementById('elements');
			// Wyczyść listę przed dodaniem nowych elementów
			tbl.innerHTML = '';
			// Wygeneruj elementy listy
			elements.forEach(element => {
				const row = document.createElement('tr');
				const playerId= document.createElement('td');
				const playerNr= document.createElement('td');
				const playerName = document.createElement('td');
				const playerPosition = document.createElement('td');
				const playerIsCaptain = document.createElement('td');
				const teamId = document.createElement('td');
				row.setAttribute('class', 'li-element')
				playerId.textContent = element['id'];
				playerId.style.color = 'rgba(0,0,0,0)';
				playerId.style.display = 'none';
				playerNr.textContent = element['nr'];
				playerName.textContent = element['first-name'] + ' ' + element['last-name'];
				playerPosition.textContent = element['is-gk'];
				playerIsCaptain.textContent = element['is-captain'];
				teamId.textContent = element['team-id'];
				teamId.style.display = 'none';



				// style! captain: bold, goalkeeper: underline

				if (element['is-captain']) {
					row.style.fontWeight = 700;
				}

				if (element['is-gk']) {
					row.style.textDecoration = 'underline';
				}

				// Dodaj obsługę zdarzenia kliknięcia elementu
				row.addEventListener('click', () => {
				    setValuesToWsElements(element);
					saveElement();
					clearSidebar();
					setNoneToWsElements();
					hideEditFrame();
				});
					row.appendChild(playerId);
					row.appendChild(playerNr);
					row.appendChild(playerName);
					row.appendChild(teamId);
					tbl.appendChild(row);
				});
		}

		function setPlayerId(element){
		    var playerId = document.getElementById('ws-player-id');
		    playerId.innerText = element['id'];
		}

        function setTeamId(element){
		    var teamId = document.getElementById('ws-team-id');
		    teamId.innerText = element['team-id'];
		}

		function saveElement() {
			let actionId = document.getElementById('ws-action-id').textContent;
			let teamId = document.getElementById('ws-team-id').textContent;
			let playerId = document.getElementById('ws-player-id').textContent;
			let currentDate = document.getElementById('ws-current-date').textContent;
			let currentSecondValue = document.getElementById('timer-display').getAttribute('data-time-seconds');
			let currentAddedSecondValue = document.getElementById('timer-display').getAttribute('data-time-added-seconds');
				if(parseInt(actionId) !== 0){
					// Wykonaj żądanie do API lub serwera backendowego, aby zapisać element w innej tabeli bazy danych
					action_data = {
                        'seconds': currentSecondValue,
                        'added_seconds': currentAddedSecondValue,
						'action_id': getValueOrNone(actionId),
						'player_id': getValueOrNone(playerId),
						'team_id': getValueOrNone(teamId),
						'current_date': getValueOrNone(currentDate)


//						'action_id': parseInt(document.getElementById("action-id").textContent),
//						'player_id': parseInt(document.getElementById("ws-player-id").textContent),
//						'team_id': parseInt(document.getElementById("ws-team-id").textContent)
					}
					console.log(action_data);
					fetch(`/insert-match-action`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify(action_data)					})
						.then(action_data => {
							console.log('Element został zapisany:', action_data);
						})
						.catch(error => {
							console.error('Wystąpił błąd podczas zapisywania elementu:', error);
						});
					}
				}

		function getMatchData(team) {
			// Wykonaj żądanie do API lub serwera backendowego
			clearSidebar();
			fetch(`/actual-match-data/${team}`)
				.then(response => response.json())
				.then(data => {
					// Po otrzymaniu danych, wygeneruj listę elementów
					document.getElementById('sidebar-head').innerHTML = data[0];
					prepareMatchData(data[1]);
				})
				.catch(error => {
					console.error('Wystąpił błąd:', error);
				});
			// document.getElementById('action-id').innerHTML = actionId;
			const sidebarBody = document.getElementById('sidebar-body');
			const cancelButton = document.createElement('button');
			cancelButton.textContent = 'Zamknij';
			cancelButton.addEventListener('click', () => {
					clearSidebar();
				});
			sidebarFooter = document.getElementById('sidebar-footer');
			cancelButton.setAttribute('id', 'sidebar-cancel-button')
			sidebarFooter.appendChild(cancelButton);

		}


		function prepareMatchData(elements) {
			const tbl = document.getElementById('elements');
			// Wyczyść listę przed dodaniem nowych elementów
			tbl.innerHTML = '';
			// Wygeneruj elementy listy
			elements.forEach(element => {
				const row = document.createElement('tr');
				const dataId = document.createElement('td');
				const playerId = document.createElement('td');
				const actionType = document.createElement('td');
				const time = document.createElement('td');
				const playerName = document.createElement('td');
				// const playerIsCaptain = document.createElement('td');
				// const teamId = document.createElement('td');
				row.setAttribute('class', 'li-element');
				if (element['is_hided'] == 1) {
					row.classList.add('not-visible');
				}
				dataId.textContent = element['data_id'];
				dataId.style.color = 'rgba(0,0,0,0)';
				dataId.style.display = 'none';
				time.textContent = element['time']['minutes'] + ':' + element['time']['seconds'];
				actionType.textContent = element['action_type'];
				playerName.textContent = element['player_first_name'] + ' ' + element['player_last_name'];
				playerId.textContent = element['player_id'];
				playerId.style.display = 'none';

				// Dodaj obsługę zdarzenia kliknięcia elementu
				row.addEventListener('click', () => {
					loadContent('/edit-match-action/', 'sidebar', element['data_id']);
					clearSidebar();
				});
					row.appendChild(dataId);
					row.appendChild(playerId);
					row.appendChild(actionType);
					row.appendChild(time);
					row.appendChild(playerName);
					tbl.appendChild(row);
				});
		}


function editData(dataId) {
    // Pobierz dane z endpointa
    fetch(`/prepare-data-to-edit/${dataId}`)
        .then(response => response.json())
        .then(data => {
			// Wyciągnij potrzebne dane z obiektu JSON
            const dropdownActions = data.actions;
			const dropdownPlayers = (data.event.action_id === 4) ? data.players["og"] : data.players["normal"];
            const selectedAction = data.event.action_id;
            const selectedPlayer = data.event.player_id;
            const selectedTime = data.event.seconds;

            // Utwórz listę rozwijaną 1
            const actionsSelect = document.createElement('select');
            Object.keys(dropdownActions).forEach(function(key) {
                const optionElement = document.createElement('option');
                optionElement.value = key;
                optionElement.textContent = dropdownActions[key];
                actionsSelect.appendChild(optionElement);
            });
            actionsSelect.value = selectedAction;

            // Utwórz listę rozwijaną 2
            const playerSelect = document.createElement('select');
			dropdownPlayers.forEach(player => {
                const optionElement2 = document.createElement('option');
                optionElement2.value = player.id;
                optionElement2.textContent = player.full_name;
                playerSelect.appendChild(optionElement2);
            });
            playerSelect.value = selectedPlayer;

            // Nasłuchuj zdarzenia zmiany wartości w actionsSelect
            actionsSelect.addEventListener('change', function () {
                const selectedActionValue = actionsSelect.value;
                const updatedPlayers = (selectedActionValue === '4') ? data.players["og"] : data.players["normal"];
                updatePlayerDropdown(playerSelect, updatedPlayers);
            });

            // Utwórz pole input dla czasu wewnątrz span
            const timeInputSpan = createTimeInputSpan(selectedTime.minutes, selectedTime.seconds);

			// Utwórz przycisk "Zapisz"
            const saveButton = createSaveButton(data.event.data_id, actionsSelect, playerSelect, timeInputSpan);

            // Wyczyść treść 'sidebar-body-div'
            const sidebarBodyDiv = document.getElementById('sidebar-body-div');
            sidebarBodyDiv.innerHTML = '';

            // Dodaj nowe elementy do 'sidebar-body-div'
            sidebarBodyDiv.appendChild(actionsSelect);
            sidebarBodyDiv.appendChild(playerSelect);
			sidebarBodyDiv.appendChild(timeInputSpan);
			sidebarBodyDiv.appendChild(saveButton);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

		function updatePlayerDropdown(selectElement, players) {
			// Wyczyść istniejące opcjedata
			selectElement.innerHTML = '';

			// Dodaj nowe opcje
			players.forEach(player => {
				const optionElement = document.createElement('option');
				optionElement.value = player.id;
				optionElement.textContent = player.full_name;
				selectElement.appendChild(optionElement);
			});
		}


		function createTimeInputSpan(selectedMinutes, selectedSeconds) {
			const spanElement = document.createElement('div');

			// Utwórz pole input dla minut wewnątrz span
			const minutesInput = document.createElement('input');
			minutesInput.type = 'number';
			minutesInput.name = 'minutes';
			minutesInput.value = selectedMinutes;
			minutesInput.min = 0;
			minutesInput.style.width = '50px';

			// Utwórz pole input dla sekund wewnątrz span
			const secondsInput = document.createElement('input');
			secondsInput.type = 'number';
			secondsInput.name = 'seconds';
			secondsInput.value = selectedSeconds;
			secondsInput.min = 0;
			secondsInput.style.width = '50px';

			// Dodaj oba pola input do span
			spanElement.appendChild(minutesInput);
			spanElement.appendChild(secondsInput);

			return spanElement;
		}

		function createSaveButton(dataId, actionsSelect, playerSelect, timeInputSpan) {
			const button = document.createElement('button');
			button.textContent = 'Zapisz';

			// Dodaj obsługę zdarzenia kliknięcia przycisku
			button.addEventListener('click', function () {
				const selectedAction = actionsSelect.value;
				const selectedPlayer = playerSelect.value;

				// Pobierz wartości z pól input dla czasu
				const minutesInputValue = parseInt(timeInputSpan.querySelector('[name="minutes"]').value, 10) || 0;
				const secondsInputValue = parseInt(timeInputSpan.querySelector('[name="seconds"]').value, 10) || 0;

				// Przekonwertuj czas z minut i sekund na sekundy
				const timeInSeconds = minutesInputValue * 60 + secondsInputValue;

				// Wyślij dane do serwera (możesz użyć tu fetch() do wysłania żądania do swojego API)
				// Poniżej zakładam, że masz odpowiedni endpoint na serwerze do obsługi aktualizacji danych w bazie
				fetch(`/update-data/${dataId}`, {
					method: 'PUT',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						action: selectedAction,
						player: selectedPlayer,
						time: timeInSeconds,
					}),
				})
				.then(response => response.json())
				.then(data => {
					console.log('Dane zaktualizowane:', data);
					// Dodaj kod obsługi sukcesu lub ewentualne odświeżenie widoku
				})
				.catch(error => {
					console.error('Błąd podczas aktualizacji danych:', error);
					// Dodaj kod obsługi błędu
				});
			});

			return button;
		}

		function clearSidebar() {
			const elementsList = document.getElementById('elements');
			elementsList.innerHTML = '';
			document.getElementById('sidebar-head').innerHTML = '';
			document.getElementById('action-id').innerHTML = '';
			document.getElementById('sidebar-body-div').innerHTML = '';
			document.getElementById('sidebar-footer').innerHTML = '';
		}


        function loadFiles() {
			clearSidebar();
            fetch('/get_files')
                .then(response => response.json())
                .then(data => {
                    const fileListElement = document.getElementById('elements');
                    fileListElement.innerHTML = '<ul>';
                    data.files.forEach(file => {
                        fileListElement.innerHTML += `<li><a href="#" onclick="processFile('${file}')">${file.slice(10, -4)}</a></li>`;

                    });
                    fileListElement.innerHTML += '</ul>';
					const cancelButton = document.createElement('button');
					cancelButton.textContent = 'Zamknij';
					cancelButton.addEventListener('click', () => {
							clearSidebar();
						});
					sidebarFooter = document.getElementById('sidebar-footer');
					cancelButton.setAttribute('id', 'sidebar-cancel-button')
					sidebarFooter.appendChild(cancelButton);
						});
        }

        var clickTimer = null;

        function handleProcessFile(file, event) {
            if (clickTimer == null) {
                clickTimer = setTimeout(function() {
                    clickTimer = null;
                    processFile(file); // Funkcja wywoływana przy pojedynczym kliknięciu
                }, 300); // Czas oczekiwania, aby sprawdzić, czy nie nastąpi dwuklik
            } else {
                clearTimeout(clickTimer);
                handleMakeYTShort(file, event);
                clickTimer = null;
            }
            event.preventDefault();
        }

        function handleMakeYTShort(file, event) {
            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
            }
            makeYTShort(file);
            event.preventDefault();
        }

        function processFile(filename) {
            fetch(`/process_file/${filename}`)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'replay_stream.mkv';
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    clearSidebar();
                });
        }

        function makeYTShort(filename) {
            fetch(`/make_yt_short/${filename}`);
        }

        function scrapeMatches(matchId) {
			clearSidebar();
            fetch(`/add-nalf-league-matches/${matchId}`)
                .then(response => response.json())
                .then(data => {
                    const message = data.message;
                    const sidebarHeader = document.getElementById('sidebar-head');
            		sidebarHeader.innerHTML = `<span>${message}</span>`;
					const cancelButton = document.createElement('button');
            		cancelButton.textContent = 'Zamknij';
            		cancelButton.addEventListener('click', () => {clearSidebar();});
            		cancelButton.setAttribute('id', 'sidebar-cancel-button');
            		sidebarFooter = document.getElementById('sidebar-footer');
		            sidebarFooter.appendChild(cancelButton);
                });
        }


function scrapeMzpnData(element) {
    let mzpnUrl = element.getAttribute('data-league-url');
    fetch('/scrape-mzpn-data', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({'mzpnUrl': mzpnUrl}),
    })
        .then(response => response.json())
        .then(data => {
            let messageElement = document.getElementById('message');
            messageElement.innerHTML = data.message;
            console.log('data:', data);
        })
        .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
        });
    }


function renderMzpnData() {
    let roundNr = document.getElementById('round-nr').value
    fetch(`/render-mzpn-data/${roundNr}`)
        .then(response => response.json())
        .then(data => {
            let messageElement = document.getElementById('message');
            messageElement.innerHTML = data.message;
            console.log('data:', data);
        })
        .catch(error => {
        console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
        });
    }


function setChecked(checkboxId, actual) {
	if (actual == true) {
        checkbox = document.getElementById(checkboxId);
		checkbox.setAttribute("checked", "checked");
    }
}

	function checkScoreboardReverse() {
		var scoreboard = document.getElementById('changeSideBtn');
		fetch('get-is-scoreboard-reversed')
		.then(response => response.json())
		.then(data => {
			var isReversed = data['data'];
			if (isReversed == 1) {
				changeSide();
			}
		}).catch(function (error) {
			console.error(error);
		});}

function showAllSubstitutions(element) {
    let confirmedSubstitutions = Array.from(document.querySelectorAll('.confirmed'));
    let processedSubstitutionButton = document.querySelector('#proceeded-substitutions-button');
    confirmedSubstitutions.forEach((confirmed) => {
        classListRemove(confirmed.id, 'invisible');
    });
    classListAdd(element.id, 'invisible');
    classListRemove(processedSubstitutionButton.id, 'invisible');

}

function showProceededSubstitutions(element) {
    let confirmedSubstitutions = Array.from(document.querySelectorAll('.confirmed'));
    let allSubstitutionButton = document.querySelector('#all-substitutions-button');
    confirmedSubstitutions.forEach((confirmed) => {
        classListAdd(confirmed.id, 'invisible');
    });
    classListAdd(element.id, 'invisible');
    classListRemove(allSubstitutionButton.id, 'invisible');
}

function selectPlayerOut(element) {
    let selectedPlayerOutElement = document.querySelector('#selected-player-out');
    selectedPlayerOutElement.innerText = element.textContent;
    selectedPlayerOutElement.setAttribute('data-player-out', element.getAttribute('data-player-id'));
    let selectedPlayerInElement = document.querySelector('#selected-player-in');
    if (selectedPlayerInElement.innerText !== '') {
        hideSubstitutionsLists();
    } else {
        showSubstitutionList();
    }
}

function selectPlayerIn(element) {
    let selectedPlayerOutElement = document.querySelector('#selected-player-out');
    let selectedPlayerInElement = document.querySelector('#selected-player-in');
    selectedPlayerInElement.innerText = element.textContent;
    selectedPlayerInElement.setAttribute('data-player-in', element.getAttribute('data-player-id'));
        if (selectedPlayerOutElement.innerText !== '') {
        hideSubstitutionsLists();
    } else {
        showSquadList();
    }
}

function showSquadList() {
    let squadList = document.querySelector('#squad-list');
    let substitutionList = document.querySelector('#substitution-list');
    classListRemove(squadList.id, 'invisible');
    classListAdd(substitutionList.id, 'invisible');
}

function showSubstitutionList() {
    let squadList = document.querySelector('#squad-list');
    let substitutionList = document.querySelector('#substitution-list');
    classListRemove(substitutionList.id, 'invisible');
    classListAdd(squadList.id, 'invisible');
}

function hideSubstitutionsLists() {
    let squadList = document.querySelector('#squad-list');
    let substitutionList = document.querySelector('#substitution-list');
    classListAdd(substitutionList.id, 'invisible');
    classListAdd(squadList.id, 'invisible');
}

function insertSubstitution() {
    let playerOutId = document.querySelector('#selected-player-out').getAttribute('data-player-out');
    let playerInId = document.querySelector('#selected-player-in').getAttribute('data-player-in');
    let teamId = document.querySelector('#substitution-data').getAttribute('data-team-id');
    if (playerOutId !== '' && playerInId !== '') {
        data = {
            'playerOutId': playerOutId,
            'playerInId': playerInId,
            'teamId': teamId
        }
        fetch(`/insert-substitution`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                loadContent(`/get-substitutions/${teamId}`, 'sidebar');
                console.log('Czas zapisany w bazie danych.');
            } else {
                console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
            }
        }).catch(error => {
            console.error('Wystąpił błąd podczas zapisywania elementu:', error);
        });
    }
}

function deleteSubstitution(substitutionId) {
    let teamId = document.querySelector('#substitution-data').getAttribute('data-team-id');
    data = {
        'substitutionId': substitutionId
    }
    fetch('/delete-substitution', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            loadContent(`/get-substitutions/${teamId}`, 'sidebar');
            console.log('Czas zapisany w bazie danych.');
        } else {
            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
        }
    }).catch(error => {
        console.error('Wystąpił błąd podczas zapisywania elementu:', error);
    });
}

function confirmSubstitutions() {
    fetch('/confirm-substitutions').then(response => {
            if (response.ok) {
                console.log('Zmiana zawodnika zapisana w bazie danych.');
                clearSidebar();
            } else {
                console.error('Wystąpił błąd podczas zapisywania zmiany zawodnikau w bazie danych.');
            }
        }).catch(error => {
            console.error('Wystąpił błąd podczas zapisywania elementu:', error);
        });
}

function changePeriod(difference) {
    let gamePeriods = Array.from(document.querySelectorAll('.game-period'));
    let currentPeriodIndex = gamePeriods.findIndex(element => element.getAttribute('data-is-current') === '1');
    let newPeriodIndex = currentPeriodIndex + difference;
    if (newPeriodIndex >= 0 && newPeriodIndex < gamePeriods.length) {
        gamePeriods.forEach((gamePeriod) => {
            classListAdd(gamePeriod.id, 'invisible');
            gamePeriod.setAttribute('data-is-current', 0)
        });
        let newPeriod = gamePeriods[newPeriodIndex];
        classListRemove(newPeriod.id, 'invisible')
        newPeriod.setAttribute('data-is-current', 1)
    }

}

function confirmNewPeriod() {
    let gamePeriods = Array.from(document.querySelectorAll('.game-period'));
    let currentPeriodIndex = gamePeriods.findIndex(element => element.getAttribute('data-is-current') === '1');
    let currentPeriod = gamePeriods[currentPeriodIndex];
    let data = {
        'periodId': currentPeriod.getAttribute('data-period-id')
    }
    fetch('/change-period', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            clearSidebar();
        } else {
            console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
        }
    }).catch(error => {
        console.error('Wystąpił błąd podczas zapisywania elementu:', error);
    });
}

function setAddedTime() {
    let addedTime = document.getElementById('added-minutes').value
    fetch(`/show-added-time/${addedTime}`)
    .then(response => {
        if (response.ok) {
            clearSidebar();
        } else {
            console.error('Wystąpił błąd podczas ustawiania dodatkowego czasu.');
        }
    }).catch(error => {
        console.error('Wystąpił błąd podczas wysyłania żądania:', error);
    });
}

function showSubstitution(team) {
    fetch(`show-substitution/${team}`);
}

    window.onload = function () {
        updateTimer();
        setTimerElementActive(matchdata.match.is_timer_active);
        checkScoreboardReverse();
    };