from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    gemini_api_key: str
    embedding_model: str = "models/embedding-001"
    gemini_model: str = "gemini-1.5-flash"
    faiss_index_path: str = "faiss_index"
    chunk_size: int = 30  # lines per chunk
    top_k: int = 5        # chunks to retrieve per query


settings = Settings()
