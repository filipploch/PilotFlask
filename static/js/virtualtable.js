async function clearResult(matchId) {
    var number1 = '';
    var number2 = '';
    var division = document.getElementById('division').innerText;
    var isChecked = document.getElementById('actual_' + matchId).checked;

    // Wysyłamy żądanie POST
    const response = await fetch(`/save-result/controller/${division}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: matchId,
            result_home: number1,
            result_away: number2,
            actual: false
        }),
    });

    // Sprawdzamy, czy żądanie było udane (status 200)
    if (response.ok) {
        // Odświeżamy stronę po pomyślnym zapisie
        // location.reload();
            document.getElementById('result_home_' + matchId).value = '';
            document.getElementById('result_away_' + matchId).value = '';
    } else {
        console.error('Wystąpił błąd podczas zapisywania wyników.');
    }
}

async function saveResult(matchId) {
    var number1 = document.getElementById('result_home_' + matchId).value;
    var number2 = document.getElementById('result_away_' + matchId).value;
    var division = document.getElementById('division').innerText;
    var isChecked = document.getElementById('actual_' + matchId).checked;


    // Wysyłamy żądanie POST
    const response = await fetch(`/save-result/controller/${division}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: matchId,
            result_home: number1,
            result_away: number2,
            actual: isChecked
        }),
    });


    // Sprawdzamy, czy żądanie było udane (status 200)
    if (response.ok) {
        // Odświeżamy stronę po pomyślnym zapisie
        console.log('Zapisano wyniki')
//        generateBaseTable();
        // location.reload();
        // handleServerResponse(response)
    } else {
        console.error('Wystąpił błąd podczas zapisywania wyników.');
    }
}


function generateBaseTable() {
    var division = document.getElementById('division').innerText;
    var sidebarBody = document.getElementById('sidebar-body')
//    var selectedRows = sidebarBody.querySelectorAll('input[type="checkbox"]:checked');
    var results = sidebarBody.getElementsByClassName('results');
    console.log('division, results', division, results);
    var selectedData = [];
    results.forEach(function (row) {
        var teams0 = row.closest('tr').getElementsByClassName('team-a-name')[0].textContent;
        var teams1 = row.closest('tr').getElementsByClassName('team-b-name')[0].textContent;
        selectedData.push(teams0, teams1);
    });

    fetch(`/generate_base_table/${division}`, {
        method: 'POST', // Użyj metody POST, aby przesłać dane w ciele zapytania
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(selectedData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        // Obsługa błędu (możesz wyświetlić komunikat o błędzie)
        console.error('Błąd podczas generowania Base Table:', error);
    });
}




async function handleServerResponse(response) {
    try {
        const data = await response.json();
        console.log('handleServerResponse', data);
        
        if (data.function) {
            console.log('Received data from server:', data);
            loadMatches(data.function);
        }
    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
}