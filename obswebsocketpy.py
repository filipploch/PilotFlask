from obswebsocket import obsws, requests
from time import sleep
import shutil
import os
from datetime import datetime
from models import Match

class OBSWebsocket:
    def __init__(self, app, host="127.20.10.3", port=4445):
        with app.app_context():
            try:
                # Próba połączenia z adresem 127.20.10.3
                self.ws = obsws(host, port)
            except Exception as e:
                print(f"Nie udało się połączyć z adresem {host}. Błąd: {e}")
                # Jeśli nie udało się połączyć, spróbuj z localhost
                localhost = "localhost"
                try:
                    # Próba połączenia z adresem localhost
                    self.ws = obsws(localhost, port)
                except Exception as e:
                    print(f"Nie udało się połączyć z adresem {localhost}. Błąd: {e}")
                    print("Żadne z dostępnych adresów IP nie jest dostępne.")

    def connect_websocket(self, app):
        with app.app_context():
            self.ws.connect()

    def close_websocket(self):
        self.ws.disconnect()

    def show_scene(self, scene_name):
        self.ws.call(requests.SetCurrentProgramScene(**{'sceneName': scene_name}))

    def get_source_id(self, scene_name, source_name):
        scene_item_id = self.ws.call(requests.GetSceneItemId(**{'sceneName': scene_name, 'sourceName': source_name}))
        response_data = scene_item_id.datain
        return response_data['sceneItemId']

    def show_source(self, scene_name, source_name, visible=True):
        source_id = self.get_source_id(scene_name, source_name)
        self.ws.call(requests.SetSceneItemEnabled(**{'sceneName': scene_name, "sceneItemId": source_id, "sceneItemEnabled": visible}))

    def mute_source(self, source_name, is_muted=True):
        self.ws.call(requests.SetInputMute(**{'inputName': source_name, 'inputMuted': is_muted}))

    def save_replay(self, type_of_action):
        self.ws.call(requests.SaveReplayBuffer())
        sleep(2)
        self._save_replay(type_of_action)

    def play_replay(self):
        self.show_scene('POWTÓRKA')
        self.mute_source('Replay')
        sleep(9)
        self.show_scene('MECZ')

    def save_replay_buffer(self):
        self.ws.call(requests.SaveReplayBuffer())
        sleep(2)
        self.play_replay()
        self._save_replay('GOL')
        self.show_source('MECZ', 'AKCJA_INFO')
        sleep(10)
        self.show_source('MECZ', 'AKCJA_INFO', visible=False)

    def _save_replay(self, type_of_action):
        file_name = self.set_replay_file_name(type_of_action)
        source_path = os.path.join('static', 'video', 'processed', 'replay.mp4')
        destination_path1 = os.path.join('static', 'video', 'replays', file_name)
        destination_path2 = os.path.join('static', 'video', 'replays', 'arch', file_name)

        try:
            shutil.copy(source_path, destination_path1)
            shutil.copy(source_path, destination_path2)
            print(f"Plik 'replay.mp4' został skopiowany do obu folderów.")
        except FileNotFoundError:
            print(f"Plik 'replay.mp4' nie istnieje w folderze źródłowym.")
        except IOError as e:
            print(f"Błąd podczas kopiowania pliku: {e}")

    def set_replay_file_name(self, type_of_action):
        _date = datetime.now().strftime("%Y%m%d-%H%M%S")
        _match = Match.query.filter_by(actual=1).first()
        _result = f'{_match.score_a}-{_match.score_b}'
        return f'{_date}___{_result}_{type_of_action}.mp4'

    def start_stop_stream(self):
        _stream_status_request = self.ws.call(requests.GetStreamStatus())
        _stream_status = _stream_status_request.datain['outputActive']
        if _stream_status:
            self.show_scene('Napisy-koncowe')
            sleep(10)
            self.stop_stream()
        else:
            self.show_scene('PUSTA')
            sleep(1)
            self.start_stream()
            sleep(1)
            self.show_source('Muzyka', 'muzyka2', visible=False)
            self.show_scene('KAMERA')
            self.show_source('Muzyka', 'muzyka')
            sleep(5)
            self.show_scene('START')


    def start_stream(self):
        self.ws.call(requests.StartStream())

    def stop_stream(self):
        self.ws.call(requests.StopStream())

    def start_replay_buffer(self):
        self.ws.call(requests.StartReplayBuffer())

    def stop_replay_buffer(self):
        self.ws.call(requests.StopReplayBuffer())

    def show_banner(self):
        self.show_source('Logo', 'Baner')
        sleep(25)
        self.show_source('Logo', 'Baner', visible=False)

    def show_action(self):
        self.show_source('MECZ', 'AKCJA_INFO')
        sleep(11)
        self.show_source('MECZ', 'AKCJA_INFO', visible=False)


    def show_virtual_table(self, division):
        divisions = ['a', 'b']
        for dvsn in divisions:
            if not dvsn == division:
                self.show_source('Logo', f'tabela_wirtualna_{dvsn}', visible=False)
        self.show_source('Logo', f'tabela_wirtualna_{division}')
        sleep(25)
        self.show_source('Logo', f'tabela_wirtualna_{division}', visible=False)