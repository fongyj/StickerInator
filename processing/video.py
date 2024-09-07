import asyncio
import os
import re

from imageio_ffmpeg._utils import get_ffmpeg_exe
from moviepy.editor import VideoFileClip


class VideoProcessor:
    def __init__(self, file, remove_bg):
        self.file = file
        self.remove_bg = remove_bg
        os.makedirs("temp", exist_ok=True)
        self.video_path = f"temp/{os.path.basename(file.file_path)}"
        self.ffmpeg_path = get_ffmpeg_exe()
        self.download_task = None
        self.downloaded = False

    def get_video(self):
        self.download_task = asyncio.create_task(self._download_video())

    async def get_duration(self):
        if not self.downloaded:
            await self.download_task
        self.downloaded = True
        return self.duration

    def process_video(self, start_min=None, start_sec=None, crop_duration=None, speed=False):
        return asyncio.create_task(self._process(start_min, start_sec, crop_duration, speed))
    
    def parse_crop(self, crop: str):
        if crop == "first":
            crop = "00:00.0 3.0"
        elif crop == "middle":
            start_min = int(((self.duration - 3) / 2) // 60)
            start_sec = round(((self.duration - 3) / 2) % 60, 1)
            crop = "{:02}:{:0>4.1f} 3.0".format(start_min, start_sec)
        elif crop == "last":
            start_min = int(((self.duration - 3)) // 60)
            start_sec = round(((self.duration - 3)) % 60, 1)
            crop = "{:02}:{:0>4.1f} 3.0".format(start_min, start_sec)
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
    
    async def _download_video(self):
        await self.file.download_to_drive(custom_path=self.video_path)
        video_file_clip = VideoFileClip(self.video_path)
        self.width, self.height, self.duration = (
            video_file_clip.w,
            video_file_clip.h,
            video_file_clip.duration,
        )
        video_file_clip.close()
        
    async def _process(self, start_min, start_sec, crop_duration, speed):
        if not self.downloaded:
            await self.download_task
        self.downloaded = True

        scale = 512 / max(self.width, self.height)
        new_width, new_height = int(self.width * scale), int(self.height * scale)

        # write temp video
        output_video_path = os.path.join(
            os.path.dirname(self.video_path),
            os.path.splitext(os.path.basename(self.video_path))[0] + "_processed.webm",
        )

        args = ""
        # speed up
        if speed:
            args += f"-itsscale {2.9 / self.duration} "
        args += f"-i {self.video_path} "
        # remove background
        if self.remove_bg:
            args += f"-loop 1 -i processing/mask/mask.png -filter_complex [0:v]scale={new_width}:{new_height}[resized],[resized][1:v]alphamerge "
        else:
            args += f"-vf scale={new_width}:{new_height} "
        # set format, quality, remove audio
        args += "-c:v libvpx-vp9 -crf 40 -an -y "
        # cropping
        if start_min:
            args += f"-ss 00:{start_min}:{start_sec}00 -t 00:00:0{crop_duration}00 "
        # append output path
        args += f"{output_video_path}"
        args = args.split(" ")

        process = await asyncio.create_subprocess_exec(self.ffmpeg_path, *args)
        await process.wait()
        video_bytes = open(output_video_path, "rb").read()
        os.remove(output_video_path)
        os.remove(self.video_path)
        return video_bytes
