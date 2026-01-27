"""Text-to-speech service with gTTS

This module handles Korean text-to-speech generation using gTTS (Google Text-to-Speech)
and implements file-based caching to reduce API calls.

Features:
- Generate Korean audio with appropriate speed (slow for beginners)
- Cache audio files using MD5 hash filenames
- Handle gTTS errors with retry logic
- Serve cached audio files efficiently
"""
import os
import hashlib
import time
from pathlib import Path
from typing import Optional
from gtts import gTTS
from gtts.tts import gTTSError
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-speech service with caching"""

    def __init__(self, cache_dir: str = "data/audio_cache"):
        """Initialize TTS service

        Args:
            cache_dir: Directory to store cached audio files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TTS Service initialized with cache dir: {self.cache_dir}")

    def _generate_cache_key(self, text: str, lang: str, slow: bool) -> str:
        """Generate MD5 hash for caching

        Args:
            text: Text to speak
            lang: Language code
            slow: Whether to use slow speed

        Returns:
            MD5 hash string
        """
        cache_string = f"{text}_{lang}_{slow}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path for cached audio file

        Args:
            cache_key: MD5 hash cache key

        Returns:
            Path to audio file
        """
        return self.cache_dir / f"{cache_key}.mp3"

    def generate_audio(
        self, text: str, lang: str = "ko", slow: bool = False, max_retries: int = 3
    ) -> Optional[str]:
        """Generate audio file for text using gTTS

        Args:
            text: Text to convert to speech
            lang: Language code (default 'ko' for Korean)
            slow: Whether to use slow speech rate (for beginners)
            max_retries: Maximum number of retry attempts

        Returns:
            Filename of audio file (just the hash.mp3, not full path) or None if failed
        """
        # Generate cache key
        cache_key = self._generate_cache_key(text, lang, slow)
        cache_path = self._get_cache_path(cache_key)

        # Return cached file if exists
        if cache_path.exists():
            logger.debug(f"Cache hit for: {text[:30]}...")
            return f"{cache_key}.mp3"

        # Generate new audio file with retry logic
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Generating TTS for: {text[:30]}... (attempt {attempt + 1}/{max_retries})"
                )

                # Create gTTS object and save
                tts = gTTS(text=text, lang=lang, slow=slow)
                tts.save(str(cache_path))

                logger.info(f"TTS generated successfully: {cache_key}.mp3")
                return f"{cache_key}.mp3"

            except gTTSError as e:
                logger.error(f"gTTS error on attempt {attempt + 1}: {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff: wait 1s, 2s, 4s
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to generate TTS after {max_retries} attempts")
                    return None

            except Exception as e:
                logger.error(f"Unexpected error generating TTS: {e}", exc_info=True)
                return None

        return None

    def get_audio_url(self, filename: str) -> str:
        """Get URL for audio file

        Args:
            filename: Audio filename (e.g., 'abc123.mp3')

        Returns:
            URL path for accessing audio file
        """
        return f"/api/audio/{filename}"

    def audio_exists(self, filename: str) -> bool:
        """Check if audio file exists in cache

        Args:
            filename: Audio filename

        Returns:
            True if file exists, False otherwise
        """
        return (self.cache_dir / filename).exists()

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear audio cache

        Args:
            older_than_days: Only delete files older than this many days.
                           If None, deletes all cache files.
        """
        deleted_count = 0

        for audio_file in self.cache_dir.glob("*.mp3"):
            try:
                if older_than_days is not None:
                    # Check file age
                    file_age_days = (time.time() - audio_file.stat().st_mtime) / 86400
                    if file_age_days < older_than_days:
                        continue

                audio_file.unlink()
                deleted_count += 1

            except Exception as e:
                logger.error(f"Error deleting {audio_file}: {e}")

        logger.info(f"Cleared {deleted_count} audio files from cache")
        return deleted_count

    def get_cache_size(self) -> dict:
        """Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        files = list(self.cache_dir.glob("*.mp3"))
        total_size = sum(f.stat().st_size for f in files)

        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


# Global TTS service instance
_tts_service: Optional[TTSService] = None


def get_tts_service(cache_dir: str = "data/audio_cache") -> TTSService:
    """Get or create global TTS service instance

    Args:
        cache_dir: Directory for audio cache

    Returns:
        TTSService instance
    """
    global _tts_service

    if _tts_service is None:
        _tts_service = TTSService(cache_dir)

    return _tts_service
