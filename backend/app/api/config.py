from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/config", tags=["config"])

# 支持的配置项
CONFIG_KEYS = {
    "llm_provider": "LLM 提供商 (openai, anthropic, deepseek)",
    "llm_model": "LLM 模型名称",
    "llm_api_key": "LLM API Key",
    "llm_base_url": "LLM Base URL (可选，用于自定义端点)",
    "llm_temperature": "Temperature (0-1)",
    "llm_max_tokens": "Max Tokens",
}


def get_or_create_config(db: Session, key: str, default_value: str = "") -> models.SystemConfig:
    """获取或创建配置项"""
    config = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
    if not config:
        config = models.SystemConfig(
            key=key,
            value=default_value,
            description=CONFIG_KEYS.get(key)
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("/llm", response_model=schemas.LLMConfigResponse)
def get_llm_config(db: Session = Depends(get_db)):
    """获取当前 LLM 配置（不包含 API Key）"""
    provider = get_or_create_config(db, "llm_provider", settings.default_llm_provider).value
    model = get_or_create_config(db, "llm_model", settings.default_llm_model).value
    base_url = get_or_create_config(db, "llm_base_url", settings.default_llm_base_url or "").value
    temperature = float(get_or_create_config(db, "llm_temperature", "0.7").value)
    max_tokens = int(get_or_create_config(db, "llm_max_tokens", "4000").value)

    return schemas.LLMConfigResponse(
        provider=provider,
        model=model,
        base_url=base_url if base_url else None,
        temperature=temperature,
        max_tokens=max_tokens
    )


@router.post("/llm")
def update_llm_config(config: schemas.LLMConfig, db: Session = Depends(get_db)):
    """更新 LLM 配置"""
    # 更新各个配置项
    get_or_create_config(db, "llm_provider", config.provider).value = config.provider
    get_or_create_config(db, "llm_model", config.model).value = config.model
    get_or_create_config(db, "llm_api_key", config.api_key).value = config.api_key
    get_or_create_config(db, "llm_base_url", config.base_url or "").value = config.base_url or ""
    get_or_create_config(db, "llm_temperature", str(config.temperature)).value = str(config.temperature)
    get_or_create_config(db, "llm_max_tokens", str(config.max_tokens)).value = str(config.max_tokens)

    db.commit()
    return {"status": "ok", "message": "LLM configuration updated"}


@router.get("/llm/status")
def check_llm_config_status(db: Session = Depends(get_db)):
    """检查 LLM 配置状态（是否已配置 API Key）"""
    api_key_config = db.query(models.SystemConfig).filter(
        models.SystemConfig.key == "llm_api_key"
    ).first()

    has_api_key = api_key_config is not None and len(api_key_config.value) > 0

    return {
        "configured": has_api_key,
        "provider": get_or_create_config(db, "llm_provider", settings.default_llm_provider).value,
        "model": get_or_create_config(db, "llm_model", settings.default_llm_model).value
    }


@router.get("/all")
def get_all_configs(db: Session = Depends(get_db)):
    """获取所有配置（不含敏感信息）"""
    configs = db.query(models.SystemConfig).all()
    result = []
    for c in configs:
        # API Key 部分隐藏
        value = c.value
        if "api_key" in c.key and value:
            value = value[:8] + "****" + value[-4:] if len(value) > 12 else "****"
        result.append({
            "key": c.key,
            "value": value,
            "description": c.description,
            "updated_at": c.updated_at
        })
    return result
