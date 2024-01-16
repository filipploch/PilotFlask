import shutil
import os
from datetime import datetime
from models import Match


def save_replay(type_of_action):
    file_name = set_replay_file_name(type_of_action)
    source_path = os.path.join('static', 'video', 'processed', 'replay.mkv')
    destination_path1 = os.path.join('static', 'video', 'replays', file_name)
    destination_path2 = os.path.join('static', 'video', 'replays', 'arch', file_name)


    try:
        # Kopiuj do pierwszego folderu
        shutil.copy(source_path, destination_path1)

        # Kopiuj do drugiego folderu
        shutil.copy(source_path, destination_path2)

        print(f"Plik 'replay.mkv' został skopiowany do obu folderów.")
    except FileNotFoundError:
        print(f"Plik 'replay.mkv' nie istnieje w folderze źródłowym.")
    except IOError as e:
        print(f"Błąd podczas kopiowania pliku: {e}")

def set_replay_file_name(type_of_action):
    _date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    _match = Match.query.filter_by(actual=1).first()
    _result = f'{_match.score_a}-{_match.score_b}'
    return f'{_date}___{_result}_{type_of_action}.mkv'

save_replay('GOL')
