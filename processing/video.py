from moviepy.editor import VideoFileClip 
import tempfile
import os
import subprocess
import re

FFMPEG_PATH = r"ffmpeg\ffmpeg.exe" # can shift this to be a environment variable

class VideoProcessor:

    def __init__(self, file):
        self.file = file
        self.video_path = f"temp/{os.path.basename(file.file_path)}"

    async def get_video(self):
        await self.file.download_to_drive(custom_path=self.video_path)
        self.video_file_clip = VideoFileClip(self.video_path)

    def process_video(self, start_min=None, start_sec=None, crop_duration=None):
        width, height = self.video_file_clip.w, self.video_file_clip.h
        scale = 512 / max(width, height)
        new_width, new_height = int(width * scale), int(height * scale)

        # write temp video
        temp_file = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
        temp_file.close()
        if start_min:
            command = f"{FFMPEG_PATH} -i {self.video_path} -c:v libvpx-vp9 -ss 00:{start_min}:{start_sec} -t 00:00:0{crop_duration} -crf 40 -an -vf scale={new_width}:{new_height} -v quiet -y {temp_file.name}"
        else:
            command = f"{FFMPEG_PATH} -i {self.video_path} -c:v libvpx-vp9 -crf 20 -an -vf scale={new_width}:{new_height} -v quiet -y {temp_file.name}"
        subprocess.call(command, shell=True)
        video_bytes = open(temp_file.name, "rb").read()
        os.remove(temp_file.name)
        return video_bytes

    def get_duration(self):
        return self.video_file_clip.duration

def parse_crop(crop: str):
    pattern = r"\d{2}:\d{2}\.\d{3} \d{1}\.\d{3}"
    if not re.match(pattern, crop):
        return None, None, None
    start_min = crop[:2]
    start_sec = crop[3:9]
    crop_duration = crop[10:]
    if int(start_min) >= 60 or float(start_sec) >= 60 or float(crop_duration) > 3:
        return None, None, None
    return start_min, start_sec, crop_duration