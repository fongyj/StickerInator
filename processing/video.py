import cv2
import os
import subprocess
import re


class VideoProcessor:
    def __init__(self, file):
        self.file = file
        os.makedirs("temp", exist_ok=True)
        self.video_path = f"temp/{os.path.basename(file.file_path)}"

    async def get_video(self):
        await self.file.download_to_drive(custom_path=self.video_path)
        self.cap = cv2.VideoCapture(self.video_path)

    def process_video(self, start_min=None, start_sec=None, crop_duration=None):
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        scale = 512 / max(width, height)
        new_width, new_height = int(width * scale), int(height * scale)

        # write temp video
        output_video_path = os.path.join(
            os.path.dirname(self.video_path),
            os.path.splitext(os.path.basename(self.video_path))[0] + ".webm",
        )
        fourcc = cv2.VideoWriter.fourcc(*"vp90")
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (new_width, new_height))
        if start_min:
            start_frame = int((start_min * 60 + start_sec) * fps)
            end_frame = start_frame + int(crop_duration * fps)
        else:
            start_frame = 0
            end_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_idx = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            if frame_idx >= start_frame or frame_idx <= end_frame:
                frame = cv2.resize(frame, (new_width, new_height))
                out.write(frame)
            frame_idx += 1
        self.cap.release()
        out.release()
        video_bytes = open(output_video_path, "rb").read()
        os.remove(output_video_path)
        os.remove(self.video_path)
        return video_bytes

    def get_duration(self):
        frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return round(frames / fps, 3)


def parse_crop(crop: str, duration):
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
        or start_time >= float(duration)
    ):
        # check out of bounds
        return None, None, None
    return start_min, start_sec, crop_duration
