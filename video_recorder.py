import cv2
import subprocess
import threading
import queue
import time
import os
import msvcrt
from cv2_enumerate_cameras import enumerate_cameras
import subprocess
import time
import os
import ffmpeg
import shutil
import threading
from utils.file_utils import get_video_duration


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
        self.camera_idx = camera_idx
        self.camera_prefix = camera_prefix
        self.camera_name = camera_name
        self.replays_dir = self.app.config['REPLAYS_FILES_DIRECTORY']
        self.segments_dir = os.path.join(self.replays_dir,
                                         self.app.config["MATCH_IDENTIFIER"])
        self.resolution = '1920x1080'
        self.fps = 30
        self.cap = None
        self.frame_queue = []
        self.segment_number = 0
        self.segment_duration = 30
        self.video_files_list = os.path.join(self.segments_dir, f'{self.camera_prefix}_video_files_list.txt')
        self.temp_file = os.path.join(self.segments_dir, f'{self.camera_prefix}_temp.mp4')

        # Ensure the output directory exists
        os.makedirs(self.segments_dir, exist_ok=True)

    def record_video(self):
        idx = 0
        check_queue = threading.Thread(target=self.check_queue)
        check_queue.start()
        while self.app.config['OBS_RECORD_STATUS']:
            record_video = threading.Thread(target=self._record_subprocess, args=([
                os.path.join
                (self.replays_dir, self.app.config["MATCH_IDENTIFIER"],
                 f'{self.camera_prefix}_{self.app.config["MATCH_IDENTIFIER"]}_segment{str(idx).zfill(3)}.mp4')
            ]))
            record_video.start()
            record_video.join()
            # merge_videos = threading.Thread(target=self.merge_videos, args=(
            #     os.path.join
            #     (self.replays_dir,
            #      f'{self.camera_prefix}_{self.app.config["MATCH_IDENTIFIER"]}_segment{str(idx).zfill(3)}.mp4'), idx))
            # merge_videos.start()
            idx += 1
        check_queue.join()

    def _record_subprocess(self, temp_file):

        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-f', 'dshow',  # Use DirectShow for Windows, use 'v4l2' for Linux
            '-rtbufsize', '157286400',
            '-i', f'video={self.camera_name}',  # Device name, change to your camera name
            '-s', f'{self.resolution}',  # Resolution
            '-r', f'{self.fps}',  # Frame rate
            '-t', f'{self.segment_duration}',  # Duration of each segment
            '-c:v', 'libx264',  # Codec
            '-preset', 'ultrafast',  # Preset
            '-movflags', 'frag_keyframe+empty_moov',
            '-f', 'mpegts',
            temp_file  # Output temporary file
        ]
        subprocess.run(ffmpeg_command)
        self.frame_queue.append(temp_file)
        # process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = process.communicate()
        # if process.returncode != 0:
        #     print(f'Error: {stderr.decode()}')

    def check_queue(self):
        while self.app.config['OBS_RECORD_STATUS']:
            if len(self.frame_queue):
                input_video_path = self.frame_queue.pop()
                self.merge_videos(input_video_path)
            else:
                time.sleep(1)

    def merge_videos(self, input_video_path):
        output_video_path = (os.path.join
                             (self.replays_dir,
                              f'{self.camera_prefix}_{self.app.config["MATCH_IDENTIFIER"]}_output.mp4'))

        with open(self.video_files_list, 'w') as f:
            f.write('')
            f.write(f"file '{output_video_path}'\n")
            f.write(f"file '{input_video_path}'")

        if os.path.exists(output_video_path):
            ffmpeg_concat_command = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', self.video_files_list,
                '-c', 'copy', self.temp_file
            ]
            subprocess.run(ffmpeg_concat_command)
            # process = subprocess.Popen(ffmpeg_concat_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # stdout, stderr = process.communicate()
            # if process.returncode != 0:
            #     print(f'Error: {stderr.decode()}')
            os.remove(output_video_path)
            os.rename(self.temp_file, output_video_path)
        else:
            os.rename(input_video_path, output_video_path)

        self.app.config['VIDEO_LENGTH'][self.camera_prefix] = get_video_duration(output_video_path)
