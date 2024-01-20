from moviepy.editor import VideoFileClip
import os
import subprocess
import re
from imageio_ffmpeg._utils import get_ffmpeg_exe


class VideoProcessor:
    def __init__(self, file, remove_bg):
        self.file = file
        self.remove_bg = remove_bg
        os.makedirs("temp", exist_ok=True)
        self.video_path = f"temp/{os.path.basename(file.file_path)}"
        self.ffmpeg_path = get_ffmpeg_exe()

    async def get_video(self):
        await self.file.download_to_drive(custom_path=self.video_path)
        video_file_clip = VideoFileClip(self.video_path)
        self.width, self.height, self.duration = (
            video_file_clip.w,
            video_file_clip.h,
            video_file_clip.duration,
        )
        video_file_clip.close()

    def process_video(self, start_min=None, start_sec=None, crop_duration=None):
        scale = 512 / max(self.width, self.height)
        new_width, new_height = int(self.width * scale), int(self.height * scale)

        # write temp video
        output_video_path = os.path.join(
            os.path.dirname(self.video_path),
            os.path.splitext(os.path.basename(self.video_path))[0] + "_processed.webm",
        )
        if self.remove_bg:
            command = f"{self.ffmpeg_path} -i {self.video_path} -loop 1 -i processing/mask/mask.png -filter_complex [0:v][1:v]alphamerge[out],[out]scale={new_width}:{new_height} -c:v libvpx-vp9 -crf 40 -an -v quiet -y"
        else:
            command = f"{self.ffmpeg_path} -i {self.video_path} -c:v libvpx-vp9 -crf 40 -an -vf scale={new_width}:{new_height} -v quiet -y"
        # append cropping
        if start_min:
            command += f" -ss 00:{start_min}:{start_sec}00 -t 00:00:0{crop_duration}00"
        # append output path
        command += f" {output_video_path}"
        subprocess.call(command, shell=True)
        video_bytes = open(output_video_path, "rb").read()
        os.remove(output_video_path)
        os.remove(self.video_path)
        return video_bytes

    def parse_crop(self, crop: str):
        pattern = r"\d{2}:\d{2}\.\d{1} \d{1}\.\d{1}"
        if not re.match(pattern, crop):
            return None, None, None
        start_min = crop[:2]
        start_sec = crop[3:7]
        crop_duration = "2.9" if crop[8:] == "3.0" else crop[8:]
        start_time = (int(start_min) * 60) + float(start_sec)
        if (
            int(start_min) >= 60
            or float(start_sec) >= 60
            or float(crop_duration) > 3
            or float(crop_duration) <= 0
            or start_time >= float(self.duration)
        ):
            # check out of bounds
            return None, None, None
        return start_min, start_sec, crop_duration
