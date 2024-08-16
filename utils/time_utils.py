def format_time(_time, _format):
    _seconds = _time['seconds']
    _added_seconds = _time['added_seconds']
    _sec = _seconds - _added_seconds - 1
    for key in _time:
        print(f'{key}: {_time[key]}')
    match _format:
        case 'min':
            if _added_seconds > 0:
                return f'{int(_sec / 60 + 1)}+{int(_added_seconds/60 + 1)}'
            return f'{int((_seconds - 1)/60 + 1)}'