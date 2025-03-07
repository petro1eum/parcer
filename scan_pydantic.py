#!/usr/bin/env python3

import logging
import json
import inspect
from typing import Any, Dict, List, Optional, Union, get_origin, get_args
from datetime import datetime, date
from pydantic import BaseModel, ValidationError
from classes import get_all_models, get_all_enums
from pydantic.fields import FieldInfo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для обработки специальных типов."""
    def default(self, obj):
        if isinstance(obj, FieldInfo):
            return {
                'type': str(obj.annotation),
                'required': obj.is_required(),
                'description': obj.description,
                'default': str(obj.default) if obj.default is not Ellipsis else None
            }
        return super().default(obj)


def generate_test_value(annotation):
    """
    Генерирует тестовое значение на основе типа аннотации.
    """
    # Проверяем базовый тип
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    # Обработка Optional[X]
    if origin is Union and type(None) in args:
        # Если это Optional, используем первый тип, который не None
        for arg in args:
            if arg is not type(None):
                return generate_test_value(arg)
    
    # Обработка списков
    if origin is list or origin is List:
        if args:
            # Создаем список с одним тестовым элементом соответствующего типа
            return [generate_test_value(args[0])]
        return []
    
    # Обработка словарей
    if origin is dict or origin is Dict:
        if len(args) >= 2:
            # Создаем словарь с одним тестовым ключом и значением
            key_type, value_type = args[0], args[1]
            key = generate_test_value(key_type)
            value = generate_test_value(value_type)
            return {key: value}
        return {}
    
    # Обработка базовых типов
    if annotation is str or getattr(annotation, "__origin__", None) is str:
        return "test_string"
    if annotation is int or getattr(annotation, "__origin__", None) is int:
        return 42
    if annotation is float or getattr(annotation, "__origin__", None) is float:
        return 3.14
    if annotation is bool or getattr(annotation, "__origin__", None) is bool:
        return True
    if annotation is datetime or getattr(annotation, "__origin__", None) is datetime:
        return datetime.now()
    if annotation is date or getattr(annotation, "__origin__", None) is date:
        return date.today()
    
    # Если это Pydantic модель
    try:
        if issubclass(annotation, BaseModel):
            # Рекурсивно создаем минимальный экземпляр вложенной модели
            required_fields = {}
            for name, field in annotation.model_fields.items():
                if field.is_required():
                    required_fields[name] = generate_test_value(field.annotation)
            return annotation(**required_fields)
    except TypeError:
        pass
    
    # Если это Enum
    try:
        if issubclass(annotation, object) and hasattr(annotation, "__members__"):
            # Берем первое значение из Enum
            return next(iter(annotation.__members__.values()))
    except TypeError:
        pass
    
    # Для всех других типов используем строковое значение
    return "test_value"


def check_type_annotation(annotation):
    """
    Проверяет корректность аннотации типа.
    Возвращает (корректно?, сообщение об ошибке)
    """
    if annotation is None:
        return False, "Отсутствует аннотация типа"
    
    try:
        # Проверка базовых типов
        if annotation in (str, int, float, bool, dict, list, Any):
            return True, ""
        
        # Проверка составных типов
        origin = get_origin(annotation)
        args = get_args(annotation)
        
        if origin is Union:
            # Проверяем каждый тип в Union
            for arg in args:
                is_valid, error_msg = check_type_annotation(arg)
                if not is_valid:
                    return False, f"Некорректный тип в Union: {error_msg}"
            return True, ""
        
        if origin in (list, List):
            if not args:
                return False, "List должен иметь указание типа элементов"
            is_valid, error_msg = check_type_annotation(args[0])
            if not is_valid:
                return False, f"Некорректный тип элемента списка: {error_msg}"
            return True, ""
        
        if origin in (dict, Dict):
            if len(args) < 2:
                return False, "Dict должен иметь указание типов ключа и значения"
            key_valid, key_error = check_type_annotation(args[0])
            value_valid, value_error = check_type_annotation(args[1])
            if not key_valid:
                return False, f"Некорректный тип ключа словаря: {key_error}"
            if not value_valid:
                return False, f"Некорректный тип значения словаря: {value_error}"
            return True, ""
        
        # Проверка Pydantic моделей
        try:
            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                return True, ""
        except TypeError:
            pass
        
        # Проверка Enum
        try:
            if inspect.isclass(annotation) and hasattr(annotation, "__members__"):
                return True, ""
        except TypeError:
            pass
        
        # Проверка других типов
        return True, ""
        
    except Exception as e:
        return False, f"Ошибка при проверке типа: {str(e)}"


def validate_pydantic_models():
    """
    Проверяет все Pydantic модели на корректность определения.
    Возвращает отчет о проверке.
    """
    import classes
    
    results = {
        "models": [],
        "enums": [],
        "summary": {
            "timestamp": datetime.now().isoformat(),
            "total_models": 0,
            "total_enums": 0,
            "models_with_errors": 0,
            "enums_with_errors": 0
        }
    }
    
    # Проверяем модели
    models = get_all_models()
    for model_name in models:
        model = getattr(classes, model_name)
        model_result = {
            "name": model_name,
            "fields_count": len(model.model_fields),
            "tests": [],
            "has_errors": False
        }
        
        # Тест 1: Проверка JSON схемы
        try:
            schema = model.model_json_schema()
            model_result["tests"].append({
                "name": "json_schema",
                "status": "passed",
                "fields_found": len(schema.get("properties", {}))
            })
        except Exception as e:
            model_result["tests"].append({
                "name": "json_schema",
                "status": "failed",
                "error": str(e)
            })
            model_result["has_errors"] = True
        
        # Тест 2: Проверка полей
        invalid_fields = []
        type_errors = []
        
        for field_name, field in model.model_fields.items():
            # Проверка на наличие типа
            if not field.annotation:
                invalid_fields.append(f"{field_name} (no type)")
                continue
            
            # Проверка на корректность типа
            is_valid, error_msg = check_type_annotation(field.annotation)
            if not is_valid:
                type_errors.append(f"{field_name}: {error_msg}")
        
        model_result["tests"].append({
            "name": "fields_validation",
            "status": "passed" if not (invalid_fields or type_errors) else "failed",
            "invalid_fields": invalid_fields,
            "type_errors": type_errors
        })
        
        if invalid_fields or type_errors:
            model_result["has_errors"] = True
        
        # Тест 3: Проверка создания минимального объекта
        try:
            required_fields = {}
            for name, field in model.model_fields.items():
                if field.is_required():
                    required_fields[name] = generate_test_value(field.annotation)
            
            instance = model(**required_fields)
            model_result["tests"].append({
                "name": "instantiation",
                "status": "passed",
                "required_fields": list(required_fields.keys())
            })
        except ValidationError as e:
            model_result["tests"].append({
                "name": "instantiation",
                "status": "failed",
                "error": str(e)
            })
            model_result["has_errors"] = True
        except Exception as e:
            model_result["tests"].append({
                "name": "instantiation",
                "status": "failed",
                "error": f"Непредвиденная ошибка: {str(e)}"
            })
            model_result["has_errors"] = True
        
        # Тест 4: Проверка документации модели
        model_doc = inspect.getdoc(model)
        model_result["tests"].append({
            "name": "documentation",
            "status": "passed" if model_doc else "warning",
            "doc": model_doc or None
        })
        
        # Тест 5: Проверка методов валидации
        has_validators = False
        for name, method in inspect.getmembers(model, predicate=inspect.isfunction):
            if name.startswith('validate_') or name == 'root_validator':
                has_validators = True
                break
        
        model_result["tests"].append({
            "name": "validators",
            "status": "info",
            "has_validators": has_validators
        })
        
        results["models"].append(model_result)
        
        if model_result["has_errors"]:
            results["summary"]["models_with_errors"] += 1
    
    # Проверяем enum'ы
    enums = get_all_enums()
    for enum_name in enums:
        enum = getattr(classes, enum_name)
        enum_result = {
            "name": enum_name,
            "values_count": len(enum.__members__),
            "tests": [],
            "has_errors": False
        }
        
        # Тест 1: Проверка значений
        try:
            values = [e.value for e in enum]
            enum_result["tests"].append({
                "name": "values",
                "status": "passed",
                "values": values
            })
        except Exception as e:
            enum_result["tests"].append({
                "name": "values",
                "status": "failed",
                "error": str(e)
            })
            enum_result["has_errors"] = True
        
        # Тест 2: Проверка документации
        enum_result["tests"].append({
            "name": "documentation",
            "status": "passed" if enum.__doc__ else "warning",
            "doc": enum.__doc__ or None
        })
        
        # Тест 3: Проверка дубликатов значений
        value_counts = {}
        duplicate_values = []
        
        for member in enum.__members__:
            value = enum.__members__[member].value
            if value in value_counts:
                duplicate_values.append(value)
            else:
                value_counts[value] = 1
        
        enum_result["tests"].append({
            "name": "duplicate_values",
            "status": "passed" if not duplicate_values else "warning",
            "duplicates": duplicate_values
        })
        
        results["enums"].append(enum_result)
        
        if enum_result["has_errors"]:
            results["summary"]["enums_with_errors"] += 1
    
    # Обновляем итоговую статистику
    results["summary"]["total_models"] = len(results["models"])
    results["summary"]["total_enums"] = len(results["enums"])
    
    return results


def print_validation_results(results):
    """Выводит результаты проверки в читаемом формате"""
    print("\n=== ОТЧЕТ О ПРОВЕРКЕ PYDANTIC МОДЕЛЕЙ ===\n")
    
    # Статистика
    total_models = results["summary"]["total_models"]
    total_enums = results["summary"]["total_enums"]
    models_with_errors = results["summary"]["models_with_errors"]
    enums_with_errors = results["summary"]["enums_with_errors"]
    
    print(f"Всего проверено:")
    print(f"  - Моделей: {total_models}")
    print(f"  - Enum'ов: {total_enums}")
    
    # Проверка моделей
    print("\n=== МОДЕЛИ ===")
    for model in results["models"]:
        print(f"\n📦 Модель: {model['name']}")
        print(f"   Полей: {model['fields_count']}")
        
        for test in model["tests"]:
            if test["name"] == "json_schema":
                status = "✅" if test["status"] == "passed" else "❌"
                print(f"   {status} JSON Schema: найдено полей - {test.get('fields_found', 0)}")
            
            elif test["name"] == "fields_validation":
                status = "✅" if test["status"] == "passed" else "❌"
                if test["status"] == "failed":
                    print(f"   ❌ Проверка полей: найдены проблемы")
                    for field in test.get("invalid_fields", []):
                        print(f"      - {field}")
                    for error in test.get("type_errors", []):
                        print(f"      - {error}")
                else:
                    print(f"   ✅ Проверка полей: все корректно")
            
            elif test["name"] == "instantiation":
                status = "✅" if test["status"] == "passed" else "❌"
                if test["status"] == "passed":
                    print(f"   ✅ Создание объекта: успешно")
                    if test.get("required_fields"):
                        print(f"      Обязательные поля: {', '.join(test['required_fields'])}")
                else:
                    print(f"   ❌ Создание объекта: ошибка")
                    print(f"      Причина: {test['error']}")
            
            elif test["name"] == "documentation":
                if test["status"] == "passed":
                    print(f"   ✅ Документация: присутствует")
                else:
                    print(f"   ⚠️ Документация: отсутствует")
            
            elif test["name"] == "validators":
                if test["has_validators"]:
                    print(f"   ℹ️ Валидаторы: присутствуют")
                else:
                    print(f"   ℹ️ Валидаторы: отсутствуют")
    
    # Проверка enum'ов
    print("\n=== ENUM'ы ===")
    for enum in results["enums"]:
        print(f"\n🔤 Enum: {enum['name']}")
        print(f"   Значений: {enum['values_count']}")
        
        for test in enum["tests"]:
            if test["name"] == "values":
                status = "✅" if test["status"] == "passed" else "❌"
                if test["status"] == "passed":
                    print(f"   ✅ Значения: {', '.join(map(str, test['values']))}")
                else:
                    print(f"   ❌ Значения: ошибка - {test['error']}")
            
            elif test["name"] == "documentation":
                if test["status"] == "passed":
                    print(f"   ✅ Документация: присутствует")
                else:
                    print(f"   ⚠️ Документация: отсутствует")
            
            elif test["name"] == "duplicate_values":
                if test["status"] == "passed":
                    print(f"   ✅ Уникальность значений: все значения уникальны")
                else:
                    print(f"   ⚠️ Уникальность значений: найдены дубликаты - {', '.join(map(str, test['duplicates']))}")
    
    # Итоговая статистика
    print("\n=== ИТОГИ ===")
    print(f"✅ Успешно проверено:")
    print(f"   - Моделей: {total_models - models_with_errors} из {total_models}")
    print(f"   - Enum'ов: {total_enums - enums_with_errors} из {total_enums}")
    
    if models_with_errors or enums_with_errors:
        print(f"\n❌ Найдены проблемы:")
        if models_with_errors:
            print(f"   - Модели с ошибками: {models_with_errors}")
        if enums_with_errors:
            print(f"   - Enum'ы с ошибками: {enums_with_errors}")


if __name__ == "__main__":
    results = validate_pydantic_models()
    print_validation_results(results)
    
    # Сохраняем также JSON для возможной автоматической обработки
    with open('pydantic_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)