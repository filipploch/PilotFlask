import time

import socketio
from obswebsocket import obsws, requests, events
from time import sleep
import shutil
import os
from datetime import datetime
from models import Match, MatchAction
from video_recorder import VideoRecorder, CameraIdxFinder, AdditionalVirtualCameras
from utils.file_utils import copy_file
from threading import Thread


class OBSWebsocket:
    def __init__(self, app, host="localhost", port=4445):
        self.app = app
        self.port = port
        with self.app.app_context():
            try:
                self.ws = obsws(host, port, authreconnect=5)
            except Exception as e:
                print(f"Nie udało się połączyć z adresem {host}. Błąd: {e}")
                print("Żadne z dostępnych adresów IP nie jest dostępne.")
            self.socketio = app.config['SOCKETIO']
            self.ws.register(self.on_record_state_change, events.RecordStateChanged)
            # self.ws.register(self.on_replay_buffer_state_change, events.ReplayBufferStateChanged)
            # self.ws.register(self.on_source_filter_enable_change, events.SourceFilterEnableStateChanged)
            # self.ws.register(self.on_replay_buffer_saved, events.ReplayBufferSaved)

    def on_replay_buffer_state_change(self, event_data):
        _status = self.app.config['OBS_REPLAY_BUFFER_STATUS']
        self.socketio.emit('replay_buffer_status', {'message': event_data.datain})
        self.app.config['OBS_REPLAY_BUFFER_STATUS'] = event_data.datain['outputActive']
        if _status != self.app.config['OBS_REPLAY_BUFFER_STATUS']:
            self.toggle_virtual_cams_state(self.app)

    def on_record_state_change(self, event_data):
        _status = self.app.config['OBS_RECORD_STATUS']
        self.socketio.emit('record_status', {'message': event_data.datain})
        self.app.config['OBS_RECORD_STATUS'] = event_data.datain['outputActive']
        if _status != self.app.config['OBS_RECORD_STATUS']:
            self.toggle_virtual_cams_state(self.app)
        if self.app.config['OBS_RECORD_STATUS']:
            self.socketio.start_background_task(self.app.config['REPLAYS_TIMER'].start_timer)
        print('OBS_RECORD_STATUS:', self.app.config['OBS_RECORD_STATUS'])



    def on_stream_state_change(self, event_data):
        _status = self.app.config['OBS_STREAM_STATUS']
        self.socketio.emit('stream_status', {'message': event_data.datain})
        self.app.config['OBS_STREAM_STATUS'] = event_data.datain['outputActive']
        if _status != self.app.config['OBS_STREAM_STATUS']:
            self.toggle_virtual_cams_state(self.app)

    def on_source_filter_enable_change(self, event_data):
        self.socketio.emit('filter_status', {'status': event_data.datain})

    def on_replay_buffer_saved(self, event_data):
        self.virtual_cameras_save_replay(automatic=False)

    def virtual_cameras_save_replay(self, automatic=True):
        for camera in self.app.config['CAMERAS']:
            print(camera)
            self.socketio.start_background_task(self.app.config['CAMERAS'][camera].save_replay, automatic)

    def connect_websocket(self, app):
        with app.app_context():
            self.ws.connect()
            self.init_virtual_cameras(app)
            self.set_config_replay_buffer_status(app)

    def init_virtual_cameras(self, app):
        with app.app_context():
            cameras = self.get_used_virtual_cameras(app)
            for camera in cameras:
                _camera = VideoRecorder(app=app, camera_idx=CameraIdxFinder.get_camera_idx(camera['camera_name']),
                                        camera_prefix=camera['camera_prefix'], camera_name=camera['camera_name'])
                app.config['CAMERAS'].update({camera['camera_name'].upper(): _camera})

    def set_config_replay_buffer_status(self, app):
        app.config['OBS_REPLAY_BUFFER_STATUS'] = self.ws.call(requests.GetReplayBufferStatus()).datain['outputActive']
        self.toggle_virtual_cams_state(app)

    def set_config_cameras_recording_status(self, app):
        record_status = app.config['OBS_RECORD_STATUS']
        if record_status:
            app.config['CAMERAS_RECORDING_STATUS'] = True
        else:
            app.config['CAMERAS_RECORDING_STATUS'] = False

    def toggle_virtual_cams_state(self, app):
        self.set_config_cameras_recording_status(app)

        for camera in app.config['CAMERAS']:
            if app.config['OBS_RECORD_STATUS']:
                app.config['SOCKETIO'].start_background_task(app.config['CAMERAS'][camera].record_video)

    def get_scene_name_by_filter_name(self, filter_name):
        scene_sources = self.ws.call(requests.GetSceneItemList(**{'sceneName': 'ŹRÓDŁO OBRAZU'})).datain
        for source in scene_sources['sceneItems']:
            source_filters = self.ws.call(
                requests.GetSourceFilterList(**{'sourceName': source['sourceName']})).datain['filters']
            for _filter in source_filters:
                if filter_name == _filter['filterName']:
                    return source['sourceName']

    def get_used_virtual_cameras(self, app):
        with app.app_context():
            cameras = []
            _cameras = AdditionalVirtualCameras.get_additional_virtual_cameras()
            for cam in _cameras:
                if cam.name in app.config['VIRTUAL_CAMERAS']:
                    _camera_settings = {}
                    camera_prefix = self.set_camera_prefix(cam.name)
                    cameras.append({
                        'camera_name': cam.name,
                        'camera_prefix': camera_prefix
                    })
            return cameras

    def set_camera_prefix(self, virtual_camera_name):
        if virtual_camera_name == 'OBS-Camera':
            camera_prefix = 'C1'
        elif virtual_camera_name.startswith('OBS-Camera'):
            camera_prefix = f'C{int(virtual_camera_name.split("OBS-Camera")[1])}'
        else:
            camera_prefix = 'CX'
        return camera_prefix

    def close_websocket(self):
        self.ws.disconnect()

    def get_current_scene(self):
        current_scene = self.ws.call(requests.GetCurrentProgramScene()).datain
        return current_scene

    def show_scene(self, scene_name):
        self.ws.call(requests.SetCurrentProgramScene(**{'sceneName': scene_name}))

    def get_source_id(self, scene_name, source_name):
        scene_item_id = self.ws.call(requests.GetSceneItemId(**{'sceneName': scene_name, 'sourceName': source_name}))
        response_data = scene_item_id.datain
        return response_data['sceneItemId']

    def show_source(self, scene_name, source_name, visible=True):
        source_id = self.get_source_id(scene_name, source_name)
        self.ws.call(requests.SetSceneItemEnabled(
            **{'sceneName': scene_name, "sceneItemId": source_id, "sceneItemEnabled": visible}))

    def mute_input(self, source_name, is_muted=True):
        self.ws.call(requests.SetInputMute(**{'inputName': source_name, 'inputMuted': is_muted}))

    def get_record_status(self, variable=None):
        if variable is None:
            return self.ws.call(requests.GetRecordStatus())
        return self.ws.call(requests.GetRecordStatus()).datain[variable]

    def get_record_file_directory(self):
        print(self.ws.call(requests.GetProfileParameter(**{'parameterCategory': 'AdvancedOutput',
                                                            'parameterName': 'FilePath'})).datain)
        record_file_directory = 'C:\\Users\\Filip\\PycharmProjects\\PilotFlask\\static\\video\\processed'
        self.app.config['PROCESSED_FILES_DIRECTORY'] = record_file_directory
        return record_file_directory

    def drop_replay(self, instant=False):
        self.ws.call(requests.SaveReplayBuffer())
        time.sleep(4)
        if instant:
            self.play_instant_replay()
        self.save_dropped_replay()

    def save_dropped_replay(self):
        action_data = self.app.config['ACTION_DATA']
        _file_name = f'{action_data['replay_file']}_C0.mkv'
        source_path = os.path.join('static', 'video', 'processed', f'replay stream.mkv')
        destination_path1 = os.path.join('static', 'video', 'replays', _file_name)
        destination_path2 = os.path.join('static', 'video', 'replays', 'arch', _file_name)
        copy_file(source_path, destination_path1)
        copy_file(source_path, destination_path2)

    # def prepare_instant_replay(self):
    #     source_path = os.path.join('static', 'video', 'processed', f'replay stream.mkv')
    #     destination_path = os.path.join('static', 'video', 'processed', f'replay stream.mkv')
    #     copy_file(source_path, destination_path)


    def save_replay(self, type_of_action, action_time=None):
        self._save_replay(type_of_action, action_time)

    def play_replay(self):
        self.show_scene('POWTÓRKA')
        self.mute_input('Replay')
        sleep(10)
        self.virtual_cameras_save_replay(automatic=True)
        self.show_scene('MECZ')

    def play_instant_replay(self, action_time=None):
        self.play_replay()
        self.show_source('MECZ', 'AKCJA_INFO')
        sleep(10)
        self.show_source('MECZ', 'AKCJA_INFO', visible=False)

    def _save_replay(self, type_of_action, action_time=None):
        with self.app.app_context():
            _file_name = f'{self.app.config['REPLAY_FILE_NAME_PREFIX']}_C0.mkv'
            source_path = os.path.join('static', 'video', 'processed', f'replay stream.mkv')
            destination_path1 = os.path.join('static', 'video', 'replays', _file_name)
            destination_path2 = os.path.join('static', 'video', 'replays', 'arch', _file_name)

            try:
                shutil.copy(source_path, destination_path1)
                shutil.copy(source_path, destination_path2)
                print(f"Plik 'replay stream.mkv' został skopiowany do obu folderów.")
            except FileNotFoundError:
                print(f"Plik 'replay stream.mkv' nie istnieje w folderze źródłowym.")
            except IOError as e:
                print(f"Błąd podczas kopiowania pliku: {e}")

    def _get_cam_nr(self):
        if self.port == '4446':
            return 'Cam1'
        elif self.port == '4447':
            return 'Cam2'
        else:
            return ''

    def get_type_of_action(self, param):
        if type(param) is None:
            return None
        elif type(param) is int:
            _action = MatchAction.query.filter_by(id=param).first()
            return _action.desc_polish
        return None

    def set_replay_file_name_prefix(self, type_of_action, action_time=None):
        with self.app.app_context():
            _type_of_action = self.get_type_of_action(type_of_action)
            _date = action_time
            if action_time is None:
                _date = datetime.now().strftime("%Y%m%d-%H%M%S")
            _match = Match.query.filter_by(actual=1).first()
            _result = f'{_match.score_a}-{_match.score_b}'
            self.app.config['REPLAY_FILE_NAME_PREFIX'] = f'{_date}___{_result}_{_type_of_action}'


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

    def start_stream_cascade(self):
        self.show_scene('PUSTA')
        sleep(1)
        self.start_stream()
        sleep(1)
        self.start_scene_cascade()

    def start_scene_cascade(self):
        self.show_source('Muzyka', 'muzyka2', visible=False)
        self.show_scene('KAMERA')
        self.show_source('Muzyka', 'muzyka')
        self.mute_input('muzyka', False)
        sleep(5)
        self.show_scene('START')
        sleep(5)
        self.mute_input('Komentator', False)
        self.mute_input('Komentator2', False)

    def stop_stream_cascade(self):
        self.mute_input('Komentator')
        self.mute_input('Komentator2')
        self.show_scene('Napisy-koncowe')
        sleep(10)
        self.stop_stream()

    def start_stream(self):
        self.ws.call(requests.StartStream())

    def stop_stream(self):
        self.ws.call(requests.StopStream())

    def get_stream_status(self):
        _status = self.ws.call(requests.GetStreamStatus()).datain
        return _status

    def show_match_scene(self):
        self.show_scene('MECZ')
        self.show_source('Muzyka', 'muzyka', False)
        self.show_source('Muzyka', 'muzyka2', False)
        self.mute_input('muzyka')
        self.mute_input('muzyka2')

    def show_half_time_scene(self):
        self.show_scene('PRZERWA')
        self.show_source('Muzyka', 'muzyka', False)
        self.show_source('Muzyka', 'muzyka2')
        self.mute_input('muzyka2', False)

    def start_replay_buffer(self):
        self.ws.call(requests.StartReplayBuffer())

    def stop_replay_buffer(self):
        self.ws.call(requests.StopReplayBuffer())

    def show_banner(self):
        self.show_source('Logo', 'Banner')
        sleep(25)
        self.show_source('Logo', 'Banner', visible=False)

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

    def toggle_filter_enable(self, source_name, filter_name):
        _status = self.get_filter_status(source_name, filter_name)
        if _status['filterEnabled']:
            self.ws.call(requests.SetSourceFilterEnabled(**{'sourceName': source_name,
                                                            'filterName': filter_name,
                                                            'filterEnabled': False}))
        else:
            self.ws.call(requests.SetSourceFilterEnabled(**{'sourceName': source_name,
                                                            'filterName': filter_name,
                                                            'filterEnabled': True}))

    def get_filter_status(self, source_name, filter_name):
        _status = self.ws.call(requests.GetSourceFilter(**{'sourceName': source_name,
                                                           'filterName': filter_name})).datain
        _status.update({'sourceName': source_name, 'filterName': filter_name})
        return _status

    def get_scene_item_list(self, scene_name):
        return self.ws.call(requests.GetSceneItemList(**{'sceneName': scene_name})).datain['sceneItems']

    def get_scene_item_id(self, scene_name, source_name):
        return self.ws.call(requests.GetSceneItemId(**{'sceneName': scene_name,
                                                       'sourceName': source_name})).datain['sceneItemId']

    def set_scene_item_index(self, scene_name, source_id, source_index):
        self.ws.call((requests.SetSceneItemIndex(**{'sceneName': scene_name,
                                                    'sceneItemId': source_id,
                                                    'sceneItemIndex': source_index})))
