from __future__ import annotations

from typing import Any

from airflow.models import BaseOperator
from airflow.providers.elevenlabs.hooks.elevenlabs import ElevenLabsHook


class ElevenLabsTextToSpeechOperator(BaseOperator):
    """
    Simple operator that generates audio from text and writes it to a file.
    """

    template_fields = ("text", "output_path", "voice_id", "model_id", "output_format")

    def __init__(
        self,
        *,
        text: str,
        output_path: str,
        elevenlabs_conn_id: str = "elevenlabs_default",
        voice_id: str | None = None,
        model_id: str | None = None,
        output_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.output_path = output_path
        self.elevenlabs_conn_id = elevenlabs_conn_id
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = output_format

    def execute(self, context: dict) -> str:
        hook = ElevenLabsHook(elevenlabs_conn_id=self.elevenlabs_conn_id)

        audio = hook.text_to_speech(
            text=self.text,
            voice_id=self.voice_id,
            model_id=self.model_id,
            output_format=self.output_format,
        )

        return audio
