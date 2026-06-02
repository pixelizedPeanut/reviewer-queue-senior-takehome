import os


class Settings:
    """
    Application configurations managed dynamically via environment variables.
     Defaults to 'development' mode for safe, local execution safety out-of-the-box.
    """

    ENV: str = os.getenv("APP_ENV", "development")

    # Simple check to see if we are currently running a local developer loop
    @property
    def is_development(self) -> bool:
        return self.ENV.lower() in ("development", "dev", "local")


settings = Settings()
