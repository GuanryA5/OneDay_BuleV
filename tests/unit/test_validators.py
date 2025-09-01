# -*- coding: utf-8 -*-
"""
验证器模块单元测试
"""

import pytest

from bluev.utils.exceptions import BlueVValidationError
from bluev.utils.validators import (
    ChoiceValidator,
    CompositeValidator,
    EmailValidator,
    LengthValidator,
    PathValidator,
    RangeValidator,
    RegexValidator,
    RequiredValidator,
    TypeValidator,
    email,
    required,
    validate_data,
)


class TestBasicValidators:
    """基础验证器测试"""

    def test_required_validator(self) -> None:
        """测试必填验证器"""
        validator = RequiredValidator()

        # 有效值
        assert validator.validate("test") is True
        assert validator.validate(123) is True
        assert validator.validate([1, 2, 3]) is True

        # 无效值
        assert validator.validate(None) is False
        assert validator.validate("") is False

    def test_type_validator(self) -> None:
        """测试类型验证器"""
        str_validator = TypeValidator(str)
        int_validator = TypeValidator(int)

        # 字符串验证器
        assert str_validator.validate("test") is True
        assert str_validator.validate(123) is False

        # 整数验证器
        assert int_validator.validate(123) is True
        assert int_validator.validate("test") is False

    def test_range_validator(self) -> None:
        """测试范围验证器"""
        validator = RangeValidator(min_value=0, max_value=100)

        # 有效值
        assert validator.validate(50) is True
        assert validator.validate(0) is True
        assert validator.validate(100) is True
        assert validator.validate("50") is True  # 可以转换的字符串

        # 无效值
        assert validator.validate(-1) is False
        assert validator.validate(101) is False
        assert validator.validate("invalid") is False

    def test_length_validator(self) -> None:
        """测试长度验证器"""
        validator = LengthValidator(min_length=2, max_length=10)

        # 有效值
        assert validator.validate("test") is True
        assert validator.validate([1, 2, 3]) is True

        # 无效值
        assert validator.validate("a") is False  # 太短
        assert validator.validate("a" * 11) is False  # 太长
        assert validator.validate(123) is False  # 没有长度

    def test_regex_validator(self) -> None:
        """测试正则表达式验证器"""
        validator = RegexValidator(r"^\d{3}-\d{4}$")

        # 有效值
        assert validator.validate("123-4567") is True

        # 无效值
        assert validator.validate("123-456") is False
        assert validator.validate("abc-defg") is False

    def test_email_validator(self) -> None:
        """测试邮箱验证器"""
        validator = EmailValidator()

        # 有效邮箱
        assert validator.validate("test@example.com") is True
        assert validator.validate("user.name@domain.co.uk") is True

        # 无效邮箱
        assert validator.validate("invalid-email") is False
        assert validator.validate("@example.com") is False
        assert validator.validate("test@") is False

    def test_choice_validator(self) -> None:
        """测试选择验证器"""
        validator = ChoiceValidator(["red", "green", "blue"])

        # 有效选择
        assert validator.validate("red") is True
        assert validator.validate("green") is True

        # 无效选择
        assert validator.validate("yellow") is False
        assert validator.validate("RED") is False  # 区分大小写


class TestPathValidator:
    """路径验证器测试"""

    def test_path_validator_basic(self) -> None:
        """测试基础路径验证"""
        validator = PathValidator()

        # 任何路径字符串都应该有效
        assert validator.validate("/some/path") is True
        assert validator.validate("relative/path") is True
        assert validator.validate("C:\\Windows\\System32") is True

    def test_path_validator_must_exist(self, tmp_path) -> None:
        """测试路径必须存在"""
        validator = PathValidator(must_exist=True)

        # 存在的路径
        assert validator.validate(str(tmp_path)) is True

        # 不存在的路径
        non_existent = tmp_path / "non_existent"
        assert validator.validate(str(non_existent)) is False

    def test_path_validator_must_be_file(self, tmp_path) -> None:
        """测试路径必须是文件"""
        validator = PathValidator(must_exist=True, must_be_file=True)

        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # 文件路径
        assert validator.validate(str(test_file)) is True

        # 目录路径
        assert validator.validate(str(tmp_path)) is False

    def test_path_validator_must_be_dir(self, tmp_path) -> None:
        """测试路径必须是目录"""
        validator = PathValidator(must_exist=True, must_be_dir=True)

        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # 目录路径
        assert validator.validate(str(tmp_path)) is True

        # 文件路径
        assert validator.validate(str(test_file)) is False


class TestCompositeValidator:
    """复合验证器测试"""

    def test_composite_validator_all_required(self) -> None:
        """测试所有验证器都必须通过"""
        validator = CompositeValidator(
            [RequiredValidator(), TypeValidator(str), LengthValidator(min_length=3)],
            require_all=True,
        )

        # 所有验证都通过
        assert validator.validate("test") is True

        # 有验证失败
        assert validator.validate("ab") is False  # 长度不够
        assert validator.validate(123) is False  # 类型错误
        assert validator.validate(None) is False  # 必填验证失败

    def test_composite_validator_any_required(self) -> None:
        """测试至少一个验证器通过"""
        validator = CompositeValidator(
            [TypeValidator(str), TypeValidator(int)], require_all=False
        )

        # 字符串类型通过
        assert validator.validate("test") is True

        # 整数类型通过
        assert validator.validate(123) is True

        # 都不通过
        assert validator.validate([1, 2, 3]) is False


class TestValidateData:
    """数据验证函数测试"""

    def test_validate_data_success(self) -> None:
        """测试数据验证成功"""
        data = {"name": "John Doe", "age": 30, "email": "john@example.com"}

        schema = {
            "name": [RequiredValidator(), TypeValidator(str)],
            "age": [RequiredValidator(), TypeValidator(int), RangeValidator(0, 150)],
            "email": [RequiredValidator(), EmailValidator()],
        }

        result = validate_data(data, schema)
        assert result == data

    def test_validate_data_failure(self) -> None:
        """测试数据验证失败"""
        data = {
            "name": "",  # 必填但为空
            "age": -5,  # 超出范围
            "email": "invalid-email",  # 无效邮箱
        }

        schema = {
            "name": [RequiredValidator()],
            "age": [RangeValidator(0, 150)],
            "email": [EmailValidator()],
        }

        with pytest.raises(BlueVValidationError) as exc_info:
            validate_data(data, schema)

        error_message = str(exc_info.value)
        assert "name" in error_message
        assert "age" in error_message
        assert "email" in error_message


class TestPreDefinedValidators:
    """预定义验证器测试"""

    def test_required_validator_instance(self) -> None:
        """测试预定义的required验证器"""
        with pytest.raises(BlueVValidationError):
            required(None)

        assert required("test") == "test"

    def test_email_validator_instance(self) -> None:
        """测试预定义的email验证器"""
        with pytest.raises(BlueVValidationError):
            email("invalid-email")

        assert email("test@example.com") == "test@example.com"
