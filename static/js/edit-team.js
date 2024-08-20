document.addEventListener('DOMContentLoaded', function() {
  setPlayersIsActive();
});

function setPlayersIsActive() {
    let playersElements = document.querySelectorAll('.player-elements');
    let isActive;
    let squadCheckbox;
    let hiddenCheckbox;
    let playerId;
    Array.from(playersElements).forEach(playerElements => {
        isActive = playerElements.getAttribute('data-is-active');
        if (parseInt(isActive) === 0){
            Array.from(playerElements.querySelectorAll('*')).forEach(playerElement => {
                playerElement.setAttribute('disabled', 'disabled');
                playerElement.style.backgroundColor = '#DDD';
            });
            playerId = playerElements.getAttribute('data-player-id');
            squadCheckbox = playerElements.querySelector(`#player_${playerId}_squad_checkbox`);
            squadCheckbox.style.display = 'none';
            hiddenCheckbox = playerElements.querySelector(`#player_${playerId}_hidden_checkbox`);
            hiddenCheckbox.style.display = 'inline-block';
            hiddenCheckbox.removeAttribute('disabled');
        } else {
            Array.from(playerElements.querySelectorAll('*')).forEach(playerElement => {
                playerElement.removeAttribute('disabled');
                playerElement.style.backgroundColor = '#FFF';
            });
            playerId = playerElements.getAttribute('data-player-id');
            squadCheckbox = playerElements.querySelector(`#player_${playerId}_squad_checkbox`);
            squadCheckbox.style.display = 'inline-block';
            hiddenCheckbox = playerElements.querySelector(`#player_${playerId}_hidden_checkbox`);
            hiddenCheckbox.style.display = 'none';
        }
    });
}

function addPlayer() {
    let teamId = document.getElementById('add-player-element').getAttribute('data-team-id');
    let firstNameElement = document.getElementById('add-player-first-name');
    let lastNameElement = document.getElementById('add-player-last-name');
    let number = document.getElementById('add-player-number').value;
    let isGoalkeeper = document.getElementById('add-player-is-goalkeeper').value;
    let isCaptain = document.getElementById('add-player-is-captain').value;

    if (firstNameElement.value !== '' && lastNameElement.value !== '') {

        var data = {
            'teamId': teamId,
            'firstName': firstNameElement.value,
            'lastName': lastNameElement.value,
            'number': number,
            'isGoalkeeper': isGoalkeeper,
            'isCaptain': isCaptain
        };

        fetch('/add-player', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                console.log('Dodano zawodnika do bazy danych.');
                location.reload();
            } else {
                console.error('Wystąpił błąd podczas dodawania zawodnika do bazy danych.');
            }
        }).catch(error => {
            console.error('Wystąpił błąd:', error);
        });
    } else if (firstNameElement.value === '' && lastNameElement.value === '') {
        firstNameElement.style.backgroundColor = 'red';
        lastNameElement.style.backgroundColor = 'red';
    } else if (firstNameElement.value === '') {
        firstNameElement.style.backgroundColor = 'red';
        lastNameElement.style.backgroundColor = '';
    } else if (lastNameElement.value === '') {
        firstNameElement.style.backgroundColor = '';
        lastNameElement.style.backgroundColor = 'red';
    }
}

function showAddPlayerElement() {
    classListRemove('add-player-element', 'invisible');
}

function hideAddPlayerElement() {
    classListAdd('add-player-element', 'invisible');
}

function deletePlayer(element) {
    let playerId = element.getAttribute('data-player-id');
        var data = {
            'playerId': playerId,
        };

        fetch('/delete-player', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                console.log('Dodano zawodnika do bazy danych.');
                location.reload();
            } else {
                console.error('Wystąpił błąd podczas dodawania zawodnika do bazy danych.');
            }
        }).catch(error => {
            console.error('Wystąpił błąd:', error);
        });
}

function toggleIsActive(element){
    let playerId = element.getAttribute('data-player-id');
    let parent = document.getElementById(`player_${playerId}`);
    let playerElements = Array.from(parent.querySelectorAll('*'));
    let hiddenCheckbox = document.getElementById(`player_${playerId}_hidden_checkbox`);
    let squadCheckbox = document.getElementById(`player_${playerId}_squad_checkbox`);
    let data = {
        'playerId': playerId
    }
    fetch('/toggle-is-active', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Dane zaktualizowane:', data);
        if (parseInt(data.is_active) === 0) {
            playerElements.forEach(playerElement => {
                playerElement.setAttribute('disabled', 'disabled');
                playerElement.style.backgroundColor = '#DDD';
                if (playerElement.id === `player_${playerId}_is_active`) {
                    playerElement.value = 0;
                }
            });
            squadCheckbox.style.display = 'none';
            hiddenCheckbox.style.display = 'inline-block';
            hiddenCheckbox.removeAttribute('disabled');
        } else {
            playerElements.forEach(playerElement => {
                playerElement.removeAttribute('disabled');
                playerElement.style.backgroundColor = '#FFF';
                if (playerElement.id === `player_${playerId}_is_active`) {
                    playerElement.value = 1;
                }
            });
            squadCheckbox.style.display = 'inline-block';
            hiddenCheckbox.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Błąd podczas aktualizacji danych:', error);
        // Dodaj kod obsługi błędu
    });
}