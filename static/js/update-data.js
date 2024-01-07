function updateData(dataId) {
    var selectedAction = document.getElementById('select-actions').value;
    var selectedPlayer = document.getElementById('select-players').value;

    var minutesInputValue = parseInt(document.getElementById('action-minute').value, 10) || 0;
    var secondsInputValue = parseInt(document.getElementById('action-second').value, 10) || 0;
    var timeInSeconds = minutesInputValue * 60 + secondsInputValue;
    var isActionHidedCheckbox = document.getElementById('action-hide');
    var isActionHidedValue = isActionHidedCheckbox.checked ? 1 : 0;
    console.log(isActionHidedValue);

    fetch(`/update-data/${dataId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: selectedAction,
            player: selectedPlayer,
            time: timeInSeconds,
            is_hided: isActionHidedValue,
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Dane zaktualizowane:', data);
        clearSidebar();
        // Dodaj kod obsługi sukcesu lub ewentualne odświeżenie widoku
    })
    .catch(error => {
        console.error('Błąd podczas aktualizacji danych:', error);
        // Dodaj kod obsługi błędu
    });
}

function deleteData(dataId) {

    fetch(`/delete-data/${dataId}`, {
        method: 'DELETE',
    })
    .then(clearSidebar())
    .catch(error => {
        console.error('Błąd podczas aktualizacji danych:', error);
        // Dodaj kod obsługi błędu
    });
}

function updatePlayersList() {
    var selectActions = document.getElementById("select-actions");
    var selectedOptionValue = selectActions.options[selectActions.selectedIndex].value;
    var playersList = document.getElementById("select-players");
    var playersListNormal = document.getElementById("select-players-normal");
    var optionsPlayersNormal = Array.from(playersListNormal.options);
    var playersListOg = document.getElementById("select-players-og");
    var optionsPlayersOg = Array.from(playersListOg.options);

    playersList.innerHTML = '';
    if (selectedOptionValue === '4') {
        optionsPlayersOg.forEach(function(option) {
        var newOption = document.createElement('option');
        newOption.value = option.value;
        newOption.text = option.text;
        playersList.add(newOption);
        });
        console.log(playersList);
    } else {
        optionsPlayersNormal.forEach(function(option) {
        var newOption = document.createElement('option');
        newOption.value = option.value;
        newOption.text = option.text;
        playersList.add(newOption);
        });
        console.log(playersList);
    }
    console.log('poszlo: updatePlayersList()')
}