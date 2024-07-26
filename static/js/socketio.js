document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect('http://127.0.0.1:5555');
    socket.on('update_time', function(data) {
        var panelTimeDisplays = document.querySelectorAll('.panel-time-display');
        var streamTimeDisplays = document.querySelectorAll('.stream-time-display');

        streamTimeDisplays.forEach(function(div) {
          div.innerHTML = getFormattedTime('stream', data.seconds, data.added_seconds);
        });
        panelTimeDisplays.forEach(function(div) {
          div.setAttribute('data-time-seconds', data.seconds);
          div.setAttribute('data-time-added-seconds', data.added_seconds);
          div.textContent = getFormattedTime('panel', data.seconds, data.added_seconds);
        });
    });
    socket.on('update-value', function(data) {
        let divId = data.divId;
        let value = data.value;
        updateValueById(value, divId);
    });
})