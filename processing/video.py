from moviepy.editor import VideoFileClip
import os
import subprocess
import re


class VideoProcessor:
    def __init__(self, file):
        self.file = file
        os.makedirs("temp", exist_ok=True)
        self.video_path = f"temp/{os.path.basename(file.file_path)}"
        self.ffmpeg_path = os.environ.get("FFMPEG_PATH")

    async def get_video(self):
        await self.file.download_to_drive(custom_path=self.video_path)
        self.video_file_clip = VideoFileClip(self.video_path)

    def process_video(self, start_min=None, start_sec=None, crop_duration=None):
        width, height = self.video_file_clip.w, self.video_file_clip.h
        scale = 512 / max(width, height)
        new_width, new_height = int(width * scale), int(height * scale)

        # write temp video
        output_video_path = os.path.join(
            os.path.dirname(self.video_path),
            os.path.splitext(os.path.basename(self.video_path))[0] + ".webm",
        )
        if start_min:
            command = f"{self.ffmpeg_path} -i {self.video_path} -c:v libvpx-vp9 -ss 00:{start_min}:{start_sec}00 -t 00:00:0{crop_duration}00 -crf 40 -an -vf scale={new_width}:{new_height} -v quiet -y {output_video_path}"
        else:
            command = f"{self.ffmpeg_path} -i {self.video_path} -c:v libvpx-vp9 -crf 40 -an -vf scale={new_width}:{new_height} -v quiet -y {output_video_path}"
        subprocess.call(command, shell=True)
        video_bytes = open(output_video_path, "rb").read()
        os.remove(output_video_path)
        self.video_file_clip.close()
        os.remove(self.video_path)
        return video_bytes

    def get_duration(self):
        return self.video_file_clip.duration


def parse_crop(crop: str):
    pattern = r"\d{2}:\d{2}\.\d{1} \d{1}\.\d{1}"
    if not re.match(pattern, crop):
        return None, None, None
    start_min = crop[:2]
    start_sec = crop[3:7]
    crop_duration = "2.9" if crop[8:] == "3.0" else crop[8:]
    if (
        int(start_min) >= 60
        or float(start_sec) >= 60
        or float(crop_duration) > 3
        or float(crop_duration) <= 0
    ):
        # check out of bounds
        return None, None, None
    return start_min, start_sec, crop_duration
