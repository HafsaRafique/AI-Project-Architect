from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    
    app_name: str = "PixelRAG"
    environment: str = Field(default="development")

    # Sec
    secret_key: str = Field(default="n/a")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


    database_url: str = Field(default="sqlite:///./pixelrag.db")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_vision_model: str = Field(default="qwen2.5vl:7b")
    ollama_embed_model: str = Field(default="nomic-embed-text")
    ollama_text_model: str = Field(default="qwen2.5:7b")

    chroma_persist_dir: str = Field(default="./chroma_data")

    # 
    cors_origins: str = Field(default="*")

   
    rate_limit_per_minute: int = Field(default=30)

    # Upload limits
    max_image_size_mb: int = Field(default=8)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
