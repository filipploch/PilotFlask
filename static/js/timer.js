		var timerElement = document.getElementById("timer-display");
		var countdownTimer = document.getElementById('countdown-timer');
		var startButton = document.getElementById('start-btn');
		var pauseButton = document.getElementById('pause-btn');
		var intervalID;
		var elapsedTime;
		var timeLimit;
//        var matchdata = JSON.parse(document.getElementById('matchdata').getAttribute('data-matchdata'));

		function pad(num) {
			return ("0" + parseInt(num)).substr(-2);
		}

		function saveTime(elapsedTime) {
			fetch('/update-time', {
				method: 'POST',
				headers: {
				'Content-Type': 'application/json',
				},
				body: JSON.stringify({ 'seconds': elapsedTime }),
			})
				.then(response => {
				if (response.ok) {
					console.log('Czas zapisany w bazie danych.');
				} else {
					console.error('Wystąpił błąd podczas zapisywania czasu w bazie danych.');
				}
				})
				.catch(error => {
				console.error('Wystąpił błąd podczas komunikacji z serwerem:', error);
				});
			}

        function controlTimer(controlVariable){
            fetch('/control-timer', {
				method: 'POST',
				headers: {
				'Content-Type': 'application/json',
				},
				body: JSON.stringify({ 'control_variable': controlVariable }),
			})
        }

		function runTimer() {
			elapsedTime += 1;
			if(elapsedTime === 1 || elapsedTime === timeLimit/2 + 1){
				saveTime(elapsedTime);
			} else if(elapsedTime === timeLimit/2 || elapsedTime === timeLimit){
			    pauseTimer();
				saveTime(elapsedTime);
			} else if(elapsedTime % 10 === 0){
				saveTime(elapsedTime);
			}
			updateTimer();
		}

		function updateTimer() {
            timerElement.innerHTML = getFormattedTime('panel');
		}

		function startTimer() {
            controlTimer(1);
            setTimerElementActive(1);
//            classListRemove(timerElement.id, 'pause');
//            classListRemove(timerElement.id, 'reset');
//            classListAdd(timerElement.id, 'start');
//			timerElement.style.backgroundColor = "#63fa11";
//			pauseButton.disabled = false;
//			startButton.disabled = true;
		}

		function setTimerElementActive(timerStateNumber){
		    classListRemove(timerElement.id, 'pause');
            classListRemove(timerElement.id, 'reset');
            classListRemove(timerElement.id, 'start');
            if (timerStateNumber === 1) {
                classListAdd(timerElement.id, 'start');
                timerElement.style.backgroundColor = "#63fa11";
                pauseButton.disabled = false;
                startButton.disabled = true;
            } else if (timerStateNumber === 0) {
                classListAdd(timerElement.id, 'pause');
                timerElement.style.backgroundColor = "#f73434";
                startButton.disabled = false;
                pauseButton.disabled = true;
            } else if (timerStateNumber === 2) {
                classListAdd(timerElement.id, 'reset');
                timerElement.style.backgroundColor = "#b5b5b5";
                startButton.disabled = false;
                pauseButton.disabled = false;
            }
		}

		function pauseTimer() {
            controlTimer(0);
            setTimerElementActive(0);
		}
		
		function resetTimer() {
            controlTimer(2);
            setTimerElementActive(2);
		}

//		function addSeconds() {
//			if (countdownTimer.checked && elapsedTime > 0) {
//				elapsedTime -= 1;
//				updateTimer();
//			} else if (countdownTimer.checked == false && elapsedTime < timeLimit) {
//				elapsedTime += 1;
//				updateTimer();
//			}
//			saveTime(elapsedTime);
//		}

        function addSeconds() {
            let timeDifference;
			if (matchdata.match.is_panel_timer_ascending) {
				timeDifference = 1;
			} else {
				timeDifference = -1;
			}
			fetch(`/increment-seconds/${timeDifference}`);
		}

		function addMinutes() {
            let timeDifference;
			if (matchdata.match.is_panel_timer_ascending) {
				timeDifference = 60;
			} else {
				timeDifference = -60;
			}
			fetch(`/increment-seconds/${timeDifference}`);
		}

		function subSeconds() {
            let timeDifference;
			if (matchdata.match.is_panel_timer_ascending) {
				timeDifference = -1;
			} else {
				timeDifference = 1;
			}
			fetch(`/increment-seconds/${timeDifference}`);
		}

		function subMinutes() {
            let timeDifference;
			if (matchdata.match.is_panel_timer_ascending) {
				timeDifference = -60;
			} else {
				timeDifference = 60;
			}
			fetch(`/increment-seconds/${timeDifference}`);
		}

		document.getElementById("start-btn").addEventListener("click", startTimer);
		document.getElementById("pause-btn").addEventListener("click", pauseTimer);
		document.getElementById("reset-btn").addEventListener("dblclick", resetTimer);
		document.getElementById("add-sec-btn").addEventListener("click", addSeconds);
		document.getElementById("add-min-btn").addEventListener("click", addMinutes);
		document.getElementById("sub-sec-btn").addEventListener("click", subSeconds);
		document.getElementById("sub-min-btn").addEventListener("click", subMinutes);