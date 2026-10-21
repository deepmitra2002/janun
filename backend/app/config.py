from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://janun:janun@localhost:5432/janun'
    environment: str = 'development'
    allowed_origins: str = 'http://localhost:3000,http://127.0.0.1:3000'
    openai_api_key: str = ''
    llm_model: str = ''
    embedding_model: str = ''
    embedding_dimensions: int = 1536
    retrieval_limit: int = 6
    session_hours: int = 8
    source_hosts: str = 'bangladesh.gov.bd,www.bangladesh.gov.bd,www.mygov.bd,mygov.bd,www.epassport.gov.bd,epassport.gov.bd,bdris.gov.bd'
    max_source_bytes: int = 5_000_000
    @property
    def origins(self): return [x.strip() for x in self.allowed_origins.split(',') if x.strip()]
    @property
    def hosts(self): return {x.strip() for x in self.source_hosts.split(',') if x.strip()}

settings = Settings()
