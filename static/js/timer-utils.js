function getFormattedTime(target, seconds, addedSeconds, optionalDisplayMode) {
    let definedDisplayMode;
    let isTimerAscending;
    if (target === 'panel'){
        definedDisplayMode = matchdata.match.panel_timer_display_mode;
        isTimerAscending = matchdata.match.is_panel_timer_ascending;
    } else if (target === 'stream'){
        definedDisplayMode = matchdata.match.stream_timer_display_mode;
        isTimerAscending = matchdata.match.is_stream_timer_ascending;
    }
    if (typeof optionalDisplayMode === 'undefined') {
        displayMode = definedDisplayMode;
    } else {
        displayMode = optionalDisplayMode;
    }
    if (typeof seconds === 'undefined' || typeof addedSeconds === 'undefined') {
        seconds = timeData.seconds;
        addedSeconds = timeData.added_seconds;
    }
    switch (displayMode) {
        case 'mm:ss':
            formattedTime = getMinSecFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata);
            break;
        case 's':
            formattedTime = getSecFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata);
            break;
        default:
            formattedTime = getMinFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata);
    }
    return formattedTime;
}

function getMinSecFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata){
    let isAddedTimeAllowed = matchdata.match.is_added_time_allowed;
    let currentPeriod = matchdata.match.current_period;
    let periodTimeLimit = matchdata.match.period_time_limit;
    let formattedTime;
    let mins;
    let secs;

    if (isTimerAscending) {
        mins = Math.floor(seconds / 60);
        secs = Math.floor(seconds % 60);
        if (seconds > periodTimeLimit){
            addedMins = Math.floor(addedSeconds / 60);
            addedSecs = Math.floor(addedSeconds % 60);
            return `+${addedMins}:${addedSecs.toString().padStart(2, '0')}`
        }

    } else {
        mins = Math.floor((periodTimeLimit - seconds + 1) / 60);
        secs = Math.floor((periodTimeLimit - seconds + 1) % 60);
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

function getMinFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata){
    let isAddedTimeAllowed = matchdata.match.is_added_time_allowed;
    let currentPeriod = matchdata.match.current_period;
    let periodTimeLimit = matchdata.match.period_time_limit;
    let formattedTime;
    let mins;
    if (isTimerAscending) {
        mins = Math.floor(seconds / 60) + 1;
        if (seconds > periodTimeLimit){
            addedMins = Math.floor(addedSeconds / 60) + 1;
            return `${mins} +${addedMins}`
        }

    } else {
        mins = Math.floor((periodTimeLimit - seconds + 1) / 60);
        secs = Math.floor((periodTimeLimit - seconds + 1) % 60);
    }
    return `${mins}`
}

function getSecFormat(seconds, addedSeconds, displayMode, isTimerAscending, matchdata){
    let isAddedTimeAllowed = matchdata.match.is_added_time_allowed;
    let currentPeriod = matchdata.match.current_period;
    let periodTimeLimit = matchdata.match.period_time_limit;
    let formattedTime;
    let secs;
    if (isTimerAscending) {
        secs = seconds;
        if (seconds > periodTimeLimit){
            return `${secs} +${addedSecs}`
        }

    } else {
        secs = periodTimeLimit - seconds + 1;
    }
    return `${secs}`
}