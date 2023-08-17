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
        output_video_path = os.path.join(os.path.dirname(self.video_path), os.path.splitext(os.path.basename(self.video_path))[0] + ".webm")
        if start_min:
            command = f"{FFMPEG_PATH} -i {self.video_path} -c:v libvpx-vp9 -ss 00:{start_min}:{start_sec} -t 00:00:0{crop_duration} -crf 40 -an -vf scale={new_width}:{new_height} -v quiet -y {output_video_path}"
        else:
            command = f"{FFMPEG_PATH} -i {self.video_path} -c:v libvpx-vp9 -crf 20 -an -vf scale={new_width}:{new_height} -v quiet -y {output_video_path}"
        subprocess.call(command, shell=True)
        video_bytes = open(output_video_path, "rb").read()
        os.remove(output_video_path)
        self.video_file_clip.close()
        os.remove(self.video_path)
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