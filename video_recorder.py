import cv2
import time
import socketio
from cv2_enumerate_cameras import enumerate_cameras
from collections import deque
import os
import shutil



class CameraIdxFinder:
    @staticmethod
    def get_camera_idx(camera_name):
        for camera_info in enumerate_cameras(cv2.CAP_DSHOW):
            if camera_info.name == camera_name:
                return camera_info.index
        return 0


class AdditionalVirtualCameras:
    @staticmethod
    def get_additional_virtual_cameras():
        additional_virtual_cameras = []
        for virtual_camera in enumerate_cameras(cv2.CAP_DSHOW):
            print(virtual_camera.name)
            if virtual_camera.name.startswith('OBS-Camera'):
                additional_virtual_cameras.append(virtual_camera)
        return additional_virtual_cameras


class VideoRecorder:
    def __init__(self, app, camera_idx, camera_prefix, camera_name):
        self.app = app
        self.socketio = self.app.config['SOCKETIO']
        self.sio = socketio.Client()
        self.camera_name = camera_name
        self.camera_prefix = camera_prefix
        self.frame_buffer = deque(maxlen=300)
        self.frame_buffer_copy = None
        self.buffer_duration = 10  # last 10 seconds
        self.capture = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.is_recording = False
        self.target_fps = 100
        self.frame_interval = 1/self.target_fps

        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # out = cv2.VideoWriter(f'{self.camera_prefix}replay.mkv', fourcc, 30.0, (1920, 1080))

    def record_video(self):
        print('record_video()')
        with self.app.app_context():
            self.is_recording = True
            prev_time = time.time()
            while self.app.config['OBS_REPLAY_BUFFER_STATUS']:
            # while self.app.config['CAMERAS_RECORDING_STATUS'] and len(self.frame_buffer) <= 2 * self.buffer_duration * int(self.capture.get(cv2.CAP_PROP_FPS)):
                ret, frame = self.capture.read()
                if not ret:
                    break
                current_time = time.time()
                elapsed_time = current_time - prev_time
                if elapsed_time >= self.frame_interval:
                    self.frame_buffer.append(frame)
                    # if len(self.frame_buffer) > self.buffer_duration * self.target_fps:
                    # if len(self.frame_buffer) > self.buffer_duration * int(self.capture.get(cv2.CAP_PROP_FPS)):
                    #     old_frames = len(self.frame_buffer) - self.buffer_duration * int(self.capture.get(cv2.CAP_PROP_FPS))
                    #     del self.frame_buffer[:old_frames]
                    # if self.app.config['OBS_DROP_REPLAY']:
                    #     print('yeah')
                    #     self.frame_buffer_copy = self.frame_buffer
                    #     print(self.app.config['CAMERAS'])
                    #     self.socketio.start_background_task(self.app.config['CAMERAS'][self.camera_name.upper()].save_replay)
                    #     time.sleep(1)
                    #     self.app.config['OBS_DROP_REPLAY'] = False
                        # self.save_replay()
                    prev_time = current_time

                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     save_replay_thread = threading.Thread(target=self.save_replay)
                #     save_replay_thread.start()

    def save_replay(self):
        with self.app.app_context():
            print('save_replay()')
            source_path = os.path.join('static', 'video', 'processed', f'{self.camera_prefix}_replay.mkv')
            self.frame_buffer_copy = list(self.frame_buffer)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(source_path, fourcc, 30,
                                  (self.frame_buffer_copy[0].shape[1], self.frame_buffer_copy[0].shape[0]))
            for frame in self.frame_buffer_copy:
                out.write(frame)
            out.release()

            _replay_file_name_prefix = self.app.config['REPLAY_FILE_NAME_PREFIX']
            _file_name = f'{_replay_file_name_prefix}_{self.camera_prefix}.mkv'
            destination_path1 = os.path.join('static', 'video', 'replays', _file_name)
            destination_path2 = os.path.join('static', 'video', 'replays', 'arch', _file_name)

            try:
                shutil.copy(source_path, destination_path1)
                shutil.copy(destination_path1, destination_path2)
                print(f"Plik '{_file_name}' został zapisany w obu folderach.")
            except FileNotFoundError:
                print(f"Plik '{_file_name}' nie istnieje w folderze źródłowym.")
            except IOError as e:
                print(f"Błąd podczas kopiowania pliku '{_file_name}': {e}")




