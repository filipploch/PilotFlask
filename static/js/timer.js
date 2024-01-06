		var timerElement = document.getElementById("timer-display");
		var countdownTimer = document.getElementById('countdown-timer');
		var startButton = document.getElementById('start-btn');
		var pauseButton = document.getElementById('pause-btn');
		var intervalID;
		var elapsedTime;
		var timeLimit;

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


		function runTimer() {
			elapsedTime += 1;
			if(elapsedTime === 1){
				saveTime(elapsedTime);
			} else if(elapsedTime % 10 === 0){
				// console.log(elapsedTime);
				saveTime(elapsedTime);
			}
			updateTimer();
		}

		function updateTimer() {
			if (elapsedTime <= timeLimit) {
				if (countdownTimer.checked) {
					var minutes = Math.floor((timeLimit - elapsedTime) / 60);
					var seconds = Math.floor((timeLimit - elapsedTime) % 60);

				} else {
					var minutes = Math.floor(elapsedTime / 60)
					var seconds = Math.floor(elapsedTime % 60);
				}
				timerElement.innerHTML = pad(minutes) + ":" + pad(seconds);
			}
		}

		function startTimer() {
			intervalID = setInterval(runTimer, 1000);
			saveTime(elapsedTime);
			timerElement.className = "start"
			timerElement.style.backgroundColor = "#63fa11";
			pauseButton.disabled = false;
			startButton.disabled = true;
		}

		function pauseTimer() {
			clearInterval(intervalID);
			saveTime(elapsedTime);
			timerElement.className = "pause"
			timerElement.style.backgroundColor = "#f73434";
			startButton.disabled = false;
			pauseButton.disabled = true;
		}
		
		function resetTimer() {
			clearInterval(intervalID);
			elapsedTime = 0;
			saveTime(elapsedTime);
			updateTimer();
			timerElement.className = "reset"
			timerElement.style.backgroundColor = "#b5b5b5";
            startButton.disabled = false;
			pauseButton.disabled = false;
		}

		function addSeconds() {
			if (countdownTimer.checked && elapsedTime > 0) {
				elapsedTime -= 1;
				updateTimer();
			} else if (countdownTimer.checked == false && elapsedTime < timeLimit) {
				elapsedTime += 1;
				updateTimer();
			}
			saveTime(elapsedTime);
		}

		function addMinutes() {
			if (countdownTimer.checked && elapsedTime > 60) {
				elapsedTime -= 60;
				updateTimer();
			} else if (countdownTimer.checked == false && elapsedTime < timeLimit - 60) {
				elapsedTime += 60;
				updateTimer();
			}
			saveTime(elapsedTime);
		}

		function subSeconds() {
			if (countdownTimer.checked && elapsedTime < timeLimit) {
				elapsedTime += 1;
				updateTimer();
			} else if (countdownTimer.checked == false && elapsedTime > 0) {
				elapsedTime -= 1;
				updateTimer();
			}
			saveTime(elapsedTime);
		}

		function subMinutes() {
			if (countdownTimer.checked && elapsedTime < timeLimit - 60) {
				elapsedTime += 60;
				updateTimer();
			} else if (countdownTimer.checked == false && elapsedTime > 60) {
				elapsedTime -= 60;
				updateTimer();
			}
			saveTime(elapsedTime);
		}

		document.getElementById("start-btn").addEventListener("click", startTimer);
		document.getElementById("pause-btn").addEventListener("click", pauseTimer);
		document.getElementById("reset-btn").addEventListener("click", resetTimer);
		document.getElementById("add-sec-btn").addEventListener("click", addSeconds);
		document.getElementById("add-min-btn").addEventListener("click", addMinutes);
		document.getElementById("sub-sec-btn").addEventListener("click", subSeconds);
		document.getElementById("sub-min-btn").addEventListener("click", subMinutes);