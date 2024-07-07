const jsonData = {
         "Boanerges":
          [[2, 3], [2, 6], [2, 6], [2, 9], [2, 9], [2, 12], [2, 13],
           [3, 13], [3, 16], [2, 19], [2, 22], [2, 22], [2, 25], [2, 28]]
         ,"Brotherm":
          [[1, 3], [4, 3], [5, 3], [7, 3], [6, 6], [7, 6], [8, 6],
           [7, 9], [6, 10], [5, 10], [6, 10], [6, 11], [6, 14], [5, 17]]
         ,"DRUGony":
          [[5, 0], [3, 3], [4, 3], [8, 3], [8, 3], [8, 3], [7, 6],
           [6, 9], [7, 9], [8, 9], [8, 9], [8, 9], [8, 9], [8, 9]]
         ,"Iglomen&RR":
          [[3, 3], [1, 6], [1, 9], [1, 12], [1, 12], [1, 15], [1, 18],
           [1, 21], [1, 24], [1, 27], [1, 30], [1, 33], [1, 36], [1, 39]]
         ,"MK Team":
          [[4, 3], [5, 3], [7, 3], [5, 6], [4, 9], [3, 12], [3, 13],
           [2, 16], [2, 17], [3, 17], [4, 17], [3, 20], [3, 21], [3, 24]]
         ,"Trivium Słomniki":
          [[6, 0], [7, 0], [6, 3], [6, 3], [7, 4], [5, 7], [4, 10],
           [4, 10], [5, 10], [7, 10], [5, 13], [5, 16], [5, 16], [6, 15]]
         ,"Ukrainian Legion":
          [[7, 0], [6, 3], [3, 6], [4, 6], [3, 9], [4, 9], [5, 9],
           [5, 9], [4, 12], [4, 15], [3, 18], [4, 19], [4, 20], [4, 20]]
         ,"WKS":
          [[8, 0], [8, 0], [8, 3], [3, 6], [5, 7], [6, 7], [6, 7],
           [8, 7], [8, 7], [6, 10], [7, 10], [7, 10], [7, 10], [7, 10]]
         };


function classListRemove(elementId, className) {
    var element = document.getElementById(elementId);
    if (element && element.classList.contains(className)) {
        element.classList.remove(className);
    }
}

function classListAdd(elementId, className) {
    var element = document.getElementById(elementId);
    if (element && !element.classList.contains(className)) {
        element.classList.add(className);
    }
}


function createCharts(data) {
  const sortedKeys = Object.keys(data).sort();
  const animationDiv = document.getElementById('animation');
  animationDiv.innerHTML = '';
  sortedKeys.forEach((key, index) => {
    const chartDiv = document.createElement('div');
    const nameDiv = document.createElement('div');
    const pointsDiv = document.createElement('div');
    chartDiv.className = 'chart';
    nameDiv.className = 'team-name';
    pointsDiv.className = 'team-points';

    const id = key.toLowerCase().replace(/&/g, 'and').replace(' ', '');
//    console.log(id);
    chartDiv.id = id;
    nameDiv.innerText = key;
    pointsDiv.innerText = 0;
    chartDiv.style.width = 0;
    animationDiv.appendChild(chartDiv);
    chartDiv.appendChild(nameDiv);
    chartDiv.appendChild(pointsDiv);
    topValue = getTopValues('chart')[index + 1];
    chartDiv.style.top = `${topValue}px`;
  });
//  console.log(document.styleSheets[0]);
  animateDivsOrder(jsonData);
}


function getTopValues() {
    let divs = Array.from(document.querySelectorAll('.chart'));
    let topValues = {};
    divs.forEach((div, index) => {
        let cssObj = getComputedStyle(div);
        let heightValue = parseInt(cssObj.getPropertyValue("height"));
        let marginTopValue = parseInt(cssObj.getPropertyValue("margin-top"));
        let marginBottomValue = parseInt(cssObj.getPropertyValue("margin-bottom"));
        topValues[index + 1] = index * (heightValue + marginTopValue + marginBottomValue);
    });
    return topValues;
}


function getWidthPercent(points, rounds) {
    let maxPoints = rounds * 3;
    return points / maxPoints * 100;
}