# class VideoRecorder:
#     def __init__(self, camera_idx, camera_prefix):
#         self.camera_prefix = camera_prefix
#         # self.camera_name = camera_name
#         self.camera_idx = camera_idx
#         self.capture = cv2.VideoCapture(self.camera_idx, cv2.CAP_DSHOW)
#         # self.capture = cv2.VideoCapture(0)
#         self.is_recording = False
#         self.video_writer = None
#         self.replay_writer = None
#         self.frame_buffer = []
#         self.audio_frames = []
#         self.buffer_lock = threading.Lock()
#         self.frame_rate = 30  # assuming 30 FPS
#         self.buffer_duration = 10  # last 10 seconds
#         self.buffer_size = self.frame_rate * self.buffer_duration
#
#         # Initialize PyAudio
#         self.audio_format = pyaudio.paInt16
#         self.channels = 1
#         self.rate = 44100
#         self.chunk = 1024
#         self.audio = pyaudio.PyAudio()
#         self.audio_stream = None
#
#     def record_video(self):
#         output_video = f'{self.camera_prefix}_stream.mp4'
#         output_audio = f'{self.camera_prefix}_stream.wav'
#         print('record_video')
#         if not self.capture.isOpened():
#             raise ValueError("Camera could not be opened.")
#
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         self.video_writer = cv2.VideoWriter(output_video, fourcc, self.frame_rate,
#                                             (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
#                                              int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))
#
#         self.is_recording = True
#
#         # Start audio recording
#         self.audio_stream = self.audio.open(format=self.audio_format,
#                                             channels=self.channels,
#                                             rate=self.rate,
#                                             input=True,
#                                             frames_per_buffer=self.chunk)
#
#
#         video_thread = threading.Thread(target=self._record_video)
#         audio_thread = threading.Thread(target=self._record_audio, args=(output_audio,))
#
#         video_thread.start()
#         audio_thread.start()
#
#         # video_thread.join()
#         # audio_thread.join()
#         print('po: thread.join()')
#
#
#     def _record_video(self):
#         print('_record_video')
#         while self.is_recording:
#             print('1')
#             ret, frame = self.capture.read()
#             print('ddddd', frame)
#             if not ret:
#                 print('3')
#                 break
#             print('4')
#             self.video_writer.write(frame)
#             with self.buffer_lock:
#
#                 self.frame_buffer.append(frame)
#                 if len(self.frame_buffer) > self.buffer_size:
#                     self.frame_buffer.pop(0)
#             time.sleep(1 / self.frame_rate)
#
#         self.capture.release()
#         self.video_writer.release()
#
#     def _record_audio(self, output_audio):
#         print('_record_audio')
#         while self.is_recording:
#             data = self.audio_stream.read(self.chunk)
#             self.audio_frames.append(data)
#
#         self.audio_stream.stop_stream()
#         self.audio_stream.close()
#
#         wf = wave.open(output_audio, 'wb')
#         wf.setnchannels(self.channels)
#         wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
#         wf.setframerate(self.rate)
#         wf.writeframes(b''.join(self.audio_frames))
#         wf.close()
#
#     def save_replay(self):
#         replay_video = f'{self.camera_prefix}_replay.mp4'
#         replay_audio = f'{self.camera_prefix}_replay.wav'
#         print('save_replay')
#         with self.buffer_lock:
#             frames_to_save = self.frame_buffer.copy()
#
#         if not frames_to_save:
#             raise ValueError("No frames in buffer to save.")
#
#         height, width, layers = frames_to_save[0].shape
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         self.replay_writer = cv2.VideoWriter(replay_video, fourcc, self.frame_rate, (width, height))
#
#         for frame in frames_to_save:
#             self.replay_writer.write(frame)
#
#         self.replay_writer.release()
#
#         # Save last 10 seconds of audio
#         audio_frames_to_save = self.audio_frames[-self.buffer_size:]
#         wf = wave.open(replay_audio, 'wb')
#         wf.setnchannels(self.channels)
#         wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
#         wf.setframerate(self.rate)
#         wf.writeframes(b''.join(audio_frames_to_save))
#         wf.close()
#
#     def stop_recording(self):
#         self.is_recording = False
#
#     def merge_audio_video(self):
#         # try:
#         video_file = f'{self.camera_prefix}_stream.mp4'
#         audio_file = f'{self.camera_prefix}_stream.wav'
#         output_file = f'{self.camera_prefix}_merged.mp4'
#         input_video = ffmpeg.input(video_file)
#         input_audio = ffmpeg.input(audio_file)
#         ffmpeg.output(input_video,
#                       input_audio,
#                           output_file, vcodec='libx264', acodec='aac', strict='experimental').run()
#         # except ffmpeg.Error as e:
#         #     print("ffmpeg error:", e.stderr.decode('utf8'))
#         #     raise e
#
# # Przykład użycia:
# # recorder = VideoRecorder("camera0")
# # recorder.record_video()
# # time.sleep(30)  # Record for 30 seconds
# # recorder.stop_recording()
# # recorder.save_replay()
# # recorder.merge_audio_video("replay.ts", "replay.wav", "replay.mkv")
