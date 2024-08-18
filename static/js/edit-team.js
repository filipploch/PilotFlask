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