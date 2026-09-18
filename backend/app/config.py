from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    fetch_timeout: float = 15.0
    fetch_max_bytes: int = 5 * 1024 * 1024
    fetch_max_redirects: int = 5
    user_agent: str = "SiteScopia/0.1"
    rdap_timeout: float = 10.0
    domain_lookup_enabled: bool = True

    cors_origins: list[str] = ["https://sitescopia.online"]
    max_stored_jobs: int = 200
    api_docs_enabled: bool = False
    analysis_rate_limit: int = 10
    rate_limit_window: int = 60
    rate_limit_max_keys: int = 10000
    max_active_analyses: int = 4
    trust_proxy_headers: bool = False


    slow_response_ms: int = 1500
    very_slow_response_ms: int = 3000
    max_html_bytes: int = 150 * 1024
    max_external_scripts: int = 15


settings = Settings()
