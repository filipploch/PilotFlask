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
        print(f"Plik '{_file_name}' został skopiowany do folderu replays.")
    except FileNotFoundError:
        print(f"Plik '{_file_name}' nie istnieje w folderze źródłowym.")
    except IOError as e:
        print(f"Błąd podczas kopiowania pliku: {e}")


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


def get_video_length(video_path):
    if not os.path.isfile(video_path):
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
            _duration += get_video_length(_videopath)
    return round(_duration)