function updateKeyframes(id, topStart, topEnd, widthPercentStart, widthPercentEnd, idx) {
  return new Promise((resolve, reject) => {
    const styleSheet = document.styleSheets[0];
    const keyframes = `
      @keyframes KF${id}${idx} {
        0% { width: ${widthPercentStart}%; top: ${topStart}px; }
        20% { top: ${topStart}px; }
        80% { top: ${topEnd}px; }
        100% { width: ${widthPercentEnd}%; top: ${topEnd}px; }
      }
    `;
        const animationClass = `
      .KF${id}${idx} {
        animation: KF${id}${idx} 1.5s both linear;
      }
    `;
    if (styleSheet) {
      let found = false;
      for (let i = 0; i < styleSheet.cssRules.length; i++) {
        if (styleSheet.cssRules[i].type === CSSRule.KEYFRAMES_RULE &&
            styleSheet.cssRules[i].name === `KF${id}${idx}`) {
          styleSheet.deleteRule(i);
          found = true;
          break;
        }
      }
      if (!found) {
      }
      styleSheet.insertRule(keyframes, styleSheet.cssRules.length);
      styleSheet.insertRule(animationClass, styleSheet.cssRules.length);
    } else {
      const styleEl = document.createElement('style');
      document.head.appendChild(styleEl);
      styleEl.sheet.insertRule(keyframes, 0);
    }
//  console.log(document.styleSheets[0]);

    // Ustawienie timeoutu wewnątrz Promise
    setTimeout(() => {
      resolve();
    }, 1500);
//document.getElementById(id).addEventListener('animationend', resolve);
  });
}



async function animateDivsOrder(jsonData) {
  let topValues = getTopValues('chart');
  const roundsNumber = jsonData[Object.keys(jsonData)[0]].length;
  const startArray = Array.from(document.querySelectorAll('.chart'));
  const teamsNumber = startArray.length;
  const startOrder = {};
  startArray.forEach((div, index) => {
    let teamNameElement = div.getElementsByClassName('team-name')[0];
    startOrder[teamNameElement.textContent] = {'rank': index + 1, 'points': 0};
  })
//  var nextOrder;
  for (let i = 0; i < roundsNumber; i++) {
      let roundNr = i + 1;
      let roundNrElement = document.getElementById('round-nr');
      roundNrElement.textContent = roundNr;
      for (let j = 0; j < teamsNumber; j++) {
            let key = Object.keys(jsonData)[j];
            let rankStart = startOrder[key]['rank'];
            let pointsStart = startOrder[key]['points'];
            let rankEnd = jsonData[Object.keys(jsonData)[j]][i][0];
            let pointsEnd = jsonData[Object.keys(jsonData)[j]][i][1];
            let topStart = getTopValues()[rankStart];
            let topEnd = getTopValues()[rankEnd];
            let pointsPercentStart = getWidthPercent(pointsStart, roundsNumber);
            let pointsPercentEnd = getWidthPercent(pointsEnd, roundsNumber);
            if (j == 0) {
                console.log(pointsPercentStart);
                console.log(pointsPercentEnd);
            }

            let id = key.toLowerCase().replace(/&/g, 'and').replace(' ', '');
            let chartElement = document.getElementById(id);
            let teamNameElement = chartElement.getElementsByClassName('team-name')[0];
            let teamPointsElement = chartElement.getElementsByClassName('team-points')[0];
            teamPointsElement.textContent = `${pointsEnd} pkt.`;
            chartElement.style.top = topStart;
            chartElement.style.zIndex = rankStart;
            classListRemove(id, `KF${id}${i - 1}`);
            startOrder[key] = {'rank': rankEnd,
                              'points': pointsEnd};
            updateKeyframes(id, topStart, topEnd, pointsPercentStart, pointsPercentEnd, i);
            classListAdd(id, `KF${id}${i}`);

//            Array.from(startOrder).forEach((div, index) => {
//              startOrder[key] = nextOrder[key];
//            });

      }
      await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

//  // Funkcja do animacji przesunięcia divów
  function animateMovement(divsClassName, nextOrder) {
      let divs = Array.from(document.querySelectorAll('.chart'));
      divs.forEach((div, index) => {
        let name = div.textContent;
        let rank = nextOrder[name].rank


        div.style.transition = 'top 0.5s';
        div.style.top = `${getTopValues(divsClassName)[rank]}px`;
      });

      setTimeout(() => {
        divs.forEach(div => {
        });
      }, 500);
  }