"""
配置管理系统

使用pydantic进行配置验证和管理
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any


from pydantic import field_validator, ValidationInfo # for pydantic v2 to replace validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # LLM基础配置
    llm_provider: str = "openrouter"
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout: int = 30

    # OpenRouter配置（备用）
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Anthropic配置
    anthropic_auth_token: Optional[str] = None
    anthropic_base_url: Optional[str] = None


    # # 向后兼容的LLM配置 (临时保留)
    # @property
    # def llm_model(self) -> str:
    #     """向后兼容：返回默认的parser模型"""
    #     return self.parser_llm_model

    # 分层LLM配置
    parser_llm_model: str = "anthropic/claude-3.5-sonnet"
    parser_llm_temperature: float = 0.1
    parser_llm_max_tokens: int = 2048

    classifier_llm_model: str = "anthropic/claude-3.5-sonnet"
    classifier_llm_temperature: float = 0.05
    classifier_llm_max_tokens: int = 1024

    # Prompt配置
    parser_prompt_version: str = "v1"
    classifier_prompt_version: str = "v1"

    # 向量数据库配置
    entity_embedding_model: str = "BAAI/bge-m3"
    property_embedding_model: str = "BAAI/bge-m3"
    vector_dim: int = 1024
    semantic_matching_threshold: float = 0.7

    # 外部服务配置
    ifc_entity_pset_api_url: Optional[
        str
    ] = "http://36.103.199.7:5000/api/property/entity-psets"


    @field_validator("llm_api_key", mode="before")
    def validate_api_key(cls, v, info: ValidationInfo):
        """Validate API key"""
        provider = info.data.get("llm_provider")
        if provider == "openrouter" and not v:
            v = os.getenv("OPENROUTER_API_KEY")  # Try to read from environment variable
            if not v:
                raise ValueError("OpenRouter API key is required")
        elif provider == "anthropic" and not v:
            v = info.data.get("anthropic_auth_token") or os.getenv("ANTHROPIC_AUTH_TOKEN")
            if not v:
                raise ValueError("Anthropic auth token is required")
        return v


    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env-pipeline",  # specify config file
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore extra fields
    )


    def get_parser_llm_config(self) -> Dict[str, Any]:
        """获取结构化解析器LLM配置"""
        # 原始实现（保留作为参考）
        # return {
        #     "provider": self.llm_provider,
        #     "model": self.parser_llm_model,
        #     "api_key": self.llm_api_key,
        #     "base_url": self.llm_base_url,
        #     "temperature": self.parser_llm_temperature,
        #     "max_tokens": self.parser_llm_max_tokens,
        #     "timeout": self.llm_timeout,
        # }

        # 新实现：支持多provider
        config = {
            "provider": self.llm_provider,
            "model": self.parser_llm_model,
            "temperature": self.parser_llm_temperature,
            "max_tokens": self.parser_llm_max_tokens,
            "timeout": self.llm_timeout,
        }

        if self.llm_provider == "anthropic":
            config["api_key"] = self.anthropic_auth_token or self.llm_api_key
            config["base_url"] = self.anthropic_base_url or self.llm_base_url
        else:
            config["api_key"] = self.llm_api_key
            config["base_url"] = self.llm_base_url

        return config

    def get_classifier_llm_config(self) -> Dict[str, Any]:
        """获取Facet分类器LLM配置"""
        # 原始实现（保留作为参考）
        # return {
        #     "provider": self.llm_provider,
        #     "model": self.classifier_llm_model,
        #     "api_key": self.llm_api_key,
        #     "base_url": self.llm_base_url,
        #     "temperature": self.classifier_llm_temperature,
        #     "max_tokens": self.classifier_llm_max_tokens,
        #     "timeout": self.llm_timeout,
        # }

        # 新实现：支持多provider
        config = {
            "provider": self.llm_provider,
            "model": self.classifier_llm_model,
            "temperature": self.classifier_llm_temperature,
            "max_tokens": self.classifier_llm_max_tokens,
            "timeout": self.llm_timeout,
        }

        if self.llm_provider == "anthropic":
            config["api_key"] = self.anthropic_auth_token or self.llm_api_key
            config["base_url"] = self.anthropic_base_url or self.llm_base_url
        else:
            config["api_key"] = self.llm_api_key
            config["base_url"] = self.llm_base_url

        return config



# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例（用于依赖注入）"""
    return settings
