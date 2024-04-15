function loadContent(endpoint, elementToChange, optionalArg) {
    // Sprawdź, czy optionalArg został przekazany
    if (typeof optionalArg !== 'undefined') {
        endpoint = endpoint + optionalArg;
        // Tutaj możesz dostosować zachowanie funkcji w zależności od optionalArg
    }

    // Wyślij żądanie na serwer Flask po kliknięciu przycisku
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            // Zaktualizuj zawartość diva id="second"
            document.getElementById(elementToChange).innerHTML = data.content;
        })
        .catch(error => console.error('Error:', error));
}