from __future__ import annotations

from typing import Any

from airflow.hooks.base import BaseHook
from airflow.models.connection import Connection
from elevenlabs.client import ElevenLabs


class ElevenLabsHook(BaseHook):
    """
    Airflow hook for ElevenLabs based on the official elevenlabs Python SDK.
    """

    conn_name_attr = "elevenlabs_conn_id"
    default_conn_name = "elevenlabs_default"
    conn_type = "elevenlabs"
    hook_name = "ElevenLabs"

    def __init__(
        self, elevenlabs_conn_id: str = default_conn_name, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.elevenlabs_conn_id = elevenlabs_conn_id

    def get_airflow_connection(self) -> Connection:
        return self.get_connection(self.elevenlabs_conn_id)

    def get_config(self) -> dict[str, Any]:
        conn = self.get_airflow_connection()
        extra = conn.extra_dejson or {}

        base_url = (conn.host or "https://api.elevenlabs.io/v1/").rstrip("/")
        api_key = conn.password

        if not api_key:
            raise ValueError(
                f"Missing ElevenLabs API key in Airflow connection "
                f"'{self.elevenlabs_conn_id}'. Put it in the Password field."
            )

        return {
            "api_key": api_key,
            "base_url": base_url,
            "voice_id": extra.get("voice_id"),
            "model_id": extra.get("model_id", "eleven_multilingual_v2"),
            "output_format": extra.get("output_format", "mp3_44100_128"),
        }

    def get_conn(self) -> ElevenLabs:
        """
        Return an initialized ElevenLabs SDK client.
        """
        cfg = self.get_config()

        client_kwargs: dict[str, Any] = {"api_key": cfg["api_key"]}

        # Keep this guarded because SDK signatures may evolve.
        # If your installed SDK does not support base_url, remove this line.
        client_kwargs["base_url"] = cfg["base_url"]

        return ElevenLabs(api_key=cfg["api_key"])

    def text_to_speech(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str | None = None,
        output_format: str | None = None,
        voice_settings: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Convert text to speech and return audio bytes.
        """
        cfg = self.get_config()
        client = self.get_conn()

        resolved_voice_id = voice_id or cfg["voice_id"]
        resolved_model_id = model_id or cfg["model_id"]
        resolved_output_format = output_format or cfg["output_format"]

        if not resolved_voice_id:
            raise ValueError(
                "voice_id is required. Set it in Connection.extra or pass it explicitly."
            )

        audio_stream = client.text_to_speech.convert_with_timestamps(
            voice_id=resolved_voice_id,
            model_id=resolved_model_id,
            output_format=resolved_output_format,
            text=text,
            voice_settings=voice_settings,
        )

        return audio_stream

    @classmethod
    def get_connection_form_widgets(cls) -> dict[str, Any]:
        """
        Extra fields rendered in Admin -> Connections.
        Stored in Connection.extra JSON.
        """
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from wtforms import StringField

        return {
            "voice_id": StringField("Default Voice ID", widget=BS3TextFieldWidget()),
            "model_id": StringField("Default Model ID", widget=BS3TextFieldWidget()),
            "output_format": StringField(
                "Default Output Format", widget=BS3TextFieldWidget()
            ),
        }

    @classmethod
    def get_ui_field_behaviour(cls) -> dict[str, Any]:
        """
        Customize which built-in fields are shown and how they are labeled.
        """
        return {
            "hidden_fields": ["schema", "login", "port"],
            "relabeling": {
                "host": "Base URL",
                "password": "XI API Key",
            },
            "placeholders": {
                "host": "https://api.elevenlabs.io",
                "password": "Paste your ElevenLabs API key",
            },
        }

    @classmethod
    def test_connection(cls, conn: Connection) -> tuple[bool, str]:
        """
        Optional test shown in Airflow UI.
        """
        try:
            extra = conn.extra_dejson or {}
            api_key = conn.password
            if not api_key:
                return False, "Missing API key in Password field."

            client_kwargs: dict[str, Any] = {"api_key": api_key}
            client_kwargs["base_url"] = (
                conn.host or "https://api.elevenlabs.io"
            ).rstrip("/")

            client = ElevenLabs(**client_kwargs)

            # Lightweight auth check: list voices
            voices = client.voices.search()
            count = len(getattr(voices, "voices", []) or [])
            default_voice = extra.get("voice_id")
            message = f"Connected successfully. Voices available: {count}."
            if default_voice:
                message += f" Default voice_id configured: {default_voice}."
            return True, message
        except Exception as exc:
            return False, f"Connection test failed: {exc}"
