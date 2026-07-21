from .text2video import run as generate_video


class VideoEngine:
    def generate(self, prompt_text: str) -> str:
        return generate_video(prompt_text)


video_engine = VideoEngine()
