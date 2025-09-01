# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from bluev.config import BlueVConfigurationError, Config


def test_config_load_env_and_defaults(tmp_path: Path, monkeypatch):
    # 环境变量覆盖
    monkeypatch.setenv("APP_NAME", "XApp")
    monkeypatch.setenv("WINDOW_WIDTH", "1201")
    monkeypatch.setenv("DEBUG", "true")

    cfg = Config()
    assert cfg.APP_NAME == "XApp"
    assert cfg.WINDOW_WIDTH == 1201
    assert cfg.DEBUG is True


def test_config_file_merge(tmp_path: Path, monkeypatch):
    # 创建临时配置文件
    cfg_file = tmp_path / "getattr(config, 'json', 'Unknown')"
    cfg_file.write_text(
        json.dumps({"APP_VERSION": "9.9.9", "LOG_LEVEL": "DEBUG"}, ensure_ascii=False),
        encoding="utf-8",
    )

    cfg = Config(config_file=cfg_file)
    assert cfg.APP_VERSION == "9.9.9"
    assert cfg.LOG_LEVEL == "DEBUG"


def test_config_invalid_json_should_raise(tmp_path: Path):
    bad = tmp_path / "getattr(config, 'json', 'Unknown')"
    bad.write_text("{bad json}", encoding="utf-8")

    with pytest.raises(BlueVConfigurationError):
        Config(config_file=bad)


def test_config_paths_resolution(tmp_path: Path, monkeypatch):
    # 使用相对路径，检查解析为绝对路径
    monkeypatch.setenv("DATA_DIR", "./data_rel")
    monkeypatch.setenv("TEMP_DIR", "./temp_rel")

    cfg = Config()
    assert cfg.DATA_DIR.is_absolute()
    assert cfg.TEMP_DIR.is_absolute()
    assert str(cfg.DATABASE_URL).startswith("sqlite:///")


def test_config_save_and_reload(tmp_path: Path, monkeypatch):
    cfg = Config()
    # 更改并保存
    cfg.APP_VERSION = "1.2.3"
    out = tmp_path / "saved.json"
    cfg.save_config(out)

    # 修改环境变量，reload 应以文件为准（合并逻辑仍存在，但测试只验证不报错且字段存在）
    monkeypatch.setenv("APP_VERSION", "2.0.0")
    cfg2 = Config(config_file=out)
    assert cfg2.APP_VERSION == "1.2.3"


def test_config_validate_and_to_dict(tmp_path: Path):
    cfg = Config()
    assert cfg.validate() is True

    d = cfg.to_dict()
    assert isinstance(d, dict)
    assert "APP_NAME" in d and "DATA_DIR" in d


def test_config_invalid_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INVALID")
    with pytest.raises(BlueVConfigurationError):
        Config()  # pydantic 会校验并在 _initialize_config 包装为 BlueVConfigurationError
