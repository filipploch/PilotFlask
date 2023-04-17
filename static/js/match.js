async function repeater(){
    const matchObj = await getJSON('http://127.0.0.1:5555/matchdata');

    document.getElementById('team_a').innerHTML = matchObj.teama.short_name;
    document.getElementById('score_a').innerHTML = matchObj.teama.scores;
    document.getElementById('fouls_a').innerHTML = setFoulsDots(matchObj.teama.fouls);
    document.getElementById('tricot_a').innerHTML = renderTricot(matchObj.teama.tricot);
    document.getElementById('team_b').innerHTML = matchObj.teamb.short_name;
    document.getElementById('score_b').innerHTML = matchObj.teamb.scores;
    document.getElementById('fouls_b').innerHTML = setFoulsDots(matchObj.teamb.fouls);
    document.getElementById('tricot_b').innerHTML = renderTricot(matchObj.teamb.tricot);
    document.getElementById('time').innerHTML = setMatchTime(matchObj.match.seconds, matchObj.match.match_lenght);
//    document.getElementById('match_date').innerHTML = getCurrentDate();
    foulsDotsColor('fouls_a', setFoulsDots(matchObj.teama.fouls));
    foulsDotsColor('fouls_b', setFoulsDots(matchObj.teamb.fouls));

	// readTextFile("bramkia.txt", "score_a");
	// readTextFile("bramkib.txt", "score_b");
	// readTextFile("faulea.txt", "fouls_a");
	// readTextFile("fauleb.txt", "fouls_b");
	// readTextFile("pasek.txt", "info_bar_text");
	// readTextFile("czasmin.txt", "time");
	// readTextFile("Akcja.txt", "action_info");
	// readTextFile("strikers_a.txt", "strikers_a");
	// readTextFile("strikers_b.txt", "strikers_b");

	setTimeout(repeater ,500);
}

async function getJSON(url) {
	const response = await fetch(url);
	return response.json();
}

function setMatchTime(seconds, match_lenght) {
    if (seconds === 0 || seconds === match_lenght * 60) {
        return '';
    }
    else {
        return String(Math.trunc(seconds/60) + 1) + "'";
    }
}

function getCurrentDate() {
    let currentDate = new Date().toJSON().slice(0, 10);
    return currentDate;
}

function renderTricot(tricot) {
    let finalTricot = '';
    let size = 100/tricot.length;

    for (const color of tricot)
        { finalTricot += '<div style="float: left; height: 6px; width: ' + size + '%; background-color: ' + color + '"></div>'; };
    return finalTricot;
}

function setFoulsDots(value) {
    return "●".repeat(value)
}

function foulsDotsColor(fouls, allText)
{
    if(allText == "●" || allText == "●●" || allText == "●●●") {document.getElementById(fouls).style.color = "#FFF";}
    else if(allText == "●●●●") {document.getElementById(fouls).style.color = "#fff700";}
    else if(allText == "●●●●●") {document.getElementById(fouls).style.color = "#F00";}
}