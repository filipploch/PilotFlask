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
			timeLimit = myData.match.match_length;

		}).catch(function (error) {
			console.error(error);
		});


		function changeSide() {
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
				.then(response => {
					if (response.ok) {
						console.log('Wartość została zapisana w bazie danych');
						divElement.innerHTML = newValue;
					} else {
						console.error('Błąd podczas zapisywania wartości w bazie danych');
					}
				})
				.catch(error => {
					console.error('Błąd podczas wykonywania żądania:', error);
				});
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
				if(parseInt(actionId) !== 0){
					// Wykonaj żądanie do API lub serwera backendowego, aby zapisać element w innej tabeli bazy danych
					action_data = {
                        'seconds': elapsedTime,
						'action_id': getValueOrNone(actionId),
						'player_id': getValueOrNone(playerId),
						'team_id': getValueOrNone(teamId),
						'current_date': getValueOrNone(currentDate)


//						'action_id': parseInt(document.getElementById("action-id").textContent),
//						'player_id': parseInt(document.getElementById("ws-player-id").textContent),
//						'team_id': parseInt(document.getElementById("ws-team-id").textContent)
					}
					fetch(`/insert-match-action`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify(action_data)					})
						// .then(response => response.json())
						.then(action_data => {
							console.log('Element został zapisany:', action_data);
						})
						.catch(error => {
							console.error('Wystąpił błąd podczas zapisywania elementu:', error);
						})
						;
					}
				}

		function getMatchData(team) {
			// Wykonaj żądanie do API lub serwera backendowego
			clearSidebar();
			fetch(`/actual-match-data/${team}`)
				.then(response => response.json())
				.then(data => {
					// Po otrzymaniu danych, wygeneruj listę elementów
					console.log(data);
					document.getElementById('sidebar-head').innerHTML = data[0];
					console.log(data[1]);
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
            const selectedTime = data.event.time;

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
					// console.log(value);
				// console.log(value.full_name);
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

        function processFile(filename) {
            fetch(`/process_file/${filename}`)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'replay.mkv';
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    clearSidebar();
                });
        }

        function scrapeMatches(matchId) {
			clearSidebar();
            fetch(`/scrape-matches/${matchId}`)
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
		    console.log(data);
			var isReversed = data['data'];
			if (isReversed == 1) {
				changeSide();
			}
		}).catch(function (error) {
			console.error(error);
		});}

    window.onload = function () {
        updateTimer();
        checkScoreboardReverse();
    };