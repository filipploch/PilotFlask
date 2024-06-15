document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect('http://127.0.0.1:5555');
//    socket.on('update_time', function(data) {
//        var timerDisplays = document.querySelectorAll('.timer_display');
//        timerDisplays.forEach(function(div) {
//          div.textContent = data.time;
//        });
//        var resultsChamber =  document.getElementById('results_chamber');
//        if (typeof(resultsChamber) != 'undefined' && resultsChamber != null) {
//          sortResults('results_chamber');
//        }
//        var resultsTeamType =  document.getElementById('results_team_type');
//        if (typeof(resultsTeamType) != 'undefined' && resultsTeamType != null) {
//          sortResults('results_team_type');
//        }
//    });
//    socket.on('toggle_classes', function(data) {
//      var elements = document.querySelectorAll(`.${data.element_class}`);
//      elements.forEach(function(element) {
//          toggleClasses(element, data.class_1_name, data.class_2_name);
//        });
//    });
    socket.on('record_state', function(data) {
      console.log(data);
    });
});