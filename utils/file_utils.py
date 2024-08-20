import json

import ffmpeg
import shutil
import time
import os
import subprocess


def _is_file_open(filepath):
    print(filepath)
    if False:
        return False
    return True


def _wait_for_file_close(filepath, check_interval=0.2):
    while _is_file_open(filepath):
        time.sleep(check_interval)


def _get_filename_from_source(src):
    _source = src
    if '\\' in _source:
        _source = _source.split('\\')[-1]
    print(_source)
    return _source


def copy_file(src, dest):
    _file_name = _get_filename_from_source(src)

    try:
        shutil.copy(src, dest)
        print(f"Plik '{_file_name}' został skopiowany do folderu archiwum.")
    except FileNotFoundError:
        print(f"(copy_file()) Plik '{_file_name}' nie istnieje w folderze powtórek.")
    except IOError as e:
        print(f"Błąd podczas kopiowania pliku: {e}")


def move_file(src, dest):
    _file_name = _get_filename_from_source(src)

    try:
        shutil.move(src, dest)
        print(f"Plik '{_file_name}' został przeniesiony do folderu powtórek.")
    except FileNotFoundError:
        print(f"(move_file()) Plik '{_file_name}' nie istnieje w folderze źródłowym.")
    except IOError as e:
        print(f"Błąd podczas przenoszenia pliku: {e}")


def rename_replay_files(directory, name_core, new_value):
    """
    Funkcja zmienia nazwy plików w zadanym katalogu, których nazwy zaczynają się od `name_core`.
    Nowa nazwa plików będzie zaczynała się od zmodyfikowanego `name_core` z zastąpionym ostatnim fragmentem na `new_value`.

    :param directory: str, ścieżka do katalogu, w którym znajdują się pliki
    :param name_core: str, początkowy fragment nazwy pliku do wyszukania
    :param new_value: str, nowy fragment nazwy pliku zastępujący ostatnią część `name_core`
    """
    for filename in os.listdir(directory):
        if filename.startswith(name_core):
            # Znajdź ostatni fragment w `name_core`
            base_name = name_core.rsplit('_', 1)[0]
            # Nowa nazwa pliku
            new_filename = filename.replace(name_core, f"{base_name}_{new_value}", 1)
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)
            os.rename(old_filepath, new_filepath)


def get_video_duration(video_path):
    if not os.path.isfile(video_path):
        print('no video file:', video_path)
        return 0
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", video_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    try:
        duration = float(result.stdout)
    except:
        duration = 0
    return int(duration)


def count_files_with_name_fragment(directory, name_fragment):
    count = 0
    for filename in os.listdir(directory):
        if name_fragment in filename:
            count += 1
    return count


def get_sum_of_recorded_files_duration_by_name_fragment(directory, name_fragment):
    _duration = 0
    for filename in os.listdir(directory):
        if name_fragment in filename:
            _videopath = directory + '\\' + filename
            _duration += get_video_duration(_videopath)
    return round(_duration)


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)



def create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass


def get_replay_playback_time(_replay_duration, _playback_speed_percent=90):
    speed_factor = _playback_speed_percent / 100.0
    new_time = _replay_duration / speed_factor
    return int(new_time)


def get_replay_file_duration(file_path):
    try:
        return ffmpeg.probe(file_path)['format']['duration'].split('.')[0]
    except:
        return 11


def process_csv_file(_file, _team_id: int, _keys: list = None): #todo is_active key
    if not _keys:
        _keys = ['default_nr', 'first_name', 'last_name', 'position', 'captain', 'team', 'full_name', 'squad']
    _players = []
    lines = _file.stream.readlines()[1:]
    for line in lines:
        _record = {}
        elements = line.decode('utf-8').split(',')
        if len(elements) < 6:
            continue
        for i, _key in enumerate(_keys):
            if _key == 'team':
                _record.update({_key: _team_id})
            elif _key == 'first_name':
                _record.update({_key: elements[1]})
            elif _key == 'last_name':
                _record.update({_key: elements[2]})
            elif _key == 'full_name':
                _record.update({_key: f'{elements[2]} {elements[1]}'})
            elif _key == 'default_nr':
                _record.update({_key: elements[0]})
            elif _key == 'position':
                _record.update({_key: 1 if 'G' in elements[3] else 0})
            elif _key == 'captain':
                _record.update({_key: 1 if 'K' in elements[4] else 0})
            elif _key == 'squad':
                _record.update({_key: 1})
        _players.append(_record)
    return _players


def get_text_file_content(file):
    with open(file, 'r', encoding='utf-8') as file:
        return file.read()


def save_txt_file(file, content):
    with open(file, 'w', encoding='utf-8') as file:
        file.write(content)