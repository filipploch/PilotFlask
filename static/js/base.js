async function repeater(){
    const matchObj = await getJSON('http://127.0.0.1:5555/matchdata');

    document.getElementById('team_a').innerHTML = matchObj.teama.short_name;
    document.getElementById('tricot_a').innerHTML = renderTricot(matchObj.teama.tricot);
    document.getElementById('team_b').innerHTML = matchObj.teamb.short_name;
    document.getElementById('tricot_b').innerHTML = renderTricot(matchObj.teamb.tricot);


	// readTextFile("bramkia.txt", "score_a");
	// readTextFile("bramkib.txt", "score_b");
	// readTextFile("faulea.txt", "fouls_a");
	// readTextFile("fauleb.txt", "fouls_b");
	// readTextFile("pasek.txt", "info_bar_text");
	// readTextFile("czasmin.txt", "time");
	// readTextFile("Akcja.txt", "action_info");
	// readTextFile("strikers_a.txt", "strikers_a");
	// readTextFile("strikers_b.txt", "strikers_b");

	setTimeout("repeater()",500);
}


async function getJSON(url) {
	const response = await fetch(url);
	return response.json();
}






function renderTricot(tricot) {
    let finalTricot = '';
    let size = 100/tricot.length;

    
    for (const color of tricot)
        { finalTricot += '<div style="float: left; height: 6px; width: ' + size + '%; background-color: ' + color + '"></div>'; };

    return finalTricot;
}