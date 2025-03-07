#!/usr/bin/env python
import sys
import traceback
import logging

from typing import Any, Dict
from pydantic import BaseModel

# ---------------------------
# Импортируем ваши же функции:
# ---------------------------
# Предположим, что ваш код хранится в файле my_module.py,
# и вы импортировали в нём все описанные функции:
from classes import (
    get_all_classes,
    get_class_details,
    Action,
    ActionType,
    Bypass,
    BypassType,
    CleaningMethod,
    CleaningProcedure,
    CleaningType,
    CleanlinessClass,
    CleanlinessPassport,
    ComponentProperty,
    Connection,
    CoolingSystem,
    CoolingSystemType,
    Corrosion,
    CorrosionType,
    DisposalMethod,
    Downtime,
    DowntimeType,
    EconomicMetricType,
    Economics,
    EnergyEfficiency,
    EnergyType,
    Equipment,
    Event,
    EventType,
    Flow,
    FlowType,
    Fouling,
    FoulingAnalysis,
    FoulingImpactAssessment,
    FoulingPrediction,
    FoulingRiskAssessment,
    FoulingType,
    ImpactCategory,
    ImpactLevel,
    Instrument,
    KnowledgeType,
    Language,
    Maintenance,
    MaintenanceCategory,
    MaintenanceSchedule,
    MaintenanceTask,
    MaintenanceType,
    MaterialBalance,
    MonitoringData,
    MonitoringParameter,
    MonitoringRegime,
    Parameter,
    PhaseState,
    PhysicalProperty,
    PriceType,
    ProcessControl,
    ProcessDescription,
    ProcessRelationship,
    ProcessSystem,
    ProcessWaste,
    ProductSpecification,
    Resource,
    ResourceCategory,
    ResourceConsumption,
    ResourcePrice,
    Risk,
    RiskSeverity,
    RiskType,
    SafetyRequirement,
    TechnicalDocumentation,
    TechnologicalRegime,
    WasteComponent,
    WasteNorm,
    WasteType
    )


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scan_all_pydantic_models() -> None:
    """Сканирует все классы и выводит только ошибки и статистику"""
    all_classes = get_all_classes()
    
    stats = {
        'total_classes': len(all_classes),
        'pydantic_models': 0,
        'enums': 0,
        'successful_validations': 0,
        'failed_validations': 0,
        'failed_models': []  # Добавляем список для хранения неудачных моделей
    }

    for class_name in all_classes:
        try:
            details: Dict[str, Any] = get_class_details(class_name)
        except Exception as e:
            logger.error(f"❌ Ошибка в {class_name}: {str(e)}")
            stats['failed_validations'] += 1
            stats['failed_models'].append(class_name)
            continue

        class_type = details.get("type")
        if class_type == "pydantic_model":
            stats['pydantic_models'] += 1
            example = details.get("example")
            
            if example:
                try:
                    cls = globals().get(class_name)
                    if cls and issubclass(cls, BaseModel):
                        _instance = cls(**example)
                        stats['successful_validations'] += 1
                    else:
                        logger.error(f"❌ {class_name}: Класс не найден в globals()")
                        stats['failed_validations'] += 1
                        stats['failed_models'].append(class_name)
                except Exception as inst_err:
                    logger.error(f"❌ {class_name}: {str(inst_err)}")
                    stats['failed_validations'] += 1
                    stats['failed_models'].append(class_name)
        elif class_type == "enum":
            stats['enums'] += 1

    # Выводим только статистику и список ошибок
    logger.info("\n=== ИТОГОВАЯ СТАТИСТИКА ===")
    logger.info(f"Всего классов: {stats['total_classes']}")
    logger.info(f"Pydantic моделей: {stats['pydantic_models']}")
    logger.info(f"Enum классов: {stats['enums']}")
    logger.info(f"Успешных валидаций: {stats['successful_validations']}")
    logger.info(f"Неудачных валидаций: {stats['failed_validations']}")
    logger.info(f"Процент успешных валидаций: {(stats['successful_validations'] / stats['pydantic_models'] * 100):.1f}%")
    
    if stats['failed_models']:
        logger.info("\n❌ Модели с ошибками:")
        for model in stats['failed_models']:
            logger.info(f"  - {model}")
    
    logger.info("========================\n")


def main():
    logger.info("Начинаем сканирование классов для проверки Pydantic-моделей...")
    scan_all_pydantic_models()
    logger.info("Сканирование завершено.")


if __name__ == "__main__":
    sys.exit(main())