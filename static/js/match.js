var matchdata = JSON.parse(document.getElementById('matchdata').getAttribute('data-matchdata'));

function setMatchData(matchdata){
    document.getElementById('team_a').innerHTML = matchdata.teama.short_name;
    document.getElementById('score-a-value').innerHTML = matchdata.teama.scores;
    document.getElementById('fouls-a-value').innerHTML = setFoulsDots(matchdata.teama.fouls);
    document.getElementById('tricot_a').innerHTML = renderTricot(matchdata.teama.tricot);
    document.getElementById('team_b').innerHTML = matchdata.teamb.short_name;
    document.getElementById('score-b-value').innerHTML = matchdata.teamb.scores;
    document.getElementById('fouls-b-value').innerHTML = setFoulsDots(matchdata.teamb.fouls);
    document.getElementById('tricot_b').innerHTML = renderTricot(matchdata.teamb.tricot);
    foulsDotsColor('fouls-a-value', setFoulsDots(matchdata.teama.fouls));
    foulsDotsColor('fouls-b-value', setFoulsDots(matchdata.teamb.fouls));


}

function updateValueById(value, divId){
    if (divId === 'fouls-a-value' || divId === 'fouls-b-value'){
        document.getElementById(divId).innerHTML = setFoulsDots(value);
        foulsDotsColor(divId, setFoulsDots(value));
    } else {
        document.getElementById(divId).innerHTML = value;
    }
}

async function getJSON(url) {
	const response = await fetch(url);
	return response.json();
}

function setMatchTime(seconds, matchLength) {
    if (seconds === 0 || seconds === matchLength/2 || seconds === matchLength) {
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
        { finalTricot += '<div style="float: left; height: 8px; width: ' + size + '%; background-color: ' + color + '"></div>'; };
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

window.onload = function () {
    setMatchData(matchdata);
};