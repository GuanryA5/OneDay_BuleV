# -*- coding: utf-8 -*-
"""
BlueV 验证器模块

提供各种数据验证功能。
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bluev.utils.exceptions import BlueVValidationError


class Validator:
    """基础验证器类"""

    def __init__(self, error_message: str = "验证失败") -> None:
        self.error_message = error_message

    def validate(self, value: Any) -> bool:
        """验证值，子类需要实现此方法"""
        raise NotImplementedError

    def __call__(self, value: Any) -> Any:
        """使验证器可调用"""
        if not self.validate(value):
            raise BlueVValidationError(self.error_message)
        return value


class RequiredValidator(Validator):
    """必填验证器"""

    def __init__(self) -> None:
        super().__init__("此字段为必填项")

    def validate(self, value: Any) -> bool:
        return value is not None and value != ""


class TypeValidator(Validator):
    """类型验证器"""

    def __init__(self, expected_type: type) -> None:
        self.expected_type = expected_type
        super().__init__(f"期望类型 {expected_type.__name__}")

    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)


class RangeValidator(Validator):
    """范围验证器"""

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ):
        self.min_value = min_value
        self.max_value = max_value

        message_parts = []
        if min_value is not None:
            message_parts.append(f"最小值 {min_value}")
        if max_value is not None:
            message_parts.append(f"最大值 {max_value}")

        super().__init__(f"值必须在范围内: {', '.join(message_parts)}")

    def validate(self, value: Any) -> bool:
        try:
            num_value = float(value)
            if self.min_value is not None and num_value < self.min_value:
                return False
            if self.max_value is not None and num_value > self.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False


class LengthValidator(Validator):
    """长度验证器"""

    def __init__(
        self, min_length: Optional[int] = None, max_length: Optional[int] = None
    ):
        self.min_length = min_length
        self.max_length = max_length

        message_parts = []
        if min_length is not None:
            message_parts.append(f"最小长度 {min_length}")
        if max_length is not None:
            message_parts.append(f"最大长度 {max_length}")

        super().__init__(f"长度必须满足: {', '.join(message_parts)}")

    def validate(self, value: Any) -> bool:
        try:
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                return False
            if self.max_length is not None and length > self.max_length:
                return False
            return True
        except TypeError:
            return False


class RegexValidator(Validator):
    """正则表达式验证器"""

    def __init__(self, pattern: str, flags: int = 0) -> None:
        self.pattern = re.compile(pattern, flags)
        super().__init__(f"值必须匹配模式: {pattern}")

    def validate(self, value: Any) -> bool:
        try:
            return bool(self.pattern.match(str(value)))
        except TypeError:
            return False


class EmailValidator(RegexValidator):
    """邮箱验证器"""

    def __init__(self) -> None:
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        super().__init__(email_pattern)
        self.error_message = "请输入有效的邮箱地址"


class PathValidator(Validator):
    """路径验证器"""

    def __init__(
        self,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
    ):
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
        super().__init__("无效的路径")

    def validate(self, value: Any) -> bool:
        try:
            path = Path(value)

            if self.must_exist and not path.exists():
                self.error_message = f"路径不存在: {path}"
                return False

            if self.must_be_file and path.exists() and not path.is_file():
                self.error_message = f"路径不是文件: {path}"
                return False

            if self.must_be_dir and path.exists() and not path.is_dir():
                self.error_message = f"路径不是目录: {path}"
                return False

            return True
        except (TypeError, OSError):
            return False


class ChoiceValidator(Validator):
    """选择验证器"""

    def __init__(self, choices: List[Any]) -> None:
        self.choices = choices
        super().__init__(f"值必须是以下选项之一: {choices}")

    def validate(self, value: Any) -> bool:
        return value in self.choices


class CompositeValidator(Validator):
    """复合验证器"""

    def __init__(self, validators: List[Validator], require_all: bool = True) -> None:
        self.validators = validators
        self.require_all = require_all
        super().__init__("复合验证失败")

    def validate(self, value: Any) -> bool:
        results = []
        errors = []

        for validator in self.validators:
            try:
                validator(value)
                results.append(True)
            except BlueVValidationError as e:
                results.append(False)
                errors.append(str(e))

        if self.require_all:
            # 所有验证器都必须通过
            success = all(results)
            if not success:
                self.error_message = "; ".join(errors)
        else:
            # 至少一个验证器通过
            success = any(results)
            if not success:
                self.error_message = f"所有验证都失败: {'; '.join(errors)}"

        return success


def validate_data(
    data: Dict[str, Any], schema: Dict[str, List[Validator]]
) -> Dict[str, Any]:
    """验证数据字典

    Args:
        data: 要验证的数据
        schema: 验证模式，键为字段名，值为验证器列表

    Returns:
        验证后的数据

    Raises:
        BlueVValidationError: 验证失败
    """
    validated_data = {}
    errors = {}

    for field_name, validators in schema.items():
        field_value = data.get(field_name)
        field_errors = []

        for validator in validators:
            try:
                validated_value = validator(field_value)
                field_value = validated_value
            except BlueVValidationError as e:
                field_errors.append(str(e))

        if field_errors:
            errors[field_name] = field_errors
        else:
            validated_data[field_name] = field_value

    if errors:
        error_message = "数据验证失败:\n"
        for field, field_errors in errors.items():
            error_message += f"  {field}: {'; '.join(field_errors)}\n"
        raise BlueVValidationError(error_message.strip())

    return validated_data


# 预定义的常用验证器实例
required = RequiredValidator()
email = EmailValidator()


def string_type():
    return TypeValidator(str)


def int_type():
    return TypeValidator(int)


def float_type():
    return TypeValidator(float)


def bool_type():
    return TypeValidator(bool)


def min_length(length: int):
    return LengthValidator(min_length=length)


def max_length(length: int):
    return LengthValidator(max_length=length)


def min_value(value: Union[int, float]):
    return RangeValidator(min_value=value)


def max_value(value: Union[int, float]):
    return RangeValidator(max_value=value)


def choices(*options):
    return ChoiceValidator(list(options))


def existing_path():
    return PathValidator(must_exist=True)


def existing_file():
    return PathValidator(must_exist=True, must_be_file=True)


def existing_dir():
    return PathValidator(must_exist=True, must_be_dir=True)
