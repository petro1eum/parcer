#!/usr/bin/env python3
# parcing.py

import inspect
import json
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from pydantic.fields import FieldInfo  # Вариант 1
import argparse
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    RU: str = Field(
        "russian",
        description="Russian language",
        example="russian"
    )
    EN: str = Field(
        "english",
        description="English language",
        example="english"
    )

class KnowledgeType(Enum):
    """Types of knowledge in documentation"""
    TECHNOLOGICAL: str = Field(
        "technological",
        description="Technical and process-related knowledge",
        example="technological"
    )
    OPERATIONAL: str = Field(
        "operational",
        description="Operational procedures and practices",
        example="operational"
    )
    SAFETY: str = Field(
        "safety",
        description="Safety-related information",
        example="safety"
    )
    RELATIONSHIP: str = Field(
        "relationship",
        description="Relationships between entities",
        example="relationship"
    )

class EventType(Enum):
    """Types of events"""
    NORMAL: str = Field(
        "normal_operation",
        description="Normal operating conditions",
        example="normal_operation"
    )
    DEVIATION: str = Field(
        "deviation",
        description="Deviation from normal operation",
        example="deviation"
    )
    EMERGENCY: str = Field(
        "emergency",
        description="Emergency situation",
        example="emergency"
    )
    MAINTENANCE: str = Field(
        "maintenance",
        description="Maintenance activities",
        example="maintenance"
    )

class RiskType(Enum):
    """Types of risks"""
    MECHANICAL: str = Field(
        "mechanical",
        description="Mechanical-related risks",
        example="mechanical"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical-related risks",
        example="chemical"
    )
    PROCESS: str = Field(
        "process",
        description="Process-related risks",
        example="process"
    )
    ENVIRONMENTAL: str = Field(
        "environmental",
        description="Environmental risks",
        example="environmental"
    )
    SAFETY: str = Field(
        "safety",
        description="Safety-related risks",
        example="safety"
    )

class RiskSeverity(Enum):
    """Risk severity levels"""
    LOW: str = Field(
        "low",
        description="Low severity risk",
        example="low"
    )
    MEDIUM: str = Field(
        "medium",
        description="Medium severity risk",
        example="medium"
    )
    HIGH: str = Field(
        "high",
        description="High severity risk",
        example="high"
    )
    CRITICAL: str = Field(
        "critical",
        description="Critical severity risk",
        example="critical"
    )

class ActionType(Enum):
    """Types of actions"""
    NORMAL: str = Field(
        "normal_procedure",
        description="Normal operating procedures",
        example="normal_procedure"
    )
    EMERGENCY: str = Field(
        "emergency_procedure",
        description="Emergency procedures",
        example="emergency_procedure"
    )
    MAINTENANCE: str = Field(
        "maintenance_procedure",
        description="Maintenance procedures",
        example="maintenance_procedure"
    )
    PREVENTION: str = Field(
        "preventive_action",
        description="Preventive actions",
        example="preventive_action"
    )
    CORRECTION: str = Field(
        "corrective_action",
        description="Corrective actions",
        example="corrective_action"
    )

class CleaningType(Enum):
    """Types of cleaning"""
    MECHANICAL: str = Field(
        "mechanical",
        description="Mechanical cleaning method",
        example="mechanical"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical cleaning method",
        example="chemical"
    )
    HYDRAULIC: str = Field(
        "hydraulic",
        description="Hydraulic cleaning method",
        example="hydraulic"
    )
    PNEUMATIC: str = Field(
        "pneumatic",
        description="Pneumatic cleaning method",
        example="pneumatic"
    )
    STEAM: str = Field(
        "steam",
        description="Steam cleaning method",
        example="steam"
    )
    ULTRASONIC: str = Field(
        "ultrasonic",
        description="Ultrasonic cleaning method",
        example="ultrasonic"
    )
    SOLVENT: str = Field(
        "solvent",
        description="Solvent cleaning method",
        example="solvent"
    )
    COMBINED: str = Field(
        "combined",
        description="Combined cleaning method",
        example="combined"
    )

class CleanlinessClass(Enum):
    """Classes of equipment cleanliness"""
    CLASS_1: str = Field(
        "class_1",
        description="High impact cleanliness class",
        example="class_1"
    )
    CLASS_2: str = Field(
        "class_2",
        description="Medium impact cleanliness class",
        example="class_2"
    )
    CLASS_3: str = Field(
        "class_3",
        description="Low impact cleanliness class",
        example="class_3"
    )

class MonitoringRegime(Enum):
    """Types of monitoring regimes"""
    GENERAL: str = Field(
        "general",
        description="General cleanliness monitoring regime (ОРПЧ)",
        example="general"
    )
    SPECIAL: str = Field(
        "special",
        description="Special cleanliness monitoring regime (СРПЧ)",
        example="special"
    )

class ImpactCategory(Enum):
    """Categories of fouling impact"""
    ECONOMIC: str = Field(
        "economic",
        description="Economic impact",
        example="economic"
    )
    RELIABILITY: str = Field(
        "reliability",
        description="Reliability impact",
        example="reliability"
    )
    QUALITY: str = Field(
        "quality",
        description="Product quality impact",
        example="quality"
    )
    ENVIRONMENTAL: str = Field(
        "environmental",
        description="Environmental impact",
        example="environmental"
    )

class ImpactLevel(Enum):
    """Levels of impact"""
    HIGH: str = Field(
        "high",
        description="High impact level",
        example="high"
    )
    MEDIUM: str = Field(
        "medium",
        description="Medium impact level",
        example="medium"
    )
    LOW: str = Field(
        "low",
        description="Low impact level",
        example="low"
    )

class FlowType(Enum):
    """Types of process flows"""
    PROCESS: str = Field(
        "process",
        description="Process flow",
        example="process"
    )
    UTILITY: str = Field(
        "utility",
        description="Utility flow",
        example="utility"
    )
    PRODUCT: str = Field(
        "product",
        description="Product flow",
        example="product"
    )
    WASTE: str = Field(
        "waste",
        description="Waste flow",
        example="waste"
    )
    RECYCLE: str = Field(
        "recycle",
        description="Recycle flow",
        example="recycle"
    )

class PhaseState(Enum):
    """Physical state of flows"""
    GAS: str = Field(
        "gas",
        description="Gas phase state",
        example="gas"
    )
    LIQUID: str = Field(
        "liquid",
        description="Liquid phase state",
        example="liquid"
    )
    SOLID: str = Field(
        "solid",
        description="Solid phase state",
        example="solid"
    )
    SLURRY: str = Field(
        "slurry",
        description="Slurry phase state",
        example="slurry"
    )
    MULTIPHASE: str = Field(
        "multiphase",
        description="Multiphase system",
        example="multiphase"
    )

class WasteType(Enum):
    """Types of waste"""
    SOLID: str = Field(
        "solid",
        description="Solid waste",
        example="solid"
    )
    LIQUID: str = Field(
        "liquid",
        description="Liquid waste",
        example="liquid"
    )
    GAS: str = Field(
        "gas",
        description="Gaseous emissions",
        example="gas"
    )
    CATALYST: str = Field(
        "catalyst",
        description="Spent catalysts",
        example="catalyst"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical waste",
        example="chemical"
    )
    BIOLOGICAL: str = Field(
        "biological",
        description="Biological waste",
        example="biological"
    )

class DisposalMethod(Enum):
    """Waste disposal methods"""
    RECYCLING: str = Field(
        "recycling",
        description="Recycling disposal method",
        example="recycling"
    )
    LANDFILL: str = Field(
        "landfill",
        description="Landfill disposal method",
        example="landfill"
    )
    INCINERATION: str = Field(
        "incineration",
        description="Incineration disposal method",
        example="incineration"
    )
    TREATMENT: str = Field(
        "treatment",
        description="Treatment disposal method",
        example="treatment"
    )
    RECOVERY: str = Field(
        "recovery",
        description="Value recovery disposal method",
        example="recovery"
    )

class MaintenanceType(Enum):
    """Types of maintenance"""
    PREVENTIVE: str = Field(
        "preventive",
        description="Preventive maintenance",
        example="preventive"
    )
    CORRECTIVE: str = Field(
        "corrective",
        description="Corrective maintenance",
        example="corrective"
    )
    PREDICTIVE: str = Field(
        "predictive",
        description="Predictive maintenance",
        example="predictive"
    )
    EMERGENCY: str = Field(
        "emergency",
        description="Emergency maintenance",
        example="emergency"
    )

class MaintenanceCategory(Enum):
    """Categories of maintenance"""
    MECHANICAL: str = Field(
        "mechanical",
        description="Mechanical maintenance",
        example="mechanical"
    )
    ELECTRICAL: str = Field(
        "electrical",
        description="Electrical maintenance",
        example="electrical"
    )
    INSTRUMENTAL: str = Field(
        "instrumental",
        description="Instrumentation maintenance",
        example="instrumental"
    )
    STRUCTURAL: str = Field(
        "structural",
        description="Structural maintenance",
        example="structural"
    )

class CorrosionType(Enum):
    """Types of corrosion"""
    UNIFORM: str = Field(
        "uniform",
        description="Uniform corrosion",
        example="uniform"
    )
    PITTING: str = Field(
        "pitting",
        description="Pitting corrosion",
        example="pitting"
    )
    STRESS: str = Field(
        "stress",
        description="Stress corrosion cracking",
        example="stress"
    )
    GALVANIC: str = Field(
        "galvanic",
        description="Galvanic corrosion",
        example="galvanic"
    )
    EROSION: str = Field(
        "erosion",
        description="Erosion corrosion",
        example="erosion"
    )

class FoulingType(Enum):
    """Types of fouling"""
    CRYSTALLIZATION: str = Field(
        "crystallization",
        description="Crystallization fouling",
        example="crystallization"
    )
    PARTICULATE: str = Field(
        "particulate",
        description="Particulate fouling",
        example="particulate"
    )
    BIOLOGICAL: str = Field(
        "biological",
        description="Biological fouling",
        example="biological"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical fouling",
        example="chemical"
    )
    CORROSION: str = Field(
        "corrosion",
        description="Corrosion fouling",
        example="corrosion"
    )

class CoolingSystemType(Enum):
    """Types of cooling systems"""
    OPEN: str = Field(
        "open",
        description="Open cooling system",
        example="open"
    )
    CLOSED: str = Field(
        "closed",
        description="Closed cooling system",
        example="closed"
    )
    HYBRID: str = Field(
        "hybrid",
        description="Hybrid cooling system",
        example="hybrid"
    )

class BypassType(Enum):
    """Types of bypass lines"""
    PROCESS: str = Field(
        "process",
        description="Process bypass",
        example="process"
    )
    SAFETY: str = Field(
        "safety",
        description="Safety bypass",
        example="safety"
    )
    MAINTENANCE: str = Field(
        "maintenance",
        description="Maintenance bypass",
        example="maintenance"
    )
    STARTUP: str = Field(
        "startup",
        description="Startup bypass",
        example="startup"
    )

class EconomicMetricType(Enum):
    """Types of economic metrics"""
    CAPEX: str = Field(
        "capex",
        description="Capital expenditure",
        example="capex"
    )
    OPEX: str = Field(
        "opex",
        description="Operating expenditure",
        example="opex"
    )
    REVENUE: str = Field(
        "revenue",
        description="Revenue",
        example="revenue"
    )
    PROFIT: str = Field(
        "profit",
        description="Profit",
        example="profit"
    )
    ROI: str = Field(
        "roi",
        description="Return on investment",
        example="roi"
    )

class EnergyType(Enum):
    """Types of energy"""
    ELECTRICAL: str = Field(
        "electrical",
        description="Electrical energy",
        example="electrical"
    )
    THERMAL: str = Field(
        "thermal",
        description="Thermal energy",
        example="thermal"
    )
    MECHANICAL: str = Field(
        "mechanical",
        description="Mechanical energy",
        example="mechanical"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical energy",
        example="chemical"
    )

class DowntimeType(Enum):
    """Types of equipment downtime"""
    PLANNED: str = Field(
        "planned",
        description="Planned downtime",
        example="planned"
    )
    UNPLANNED: str = Field(
        "unplanned",
        description="Unplanned downtime",
        example="unplanned"
    )
    MAINTENANCE: str = Field(
        "maintenance",
        description="Maintenance downtime",
        example="maintenance"
    )
    EMERGENCY: str = Field(
        "emergency",
        description="Emergency downtime",
        example="emergency"
    )

class PriceType(Enum):
    """Types of resource pricing"""
    CONTRACT: str = Field(
        "contract",
        description="Contract price",
        example="contract"
    )
    MARKET: str = Field(
        "market",
        description="Market price",
        example="market"
    )
    ESTIMATED: str = Field(
        "estimated",
        description="Estimated price",
        example="estimated"
    )
    HISTORICAL: str = Field(
        "historical",
        description="Historical price",
        example="historical"
    )

class ResourceCategory(Enum):
    """Categories of resources"""
    RAW: str = Field(
        "raw",
        description="Raw materials",
        example="raw"
    )
    CATALYST: str = Field(
        "catalyst",
        description="Catalysts",
        example="catalyst"
    )
    CHEMICAL: str = Field(
        "chemical",
        description="Chemical reagents",
        example="chemical"
    )
    UTILITY: str = Field(
        "utility",
        description="Utilities",
        example="utility"
    )
    CONSUMABLE: str = Field(
        "consumable",
        description="Consumable materials",
        example="consumable"
    )
      
# ============= Base Models =============
 
class Parameter(BaseModel):
    """Model for equipment parameters"""
    name: str = Field(
        description="Name of the parameter",
        example="operating_pressure"
    )
    value: Union[float, str, Dict[str, Any]] = Field(
        description="Parameter value in various formats",
        example=10.5
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement",
        example="MPa"
    )
    description: Optional[str] = Field(
        default=None,
        description="Parameter description",
        example="Maximum allowable operating pressure"
    )
    dynamic_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dynamic properties extracted from documentation",
        example=[{
            "name": "pressure_limit",
            "value": 12.0,
            "unit": "MPa"
        }]
    )

class Instrument(BaseModel):
    """Model for instrumentation"""
    tag: str = Field(
        description="Instrument tag number",
        example="PT-101"
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of instrument",
        example="pressure_transmitter"
    )
    function: Optional[str] = Field(
        default=None,
        description="Instrument function",
        example="pressure_monitoring"
    )
    alarm_points: Optional[Dict[str, float]] = Field(
        default=None,
        description="Alarm setpoints",
        example={"high": 11.0, "low": 9.0}
    )
    interlock_points: Optional[Dict[str, Union[float, str, None]]] = Field(
        default_factory=dict,
        description="Interlock setpoints",
        example={"shutdown": 12.0}
    )
    dynamic_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dynamic properties extracted from documentation",
        example=[{
            "name": "calibration_range",
            "value": {"min": 0, "max": 15},
            "unit": "MPa"
        }]
    )

class Connection(BaseModel):
    """Model for physical, logical and semantic connections between process elements"""
    from_id: str = Field(
        description="Source identifier (equipment, stream, parameter, or logical entity)",
        example="P-101"
    )
    to_id: str = Field(
        description="Destination identifier (equipment, stream, parameter, or logical entity)",
        example="E-102"
    )
    connection_type: Optional[str] = Field(
        default=None,
        description="Type of connection or relationship between entities",
        example="process_flow"  # physical, logical, control, safety relationship
    )
    medium: Optional[str] = Field(
        default=None,
        description="Physical medium or logical relationship type",
        example="liquid_hydrocarbon"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the connection or relationship",
        example="Main process feed line from pump P-101 to heat exchanger E-102 with high pressure interlock"
    )
    relationship_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Properties defining the relationship between entities",
        example={
            "relationship_type": "control_dependency",
            "criticality": "high",
            "response_time": {"value": 2, "unit": "seconds"},
            "failure_impact": "process_shutdown"
        }
    )
    logical_conditions: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Logical conditions and rules governing the connection",
        example=[
            {
                "condition": "pressure > 10 bar",
                "action": "close_inlet_valve",
                "priority": "emergency",
                "delay": {"value": 0, "unit": "seconds"}
            }
        ]
    )
    physical_specifications: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Physical specifications if applicable",
        example={
            "line_size": {"value": 6, "unit": "inches"},
            "material": "316L SS",
            "design_pressure": {"value": 10, "unit": "barg"},
            "design_temperature": {"value": 150, "unit": "°C"}
        }
    )
    control_logic: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Control logic and automation rules",
        example={
            "control_type": "cascade",
            "master_controller": "FIC-101",
            "slave_controller": "TIC-101",
            "fallback_mode": "fail_safe"
        }
    )
    safety_implications: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Safety implications and requirements",
        example={
            "sil_level": "SIL 2",
            "risk_level": "high",
            "failure_mode": "fail_close",
            "safety_function": "pressure_protection"
        }
    )
    operational_states: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Valid operational states and transitions",
        example=[
            {
                "state": "normal_operation",
                "conditions": ["all_permissives_ok", "no_alarms"],
                "allowed_transitions": ["shutdown", "maintenance"]
            }
        ]
    )
    dependencies: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dependencies and relationships with other system elements",
        example=[
            {
                "entity_id": "TIC-101",
                "relationship": "provides_control_input",
                "criticality": "high"
            }
        ]
    )
    dynamic_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dynamic properties of the connection or relationship",
        example=[
            {
                "name": "reliability_index",
                "value": 0.99,
                "calculation_date": "2024-01-20"
            }
        ]
    )

class Event(BaseModel):
    """Model for process events, operational changes, and incidents"""
    id: str = Field(
        description="Unique event identifier",
        example="EV-2024-001"  # Event number 001 in 2024
    )
    type: str = Field(
        description="Type of process or operational event",
        example="process_upset"  # startup, shutdown, emergency, normal_operation_change
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the event",
        example="Sudden pressure drop in reactor feed system causing process upset and emergency shutdown initiation"
    )
    timestamp: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Timing details of the event",
        example={
            "start_time": "2024-01-15T14:30:00",
            "end_time": "2024-01-15T16:45:00",
            "duration": {"value": 2.25, "unit": "hours"},
            "detection_time": "2024-01-15T14:30:00",
            "response_time": "2024-01-15T14:32:00"
        }
    )
    severity: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Event severity classification",
        example={
            "level": "high",
            "safety_impact": "moderate",
            "production_impact": "significant",
            "equipment_impact": "minor",
            "environmental_impact": "none"
        }
    )
    conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Process conditions during the event",
        example={
            "pressure": {"value": 2.5, "unit": "barg", "normal": 10.0},
            "temperature": {"value": 150, "unit": "°C", "normal": 180},
            "flow_rate": {"value": 0, "unit": "m3/h", "normal": 100},
            "level": {"value": 85, "unit": "percent", "normal": 50}
        }
    )
    equipment_involved: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Equipment affected by or involved in the event",
        example=[
            {
                "id": "P-101",
                "type": "centrifugal_pump",
                "role": "primary_involved",
                "status": "tripped",
                "damage_assessment": "none"
            },
            {
                "id": "R-101",
                "type": "reactor",
                "role": "secondary_affected",
                "status": "emergency_shutdown",
                "damage_assessment": "none"
            }
        ]
    )
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical parameters monitored during the event",
        example=[
            {
                "name": "reactor_pressure",
                "trend": "rapid_decrease",
                "min_value": {"value": 2.5, "unit": "barg"},
                "max_value": {"value": 10.0, "unit": "barg"},
                "normal_range": {"min": 9.5, "max": 10.5, "unit": "barg"}
            }
        ]
    )
    root_cause: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Root cause analysis of the event",
        example={
            "primary_cause": "pump_mechanical_seal_failure",
            "contributing_factors": [
                "seal_wear",
                "inadequate_lubrication",
                "vibration"
            ],
            "verification_method": "visual_inspection",
            "confidence_level": "high"
        }
    )
    actions_taken: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Actions taken in response to the event",
        example=[
            {
                "time": "2024-01-15T14:32:00",
                "action": "emergency_shutdown_initiated",
                "operator": "John Smith",
                "result": "successful"
            },
            {
                "time": "2024-01-15T14:35:00",
                "action": "backup_pump_started",
                "operator": "John Smith",
                "result": "successful"
            }
        ]
    )
    consequences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Impact and consequences of the event",
        example={
            "production_loss": {"value": 50, "unit": "tons"},
            "downtime": {"value": 2.25, "unit": "hours"},
            "equipment_damage": "none",
            "environmental_release": "none",
            "safety_incidents": "none"
        }
    )
    notifications: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Notifications and communications during the event",
        example=[
            {
                "time": "2024-01-15T14:33:00",
                "type": "emergency_notification",
                "recipients": ["shift_supervisor", "maintenance"],
                "message": "Emergency shutdown due to pump failure"
            }
        ]
    )
    corrective_actions: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Corrective actions to prevent recurrence",
        example=[
            {
                "action": "replace_mechanical_seal",
                "priority": "high",
                "status": "completed",
                "completion_date": "2024-01-15T18:00:00",
                "verification": "post_maintenance_test"
            },
            {
                "action": "update_preventive_maintenance_schedule",
                "priority": "medium",
                "status": "in_progress",
                "due_date": "2024-01-22"
            }
        ]
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Related documentation and records",
        example=[
            {
                "type": "incident_report",
                "number": "IR-2024-001",
                "title": "Pump Seal Failure Incident",
                "date": "2024-01-15"
            },
            {
                "type": "work_order",
                "number": "WO-2024-123",
                "description": "Emergency Pump Repair",
                "status": "completed"
            }
        ]
    )
    lessons_learned: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Lessons learned and recommendations",
        example=[
            {
                "category": "maintenance",
                "finding": "Inadequate seal inspection frequency",
                "recommendation": "Increase inspection frequency to monthly",
                "implementation_status": "approved"
            },
            {
                "category": "monitoring",
                "finding": "Early warning signs missed",
                "recommendation": "Implement vibration monitoring",
                "implementation_status": "under_review"
            }
        ]
    )

class Risk(BaseModel):
    """Model for process and operational risk assessment"""
    id: str = Field(
        description="Unique risk identifier",
        example="RISK-2024-001"  # Risk assessment record 001
    )
    type: str = Field(
        description="Type of risk being assessed",
        example="process_safety"  # operational, environmental, mechanical_integrity
    )
    severity: str = Field(
        description="Severity level of the risk",
        example="high"  # low, medium, critical
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the risk scenario",
        example="Potential loss of containment in high-pressure reactor system due to mechanical seal failure"
    )
    hazard_identification: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Hazard identification details",
        example={
            "hazard_type": "pressure_containment",
            "source": "reactor_seal",
            "potential_causes": [
                "seal_degradation",
                "excessive_vibration",
                "pressure_excursion"
            ],
            "detection_methods": [
                "pressure_monitoring",
                "seal_pot_level",
                "vibration_analysis"
            ]
        }
    )
    risk_assessment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Risk assessment details",
        example={
            "likelihood": {
                "rating": "medium",
                "frequency": {"value": 1, "unit": "per_year"},
                "confidence_level": {"value": 80, "unit": "percent"}
            },
            "consequences": {
                "safety": {
                    "severity": "high",
                    "potential_impacts": ["personnel_injury", "equipment_damage"]
                },
                "environmental": {
                    "severity": "medium",
                    "potential_impacts": ["local_contamination"]
                },
                "economic": {
                    "severity": "high",
                    "estimated_cost": {"value": 1000000, "unit": "USD"}
                }
            },
            "risk_level": "high",
            "risk_matrix_position": {"likelihood": 3, "consequence": 4}
        }
    )
    affected_systems: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Systems and equipment affected by the risk",
        example=[
            {
                "system_id": "R-101",
                "system_type": "reactor",
                "vulnerability": "high",
                "critical_parameters": ["pressure", "temperature"]
            },
            {
                "system_id": "P-101",
                "system_type": "pump",
                "vulnerability": "medium",
                "critical_parameters": ["seal_pressure", "vibration"]
            }
        ]
    )
    existing_safeguards: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Existing risk control measures",
        example=[
            {
                "type": "engineering_control",
                "description": "High pressure shutdown system",
                "effectiveness": "high",
                "reliability": {"value": 99.9, "unit": "percent"},
                "testing_frequency": "monthly"
            },
            {
                "type": "procedural_control",
                "description": "Regular seal inspection program",
                "effectiveness": "medium",
                "frequency": "weekly"
            }
        ]
    )
    mitigation_measures: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Recommended risk mitigation measures",
        example=[
            {
                "measure": "install_dual_mechanical_seal",
                "type": "engineering",
                "priority": "high",
                "estimated_cost": {"value": 50000, "unit": "USD"},
                "implementation_timeline": {"value": 3, "unit": "months"},
                "expected_risk_reduction": {"value": 70, "unit": "percent"}
            }
        ]
    )
    monitoring_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Risk monitoring and review requirements",
        example={
            "parameters": [
                {
                    "name": "seal_pressure",
                    "normal_range": {"min": 5, "max": 10, "unit": "barg"},
                    "alarm_settings": {"low": 4, "high": 11, "unit": "barg"},
                    "monitoring_frequency": "continuous"
                }
            ],
            "inspections": [
                {
                    "type": "visual_inspection",
                    "frequency": "daily",
                    "responsibility": "operations"
                }
            ],
            "review_frequency": {"value": 6, "unit": "months"}
        }
    )
    emergency_response: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Emergency response procedures",
        example={
            "initial_response": [
                "activate_emergency_shutdown",
                "evacuate_area",
                "notify_emergency_response_team"
            ],
            "communication_protocol": {
                "primary_contact": "shift_supervisor",
                "emergency_numbers": ["internal_emergency", "fire_department"]
            },
            "response_resources": [
                "fire_fighting_equipment",
                "spill_containment_kit"
            ]
        }
    )
    regulatory_compliance: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Regulatory requirements and compliance",
        example={
            "applicable_regulations": [
                "OSHA_PSM",
                "EPA_RMP"
            ],
            "compliance_requirements": [
                "hazard_assessment",
                "management_of_change",
                "incident_investigation"
            ],
            "reporting_obligations": {
                "frequency": "annual",
                "authorities": ["regulatory_agency", "corporate_safety"]
            }
        }
    )
    historical_incidents: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Related historical incidents",
        example=[
            {
                "date": "2023-06-15",
                "description": "Minor seal leak detected during inspection",
                "consequences": "No injury or environmental impact",
                "corrective_actions": "Seal replacement",
                "lessons_learned": "Improve preventive maintenance frequency"
            }
        ]
    )
    review_status: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Risk assessment review status",
        example={
            "last_review": "2024-01-15",
            "reviewed_by": "Process Safety Team",
            "next_review_due": "2024-07-15",
            "review_findings": "Additional monitoring recommended",
            "action_items": [
                {
                    "item": "Update inspection procedure",
                    "status": "in_progress",
                    "due_date": "2024-02-15"
                }
            ]
        }
    )

class Action(BaseModel):
    """Model for actions"""
    id: str = Field(
        description="Unique action identifier",
        example="ACT-001"
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of action",
        example="emergency_procedure"
    )
    description: Optional[str] = Field(
        default=None,
        description="Action description",
        example="Emergency shutdown procedure"
    )
    steps: Optional[List[str]] = Field(
        default_factory=list,
        description="Sequential steps of the action",
        example=["Stop feed pump", "Close main valve"]
    )
    required_parameters: Optional[List[str]] = Field(
        default_factory=list,
        description="Parameters to be monitored/controlled",
        example=["pressure", "temperature"]
    )
    equipment_involved: Optional[List[str]] = Field(
        default_factory=list,
        description="Equipment involved in the action",
        example=["P-101", "V-102"]
    )
    personnel: Optional[List[str]] = Field(
        default_factory=list,
        description="Required personnel",
        example=["Operator", "Supervisor"]
    )
    timeframe: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Time-related requirements",
        example={"duration": "30 minutes", "frequency": "daily"}
    )
    source_text: Optional[str] = Field(
        default=None,
        description="Source text from documentation",
        example="In case of emergency, immediately stop the feed pump"
    )
    confidence: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of extraction",
        example=0.95
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of source text",
        example="RU"
    )
    dynamic_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dynamic properties extracted from documentation",
        example=[{"name": "last_revision", "value": "2024-01-01"}]
    )

class ProcessRelationship(BaseModel):
    """Model for relationships and dependencies between process elements"""
    id: str = Field(
        description="Unique relationship identifier",
        example="REL-2024-001"  # Relationship identifier 001 in 2024
    )
    from_entity: str = Field(
        description="Source entity identifier in the relationship",
        example="R-101"  # Source entity (e.g., Reactor 101)
    )
    to_entity: str = Field(
        description="Target entity identifier in the relationship",
        example="E-102"  # Target entity (e.g., Heat Exchanger 102)
    )
    relationship_type: str = Field(
        description="Type of relationship between entities",
        example="heat_integration"  # process_flow, control_dependency, safety_interlock
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the relationship",
        example="Reactor effluent heat recovery to feed preheating with minimum approach temperature control"
    )
    nature: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Nature and characteristics of the relationship",
        example={
            "category": "process_integration",
            "criticality": "high",
            "bidirectional": True,
            "strength": "strong",
            "variability": "dynamic"
        }
    )
    operational_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Operating parameters governing the relationship",
        example=[
            {
                "parameter": "temperature_approach",
                "normal_value": {"value": 20, "unit": "°C"},
                "minimum": {"value": 15, "unit": "°C"},
                "maximum": {"value": 30, "unit": "°C"},
                "criticality": "high"
            },
            {
                "parameter": "heat_duty",
                "normal_value": {"value": 5000, "unit": "kW"},
                "range": {"min": 4000, "max": 6000, "unit": "kW"},
                "monitoring": "continuous"
            }
        ]
    )
    control_aspects: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Control relationships and dependencies",
        example={
            "control_type": "cascade",
            "master_controller": "TIC-101",
            "slave_controller": "FIC-102",
            "override_conditions": [
                {
                    "parameter": "min_approach_temperature",
                    "limit": {"value": 15, "unit": "°C"},
                    "action": "reduce_throughput"
                }
            ]
        }
    )
    safety_implications: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety implications of the relationship",
        example=[
            {
                "scenario": "loss_of_heat_integration",
                "consequence": "reactor_feed_temperature_drop",
                "severity": "medium",
                "safeguards": [
                    "backup_heating_system",
                    "automatic_throughput_reduction"
                ]
            }
        ]
    )
    optimization_objectives: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Optimization objectives for the relationship",
        example=[
            {
                "objective": "maximize_heat_recovery",
                "constraint": "minimum_approach_temperature",
                "priority": "high",
                "measurement": "energy_savings",
                "target": {"value": 5500, "unit": "kW"}
            }
        ]
    )
    dependencies: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Dependencies and related relationships",
        example=[
            {
                "entity_id": "P-101",
                "relationship": "flow_provider",
                "criticality": "high",
                "impact_on_relationship": "direct"
            },
            {
                "entity_id": "FIC-101",
                "relationship": "flow_control",
                "criticality": "medium",
                "impact_on_relationship": "indirect"
            }
        ]
    )
    constraints: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Operational constraints on the relationship",
        example=[
            {
                "type": "temperature_constraint",
                "description": "Minimum approach temperature",
                "value": {"min": 15, "unit": "°C"},
                "enforcement": "hard_constraint",
                "violation_action": "reduce_throughput"
            }
        ]
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Performance indicators for the relationship",
        example={
            "energy_efficiency": {
                "current": {"value": 85, "unit": "percent"},
                "target": {"value": 90, "unit": "percent"},
                "monitoring": "continuous"
            },
            "stability": {
                "measure": "variance",
                "value": {"value": 2.5, "unit": "percent"},
                "acceptable_range": {"max": 5, "unit": "percent"}
            }
        }
    )
    maintenance_implications: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Maintenance considerations for the relationship",
        example=[
            {
                "aspect": "heat_exchanger_cleaning",
                "frequency": {"value": 6, "unit": "months"},
                "impact": "reduced_heat_transfer",
                "mitigation": "scheduled_cleaning",
                "coordination_required": ["production_planning", "maintenance"]
            }
        ]
    )
    dynamic_behavior: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dynamic characteristics of the relationship",
        example={
            "response_time": {"value": 30, "unit": "minutes"},
            "stability": "stable",
            "oscillatory_tendency": "low",
            "disturbance_sensitivity": "medium"
        }
    )

class Equipment(BaseModel):
    """Model for process equipment specification and characteristics"""
    id: str = Field(
        description="Unique equipment identifier in the process system",
        example="HE-101"  # Heat Exchanger 101
    )
    name: Optional[str] = Field(
        default=None,
        description="Descriptive name of the equipment",
        example="Feed/Effluent Heat Exchanger"
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of process equipment",
        example="shell_and_tube_heat_exchanger"  # centrifugal_pump, distillation_column
    )
    service: Optional[str] = Field(
        default=None,
        description="Primary service or function of the equipment",
        example="Process feed preheating using reactor effluent"
    )
    design_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Key design parameters and specifications",
        example={
            "heat_transfer_area": {"value": 500, "unit": "m2"},
            "design_pressure": {
                "shell_side": {"value": 10, "unit": "barg"},
                "tube_side": {"value": 20, "unit": "barg"}
            },
            "design_temperature": {
                "shell_side": {"value": 200, "unit": "°C"},
                "tube_side": {"value": 300, "unit": "°C"}
            },
            "material_of_construction": {
                "shell": "carbon_steel",
                "tubes": "316L_stainless_steel",
                "tube_sheet": "316L_stainless_steel"
            }
        }
    )
    operating_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Normal operating parameters",
        example={
            "shell_side": {
                "fluid": "hot_reactor_effluent",
                "flow_rate": {"value": 100, "unit": "m3/h"},
                "inlet_temperature": {"value": 280, "unit": "°C"},
                "outlet_temperature": {"value": 160, "unit": "°C"},
                "operating_pressure": {"value": 8, "unit": "barg"}
            },
            "tube_side": {
                "fluid": "cold_process_feed",
                "flow_rate": {"value": 80, "unit": "m3/h"},
                "inlet_temperature": {"value": 120, "unit": "°C"},
                "outlet_temperature": {"value": 240, "unit": "°C"},
                "operating_pressure": {"value": 15, "unit": "barg"}
            }
        }
    )
    performance_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Key performance indicators",
        example={
            "heat_duty": {"value": 5000, "unit": "kW"},
            "heat_transfer_coefficient": {"value": 750, "unit": "W/m2K"},
            "pressure_drop": {
                "shell_side": {"value": 0.5, "unit": "bar"},
                "tube_side": {"value": 0.8, "unit": "bar"}
            },
            "effectiveness": {"value": 0.85, "unit": "ratio"}
        }
    )
    mechanical_design: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Mechanical design specifications",
        example={
            "shell_diameter": {"value": 1000, "unit": "mm"},
            "tube_details": {
                "outer_diameter": {"value": 25, "unit": "mm"},
                "wall_thickness": {"value": 2.5, "unit": "mm"},
                "length": {"value": 6, "unit": "m"},
                "number": 500,
                "layout": "triangular",
                "pitch": {"value": 31.25, "unit": "mm"}
            },
            "number_of_passes": {
                "shell": 1,
                "tube": 4
            },
            "baffle_details": {
                "type": "single_segmental",
                "cut": {"value": 25, "unit": "percent"},
                "spacing": {"value": 500, "unit": "mm"}
            }
        }
    )
    instruments: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Associated instrumentation",
        example=[
            {
                "tag": "TI-1001",
                "type": "temperature_indicator",
                "location": "shell_inlet",
                "range": {"min": 0, "max": 400, "unit": "°C"}
            },
            {
                "tag": "PI-1001",
                "type": "pressure_indicator",
                "location": "tube_inlet",
                "range": {"min": 0, "max": 25, "unit": "barg"}
            }
        ]
    )
    connections: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process and utility connections",
        example=[
            {
                "id": "shell_inlet",
                "type": "process",
                "size": {"value": 8, "unit": "inches"},
                "rating": "ANSI_150",
                "location": "shell_end"
            },
            {
                "id": "tube_inlet",
                "type": "process",
                "size": {"value": 6, "unit": "inches"},
                "rating": "ANSI_300",
                "location": "channel_end"
            }
        ]
    )
    maintenance_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Maintenance specifications and requirements",
        example=[
            {
                "task": "tube_bundle_cleaning",
                "frequency": {"value": 12, "unit": "months"},
                "procedure": "chemical_cleaning",
                "acceptance_criteria": "pressure_drop_within_10_percent_of_design"
            },
            {
                "task": "thickness_monitoring",
                "frequency": {"value": 6, "unit": "months"},
                "locations": ["shell_inlet", "tube_sheet"],
                "method": "ultrasonic_testing"
            }
        ]
    )
    safety_features: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety features and protection devices",
        example=[
            {
                "type": "pressure_relief_valve",
                "tag": "PSV-1001",
                "location": "shell_side",
                "set_pressure": {"value": 11, "unit": "barg"},
                "capacity": {"value": 150, "unit": "m3/h"}
            }
        ]
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Associated technical documentation",
        example=[
            {
                "type": "datasheet",
                "number": "DS-HE101-001",
                "revision": "2",
                "date": "2024-01-15"
            },
            {
                "type": "drawing",
                "number": "DWG-HE101-001",
                "revision": "1",
                "date": "2024-01-15"
            }
        ]
    )
    vendor_information: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Equipment vendor and manufacturing information",
        example={
            "manufacturer": "Heat Transfer Solutions Inc.",
            "model_number": "STS-500-4",
            "serial_number": "12345",
            "manufacturing_date": "2023-06-15",
            "warranty_period": {"value": 24, "unit": "months"}
        }
    )
    cost_information: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cost and economic information",
        example={
            "purchase_cost": {"value": 250000, "unit": "USD"},
            "installation_cost": {"value": 75000, "unit": "USD"},
            "annual_maintenance_cost": {"value": 15000, "unit": "USD"},
            "replacement_value": {"value": 350000, "unit": "USD"}
        }
    )

class ComponentProperty(BaseModel):
    """Model for component properties in a flow"""
    name: str = Field(
        description="Component name",
        example="methane"
    )
    concentration: Union[float, Dict[str, float]] = Field(
        default=0.0,  # Добавили default для float
        description="Component concentration or range",
        example={"min": 0.85, "max": 0.95}
    )
    unit: str = Field(
        description="Concentration unit",
        example="mol%"
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional description",
        example="Main component"
    )

class PhysicalProperty(BaseModel):
    """Model for physical properties of a flow"""
    name: str = Field(
        description="Property name",
        example="density"
    )
    value: Union[float, Dict[str, float]] = Field(
        default=0.0,  # Добавили только default для валидации
        description="Property value or range",
        example={"min": 800, "max": 850}
    )
    unit: str = Field(
        description="Property unit",
        example="kg/m3"
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional description",
        example="At operating conditions"
    )

class Flow(BaseModel):
    """Model for process flows and stream specifications"""
    id: str = Field(
        description="Unique process flow identifier",
        example="F-101"  # Flow/Stream 101
    )
    name: Optional[str] = Field(
        default=None,
        description="Descriptive name of the process flow",
        example="Reactor Feed Stream"
    )
    type: str = Field(
        description="Type of process flow or stream",
        example="process_feed"  # product, intermediate, utility, waste
    )
    phase_state: str = Field(
        description="Physical state of the flow",
        example="liquid"  # vapor, two_phase, supercritical
    )
    from_equipment: Optional[str] = Field(
        default=None,
        description="Source equipment identifier",
        example="P-101"  # Pump 101
    )
    to_equipment: Optional[str] = Field(
        default=None,
        description="Destination equipment identifier",
        example="R-101"  # Reactor 101
    )
    components: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Chemical composition of the flow",
        example=[
            {
                "name": "n-hexane",
                "formula": "C6H14",
                "concentration": {"value": 85.0, "unit": "mol%"},
                "phase": "liquid",
                "is_key_component": True
            },
            {
                "name": "n-heptane",
                "formula": "C7H16",
                "concentration": {"value": 15.0, "unit": "mol%"},
                "phase": "liquid",
                "is_key_component": False
            }
        ]
    )
    physical_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Physical properties of the flow",
        example=[
            {
                "property": "density",
                "value": 680.0,
                "unit": "kg/m3",
                "conditions": {
                    "temperature": {"value": 25, "unit": "°C"},
                    "pressure": {"value": 1, "unit": "atm"}
                }
            },
            {
                "property": "viscosity",
                "value": 0.45,
                "unit": "cP",
                "conditions": {
                    "temperature": {"value": 25, "unit": "°C"}
                }
            },
            {
                "property": "thermal_conductivity",
                "value": 0.13,
                "unit": "W/m·K",
                "conditions": {
                    "temperature": {"value": 25, "unit": "°C"}
                }
            }
        ]
    )
    operating_conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating conditions of the flow",
        example={
            "pressure": {
                "value": 10.0,
                "unit": "barg",
                "min": 8.0,
                "max": 12.0,
                "design": 15.0
            },
            "temperature": {
                "value": 80.0,
                "unit": "°C",
                "min": 75.0,
                "max": 85.0,
                "design": 100.0
            },
            "flow_rate": {
                "value": 100.0,
                "unit": "m3/h",
                "min": 80.0,
                "max": 120.0,
                "design": 125.0
            }
        }
    )
    design_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Design parameters for the flow",
        example={
            "line_size": {"value": 6, "unit": "inches"},
            "material": "carbon_steel",
            "insulation": {
                "type": "mineral_wool",
                "thickness": {"value": 50, "unit": "mm"}
            },
            "design_velocity": {"value": 2.5, "unit": "m/s"}
        }
    )
    quality_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Quality specifications and requirements",
        example={
            "contaminants": {
                "water": {"max": 50, "unit": "ppm"},
                "sulfur": {"max": 10, "unit": "ppm"}
            },
            "physical_properties": {
                "reid_vapor_pressure": {"max": 0.7, "unit": "bar"},
                "flash_point": {"min": 35, "unit": "°C"}
            }
        }
    )
    instrumentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Flow measurement and monitoring instruments",
        example=[
            {
                "tag": "FT-101",
                "type": "flow_transmitter",
                "technology": "coriolis",
                "range": {"min": 0, "max": 150, "unit": "m3/h"},
                "accuracy": {"value": 0.5, "unit": "percent"}
            },
            {
                "tag": "TT-101",
                "type": "temperature_transmitter",
                "range": {"min": 0, "max": 150, "unit": "°C"}
            }
        ]
    )
    safety_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Safety considerations and requirements",
        example={
            "hazard_classification": "flammable_liquid",
            "flash_point": {"value": 35, "unit": "°C"},
            "auto_ignition_temperature": {"value": 225, "unit": "°C"},
            "protective_measures": [
                "earthing_required",
                "explosion_proof_equipment"
            ]
        }
    )
    energy_content: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Energy characteristics of the flow",
        example={
            "heating_value": {"value": 45000, "unit": "kJ/kg"},
            "specific_heat": {"value": 2.2, "unit": "kJ/kg·K"},
            "enthalpy": {"value": 250, "unit": "kJ/kg"}
        }
    )
    economic_value: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic characteristics of the flow",
        example={
            "unit_cost": {"value": 500, "unit": "USD/ton"},
            "annual_value": {"value": 5000000, "unit": "USD/year"},
            "quality_premium": {"value": 25, "unit": "USD/ton"}
        }
    )

class Corrosion(BaseModel):
    """Model for tracking and analyzing corrosion in process equipment"""
    id: str = Field(
        description="Unique corrosion case identifier",
        example="COR-2024-HE101-01"
    )
    type: str = Field(
        description="Type of corrosion mechanism",
        example="pitting_corrosion"  # uniform_corrosion, stress_corrosion_cracking, galvanic_corrosion
    )
    location: Optional[str] = Field(
        default=None,
        description="Specific location of corrosion in equipment",
        example="Heat exchanger tube sheet, inlet side, tubes 15-20 in outer ring"
    )
    equipment_id: str = Field(
        description="Identifier of affected equipment",
        example="HE-101"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of corrosion issue",
        example="Localized pitting corrosion observed on 316L stainless steel tube sheet, concentrated near seawater inlet"
    )
    rate: Optional[float] = Field(
        default=None,
        description="Measured corrosion rate",
        example=0.5  # mm/year
    )
    rate_unit: Optional[str] = Field(
        default=None,
        description="Unit of corrosion rate measurement",
        example="mm/year"
    )
    severity_assessment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Assessment of corrosion severity and impact",
        example={
            "level": "high",
            "wall_thickness_remaining": {"value": 4.5, "unit": "mm"},
            "minimum_required_thickness": {"value": 3.8, "unit": "mm"},
            "estimated_remaining_life": {"value": 2, "unit": "years"},
            "risk_level": "significant",
            "immediate_action_required": True
        }
    )
    monitoring_data: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Corrosion monitoring measurements and observations",
        example=[
            {
                "date": "2024-01-15",
                "method": "ultrasonic_thickness",
                "location": "TS-point-1",
                "reading": {"value": 4.5, "unit": "mm"},
                "baseline": {"value": 6.0, "unit": "mm"},
                "inspector": "John Smith"
            },
            {
                "date": "2024-01-15",
                "method": "visual_inspection",
                "findings": "Multiple pits observed, max depth 1.5mm",
                "photos": ["COR-HE101-P001", "COR-HE101-P002"]
            }
        ]
    )
    root_cause_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Analysis of corrosion root causes",
        example={
            "primary_causes": [
                "chloride_concentration_exceeds_limits",
                "local_flow_turbulence",
                "temperature_above_design"
            ],
            "contributing_factors": [
                "inadequate_chemical_treatment",
                "periodic_stagnant_conditions"
            ],
            "verification_tests": [
                "water_analysis",
                "metallurgical_examination"
            ]
        }
    )
    environmental_conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Environmental conditions contributing to corrosion",
        example={
            "process_fluid": "seawater",
            "temperature": {"value": 65, "unit": "°C"},
            "pressure": {"value": 4, "unit": "barg"},
            "flow_velocity": {"value": 1.5, "unit": "m/s"},
            "pH": 6.5,
            "chlorides": {"value": 19000, "unit": "ppm"},
            "oxygen_content": {"value": 7, "unit": "ppb"}
        }
    )
    material_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Material specifications and properties",
        example={
            "material": "316L stainless steel",
            "composition": {
                "Cr": "16-18%",
                "Ni": "10-14%",
                "Mo": "2-3%"
            },
            "heat_treatment": "solution_annealed",
            "surface_condition": "pickled_and_passivated"
        }
    )
    mitigation_measures: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Implemented and planned corrosion mitigation measures",
        example=[
            {
                "type": "chemical_treatment",
                "description": "Increased inhibitor dosage",
                "implementation_date": "2024-01-20",
                "effectiveness": "under_evaluation"
            },
            {
                "type": "operational_change",
                "description": "Reduced operating temperature",
                "implementation_date": "2024-01-15",
                "effectiveness": "positive"
            }
        ]
    )
    inspection_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Inspection and monitoring requirements",
        example={
            "methods": ["UT_thickness", "visual_inspection", "pit_depth_measurement"],
            "frequency": "monthly",
            "critical_locations": ["tube_sheet_inlet", "first_pass_tubes"],
            "acceptance_criteria": {
                "minimum_thickness": {"value": 3.8, "unit": "mm"},
                "maximum_pit_depth": {"value": 2.0, "unit": "mm"}
            }
        }
    )
    repair_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="History of repairs and interventions",
        example=[
            {
                "date": "2023-07-15",
                "type": "weld_overlay",
                "location": "tube_sheet_face",
                "contractor": "Specialty Welding Inc",
                "work_reference": "WO-2023-156",
                "post_repair_inspection": "passed"
            }
        ]
    )
    economic_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic impact assessment",
        example={
            "monitoring_costs": {"value": 5000, "unit": "USD/year"},
            "repair_costs": {"value": 25000, "unit": "USD"},
            "production_loss": {"value": 50000, "unit": "USD"},
            "estimated_replacement_cost": {"value": 150000, "unit": "USD"}
        }
    )
    recommendations: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Recommendations for corrosion management",
        example=[
            {
                "priority": "high",
                "action": "Replace tube sheet with higher grade alloy",
                "estimated_cost": {"value": 75000, "unit": "USD"},
                "implementation_timeline": "Next shutdown",
                "expected_benefit": "Extended equipment life by 10 years"
            }
        ]
    )

class Fouling(BaseModel):
    """Model for tracking and analyzing fouling in process equipment"""
    id: str = Field(
        description="Unique fouling case identifier",
        example="FOUL-2024-HE101-01"  # Fouling case 01 for Heat Exchanger 101 in 2024
    )
    type: str = Field(
        description="Type of fouling mechanism",
        example="crystallization_fouling"  # particulate_fouling, chemical_reaction_fouling, biological_fouling
    )
    location: Optional[str] = Field(
        default=None,
        description="Specific location of fouling in equipment",
        example="Tube-side inlet passes, first 1 meter of tubes in lower bundle"
    )
    equipment_id: str = Field(
        description="Identifier of affected equipment",
        example="HE-101"  # Heat Exchanger 101
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of fouling issue",
        example="Calcium carbonate scale formation on tube inner surfaces, predominantly in inlet passes"
    )
    severity_assessment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Assessment of fouling severity and impact",
        example={
            "level": "moderate",
            "heat_transfer_reduction": {"value": 25, "unit": "percent"},
            "pressure_drop_increase": {"value": 35, "unit": "percent"},
            "estimated_thickness": {"value": 2.5, "unit": "mm"},
            "affected_area": {"value": 30, "unit": "percent"}
        }
    )
    monitoring_data: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Fouling monitoring measurements and observations",
        example=[
            {
                "date": "2024-01-15",
                "parameter": "heat_transfer_coefficient",
                "value": {"current": 750, "clean": 1000, "unit": "W/m²K"},
                "fouling_factor": {"value": 0.0003, "unit": "m²K/W"}
            },
            {
                "date": "2024-01-15",
                "parameter": "pressure_drop",
                "value": {"current": 1.2, "clean": 0.8, "unit": "bar"},
                "increase": {"value": 50, "unit": "percent"}
            }
        ]
    )
    composition: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Chemical composition of fouling deposits",
        example=[
            {
                "compound": "calcium_carbonate",
                "formula": "CaCO3",
                "concentration": {"value": 65, "unit": "weight_percent"},
                "form": "crystalline"
            },
            {
                "compound": "iron_oxide",
                "formula": "Fe2O3",
                "concentration": {"value": 15, "unit": "weight_percent"},
                "form": "amorphous"
            }
        ]
    )
    operating_conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating conditions contributing to fouling",
        example={
            "temperature": {
                "bulk": {"value": 75, "unit": "°C"},
                "wall": {"value": 95, "unit": "°C"},
                "critical_value": 85
            },
            "flow_velocity": {"value": 1.5, "unit": "m/s"},
            "reynolds_number": 15000,
            "supersaturation_ratio": 2.5
        }
    )
    rate: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Fouling rate characteristics",
        example={
            "thickness_growth": {"value": 0.1, "unit": "mm/month"},
            "thermal_resistance_increase": {"value": 0.0001, "unit": "m²K/W/month"},
            "pressure_drop_increase": {"value": 0.1, "unit": "bar/month"},
            "pattern": "asymptotic"  # linear, falling, accelerating
        }
    )
    cleaning_methods: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Applicable cleaning methods and their effectiveness",
        example=[
            {
                "method": "chemical_cleaning",
                "chemical": "hydrochloric_acid",
                "concentration": {"value": 5, "unit": "percent"},
                "temperature": {"value": 40, "unit": "°C"},
                "duration": {"value": 6, "unit": "hours"},
                "effectiveness": {"value": 95, "unit": "percent"}
            },
            {
                "method": "mechanical_cleaning",
                "technique": "hydroblasting",
                "pressure": {"value": 1000, "unit": "bar"},
                "effectiveness": {"value": 90, "unit": "percent"}
            }
        ]
    )
    prevention_measures: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Fouling prevention and mitigation measures",
        example=[
            {
                "measure": "antiscalant_dosing",
                "chemical": "phosphonate_based",
                "dosage": {"value": 5, "unit": "ppm"},
                "effectiveness": "high"
            },
            {
                "measure": "flow_velocity_control",
                "minimum": {"value": 1.2, "unit": "m/s"},
                "target": {"value": 1.5, "unit": "m/s"},
                "effectiveness": "moderate"
            }
        ]
    )
    economic_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic impact assessment",
        example={
            "energy_loss": {"value": 50000, "unit": "USD/year"},
            "cleaning_cost": {"value": 15000, "unit": "USD/event"},
            "production_loss": {"value": 25000, "unit": "USD/event"},
            "total_annual_impact": {"value": 120000, "unit": "USD/year"}
        }
    )
    cleaning_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="History of cleaning operations",
        example=[
            {
                "date": "2023-07-15",
                "method": "chemical_cleaning",
                "effectiveness": {"value": 95, "unit": "percent"},
                "cost": {"value": 15000, "unit": "USD"},
                "downtime": {"value": 24, "unit": "hours"}
            }
        ]
    )
    recommendations: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Recommendations for fouling management",
        example=[
            {
                "category": "prevention",
                "action": "install_online_monitoring",
                "priority": "high",
                "cost": {"value": 25000, "unit": "USD"},
                "benefit": "Early detection and intervention"
            },
            {
                "category": "operation",
                "action": "increase_flow_velocity",
                "priority": "medium",
                "cost": {"value": 0, "unit": "USD"},
                "benefit": "Reduce deposition rate"
            }
        ]
    )

class CoolingSystem(BaseModel):
    """Model for industrial cooling water systems and cooling circuits"""
    id: str = Field(
        description="Unique cooling system identifier",
        example="CWS-101"
    )
    type: str = Field(
        description="Type of cooling system configuration",
        example="closed_loop"  # open_loop, once_through, hybrid
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of cooling system and its purpose",
        example="Closed-loop cooling water system serving process heat exchangers in Unit 100"
    )
    equipment_served: Optional[List[str]] = Field(
        default_factory=list,
        description="List of equipment IDs served by this cooling system",
        example=["E-101", "E-102", "R-101-jacket"]
    )
    water_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical cooling water parameters and specifications",
        example=[
            {
                "parameter": "supply_temperature",
                "normal": 30,
                "max": 35,
                "unit": "°C",
                "monitoring": "continuous"
            },
            {
                "parameter": "return_temperature",
                "normal": 40,
                "max": 45,
                "unit": "°C",
                "monitoring": "continuous"
            },
            {
                "parameter": "pressure",
                "normal": 4,
                "min": 3,
                "max": 6,
                "unit": "barg"
            }
        ]
    )
    water_treatment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Water treatment system specifications and requirements",
        example={
            "chemicals": [
                {
                    "name": "corrosion_inhibitor",
                    "dosage": 100,
                    "unit": "ppm",
                    "control": "automatic"
                },
                {
                    "name": "biocide",
                    "dosage": 5,
                    "unit": "ppm",
                    "frequency": "weekly"
                }
            ],
            "monitoring_parameters": [
                "pH",
                "conductivity",
                "chlorides",
                "bacterial_count"
            ]
        }
    )
    cooling_tower: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cooling tower specifications and operating parameters",
        example={
            "type": "induced_draft",
            "capacity": {"value": 1000, "unit": "m3/h"},
            "design_parameters": {
                "wet_bulb": {"value": 28, "unit": "°C"},
                "approach": {"value": 5, "unit": "°C"},
                "range": {"value": 10, "unit": "°C"}
            },
            "fan_details": {
                "quantity": 2,
                "power": {"value": 75, "unit": "kW"},
                "control": "variable_speed"
            }
        }
    )
    pumps: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Cooling water circulation pump specifications",
        example=[
            {
                "id": "P-101",
                "type": "centrifugal",
                "service": "main_circulation",
                "capacity": {"value": 1000, "unit": "m3/h"},
                "head": {"value": 40, "unit": "m"},
                "power": {"value": 132, "unit": "kW"},
                "configuration": "duty"
            },
            {
                "id": "P-102",
                "type": "centrifugal",
                "service": "main_circulation",
                "configuration": "standby"
            }
        ]
    )
    heat_exchangers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Heat exchangers in the cooling system",
        example=[
            {
                "id": "E-101",
                "service": "process_cooling",
                "duty": {"value": 5000, "unit": "kW"},
                "design_temperatures": {
                    "cw_inlet": {"value": 30, "unit": "°C"},
                    "cw_outlet": {"value": 40, "unit": "°C"}
                }
            }
        ]
    )
    operational_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="System operational limits and constraints",
        example={
            "max_system_pressure": {"value": 6, "unit": "barg"},
            "min_flow_rate": {"value": 500, "unit": "m3/h"},
            "max_return_temperature": {"value": 45, "unit": "°C"},
            "water_quality_limits": {
                "pH": {"min": 7.0, "max": 8.5},
                "conductivity": {"max": 2500, "unit": "µS/cm"},
                "chlorides": {"max": 200, "unit": "ppm"}
            }
        }
    )
    quality_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Water quality monitoring parameters",
        example=[
            {
                "parameter": "pH",
                "normal_range": {"min": 7.0, "max": 8.5},
                "monitoring_frequency": "continuous",
                "control_method": "acid_dosing"
            },
            {
                "parameter": "corrosion_rate",
                "target": {"max": 0.1, "unit": "mm/year"},
                "monitoring_frequency": "monthly"
            }
        ]
    )
    makeup_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Makeup water specifications and requirements",
        example={
            "source": "demineralized_water",
            "average_rate": {"value": 10, "unit": "m3/h"},
            "quality_requirements": {
                "conductivity": {"max": 10, "unit": "µS/cm"},
                "silica": {"max": 0.1, "unit": "ppm"}
            },
            "control": "automatic_level_control"
        }
    )
    blowdown_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Blowdown specifications and control parameters",
        example={
            "control_basis": "conductivity",
            "setpoint": {"value": 2000, "unit": "µS/cm"},
            "average_rate": {"value": 5, "unit": "m3/h"},
            "disposal": "neutralization_pit"
        }
    )
    energy_efficiency: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Energy efficiency parameters and monitoring",
        example={
            "specific_power": {"value": 0.15, "unit": "kW/RT"},
            "efficiency_indicators": {
                "approach_temperature": {"target": 5, "unit": "°C"},
                "cycles_of_concentration": {"target": 6}
            }
        }
    )
    maintenance_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Maintenance requirements and schedules",
        example=[
            {
                "item": "cooling_tower_fill",
                "frequency": "annual",
                "type": "inspection_cleaning",
                "procedure": "CT-MAINT-001"
            },
            {
                "item": "water_quality",
                "frequency": "daily",
                "type": "monitoring",
                "parameters": ["pH", "conductivity", "chlorine"]
            }
        ]
    )

class MaintenanceTask(BaseModel):
    """Model for individual maintenance tasks"""
    id: str = Field(
        description="Unique task identifier",
        example="TASK-001"
    )
    description: Optional[str] = Field(
        default=None,
        description="Task description",
        example="Pump bearing inspection and lubrication"
    )
    duration: Optional[float] = Field(
        default=None,
        description="Task duration",
        example=2.5
    )
    duration_unit: Optional[str] = Field(
        default=None,
        description="Duration unit",
        example="hours"
    )
    required_personnel: Optional[List[str]] = Field(
        default_factory=list,
        description="Required personnel",
        example=["mechanic", "supervisor"]
    )
    tools_equipment: Optional[List[str]] = Field(
        default_factory=list,
        description="Required tools and equipment",
        example=["grease gun", "bearing puller"]
    )
    safety_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Safety requirements",
        example=["safety glasses", "gloves"]
    )
    steps: Optional[List[str]] = Field(
        default_factory=list,
        description="Task steps",
        example=["Stop equipment", "Lock out power"]
    )
    acceptance_criteria: Optional[List[str]] = Field(
        default=None,
        description="Acceptance criteria",
        example=["No unusual noise", "Normal temperature"]
    )

class MaintenanceSchedule(BaseModel):
    """Model for maintenance scheduling"""
    frequency: Optional[float] = Field(
        default=None,
        description="Maintenance frequency",
        example=30
    )
    frequency_unit: Optional[str] = Field(
        default=None,
        description="Frequency unit",
        example="days"
    )
    last_performed: Optional[datetime] = Field(
        default=None,
        description="Last maintenance date",
        example="2024-01-15T10:00:00"
    )
    next_due: Optional[datetime] = Field(
        default=None,
        description="Next maintenance due date",
        example="2024-02-15T10:00:00"
    )
    flexibility: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Schedule flexibility",
        example={"early": "5 days", "late": "3 days"}
    )

class Maintenance(BaseModel):
    """Model for maintenance activities and maintenance management"""
    id: str = Field(
        description="Unique maintenance activity identifier",
        example="MAINT-2024-HE101-01"  # Maintenance activity 01 for Heat Exchanger 101 in 2024
    )
    type: str = Field(
        description="Type of maintenance activity",
        example="preventive_maintenance"  # corrective_maintenance, predictive_maintenance, condition_based
    )
    category: str = Field(
        description="Category of maintenance work",
        example="mechanical"  # electrical, instrumentation, civil, inspection
    )
    equipment_id: str = Field(
        description="Equipment identifier for maintenance target",
        example="HE-101"  # Heat Exchanger 101
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of maintenance activity",
        example="Annual preventive maintenance of shell and tube heat exchanger including tube bundle cleaning and inspection"
    )
    schedule: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Maintenance scheduling information",
        example={
            "planned_start": "2024-03-15T08:00:00",
            "planned_end": "2024-03-17T16:00:00",
            "duration": {"value": 20, "unit": "hours"},
            "frequency": {"value": 12, "unit": "months"},
            "last_performed": "2023-03-15",
            "next_due": "2024-03-15"
        }
    )
    tasks: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Detailed maintenance tasks to be performed",
        example=[
            {
                "task_id": "T001",
                "description": "Remove tube bundle",
                "duration": {"value": 4, "unit": "hours"},
                "required_skills": ["mechanical_technician"],
                "tools_required": ["bundle_puller", "crane"],
                "safety_requirements": ["confined_space_permit", "lifting_permit"]
            },
            {
                "task_id": "T002",
                "description": "High pressure water cleaning of tubes",
                "duration": {"value": 8, "unit": "hours"},
                "required_skills": ["cleaning_specialist"],
                "tools_required": ["hydroblasting_unit"],
                "safety_requirements": ["high_pressure_work_permit"]
            }
        ]
    )
    resources: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Resources required for maintenance",
        example={
            "personnel": [
                {"role": "mechanical_technician", "quantity": 2, "hours": 16},
                {"role": "supervisor", "quantity": 1, "hours": 4}
            ],
            "equipment": [
                {"item": "mobile_crane", "duration": {"value": 4, "unit": "hours"}},
                {"item": "hydroblasting_unit", "duration": {"value": 8, "unit": "hours"}}
            ],
            "materials": [
                {"item": "gaskets", "quantity": 2, "specification": "spiral_wound_316L"},
                {"item": "cleaning_chemicals", "quantity": {"value": 100, "unit": "liters"}}
            ]
        }
    )
    procedures: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Reference procedures and work instructions",
        example=[
            {
                "document_id": "SOP-HE-001",
                "title": "Heat Exchanger Bundle Removal",
                "revision": "Rev.3",
                "type": "standard_operating_procedure"
            },
            {
                "document_id": "WI-HE-002",
                "title": "Tube Bundle Cleaning Procedure",
                "revision": "Rev.2",
                "type": "work_instruction"
            }
        ]
    )
    safety_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety requirements and precautions",
        example=[
            {
                "requirement": "confined_space_entry",
                "permit_type": "hot_work",
                "ppe": ["breathing_apparatus", "safety_harness"],
                "monitoring": ["oxygen_level", "toxic_gases"]
            },
            {
                "requirement": "isolation",
                "type": "lock_out_tag_out",
                "points": ["inlet_valve", "outlet_valve"],
                "verification": "pressure_test"
            }
        ]
    )
    quality_checks: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Quality control and acceptance criteria",
        example=[
            {
                "check": "tube_thickness",
                "method": "ultrasonic_testing",
                "acceptance_criteria": {"min": 2.5, "unit": "mm"},
                "sampling": "100%"
            },
            {
                "check": "pressure_test",
                "method": "hydrostatic_test",
                "acceptance_criteria": {"value": 15, "unit": "barg"},
                "hold_time": {"value": 1, "unit": "hour"}
            }
        ]
    )
    cost_tracking: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cost tracking and budget information",
        example={
            "budget": {"value": 25000, "unit": "USD"},
            "actual_costs": {
                "labor": {"value": 12000, "unit": "USD"},
                "materials": {"value": 5000, "unit": "USD"},
                "equipment": {"value": 3000, "unit": "USD"},
                "contractors": {"value": 4000, "unit": "USD"}
            },
            "variance": {"value": 1000, "unit": "USD"}
        }
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Historical maintenance records",
        example=[
            {
                "date": "2023-03-15",
                "type": "preventive_maintenance",
                "findings": "Normal wear and tear",
                "work_performed": "Standard cleaning and inspection",
                "cost": {"value": 23000, "unit": "USD"}
            }
        ]
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Maintenance performance indicators",
        example={
            "mean_time_between_failures": {"value": 365, "unit": "days"},
            "mean_time_to_repair": {"value": 24, "unit": "hours"},
            "maintenance_effectiveness": {"value": 95, "unit": "percent"},
            "schedule_compliance": {"value": 90, "unit": "percent"}
        }
    )

class CleaningMethod(BaseModel):
    """Model for industrial cleaning methods and procedures"""
    type: str = Field(
        description="Type of cleaning method used in industrial equipment",
        example="chemical_cleaning"
    )
    duration: float = Field(  # Только добавили тип float
        description="Expected duration of the cleaning procedure",
        example=4.5,  # hours
        default=0.0  # Добавили default для валидации
    )
    description: str = Field(
        description="Detailed description of the cleaning method and its application",
        example="Acid cleaning procedure using 5% hydrochloric acid solution for removal of calcium carbonate deposits in heat exchanger tubes"
    )
    chemicals: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Chemical agents used in the cleaning process with their specifications",
        example=[
            {
                "name": "hydrochloric_acid",
                "concentration": "5%",
                "quantity": "1000 liters",
                "supplier": "ChemCorp Ltd",
                "safety_class": "Corrosive"
            },
            {
                "name": "inhibitor_a12",
                "concentration": "0.1%",
                "quantity": "10 liters",
                "purpose": "Corrosion protection"
            }
        ]
    )
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical process parameters for the cleaning method",
        example=[
            {
                "name": "temperature",
                "value": 40,
                "unit": "°C",
                "critical_max": 50,
                "notes": "Monitor continuously"
            },
            {
                "name": "circulation_rate",
                "value": 100,
                "unit": "m3/h",
                "minimum": 80,
                "notes": "Maintain turbulent flow"
            },
            {
                "name": "pH",
                "value": 2,
                "acceptable_range": {"min": 1, "max": 3},
                "monitoring_frequency": "30 minutes"
            }
        ]
    )
    duration_unit: str = Field(
        description="Unit of measurement for cleaning duration",
        example="hours"  # Other examples: days, minutes
    )
    restrictions: Optional[List[str]] = Field(
        default_factory=list,
        description="Operating restrictions and limitations during cleaning",
        example=[
            "Maximum temperature must not exceed 50°C to prevent damage to gaskets",
            "pH must be maintained between 1-3 throughout the cleaning process",
            "Continuous ventilation required in confined spaces",
            "Not suitable for titanium equipment parts"
        ]
    )
    safety_measures: Optional[List[str]] = Field(
        default_factory=list,
        description="Required safety measures and precautions during cleaning",
        example=[
            "Full chemical resistant PPE including face shield required",
            "Continuous hydrogen gas monitoring in confined spaces",
            "Emergency shower and eyewash station must be readily available",
            "Acid proof gloves and rubber boots mandatory",
            "Two-way radio communication required between operators"
        ]
    )

class CleaningProcedure(BaseModel):
    """Model for detailed industrial cleaning procedures and protocols"""
    id: str = Field(
        description="Unique identifier for the cleaning procedure",
        example="CLEAN-2024-001"
    )
    equipment_id: str = Field(
        description="Identifier of equipment requiring cleaning",
        example="HE-101"  # Heat Exchanger 101
    )
    description: Optional[str] = Field(
        default=None,
        description="Comprehensive description of the cleaning procedure",
        example="Two-stage chemical cleaning procedure for shell and tube heat exchanger HE-101 including alkaline and acid cleaning steps"
    )
    cleaning_methods: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Sequence of cleaning methods to be applied",
        example=[
            {
                "step": 1,
                "type": "alkaline_cleaning",
                "description": "Initial degreasing with 3% NaOH solution",
                "duration": "2 hours",
                "temperature": "60°C"
            },
            {
                "step": 2,
                "type": "acid_cleaning",
                "description": "Scale removal with 5% HCl solution",
                "duration": "4 hours",
                "temperature": "40°C"
            }
        ]
    )
    trigger_conditions: Optional[List[str]] = Field(
        default_factory=list,
        description="Conditions that trigger the need for cleaning",
        example=[
            "Pressure drop increase > 25% above baseline",
            "Heat transfer coefficient decrease > 20%",
            "Visual inspection shows significant fouling",
            "After 6 months of continuous operation"
        ]
    )
    acceptance_criteria: Optional[List[str]] = Field(
        default_factory=list,
        description="Criteria for successful cleaning completion",
        example=[
            "Pressure drop restored to within 10% of design value",
            "Heat transfer coefficient restored to > 85% of design value",
            "Visual inspection shows no visible deposits",
            "Neutralization confirmed by pH measurement",
            "Equipment integrity verified by NDT inspection"
        ]
    )
    operational_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating limitations during cleaning process",
        example={
            "max_pressure": {"value": 5, "unit": "barg"},
            "max_temperature": {"value": 65, "unit": "°C"},
            "min_flow_rate": {"value": 50, "unit": "m3/h"},
            "pH_limits": {"min": 2, "max": 12}
        }
    )
    preparation_steps: Optional[List[str]] = Field(
        default_factory=list,
        description="Required preparation steps before cleaning",
        example=[
            "1. Isolate equipment using double block and bleed",
            "2. Drain and vent system completely",
            "3. Install temporary cleaning connections",
            "4. Verify all gaskets are compatible with cleaning chemicals",
            "5. Set up temporary waste collection system"
        ]
    )
    required_materials: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Materials and chemicals required for cleaning",
        example=[
            {
                "name": "Sodium hydroxide",
                "concentration": "3%",
                "quantity": 2000,
                "unit": "liters",
                "specification": "Technical grade"
            },
            {
                "name": "Hydrochloric acid",
                "concentration": "5%",
                "quantity": 3000,
                "unit": "liters",
                "specification": "Industrial grade"
            }
        ]
    )
    safety_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Safety requirements and precautions",
        example=[
            "Continuous gas monitoring for confined space entry",
            "Chemical resistant PPE including full face protection",
            "Emergency shower and eyewash station must be operational",
            "Minimum two person team required",
            "Emergency response team on standby"
        ]
    )
    environmental_measures: Optional[List[str]] = Field(
        default_factory=list,
        description="Environmental protection measures",
        example=[
            "pH neutralization before disposal",
            "Heavy metals monitoring in waste stream",
            "Proper segregation of chemical waste",
            "Use of closed loop cleaning system",
            "Air emissions monitoring during cleaning"
        ]
    )
    waste_handling: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Waste handling and disposal requirements",
        example={
            "waste_type": "Hazardous chemical waste",
            "estimated_volume": 5000,
            "unit": "liters",
            "disposal_method": "Licensed chemical waste contractor",
            "neutralization_requirements": "pH adjustment to 6-8",
            "special_handling": "Separate heavy metal containing streams"
        }
    )
    cleaning_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Historical cleaning records",
        example=[
            {
                "date": "2024-01-15",
                "type": "Chemical cleaning",
                "effectiveness": "Good",
                "contractor": "Industrial Cleaning Services Ltd",
                "cost": 25000,
                "findings": "Heavy scale deposits removed successfully"
            }
        ]
    )
    effectiveness_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metrics for measuring cleaning effectiveness",
        example={
            "pressure_drop_improvement": "85%",
            "heat_transfer_improvement": "90%",
            "cleaning_time": "6 hours",
            "chemical_consumption": "Within planned limits",
            "cost_effectiveness": "High"
        }
    )

class Economics(BaseModel):
    """Model for economic metrics and financial analysis of process equipment and operations"""
    id: str = Field(
        description="Unique economic metric identifier",
        example="ECON-2024-HE101"
    )
    equipment_id: Optional[str] = Field(
        default=None,
        description="Equipment identifier for specific equipment analysis",
        example="HE-101"  # Heat Exchanger 101
    )
    metric_type: str = Field(
        description="Type of economic metric being tracked",
        example="operating_cost"  # capital_cost, maintenance_cost, energy_cost, total_cost_of_ownership
    )
    period: Optional[str] = Field(
        default=None,
        description="Time period for economic analysis",
        example="2024-Q1"  # annual, monthly, quarterly
    )
    capital_costs: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Capital investment and fixed costs",
        example={
            "equipment_cost": {"value": 250000, "unit": "USD"},
            "installation_cost": {"value": 75000, "unit": "USD"},
            "engineering_cost": {"value": 25000, "unit": "USD"},
            "commissioning_cost": {"value": 15000, "unit": "USD"},
            "total_installed_cost": {"value": 365000, "unit": "USD"}
        }
    )
    operating_costs: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating and variable costs",
        example={
            "energy_consumption": {
                "electricity": {"value": 50000, "unit": "USD/year"},
                "steam": {"value": 30000, "unit": "USD/year"}
            },
            "raw_materials": {"value": 100000, "unit": "USD/year"},
            "utilities": {"value": 25000, "unit": "USD/year"},
            "labor": {"value": 40000, "unit": "USD/year"}
        }
    )
    maintenance_costs: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Maintenance and repair costs",
        example={
            "routine_maintenance": {"value": 15000, "unit": "USD/year"},
            "preventive_maintenance": {"value": 25000, "unit": "USD/year"},
            "repairs": {"value": 10000, "unit": "USD/year"},
            "spare_parts": {"value": 8000, "unit": "USD/year"}
        }
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic performance indicators",
        example={
            "availability": {"value": 0.95, "unit": "ratio"},
            "production_rate": {"value": 1000, "unit": "tons/day"},
            "specific_energy_consumption": {"value": 0.5, "unit": "kWh/ton"},
            "product_quality": {"value": 0.98, "unit": "ratio"}
        }
    )
    lifecycle_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Lifecycle cost analysis",
        example={
            "expected_lifetime": {"value": 20, "unit": "years"},
            "depreciation_period": {"value": 10, "unit": "years"},
            "salvage_value": {"value": 25000, "unit": "USD"},
            "total_lifecycle_cost": {"value": 1500000, "unit": "USD"}
        }
    )
    efficiency_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic efficiency indicators",
        example={
            "cost_per_unit": {"value": 25, "unit": "USD/ton"},
            "energy_cost_ratio": {"value": 0.15, "unit": "ratio"},
            "maintenance_cost_ratio": {"value": 0.08, "unit": "ratio"},
            "return_on_investment": {"value": 0.25, "unit": "ratio"}
        }
    )
    cost_drivers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Major cost contributing factors",
        example=[
            {
                "driver": "energy_consumption",
                "contribution": {"value": 0.35, "unit": "ratio"},
                "trend": "increasing",
                "control_measures": ["efficiency_improvement", "load_optimization"]
            },
            {
                "driver": "maintenance",
                "contribution": {"value": 0.20, "unit": "ratio"},
                "trend": "stable",
                "control_measures": ["predictive_maintenance", "reliability_improvement"]
            }
        ]
    )
    optimization_opportunities: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Identified cost optimization opportunities",
        example=[
            {
                "opportunity": "energy_efficiency",
                "potential_savings": {"value": 15000, "unit": "USD/year"},
                "implementation_cost": {"value": 25000, "unit": "USD"},
                "payback_period": {"value": 1.7, "unit": "years"},
                "status": "evaluation"
            }
        ]
    )
    financial_risks: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Identified financial risks and mitigation measures",
        example=[
            {
                "risk": "energy_price_volatility",
                "impact": "high",
                "probability": "medium",
                "mitigation_measures": ["long_term_contracts", "efficiency_improvements"],
                "contingency": {"value": 20000, "unit": "USD/year"}
            }
        ]
    )
    budget_tracking: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Budget versus actual cost tracking",
        example={
            "period": "2024-Q1",
            "budget": {"value": 100000, "unit": "USD"},
            "actual": {"value": 95000, "unit": "USD"},
            "variance": {"value": -5000, "unit": "USD"},
            "variance_explanation": "Lower than expected maintenance costs"
        }
    )
    benchmarking: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Cost benchmarking against industry standards",
        example=[
            {
                "metric": "operating_cost_per_ton",
                "actual": {"value": 25, "unit": "USD/ton"},
                "industry_average": {"value": 28, "unit": "USD/ton"},
                "percentile": 75,
                "comments": "Better than industry average"
            }
        ]
    )

class EnergyEfficiency(BaseModel):
    """Model for tracking and analyzing energy efficiency in process equipment and systems"""
    id: str = Field(
        description="Unique energy efficiency record identifier",
        example="EE-2024-HE101"
    )
    equipment_id: Optional[str] = Field(
        default=None,
        description="Equipment identifier for specific equipment analysis",
        example="HE-101"  # Heat Exchanger 101
    )
    energy_type: str = Field(
        description="Type of energy consumption being monitored",
        example="thermal"  # electrical, mechanical, combined
    )
    consumption: Optional[float] = Field(
        default=None,
        description="Measured energy consumption value",
        example=1500.5  # kW or appropriate unit
    )
    consumption_unit: Optional[str] = Field(
        default=None,
        description="Unit of energy consumption measurement",
        example="kW"  # kWh, MJ, GJ
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Key energy performance indicators",
        example={
            "thermal_efficiency": {"value": 0.82, "unit": "ratio"},
            "heat_recovery": {"value": 75, "unit": "percent"},
            "specific_energy_consumption": {"value": 2.5, "unit": "kWh/ton"},
            "energy_intensity": {"value": 3.2, "unit": "GJ/ton_product"}
        }
    )
    operating_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Current operating parameters affecting energy efficiency",
        example={
            "flow_rate": {"value": 100, "unit": "m3/h"},
            "inlet_temperature": {"value": 80, "unit": "°C"},
            "outlet_temperature": {"value": 120, "unit": "°C"},
            "pressure_drop": {"value": 0.5, "unit": "bar"},
            "fouling_factor": {"value": 0.0002, "unit": "m2K/W"}
        }
    )
    design_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Design energy efficiency parameters",
        example={
            "design_efficiency": {"value": 0.85, "unit": "ratio"},
            "design_duty": {"value": 2000, "unit": "kW"},
            "minimum_approach": {"value": 10, "unit": "°C"},
            "maximum_pressure_drop": {"value": 0.7, "unit": "bar"}
        }
    )
    energy_losses: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Identified energy loss sources and quantities",
        example=[
            {
                "source": "heat_loss_to_ambient",
                "value": {"amount": 50, "unit": "kW"},
                "percentage": 2.5,
                "mitigation": "improve_insulation"
            },
            {
                "source": "fouling",
                "value": {"amount": 100, "unit": "kW"},
                "percentage": 5.0,
                "mitigation": "cleaning_required"
            }
        ]
    )
    monitoring_data: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Energy efficiency monitoring measurements",
        example=[
            {
                "timestamp": "2024-01-15T10:00:00",
                "parameter": "heat_transfer_coefficient",
                "value": {"current": 750, "design": 850, "unit": "W/m2K"},
                "efficiency_impact": {"value": -5, "unit": "percent"}
            }
        ]
    )
    improvement_opportunities: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Identified energy efficiency improvement opportunities",
        example=[
            {
                "opportunity": "heat_recovery_optimization",
                "potential_saving": {"value": 200, "unit": "kW"},
                "investment_required": {"value": 50000, "unit": "USD"},
                "payback_period": {"value": 1.5, "unit": "years"},
                "implementation_status": "evaluation"
            }
        ]
    )
    maintenance_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Impact of maintenance activities on energy efficiency",
        example={
            "last_cleaning": "2024-01-01",
            "efficiency_improvement": {"value": 5, "unit": "percent"},
            "energy_saving": {"value": 100, "unit": "kW"},
            "next_maintenance_due": "2024-07-01"
        }
    )
    economic_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic aspects of energy efficiency",
        example={
            "energy_cost": {"value": 0.1, "unit": "USD/kWh"},
            "annual_consumption": {"value": 13140, "unit": "MWh"},
            "annual_cost": {"value": 1314000, "unit": "USD"},
            "potential_savings": {"value": 131400, "unit": "USD/year"}
        }
    )
    benchmarking: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Energy efficiency benchmarking data",
        example={
            "industry_average": {"value": 3.5, "unit": "GJ/ton"},
            "best_practice": {"value": 2.8, "unit": "GJ/ton"},
            "current_performance": {"value": 3.2, "unit": "GJ/ton"},
            "ranking_percentile": 65
        }
    )
    optimization_controls: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Energy efficiency control and optimization measures",
        example=[
            {
                "control_type": "advanced_process_control",
                "variables": ["flow_rate", "temperature"],
                "objective": "minimize_energy_consumption",
                "constraints": ["product_quality", "safety_limits"],
                "savings_achieved": {"value": 3, "unit": "percent"}
            }
        ]
    )
    environmental_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Environmental impact of energy consumption",
        example={
            "co2_emissions": {"value": 5000, "unit": "tons/year"},
            "carbon_intensity": {"value": 0.4, "unit": "kgCO2/kWh"},
            "reduction_target": {"value": 10, "unit": "percent"},
            "green_energy_ratio": {"value": 0.15, "unit": "ratio"}
        }
    )
    
class Downtime(BaseModel):
    """Model for tracking and analyzing equipment and process downtimes"""
    id: str = Field(
        description="Unique downtime event identifier",
        example="DT-2024-P101-01"
    )
    equipment_id: str = Field(
        description="Equipment identifier affected by downtime",
        example="P-101"  # Pump 101
    )
    type: str = Field(
        description="Type of downtime event",
        example="planned_maintenance"  # unplanned_failure, emergency_shutdown, operational_delay
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of downtime event",
        example="Scheduled maintenance shutdown for pump bearing replacement and mechanical seal inspection"
    )
    duration: Optional[float] = Field(
        default=None,
        description="Duration of downtime",
        example=8.5  # hours
    )
    duration_unit: Optional[str] = Field(
        default=None,
        description="Unit of duration measurement",
        example="hours"  # days, minutes
    )
    timing: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Timing details of the downtime event",
        example={
            "start_time": "2024-01-15T08:00:00",
            "end_time": "2024-01-15T16:30:00",
            "planned_duration": {"value": 8, "unit": "hours"},
            "actual_duration": {"value": 8.5, "unit": "hours"},
            "deviation": {"value": 0.5, "unit": "hours"}
        }
    )
    root_cause: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Root cause analysis of the downtime",
        example={
            "primary_cause": "bearing_wear",
            "contributing_factors": [
                "inadequate_lubrication",
                "misalignment",
                "excessive_vibration"
            ],
            "detection_method": "vibration_monitoring",
            "verification": "bearing_inspection_report"
        }
    )
    impact_assessment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Assessment of downtime impact",
        example={
            "production_loss": {
                "quantity": {"value": 100, "unit": "tons"},
                "cost": {"value": 50000, "unit": "USD"}
            },
            "quality_impact": "none",
            "customer_impact": "minimal",
            "environmental_impact": "none",
            "safety_impact": "none"
        }
    )
    affected_systems: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Systems affected by the downtime",
        example=[
            {
                "system_id": "UNIT-100",
                "impact_level": "direct",
                "status": "reduced_capacity"
            },
            {
                "system_id": "UNIT-200",
                "impact_level": "indirect",
                "status": "normal_operation"
            }
        ]
    )
    mitigation_actions: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Actions taken to mitigate downtime impact",
        example=[
            {
                "action": "temporary_bypass_established",
                "timing": "2024-01-15T08:30:00",
                "effectiveness": "partial",
                "details": "Temporary connection to backup pump"
            },
            {
                "action": "production_rate_increased",
                "timing": "2024-01-15T16:30:00",
                "effectiveness": "full",
                "details": "Increased throughput to recover lost production"
            }
        ]
    )
    maintenance_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Details of maintenance activities during downtime",
        example={
            "work_order": "WO-2024-156",
            "maintenance_type": "preventive",
            "tasks_completed": [
                "bearing_replacement",
                "shaft_alignment",
                "seal_inspection"
            ],
            "spare_parts_used": [
                {"item": "bearing_set", "quantity": 1, "part_number": "BRG-123"},
                {"item": "mechanical_seal", "quantity": 1, "part_number": "MS-456"}
            ],
            "personnel_involved": [
                {"role": "mechanic", "hours": 6},
                {"role": "supervisor", "hours": 2}
            ]
        }
    )
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Financial impact analysis of downtime",
        example={
            "direct_costs": {
                "labor": {"value": 1500, "unit": "USD"},
                "materials": {"value": 3500, "unit": "USD"},
                "contractors": {"value": 0, "unit": "USD"}
            },
            "indirect_costs": {
                "production_loss": {"value": 50000, "unit": "USD"},
                "startup_costs": {"value": 1000, "unit": "USD"}
            },
            "total_impact": {"value": 56000, "unit": "USD"}
        }
    )
    lessons_learned: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Lessons learned and recommendations",
        example=[
            {
                "category": "preventive_maintenance",
                "finding": "Bearing inspection frequency inadequate",
                "recommendation": "Increase inspection frequency to monthly",
                "priority": "high",
                "status": "implemented"
            },
            {
                "category": "spare_parts",
                "finding": "Critical spares not available",
                "recommendation": "Update spare parts inventory policy",
                "priority": "medium",
                "status": "pending"
            }
        ]
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Related documentation and records",
        example=[
            {
                "type": "work_order",
                "reference": "WO-2024-156",
                "description": "Pump maintenance work order"
            },
            {
                "type": "inspection_report",
                "reference": "IR-2024-089",
                "description": "Post-maintenance inspection report"
            }
        ]
    )

class Bypass(BaseModel):
    """Model for bypass lines in process equipment and systems"""
    id: str = Field(
        description="Unique bypass line identifier in the system",
        example="BYP-001"
    )
    type: str = Field(
        description="Type of bypass line (e.g., process, maintenance, safety, startup)",
        example="process_bypass"
    )
    from_equipment: str = Field(
        description="Equipment identifier where bypass line starts",
        example="E-101-shell-inlet"
    )
    to_equipment: str = Field(
        description="Equipment identifier where bypass line ends",
        example="E-101-shell-outlet"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of bypass line purpose and characteristics",
        example="Process bypass line for shell-and-tube heat exchanger E-101 maintenance operations"
    )
    purpose: Optional[str] = Field(
        default=None,
        description="Primary purpose and function of the bypass line in the process",
        example="Allow maintenance of heat exchanger while maintaining process flow continuity"
    )
    operation_conditions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of operating conditions and limitations for bypass usage",
        example=[
            "Maximum allowable flow rate: 50 m3/h",
            "Maximum operating pressure: 10 barg",
            "Maximum temperature differential: 50°C"
        ]
    )
    restrictions: Optional[List[str]] = Field(
        default_factory=list,
        description="Usage restrictions and limitations for the bypass line",
        example=[
            "Not to be used for continuous operation exceeding 48 hours",
            "Requires supervisor approval for activation",
            "Not suitable for two-phase flow service"
        ]
    )
    safety_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Safety requirements and precautions for bypass operation",
        example=[
            "Double block and bleed isolation required before activation",
            "Pressure test at 15 barg required after maintenance",
            "Continuous monitoring of differential pressure required during operation"
        ]
    )
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Technical parameters and design characteristics of the bypass",
        example=[
            {
                "name": "design_pressure",
                "value": 15,
                "unit": "barg",
                "notes": "Maximum allowable working pressure"
            },
            {
                "name": "line_size",
                "value": 4,
                "unit": "inches",
                "notes": "Nominal pipe diameter"
            }
        ]
    )
    valves: Optional[List[str]] = Field(
        default_factory=list,
        description="List of valve identifiers associated with the bypass line",
        example=[
            "XV-1012A - Inlet block valve",
            "XV-1012B - Outlet block valve",
            "PCV-1013 - Pressure control valve"
        ]
    )
    interlocks: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety and operational interlocks for bypass operation",
        example=[
            {
                "type": "pressure_high",
                "setpoint": 12,
                "unit": "barg",
                "action": "close_bypass_valves",
                "priority": "high"
            },
            {
                "type": "flow_low",
                "setpoint": 10,
                "unit": "m3/h",
                "action": "alarm_only",
                "priority": "medium"
            }
        ]
    )
    source_text: Optional[str] = Field(
        default=None,
        description="Original text from technical documentation describing the bypass",
        example="Bypass line BYP-001 provides alternative flow path during E-101 maintenance, equipped with double block and bleed arrangement"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of the source documentation and descriptions",
        example="EN"
    )
    dynamic_properties: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Additional dynamic properties and characteristics extracted from documentation",
        example=[
            {
                "name": "last_inspection_date",
                "value": "2024-01-15",
                "inspector": "John Smith"
            },
            {
                "name": "maintenance_status",
                "value": "operational",
                "last_updated": "2024-01-20"
            }
        ]
    )

class ResourcePrice(BaseModel):
    """Model for resource pricing and cost tracking"""
    id: str = Field(
        description="Unique resource price record identifier",
        example="RP-2024-CAT-001"  # Resource Price record for Catalyst
    )
    resource_id: str = Field(
        description="Reference to the resource being priced",
        example="RES-2024-CAT-001"  # Reference to specific catalyst
    )
    type: str = Field(
        description="Type of pricing arrangement",
        example="contract_price"  # spot_price, index_linked, formula_based
    )
    price_components: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Breakdown of price components",
        example={
            "base_price": {
                "value": 1000,
                "unit": "USD/kg",
                "basis": "platinum_content"
            },
            "premium": {
                "value": 100,
                "unit": "USD/kg",
                "basis": "quality_grade"
            },
            "transportation": {
                "value": 50,
                "unit": "USD/kg",
                "basis": "delivery_terms"
            },
            "taxes": {
                "value": 115,
                "unit": "USD/kg",
                "type": "value_added_tax"
            }
        }
    )
    validity_period: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Price validity period",
        example={
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-12-31T23:59:59",
            "duration": {"value": 12, "unit": "months"},
            "review_frequency": "quarterly"
        }
    )
    price_formula: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Formula for price calculation",
        example={
            "base_component": "LME_platinum_price",
            "multiplier": 1.2,
            "adjustments": [
                {
                    "factor": "quality_premium",
                    "value": 0.1,
                    "application": "multiplicative"
                },
                {
                    "factor": "volume_discount",
                    "value": 0.05,
                    "application": "subtractive"
                }
            ],
            "currency_basis": "USD"
        }
    )
    volume_tiers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Volume-based pricing tiers",
        example=[
            {
                "tier": 1,
                "volume_range": {"min": 0, "max": 1000, "unit": "kg"},
                "price": {"value": 1000, "unit": "USD/kg"},
                "discount": {"value": 0, "unit": "percent"}
            },
            {
                "tier": 2,
                "volume_range": {"min": 1001, "max": 5000, "unit": "kg"},
                "price": {"value": 950, "unit": "USD/kg"},
                "discount": {"value": 5, "unit": "percent"}
            }
        ]
    )
    price_adjustments: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Conditions for price adjustments",
        example=[
            {
                "trigger": "market_index_change",
                "threshold": {"value": 5, "unit": "percent"},
                "adjustment_mechanism": "proportional",
                "notice_period": {"value": 30, "unit": "days"}
            },
            {
                "trigger": "exchange_rate_fluctuation",
                "threshold": {"value": 3, "unit": "percent"},
                "adjustment_mechanism": "monthly_average",
                "currency_pair": "USD/EUR"
            }
        ]
    )
    payment_terms: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Payment and billing terms",
        example={
            "payment_deadline": {"value": 30, "unit": "days"},
            "early_payment_discount": {"value": 2, "unit": "percent"},
            "late_payment_penalty": {"value": 1.5, "unit": "percent_monthly"},
            "billing_frequency": "monthly",
            "payment_method": "bank_transfer"
        }
    )
    market_references: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Market reference prices and indices",
        example=[
            {
                "index": "platinum_spot_price",
                "source": "LME",
                "frequency": "daily",
                "correlation": {"value": 0.85, "unit": "ratio"}
            },
            {
                "index": "chemical_price_index",
                "source": "IHS_Markit",
                "frequency": "monthly",
                "weight": {"value": 0.3, "unit": "ratio"}
            }
        ]
    )
    historical_prices: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Historical price data",
        example=[
            {
                "date": "2023-12-01",
                "price": {"value": 980, "unit": "USD/kg"},
                "volume": {"value": 1000, "unit": "kg"},
                "market_conditions": "normal"
            },
            {
                "date": "2023-11-01",
                "price": {"value": 950, "unit": "USD/kg"},
                "volume": {"value": 1200, "unit": "kg"},
                "market_conditions": "oversupply"
            }
        ]
    )
    price_forecast: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Price forecasts and projections",
        example={
            "short_term": {
                "horizon": {"value": 3, "unit": "months"},
                "expected_price": {"value": 1050, "unit": "USD/kg"},
                "confidence_interval": {"min": 1000, "max": 1100, "unit": "USD/kg"}
            },
            "long_term": {
                "horizon": {"value": 12, "unit": "months"},
                "trend": "increasing",
                "annual_growth": {"value": 3, "unit": "percent"}
            }
        }
    )
    risk_assessment: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Price risk assessment",
        example={
            "volatility": {"value": 15, "unit": "percent_annual"},
            "key_risk_factors": [
                "raw_material_prices",
                "market_demand",
                "supply_chain_disruptions"
            ],
            "hedging_strategy": "fixed_price_contracts",
            "contingency_plans": ["alternative_suppliers", "inventory_management"]
        }
    )

class Resource(BaseModel):
    """Model for process resources and utilities management"""
    id: str = Field(
        description="Unique resource identifier",
        example="RES-2024-CAT-001"  # Resource: Catalyst batch 001
    )
    name: str = Field(
        description="Resource name or designation",
        example="Platinum-Rhenium Reforming Catalyst"
    )
    category: str = Field(
        description="Resource category or type",
        example="process_catalyst"  # utility, chemical, consumable
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the resource",
        example="Bi-metallic reforming catalyst containing 0.3% Pt and 0.3% Re on alumina support"
    )
    specifications: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Technical specifications and properties",
        example={
            "composition": {
                "platinum": {"value": 0.3, "unit": "wt%"},
                "rhenium": {"value": 0.3, "unit": "wt%"},
                "support": "gamma_alumina"
            },
            "physical_properties": {
                "particle_size": {"value": 1.6, "unit": "mm"},
                "surface_area": {"value": 200, "unit": "m2/g"},
                "bulk_density": {"value": 0.7, "unit": "g/cm3"}
            },
            "performance_properties": {
                "activity": {"minimum": 95, "unit": "percent"},
                "selectivity": {"minimum": 90, "unit": "percent"},
                "stability": {"minimum": 12, "unit": "months"}
            }
        }
    )
    quality_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Quality requirements and acceptance criteria",
        example={
            "chemical_purity": {
                "chlorides": {"max": 100, "unit": "ppm"},
                "sulfur": {"max": 50, "unit": "ppm"},
                "moisture": {"max": 0.5, "unit": "wt%"}
            },
            "physical_quality": {
                "crush_strength": {"min": 2.0, "unit": "kg"},
                "attrition_loss": {"max": 1.0, "unit": "wt%"},
                "uniformity": {"within": 10, "unit": "percent"}
            }
        }
    )
    consumption_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Consumption patterns and rates",
        example={
            "normal_rate": {"value": 0.1, "unit": "kg/day"},
            "peak_rate": {"value": 0.15, "unit": "kg/day"},
            "annual_consumption": {"value": 36.5, "unit": "kg/year"},
            "lifetime": {"value": 2, "unit": "years"},
            "replacement_criteria": [
                "activity_below_80_percent",
                "selectivity_below_85_percent"
            ]
        }
    )
    inventory_management: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Inventory control parameters",
        example={
            "minimum_stock": {"value": 1000, "unit": "kg"},
            "maximum_stock": {"value": 5000, "unit": "kg"},
            "reorder_point": {"value": 2000, "unit": "kg"},
            "order_quantity": {"value": 3000, "unit": "kg"},
            "lead_time": {"value": 90, "unit": "days"}
        }
    )
    storage_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Storage conditions and requirements",
        example={
            "temperature": {"range": {"min": 10, "max": 30}, "unit": "°C"},
            "humidity": {"max": 60, "unit": "percent"},
            "container_type": "sealed_steel_drums",
            "stack_height": {"max": 2, "unit": "drums"},
            "segregation": "away_from_oxidizers",
            "special_conditions": [
                "keep_dry",
                "protect_from_direct_sunlight"
            ]
        }
    )
    handling_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Handling and safety requirements",
        example={
            "ppe_required": [
                "dust_mask",
                "chemical_resistant_gloves",
                "safety_glasses"
            ],
            "special_equipment": [
                "drum_handler",
                "vacuum_loader"
            ],
            "procedures": [
                "avoid_dust_generation",
                "use_inert_gas_purge"
            ],
            "safety_precautions": [
                "ground_equipment",
                "monitor_oxygen_levels"
            ]
        }
    )
    suppliers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Approved suppliers and vendor information",
        example=[
            {
                "name": "Catalyst Technologies Inc.",
                "qualification_status": "approved",
                "contract_number": "CT-2024-001",
                "lead_time": {"value": 90, "unit": "days"},
                "minimum_order": {"value": 1000, "unit": "kg"},
                "quality_certification": ["ISO_9001", "ISO_14001"]
            }
        ]
    )
    cost_information: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cost and economic information",
        example={
            "unit_cost": {"value": 1000, "unit": "USD/kg"},
            "delivery_cost": {"value": 50, "unit": "USD/kg"},
            "disposal_cost": {"value": 200, "unit": "USD/kg"},
            "total_lifecycle_cost": {"value": 1250, "unit": "USD/kg"},
            "cost_drivers": [
                "precious_metal_content",
                "transportation_requirements"
            ]
        }
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Required documentation and certificates",
        example=[
            {
                "type": "material_safety_data_sheet",
                "number": "MSDS-2024-001",
                "revision": "Rev.2",
                "validity": "2024-2026"
            },
            {
                "type": "certificate_of_analysis",
                "frequency": "per_batch",
                "retention_period": {"value": 5, "unit": "years"}
            }
        ]
    )

class ResourceConsumption(BaseModel):
    """Model for tracking and analyzing resource consumption patterns"""
    id: str = Field(
        description="Unique resource consumption record identifier",
        example="RC-2024-CAT-001"  # Resource Consumption record for Catalyst
    )
    resource_id: str = Field(
        description="Reference to the resource being consumed",
        example="RES-2024-CAT-001"  # Reference to specific catalyst
    )
    equipment_id: Optional[str] = Field(
        default=None,
        description="Equipment or unit consuming the resource",
        example="R-101"  # Reactor 101
    )
    period: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Time period for consumption measurement",
        example={
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-01-31T23:59:59",
            "duration": {"value": 31, "unit": "days"},
            "type": "monthly_consumption"
        }
    )
    consumption_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Actual consumption measurements",
        example={
            "quantity": {"value": 100, "unit": "kg"},
            "rate": {"value": 3.23, "unit": "kg/day"},
            "cumulative": {"value": 1200, "unit": "kg"},
            "specific_consumption": {"value": 0.5, "unit": "kg/ton_product"}
        }
    )
    operating_conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Process conditions during consumption",
        example={
            "temperature": {"average": 500, "unit": "°C"},
            "pressure": {"average": 15, "unit": "barg"},
            "throughput": {"average": 100, "unit": "tons/day"},
            "severity": {"value": 0.85, "unit": "ratio"}
        }
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Performance indicators related to consumption",
        example={
            "efficiency": {"value": 95, "unit": "percent"},
            "utilization": {"value": 90, "unit": "percent"},
            "yield_impact": {"value": 0.98, "unit": "ratio"},
            "quality_impact": {"value": "within_specs"}
        }
    )
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic analysis of consumption",
        example={
            "unit_cost": {"value": 1000, "unit": "USD/kg"},
            "total_cost": {"value": 100000, "unit": "USD"},
            "cost_per_unit_production": {"value": 5, "unit": "USD/ton_product"},
            "budget_variance": {"value": -2000, "unit": "USD"}
        }
    )
    inventory_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Impact on inventory levels",
        example={
            "opening_stock": {"value": 5000, "unit": "kg"},
            "closing_stock": {"value": 4900, "unit": "kg"},
            "minimum_level": {"value": 1000, "unit": "kg"},
            "reorder_point": {"value": 2000, "unit": "kg"},
            "stock_status": "adequate"
        }
    )
    consumption_pattern: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Analysis of consumption patterns",
        example={
            "trend": "stable",  # increasing, decreasing, cyclical
            "variability": {"value": 5, "unit": "percent"},
            "seasonality": "none",
            "peak_factors": ["high_throughput", "severe_conditions"],
            "pattern_type": "continuous"  # batch, intermittent
        }
    )
    quality_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Quality aspects affecting consumption",
        example=[
            {
                "parameter": "activity",
                "initial": {"value": 100, "unit": "percent"},
                "final": {"value": 95, "unit": "percent"},
                "decline_rate": {"value": 0.16, "unit": "percent/day"}
            },
            {
                "parameter": "selectivity",
                "initial": {"value": 98, "unit": "percent"},
                "final": {"value": 96, "unit": "percent"},
                "impact": "minimal"
            }
        ]
    )
    optimization_opportunities: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Identified consumption optimization opportunities",
        example=[
            {
                "opportunity": "operating_temperature_optimization",
                "potential_saving": {"value": 5, "unit": "percent"},
                "implementation_cost": {"value": 10000, "unit": "USD"},
                "payback_period": {"value": 6, "unit": "months"}
            }
        ]
    )
    environmental_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Environmental aspects of consumption",
        example={
            "waste_generation": {"value": 10, "unit": "kg"},
            "emissions": {"value": 50, "unit": "kg_CO2e"},
            "resource_efficiency": {"value": 0.95, "unit": "ratio"},
            "environmental_cost": {"value": 1000, "unit": "USD"}
        }
    )
    forecasting: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Consumption forecasts and predictions",
        example={
            "next_period": {"value": 105, "unit": "kg"},
            "annual_forecast": {"value": 1200, "unit": "kg"},
            "replacement_date": "2024-12-31",
            "confidence_level": {"value": 90, "unit": "percent"}
        }
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Related consumption documentation",
        example=[
            {
                "type": "consumption_report",
                "number": "CR-2024-001",
                "date": "2024-01-31",
                "retention_period": {"value": 5, "unit": "years"}
            }
        ]
    )

class WasteComponent(BaseModel):
    """Model for waste components"""
    name: str = Field(
        description="Component name",
        example="Sulfur compounds"
    )
    concentration: Union[float, Dict[str, float]] = Field(
        default=0.0,  # Добавили только default для валидации
        description="Component concentration or range",
        example={"min": 0.1, "max": 0.5}
    )
    unit: str = Field(
        description="Concentration unit",
        example="wt%"
    )
    description: Optional[str] = Field(
        default=None,
        description="Component description",
        example="Sulfur compounds from catalyst deactivation"
    )

class WasteNorm(BaseModel):
    """Model for waste generation norms"""
    value: float = Field(
        default=0.0,  # Добавили default
        description="Norm value",
        example=2.5
    )
    unit: str = Field(
        description="Norm unit",
        example="kg/ton product"
    )
    basis: str = Field(
        description="Norm basis",
        example="per ton of product"
    )
    type: str = Field(
        default="project",
        description="Norm type",
        example="project"
    )
    date: Optional[datetime] = Field(
        default=None,
        description="Norm effective date",
        example="2024-01-01T00:00:00"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
        example="Based on design capacity"
    )

class ProcessWaste(BaseModel):
    """Model for process waste streams and waste management"""
    id: str = Field(
        description="Unique waste stream identifier",
        example="WS-2024-UNIT100-01"  # Waste Stream 01 from Unit 100
    )
    name: Optional[str] = Field(
        default=None,
        description="Descriptive name of waste stream",
        example="Spent Catalyst Waste"
    )
    type: str = Field(
        description="Type of process waste",
        example="spent_catalyst"  # chemical_waste, biological_waste, hazardous_waste
    )
    source: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Origin and source of waste",
        example={
            "equipment_id": "R-101",
            "process_stage": "catalytic_reaction",
            "generation_point": "reactor_bed",
            "generation_mechanism": "catalyst_deactivation"
        }
    )
    classification: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Waste classification and categorization",
        example={
            "hazard_class": "hazardous",
            "regulatory_category": "spent_industrial_catalyst",
            "disposal_category": "special_waste",
            "environmental_risk": "moderate",
            "handling_requirements": "specialized_contractor"
        }
    )
    composition: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Chemical composition of waste",
        example=[
            {
                "component": "platinum",
                "concentration": {"value": 0.3, "unit": "wt%"},
                "form": "metal_on_support",
                "recoverable": True
            },
            {
                "component": "coke",
                "concentration": {"value": 15, "unit": "wt%"},
                "form": "carbonaceous_deposit",
                "recoverable": False
            }
        ]
    )
    physical_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Physical properties of waste",
        example={
            "phase": "solid",
            "particle_size": {"value": 2, "unit": "mm"},
            "bulk_density": {"value": 800, "unit": "kg/m3"},
            "moisture_content": {"value": 2, "unit": "wt%"}
        }
    )
    generation_rate: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Waste generation characteristics",
        example={
            "normal_rate": {"value": 1000, "unit": "kg/month"},
            "peak_rate": {"value": 5000, "unit": "kg/month"},
            "variability": "batch",
            "frequency": "quarterly",
            "factors_affecting_rate": [
                "catalyst_cycle_length",
                "operating_severity"
            ]
        }
    )
    handling_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Waste handling and storage requirements",
        example={
            "ppe_requirements": [
                "chemical_resistant_gloves",
                "dust_mask",
                "safety_glasses"
            ],
            "storage_conditions": {
                "container_type": "sealed_drums",
                "temperature": {"max": 30, "unit": "°C"},
                "humidity": {"max": 60, "unit": "percent"},
                "segregation": "away_from_oxidizers"
            },
            "special_precautions": [
                "avoid_moisture_contact",
                "prevent_dust_formation"
            ]
        }
    )
    disposal_method: str = Field(
        description="Primary method of waste disposal or treatment",
        example="metal_recovery"  # incineration, landfill, biological_treatment
    )
    treatment_process: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Waste treatment process details",
        example={
            "method": "hydrometallurgical_recovery",
            "steps": [
                "acid_leaching",
                "metal_precipitation",
                "filtration"
            ],
            "efficiency": {"value": 95, "unit": "percent"},
            "residuals": [
                {
                    "type": "spent_acid",
                    "quantity": {"value": 2, "unit": "m3/ton"},
                    "disposal": "neutralization"
                }
            ]
        }
    )
    regulatory_compliance: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Regulatory requirements and compliance",
        example={
            "permits_required": ["hazardous_waste_transport", "treatment_facility"],
            "reporting_requirements": ["quarterly_generation_report", "annual_summary"],
            "applicable_regulations": ["RCRA", "local_environmental_code"],
            "monitoring_requirements": ["composition_analysis", "leachate_testing"]
        }
    )
    environmental_impact: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Environmental impact assessment",
        example={
            "air_emissions": {"significance": "low", "components": ["dust"]},
            "water_impact": {"significance": "medium", "concerns": ["heavy_metals"]},
            "soil_impact": {"significance": "low", "mitigation": "contained_storage"},
            "resource_depletion": {"significance": "high", "recovery_potential": "yes"}
        }
    )
    cost_analysis: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Economic aspects of waste management",
        example={
            "handling_cost": {"value": 200, "unit": "USD/ton"},
            "treatment_cost": {"value": 1500, "unit": "USD/ton"},
            "transportation_cost": {"value": 300, "unit": "USD/ton"},
            "recovery_value": {"value": 5000, "unit": "USD/ton"},
            "net_cost": {"value": -3000, "unit": "USD/ton"}
        }
    )
    tracking_records: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Waste generation and disposal tracking",
        example=[
            {
                "date": "2024-01-15",
                "quantity": {"value": 1000, "unit": "kg"},
                "disposal_contractor": "Metal Recovery Services Inc.",
                "manifest_number": "MAN-2024-001",
                "disposal_location": "Recovery Facility Alpha"
            }
        ]
    )

class ProductSpecification(BaseModel):
    """Model for product specifications and quality requirements"""
    id: str = Field(
        description="Unique product specification identifier",
        example="SPEC-2024-REF-001"  # Specification for Reformate Product
    )
    name: str = Field(
        description="Product name or designation",
        example="High Octane Reformate"
    )
    grade: Optional[str] = Field(
        default=None,
        description="Product grade or quality level",
        example="Premium Grade"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed product description",
        example="High octane reformate for premium gasoline blending, produced by catalytic reforming"
    )
    physical_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Physical properties and specifications",
        example={
            "density": {
                "target": {"value": 0.775, "unit": "g/cm3"},
                "range": {"min": 0.770, "max": 0.780, "unit": "g/cm3"},
                "test_method": "ASTM D4052",
                "frequency": "per_batch"
            },
            "vapor_pressure": {
                "target": {"value": 7.5, "unit": "psi"},
                "range": {"min": 7.0, "max": 8.0, "unit": "psi"},
                "test_method": "ASTM D323",
                "frequency": "daily"
            },
            "distillation": {
                "IBP": {"target": 40, "range": {"min": 35, "max": 45}, "unit": "°C"},
                "T50": {"target": 105, "range": {"min": 100, "max": 110}, "unit": "°C"},
                "FBP": {"target": 180, "range": {"min": 175, "max": 185}, "unit": "°C"},
                "test_method": "ASTM D86"
            }
        }
    )
    chemical_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Chemical properties and composition specifications",
        example={
            "octane_number": {
                "RON": {
                    "target": 98,
                    "minimum": 97,
                    "test_method": "ASTM D2699"
                },
                "MON": {
                    "target": 87,
                    "minimum": 86,
                    "test_method": "ASTM D2700"
                }
            },
            "aromatics": {
                "total": {"max": 65, "unit": "vol%"},
                "benzene": {"max": 1.0, "unit": "vol%"},
                "test_method": "ASTM D5580"
            },
            "sulfur": {
                "max": 1.0,
                "unit": "ppm",
                "test_method": "ASTM D5453"
            }
        }
    )
    quality_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical quality parameters and requirements",
        example=[
            {
                "parameter": "color",
                "specification": "clear_and_bright",
                "test_method": "visual",
                "frequency": "per_batch"
            },
            {
                "parameter": "copper_corrosion",
                "specification": "class_1",
                "test_method": "ASTM D130",
                "frequency": "daily"
            }
        ]
    )
    contaminant_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Maximum allowable contaminant levels",
        example={
            "water": {"max": 50, "unit": "ppm", "test_method": "ASTM D6304"},
            "chlorides": {"max": 1, "unit": "ppm", "test_method": "ASTM D4929"},
            "metals": {
                "lead": {"max": 0.5, "unit": "ppm"},
                "iron": {"max": 0.1, "unit": "ppm"}
            }
        }
    )
    storage_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Product storage specifications",
        example={
            "temperature": {"max": 35, "unit": "°C"},
            "pressure": {"max": 1.5, "unit": "barg"},
            "inert_blanket": "nitrogen",
            "tank_materials": ["carbon_steel", "epoxy_lined"],
            "special_precautions": [
                "prevent_water_ingress",
                "minimize_light_exposure"
            ]
        }
    )
    handling_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Product handling requirements",
        example={
            "loading_temperature": {"range": {"min": 15, "max": 30}, "unit": "°C"},
            "loading_rate": {"max": 1000, "unit": "m3/h"},
            "ppe_requirements": ["chemical_resistant_gloves", "safety_glasses"],
            "special_procedures": ["static_electricity_prevention", "vapor_recovery"]
        }
    )
    testing_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Quality testing requirements and procedures",
        example=[
            {
                "test": "octane_number",
                "frequency": "per_batch",
                "method": "ASTM D2699",
                "sampling_point": "product_tank",
                "sample_size": {"value": 1, "unit": "liter"}
            },
            {
                "test": "composition_analysis",
                "frequency": "daily",
                "method": "GC_analysis",
                "critical_components": ["benzene", "toluene", "xylenes"]
            }
        ]
    )
    certification_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Product certification requirements",
        example={
            "required_certificates": ["certificate_of_analysis", "safety_data_sheet"],
            "approvals_needed": ["quality_manager", "laboratory_manager"],
            "retention_samples": {"duration": 90, "unit": "days"},
            "documentation_retention": {"duration": 5, "unit": "years"}
        }
    )
    regulatory_compliance: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Regulatory requirements and standards",
        example={
            "specifications": ["ASTM D4814", "EN 228"],
            "environmental_regulations": ["EPA_MSAT", "EU_Fuels_Directive"],
            "reporting_requirements": ["quarterly_quality_report", "annual_compliance_report"]
        }
    )

class ProcessDescription(BaseModel):
    """Model for detailed process unit and operation descriptions"""
    id: str = Field(
        description="Unique process description identifier",
        example="PD-2024-UNIT100"  # Process Description for Unit 100
    )
    name: str = Field(
        description="Name of the process unit or operation",
        example="Catalytic Reforming Unit"
    )
    description: Optional[str] = Field(
        default=None,
        description="General description of the process",
        example="Continuous catalytic reforming process for converting low-octane naphtha to high-octane reformate"
    )
    process_stages: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Sequential stages of the process",
        example=[
            {
                "stage_id": "STAGE-001",
                "name": "feed_pretreatment",
                "description": "Hydrodesulfurization of naphtha feed",
                "equipment": ["R-101", "E-101", "V-101"],
                "key_parameters": [
                    {
                        "name": "reactor_temperature",
                        "normal": {"value": 320, "unit": "°C"},
                        "range": {"min": 300, "max": 340, "unit": "°C"}
                    }
                ],
                "critical_controls": ["TIC-101", "PIC-101"]
            },
            {
                "stage_id": "STAGE-002",
                "name": "reforming_reaction",
                "description": "Catalytic reforming in multiple fixed-bed reactors",
                "equipment": ["R-201", "R-202", "R-203"],
                "key_parameters": [
                    {
                        "name": "reactor_pressure",
                        "normal": {"value": 15, "unit": "barg"},
                        "range": {"min": 14, "max": 16, "unit": "barg"}
                    }
                ]
            }
        ]
    )
    process_chemistry: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Chemical reactions and transformations",
        example={
            "main_reactions": [
                {
                    "type": "dehydrogenation",
                    "description": "Conversion of naphthenes to aromatics",
                    "example": "Cyclohexane → Benzene + 3H2",
                    "heat_of_reaction": {"value": 75, "unit": "kJ/mol"}
                },
                {
                    "type": "isomerization",
                    "description": "Rearrangement of paraffins",
                    "example": "n-Hexane → iso-Hexane",
                    "heat_of_reaction": {"value": -5, "unit": "kJ/mol"}
                }
            ],
            "catalysts": [
                {
                    "name": "platinum_alumina",
                    "composition": "0.3% Pt on Al2O3",
                    "form": "spherical_pellets",
                    "regeneration_cycle": {"value": 12, "unit": "months"}
                }
            ]
        }
    )
    operating_conditions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Normal operating conditions and ranges",
        example={
            "temperature_regime": {
                "inlet": {"value": 495, "unit": "°C"},
                "outlet": {"value": 515, "unit": "°C"},
                "control_range": {"min": 490, "max": 520, "unit": "°C"}
            },
            "pressure_regime": {
                "inlet": {"value": 15, "unit": "barg"},
                "outlet": {"value": 14, "unit": "barg"},
                "control_range": {"min": 13, "max": 16, "unit": "barg"}
            },
            "flow_regime": {
                "feed_rate": {"value": 100, "unit": "m3/h"},
                "recycle_ratio": {"value": 3, "unit": "mol/mol"}
            }
        }
    )
    process_controls: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical process control systems",
        example=[
            {
                "parameter": "reactor_temperature",
                "control_strategy": "cascade",
                "primary_controller": "TIC-201",
                "secondary_controller": "FIC-201",
                "critical_limits": {
                    "high_high": {"value": 530, "unit": "°C"},
                    "low_low": {"value": 480, "unit": "°C"}
                }
            }
        ]
    )
    safety_considerations: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process safety considerations",
        example=[
            {
                "hazard": "high_temperature",
                "risk": "thermal_expansion",
                "mitigation": "temperature_monitoring_and_control",
                "critical_limits": {"max": {"value": 530, "unit": "°C"}},
                "protective_systems": ["high_temperature_shutdown"]
            },
            {
                "hazard": "hydrogen_handling",
                "risk": "leakage_and_fire",
                "mitigation": "leak_detection_and_prevention",
                "protective_systems": ["gas_detection", "fire_suppression"]
            }
        ]
    )
    quality_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Product quality specifications",
        example={
            "reformate": {
                "octane_number": {"min": 95},
                "benzene_content": {"max": {"value": 1, "unit": "vol%"}},
                "sulfur": {"max": {"value": 0.5, "unit": "ppm"}}
            }
        }
    )
    utilities_required: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Required process utilities",
        example=[
            {
                "utility": "steam",
                "pressure": {"value": 40, "unit": "barg"},
                "consumption": {"value": 10, "unit": "tons/h"},
                "purpose": "reboiler_heating"
            },
            {
                "utility": "cooling_water",
                "temperature": {"value": 30, "unit": "°C"},
                "consumption": {"value": 1000, "unit": "m3/h"},
                "purpose": "product_cooling"
            }
        ]
    )
    environmental_aspects: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Environmental considerations and impacts",
        example={
            "emissions": [
                {
                    "type": "CO2",
                    "source": "fired_heater",
                    "quantity": {"value": 10, "unit": "tons/day"}
                }
            ],
            "waste_streams": [
                {
                    "type": "spent_catalyst",
                    "quantity": {"value": 50, "unit": "tons/year"},
                    "disposal_method": "regeneration"
                }
            ]
        }
    )

class MaterialBalance(BaseModel):
    """Model for process material balance calculations and tracking"""
    id: str = Field(
        description="Unique material balance identifier",
        example="MB-2024-UNIT100"  # Material Balance for Unit 100 in 2024
    )
    stage_id: str = Field(
        description="Process stage or unit operation identifier",
        example="UNIT-100"  # Process Unit 100
    )
    period: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Time period for material balance",
        example={
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-31T23:59:59",
            "duration": {"value": 31, "unit": "days"},
            "type": "monthly_balance"
        }
    )
    input_streams: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Input process streams and their quantities",
        example=[
            {
                "stream_id": "F-101",
                "name": "fresh_feed",
                "type": "raw_material",
                "quantity": {"value": 1000, "unit": "tons"},
                "composition": [
                    {"component": "n-hexane", "value": 85, "unit": "wt%"},
                    {"component": "n-heptane", "value": 15, "unit": "wt%"}
                ],
                "conditions": {
                    "temperature": {"value": 25, "unit": "°C"},
                    "pressure": {"value": 1, "unit": "barg"}
                }
            },
            {
                "stream_id": "F-102",
                "name": "recycle_stream",
                "type": "recycle",
                "quantity": {"value": 500, "unit": "tons"},
                "composition": [
                    {"component": "n-hexane", "value": 90, "unit": "wt%"},
                    {"component": "n-heptane", "value": 10, "unit": "wt%"}
                ]
            }
        ]
    )
    output_streams: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Output process streams and their quantities",
        example=[
            {
                "stream_id": "F-201",
                "name": "main_product",
                "type": "product",
                "quantity": {"value": 1200, "unit": "tons"},
                "composition": [
                    {"component": "n-hexane", "value": 95, "unit": "wt%"},
                    {"component": "n-heptane", "value": 5, "unit": "wt%"}
                ]
            },
            {
                "stream_id": "F-202",
                "name": "waste_stream",
                "type": "waste",
                "quantity": {"value": 300, "unit": "tons"},
                "composition": [
                    {"component": "n-hexane", "value": 60, "unit": "wt%"},
                    {"component": "n-heptane", "value": 40, "unit": "wt%"}
                ]
            }
        ]
    )
    process_losses: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process losses and their categorization",
        example=[
            {
                "type": "evaporation_loss",
                "quantity": {"value": 10, "unit": "tons"},
                "location": "storage_tanks",
                "prevention_measures": ["floating_roof", "vapor_recovery"]
            },
            {
                "type": "purge_loss",
                "quantity": {"value": 5, "unit": "tons"},
                "location": "reactor_purge",
                "reason": "inert_removal"
            }
        ]
    )
    conversion_yields: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Process conversion and yield calculations",
        example={
            "overall_conversion": {"value": 95, "unit": "percent"},
            "product_yield": {"value": 92, "unit": "percent"},
            "selectivity": {"value": 98, "unit": "percent"},
            "mass_efficiency": {"value": 0.95, "unit": "ratio"}
        }
    )
    component_balances: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Individual component material balances",
        example=[
            {
                "component": "n-hexane",
                "input": {"value": 850, "unit": "tons"},
                "output": {"value": 840, "unit": "tons"},
                "accumulated": {"value": 5, "unit": "tons"},
                "lost": {"value": 5, "unit": "tons"},
                "closure": {"value": 99.5, "unit": "percent"}
            }
        ]
    )
    balance_checks: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Material balance validation and checks",
        example={
            "total_mass_closure": {"value": 99.8, "unit": "percent"},
            "component_closure": {"value": 99.5, "unit": "percent"},
            "deviation_threshold": {"value": 2, "unit": "percent"},
            "reconciliation_status": "within_limits"
        }
    )
    inventory_changes: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process inventory changes during balance period",
        example=[
            {
                "location": "feed_tank",
                "material": "raw_feed",
                "initial": {"value": 100, "unit": "tons"},
                "final": {"value": 95, "unit": "tons"},
                "change": {"value": -5, "unit": "tons"}
            }
        ]
    )
    key_performance_indicators: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Material balance related performance indicators",
        example={
            "raw_material_efficiency": {"value": 0.95, "unit": "ratio"},
            "product_recovery": {"value": 98, "unit": "percent"},
            "waste_generation_rate": {"value": 0.25, "unit": "tons/ton_product"},
            "recycle_ratio": {"value": 0.5, "unit": "ratio"}
        }
    )
    reconciliation_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Data reconciliation information",
        example={
            "method": "least_squares",
            "constraints": ["total_mass", "component_mass"],
            "adjustments": [
                {"stream": "F-101", "adjustment": {"value": 2, "unit": "percent"}},
                {"stream": "F-201", "adjustment": {"value": -1, "unit": "percent"}}
            ],
            "confidence_level": {"value": 95, "unit": "percent"}
        }
    )

class ProcessControl(BaseModel):
    """Model for process control systems and control strategies"""
    id: str = Field(
        description="Unique process control identifier",
        example="PC-2024-UNIT100-01"  # Process Control for Unit 100, loop 01
    )
    parameter: str = Field(
        description="Process parameter being controlled",
        example="reactor_temperature"  # pressure, flow, level, composition
    )
    method: str = Field(
        description="Control method or strategy",
        example="cascade_control"  # PID, feedforward, ratio, override
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of control strategy",
        example="Cascade control of reactor temperature using jacket temperature as secondary loop"
    )
    control_objective: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Control objectives and requirements",
        example={
            "primary_objective": "maintain_reaction_temperature",
            "setpoint": {"value": 120, "unit": "°C"},
            "allowable_deviation": {"value": 2, "unit": "°C"},
            "response_time": {"value": 30, "unit": "seconds"},
            "stability_criteria": "minimum_oscillation"
        }
    )
    control_configuration: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Control loop configuration details",
        example={
            "control_type": "cascade",
            "primary_loop": {
                "controlled_variable": "reactor_temperature",
                "manipulated_variable": "jacket_temperature_setpoint",
                "controller": "TIC-101",
                "parameters": {
                    "kp": 2.5,
                    "ti": 300,
                    "td": 0
                }
            },
            "secondary_loop": {
                "controlled_variable": "jacket_temperature",
                "manipulated_variable": "cooling_water_flow",
                "controller": "TIC-102",
                "parameters": {
                    "kp": 1.0,
                    "ti": 60,
                    "td": 0
                }
            }
        }
    )
    instruments: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Control instruments and devices",
        example=[
            {
                "tag": "TT-101",
                "type": "temperature_transmitter",
                "location": "reactor_outlet",
                "range": {"min": 0, "max": 200, "unit": "°C"},
                "accuracy": {"value": 0.1, "unit": "°C"},
                "response_time": {"value": 5, "unit": "seconds"}
            },
            {
                "tag": "TCV-101",
                "type": "control_valve",
                "service": "cooling_water_control",
                "size": {"value": 4, "unit": "inches"},
                "characteristic": "equal_percentage",
                "rangeability": 50
            }
        ]
    )
    operating_ranges: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating ranges and limits",
        example={
            "process_variable": {
                "min": {"value": 100, "unit": "°C"},
                "max": {"value": 140, "unit": "°C"},
                "normal": {"value": 120, "unit": "°C"}
            },
            "manipulated_variable": {
                "min": {"value": 0, "unit": "percent"},
                "max": {"value": 100, "unit": "percent"},
                "normal": {"value": 45, "unit": "percent"}
            }
        }
    )
    alarms: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Associated alarms and alerts",
        example=[
            {
                "tag": "TAH-101",
                "type": "high_temperature_alarm",
                "setpoint": {"value": 130, "unit": "°C"},
                "priority": "high",
                "action": "operator_notification"
            },
            {
                "tag": "TAL-101",
                "type": "low_temperature_alarm",
                "setpoint": {"value": 110, "unit": "°C"},
                "priority": "medium",
                "action": "operator_notification"
            }
        ]
    )
    interlocks: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety interlocks and trips",
        example=[
            {
                "tag": "TAHH-101",
                "type": "high_high_temperature_trip",
                "setpoint": {"value": 140, "unit": "°C"},
                "action": "reactor_shutdown",
                "voting_logic": "2oo3",
                "response_time": {"value": 2, "unit": "seconds"}
            }
        ]
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Control performance indicators",
        example={
            "setpoint_tracking": {
                "rise_time": {"value": 45, "unit": "seconds"},
                "overshoot": {"value": 5, "unit": "percent"},
                "settling_time": {"value": 180, "unit": "seconds"}
            },
            "disturbance_rejection": {
                "maximum_deviation": {"value": 3, "unit": "°C"},
                "recovery_time": {"value": 120, "unit": "seconds"}
            },
            "control_quality": {
                "variance": {"value": 0.5, "unit": "°C"},
                "integral_absolute_error": 125
            }
        }
    )
    tuning_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Controller tuning history",
        example=[
            {
                "date": "2024-01-15",
                "reason": "oscillatory_response",
                "method": "lambda_tuning",
                "parameters": {
                    "kp": 2.5,
                    "ti": 300,
                    "td": 0
                },
                "performance_improvement": {"value": 30, "unit": "percent"}
            }
        ]
    )
    maintenance_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Control system maintenance requirements",
        example=[
            {
                "item": "control_valve",
                "task": "stroke_test",
                "frequency": {"value": 6, "unit": "months"},
                "acceptance_criteria": "full_stroke_5_seconds"
            },
            {
                "item": "temperature_transmitter",
                "task": "calibration",
                "frequency": {"value": 12, "unit": "months"},
                "acceptance_criteria": "accuracy_within_0.1_degree"
            }
        ]
    )

class TechnologicalRegime(BaseModel):
    """Model for process technological regimes and operating modes"""
    id: str = Field(
        description="Unique technological regime identifier",
        example="TR-2024-UNIT100-001"  # Technological Regime for Unit 100
    )
    name: str = Field(
        description="Name of the technological regime",
        example="Normal Production Mode"  # startup_mode, turndown_mode, regeneration_mode
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the technological regime",
        example="Standard operating regime for catalytic reforming unit at 100% design capacity"
    )
    operating_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical operating parameters for the regime",
        example=[
            {
                "parameter": "reactor_temperature",
                "target": {"value": 510, "unit": "°C"},
                "range": {
                    "min": {"value": 500, "unit": "°C"},
                    "max": {"value": 520, "unit": "°C"}
                },
                "criticality": "high",
                "control_method": "cascade_control",
                "monitoring_frequency": "continuous"
            },
            {
                "parameter": "system_pressure",
                "target": {"value": 15, "unit": "barg"},
                "range": {
                    "min": {"value": 14, "unit": "barg"},
                    "max": {"value": 16, "unit": "barg"}
                },
                "criticality": "high",
                "control_method": "direct_control",
                "monitoring_frequency": "continuous"
            }
        ]
    )
    process_flows: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process flow specifications",
        example=[
            {
                "stream_id": "F-101",
                "description": "Fresh feed",
                "flow_rate": {
                    "target": {"value": 100, "unit": "m3/h"},
                    "range": {"min": 90, "max": 110, "unit": "m3/h"}
                },
                "composition": {
                    "naphtha": {"value": 98, "unit": "wt%"},
                    "light_ends": {"value": 2, "unit": "wt%"}
                }
            }
        ]
    )
    equipment_settings: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Equipment-specific settings and configurations",
        example=[
            {
                "equipment_id": "P-101",
                "type": "centrifugal_pump",
                "settings": {
                    "speed": {"value": 3000, "unit": "rpm"},
                    "minimum_flow": {"value": 20, "unit": "m3/h"},
                    "seal_flush": "enabled"
                }
            },
            {
                "equipment_id": "E-101",
                "type": "heat_exchanger",
                "settings": {
                    "bypass_position": {"value": 0, "unit": "percent"},
                    "temperature_approach": {"value": 10, "unit": "°C"}
                }
            }
        ]
    )
    control_strategy: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Process control strategy for the regime",
        example={
            "primary_controls": [
                {
                    "loop": "temperature_control",
                    "controller": "TIC-101",
                    "setpoint": {"value": 510, "unit": "°C"},
                    "control_mode": "cascade"
                }
            ],
            "constraints": [
                {
                    "type": "maximum_temperature_rise",
                    "limit": {"value": 50, "unit": "°C/h"},
                    "action": "rate_limiting"
                }
            ],
            "interlocks": [
                {
                    "condition": "high_temperature",
                    "limit": {"value": 530, "unit": "°C"},
                    "action": "emergency_shutdown"
                }
            ]
        }
    )
    performance_targets: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Performance targets and KPIs",
        example={
            "conversion": {"target": 95, "unit": "percent"},
            "selectivity": {"target": 90, "unit": "percent"},
            "product_quality": {
                "octane_number": {"target": 98, "minimum": 97},
                "yield": {"target": 85, "unit": "percent"}
            },
            "energy_efficiency": {
                "specific_consumption": {"target": 2.5, "unit": "GJ/ton"}
            }
        }
    )
    operational_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Operating limits and constraints",
        example={
            "safety_limits": {
                "maximum_pressure": {"value": 20, "unit": "barg"},
                "maximum_temperature": {"value": 550, "unit": "°C"}
            },
            "equipment_limits": {
                "maximum_throughput": {"value": 120, "unit": "m3/h"},
                "minimum_turndown": {"value": 40, "unit": "percent"}
            },
            "quality_limits": {
                "maximum_sulfur": {"value": 0.5, "unit": "ppm"},
                "minimum_octane": {"value": 95, "unit": "RON"}
            }
        }
    )
    transition_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Requirements for regime transitions",
        example=[
            {
                "from_regime": "startup",
                "to_regime": "normal_operation",
                "conditions": [
                    "reactor_temperature_stable",
                    "product_quality_in_spec"
                ],
                "steps": [
                    {
                        "sequence": 1,
                        "action": "increase_feed_rate",
                        "target": {"value": 100, "unit": "m3/h"},
                        "rate": {"value": 10, "unit": "m3/h/hour"}
                    }
                ]
            }
        ]
    )
    monitoring_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Process monitoring requirements",
        example=[
            {
                "parameter": "catalyst_activity",
                "method": "temperature_profile",
                "frequency": "hourly",
                "acceptance_criteria": {
                    "maximum_deviation": {"value": 5, "unit": "°C"}
                }
            }
        ]
    )
    material_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Material and utility requirements",
        example={
            "raw_materials": [
                {
                    "material": "naphtha",
                    "specification": "low_sulfur",
                    "consumption": {"value": 100, "unit": "m3/h"}
                }
            ],
            "utilities": [
                {
                    "utility": "steam",
                    "pressure": {"value": 40, "unit": "barg"},
                    "consumption": {"value": 10, "unit": "tons/h"}
                }
            ]
        }
    )
    documentation_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Required documentation and records",
        example=[
            {
                "document_type": "operating_log",
                "frequency": "per_shift",
                "parameters": ["temperatures", "pressures", "flows"],
                "retention_period": {"value": 5, "unit": "years"}
            }
        ]
    )

class SafetyRequirement(BaseModel):
    """Model for process safety requirements and safety systems"""
    id: str = Field(
        description="Unique safety requirement identifier",
        example="SR-2024-R101-001"  # Safety Requirement for Reactor 101
    )
    category: str = Field(
        description="Category of safety requirement",
        example="process_safety"  # personnel_safety, environmental_safety, equipment_protection
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of safety requirement",
        example="High pressure protection system for reactor R-101 including pressure relief, emergency shutdown, and alarm systems"
    )
    scope: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Scope and applicability of safety requirement",
        example={
            "equipment_covered": ["R-101", "P-101", "E-101"],
            "process_conditions": {
                "pressure_range": {"max": 50, "unit": "barg"},
                "temperature_range": {"max": 350, "unit": "°C"}
            },
            "operational_phases": [
                "normal_operation",
                "startup",
                "shutdown",
                "emergency"
            ]
        }
    )
    protection_layers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Layers of protection analysis",
        example=[
            {
                "layer": "basic_process_control",
                "description": "Pressure control system",
                "components": ["PIC-101", "PCV-101"],
                "effectiveness": {"value": 99, "unit": "percent"},
                "response_time": {"value": 30, "unit": "seconds"}
            },
            {
                "layer": "alarm_system",
                "description": "High pressure alarm",
                "components": ["PAH-101"],
                "setpoint": {"value": 45, "unit": "barg"},
                "operator_response_time": {"value": 2, "unit": "minutes"}
            },
            {
                "layer": "safety_instrumented_system",
                "description": "Emergency shutdown system",
                "components": ["PSH-101", "XV-101"],
                "SIL_level": "SIL-2",
                "test_interval": {"value": 6, "unit": "months"}
            }
        ]
    )
    critical_parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical safety parameters and limits",
        example=[
            {
                "parameter": "pressure",
                "normal_range": {"min": 30, "max": 40, "unit": "barg"},
                "alarm_settings": {
                    "high": {"value": 45, "unit": "barg"},
                    "high_high": {"value": 47, "unit": "barg"}
                },
                "trip_point": {"value": 48, "unit": "barg"},
                "relief_setting": {"value": 50, "unit": "barg"}
            }
        ]
    )
    safety_systems: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Required safety systems and devices",
        example=[
            {
                "type": "pressure_relief_valve",
                "tag": "PSV-101",
                "capacity": {"value": 50000, "unit": "kg/h"},
                "set_pressure": {"value": 50, "unit": "barg"},
                "certification": "ASME_VIII",
                "inspection_interval": {"value": 2, "unit": "years"}
            },
            {
                "type": "emergency_shutdown_valve",
                "tag": "XV-101",
                "fail_position": "closed",
                "closure_time": {"value": 2, "unit": "seconds"},
                "testing_frequency": {"value": 6, "unit": "months"}
            }
        ]
    )
    operational_procedures: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety-related operational procedures",
        example=[
            {
                "title": "Emergency Shutdown Procedure",
                "document_number": "SOP-101-ESD",
                "revision": "Rev.3",
                "key_steps": [
                    "Verify alarm condition",
                    "Initiate emergency shutdown",
                    "Isolate affected equipment"
                ],
                "required_training": "Level_2_Operator"
            }
        ]
    )
    maintenance_requirements: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Safety system maintenance requirements",
        example=[
            {
                "equipment": "PSV-101",
                "task": "relief_valve_testing",
                "frequency": {"value": 2, "unit": "years"},
                "acceptance_criteria": "pop_pressure_within_3_percent",
                "required_certification": "pressure_relief_specialist"
            }
        ]
    )
    personnel_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Personnel safety requirements",
        example={
            "training_requirements": [
                {
                    "type": "process_safety_training",
                    "frequency": "annual",
                    "target_personnel": ["operators", "maintenance"]
                }
            ],
            "ppe_requirements": [
                {
                    "type": "chemical_protective_suit",
                    "specification": "Level_B",
                    "conditions_for_use": "during_chemical_handling"
                }
            ],
            "certifications_required": [
                "confined_space_entry",
                "hot_work_permit"
            ]
        }
    )
    emergency_response: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Emergency response requirements",
        example={
            "emergency_procedures": [
                "activation_of_emergency_shutdown",
                "area_evacuation",
                "emergency_services_notification"
            ],
            "emergency_equipment": [
                "fire_suppression_system",
                "emergency_shower",
                "escape_breathing_apparatus"
            ],
            "communication_protocol": {
                "primary": "plant_radio",
                "backup": "emergency_phones"
            }
        }
    )
    compliance_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Regulatory compliance requirements",
        example={
            "standards": ["OSHA_PSM", "API_521", "IEC_61511"],
            "permits_required": ["hot_work", "confined_space"],
            "inspections": [
                {
                    "type": "regulatory_inspection",
                    "frequency": "annual",
                    "authority": "state_safety_board"
                }
            ]
        }
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Required safety documentation",
        example=[
            {
                "type": "safety_case",
                "document_number": "SC-R101-001",
                "revision": "Rev.2",
                "review_frequency": "3_years"
            },
            {
                "type": "risk_assessment",
                "document_number": "RA-R101-001",
                "revision": "Rev.1",
                "review_frequency": "annual"
            }
        ]
    )

class TechnicalDocumentation(BaseModel):
    """Model for technical documentation management"""
    id: str = Field(
        description="Unique document identifier",
        example="DOC-2024-R101-001"  # Document for Reactor 101
    )
    type: str = Field(
        description="Type of technical document",
        example="operating_manual"  # process_description, P&ID, equipment_datasheet
    )
    title: str = Field(
        description="Document title",
        example="Reactor R-101 Operating Manual"
    )
    document_number: Optional[str] = Field(
        default=None,
        description="Official document number in document management system",
        example="OM-R101-2024-001"  # Operating Manual for R-101
    )
    revision_control: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Document revision information",
        example={
            "current_revision": "Rev.3",
            "revision_date": "2024-01-15",
            "revision_history": [
                {
                    "revision": "Rev.3",
                    "date": "2024-01-15",
                    "changes": "Updated operating parameters",
                    "approved_by": "John Smith"
                },
                {
                    "revision": "Rev.2",
                    "date": "2023-06-15",
                    "changes": "Added safety procedures",
                    "approved_by": "Jane Doe"
                }
            ],
            "next_review_date": "2025-01-15"
        }
    )
    content_structure: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Document content organization",
        example={
            "sections": [
                {
                    "number": "1.0",
                    "title": "Introduction",
                    "subsections": ["1.1 Purpose", "1.2 Scope"]
                },
                {
                    "number": "2.0",
                    "title": "Equipment Description",
                    "subsections": ["2.1 Design", "2.2 Specifications"]
                }
            ],
            "appendices": [
                "A. Technical Drawings",
                "B. Maintenance Procedures"
            ]
        }
    )
    related_equipment: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Equipment covered by the document",
        example=[
            {
                "equipment_id": "R-101",
                "type": "reactor",
                "description": "Main reaction vessel",
                "related_systems": ["cooling_system", "control_system"]
            }
        ]
    )
    technical_content: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Technical information and specifications",
        example={
            "design_basis": {
                "capacity": {"value": 1000, "unit": "kg/h"},
                "operating_pressure": {"value": 10, "unit": "barg"},
                "design_temperature": {"value": 200, "unit": "°C"}
            },
            "operating_procedures": [
                {
                    "title": "Normal Startup",
                    "steps": ["1. Verify utilities", "2. Pressurize system"],
                    "critical_parameters": ["pressure", "temperature"]
                }
            ],
            "safety_information": {
                "hazards": ["high_pressure", "high_temperature"],
                "protective_measures": ["pressure_relief", "temperature_control"]
            }
        }
    )
    references: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Referenced documents and standards",
        example=[
            {
                "document_id": "STD-001",
                "title": "Process Safety Standard",
                "revision": "Rev.2",
                "relevance": "Safety requirements"
            },
            {
                "document_id": "DWG-101",
                "title": "Reactor Assembly Drawing",
                "revision": "Rev.1",
                "relevance": "Equipment details"
            }
        ]
    )
    approval_status: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Document approval information",
        example={
            "status": "approved",
            "approvers": [
                {
                    "name": "John Smith",
                    "role": "Technical Manager",
                    "date": "2024-01-15"
                },
                {
                    "name": "Jane Doe",
                    "role": "Operations Manager",
                    "date": "2024-01-14"
                }
            ],
            "validity_period": {"value": 2, "unit": "years"}
        }
    )
    distribution_control: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Document distribution and access control",
        example={
            "access_level": "restricted",
            "authorized_users": ["operations", "maintenance", "engineering"],
            "controlled_copies": [
                {
                    "copy_number": "1",
                    "location": "Control Room",
                    "holder": "Shift Supervisor"
                }
            ],
            "electronic_access": {
                "path": "/technical_docs/operations/",
                "permissions": "read_only"
            }
        }
    )
    change_management: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Document change control information",
        example={
            "change_procedure": "MOC-DOC-001",
            "change_requests": [
                {
                    "request_id": "CR-2024-001",
                    "description": "Update operating parameters",
                    "status": "implemented",
                    "date": "2024-01-15"
                }
            ],
            "verification_requirements": [
                "technical_review",
                "safety_review",
                "operational_review"
            ]
        }
    )
    training_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Training requirements related to document",
        example={
            "required_training": [
                {
                    "course": "Reactor Operations",
                    "target_audience": "operators",
                    "frequency": "annual"
                }
            ],
            "competency_verification": {
                "method": "written_test",
                "passing_score": {"value": 80, "unit": "percent"}
            }
        }
    )
    attachments: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Document attachments and supporting files",
        example=[
            {
                "file_name": "reactor_diagram.pdf",
                "type": "technical_drawing",
                "revision": "Rev.2",
                "file_path": "/attachments/R101/"
            }
        ]
    )

class ProcessSystem(BaseModel):
    """Model for complete process system integration and overview"""
    id: str = Field(
        description="Unique process system identifier",
        example="PS-2024-UNIT100"  # Process System Unit 100
    )
    name: str = Field(
        description="Name of the process system",
        example="Catalytic Reforming Complex"
    )
    description: Optional[str] = Field(
        default=None,
        description="General description of the process system",
        example="Integrated catalytic reforming unit including feed preparation, reaction system, and product separation"
    )
    system_boundaries: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="System boundaries and interfaces",
        example={
            "upstream_systems": ["naphtha_hydrotreater", "hydrogen_system"],
            "downstream_systems": ["reformate_splitter", "hydrogen_distribution"],
            "utility_systems": ["cooling_water", "steam", "power"],
            "battery_limits": {
                "north": "Unit_200",
                "south": "Tank_farm",
                "east": "Utility_area",
                "west": "Pipe_rack"
            }
        }
    )
    subsystems: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Major subsystems within the process system",
        example=[
            {
                "id": "SUB-001",
                "name": "feed_preparation",
                "description": "Feed preheating and preparation system",
                "equipment": ["E-101", "P-101", "V-101"],
                "key_parameters": ["feed_temperature", "feed_pressure"]
            },
            {
                "id": "SUB-002",
                "name": "reaction_system",
                "description": "Multi-bed catalytic reforming reactors",
                "equipment": ["R-201", "R-202", "R-203"],
                "key_parameters": ["reaction_temperature", "hydrogen_recycle_ratio"]
            }
        ]
    )
    process_flows: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Major process flows within the system",
        example=[
            {
                "id": "F-101",
                "name": "fresh_feed",
                "type": "process_feed",
                "from": "naphtha_storage",
                "to": "feed_preheater",
                "normal_flow": {"value": 100, "unit": "m3/h"}
            },
            {
                "id": "F-102",
                "name": "hydrogen_recycle",
                "type": "recycle",
                "from": "recycle_compressor",
                "to": "reactor_inlet",
                "normal_flow": {"value": 50000, "unit": "Nm3/h"}
            }
        ]
    )
    control_philosophy: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Overall control philosophy and strategy",
        example={
            "control_objectives": [
                "maintain_product_quality",
                "optimize_energy_efficiency",
                "ensure_safe_operation"
            ],
            "critical_controls": [
                {
                    "parameter": "reactor_temperature",
                    "strategy": "cascade_control",
                    "importance": "critical"
                }
            ],
            "control_hierarchy": {
                "regulatory_control": "DCS",
                "advanced_control": "MPC",
                "optimization": "RTO"
            }
        }
    )
    operating_modes: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Different operating modes of the system",
        example=[
            {
                "mode": "normal_operation",
                "description": "Standard throughput operation",
                "key_setpoints": {
                    "feed_rate": {"value": 100, "unit": "m3/h"},
                    "reactor_temperature": {"value": 510, "unit": "°C"}
                }
            },
            {
                "mode": "reduced_throughput",
                "description": "Operation at reduced capacity",
                "key_setpoints": {
                    "feed_rate": {"value": 70, "unit": "m3/h"},
                    "reactor_temperature": {"value": 505, "unit": "°C"}
                }
            }
        ]
    )
    safety_systems: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Integrated safety systems",
        example=[
            {
                "id": "SIS-001",
                "type": "emergency_shutdown",
                "coverage": "complete_unit",
                "sil_level": "SIL-3",
                "critical_actions": ["isolate_feed", "depressurize_reactors"]
            }
        ]
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="System-wide performance indicators",
        example={
            "production": {
                "throughput": {"target": 100, "unit": "m3/h"},
                "yield": {"target": 0.92, "unit": "m3/m3"},
                "quality": {"octane": {"target": 95, "unit": "RON"}}
            },
            "efficiency": {
                "energy_consumption": {"target": 2.5, "unit": "GJ/m3"},
                "hydrogen_efficiency": {"target": 0.95, "unit": "ratio"}
            }
        }
    )
    integration_points: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Key integration points with other systems",
        example=[
            {
                "type": "material",
                "stream": "hydrogen_makeup",
                "source": "hydrogen_plant",
                "criticality": "high",
                "requirements": {
                    "pressure": {"value": 20, "unit": "barg"},
                    "purity": {"value": 99.9, "unit": "mol%"}
                }
            },
            {
                "type": "energy",
                "service": "steam_supply",
                "source": "central_utility_plant",
                "criticality": "medium",
                "requirements": {
                    "pressure": {"value": 40, "unit": "barg"},
                    "temperature": {"value": 250, "unit": "°C"}
                }
            }
        ]
    )
    maintenance_strategy: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="System-wide maintenance approach",
        example={
            "philosophy": "reliability_centered_maintenance",
            "critical_equipment": ["reactors", "compressors"],
            "maintenance_intervals": {
                "catalyst_regeneration": {"value": 12, "unit": "months"},
                "major_turnaround": {"value": 4, "unit": "years"}
            }
        }
    )
    documentation: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="System documentation references",
        example=[
            {
                "type": "process_flow_diagram",
                "number": "PFD-100-001",
                "revision": "R3",
                "date": "2024-01-15"
            },
            {
                "type": "operating_manual",
                "number": "OM-100-001",
                "revision": "R2",
                "date": "2024-01-15"
            }
        ]
    )

class CleanlinessPassport(BaseModel):
    """Model for equipment cleanliness certification and monitoring documentation"""
    id: str = Field(
        description="Unique identifier for cleanliness passport",
        example="CP-2024-HE101"  # CP = Cleanliness Passport, HE101 = Heat Exchanger 101
    )
    equipment_id: str = Field(
        description="Equipment identifier for which passport is issued",
        example="HE-101"  # Heat Exchanger 101
    )
    cleanliness_class: str = Field(
        description="Assigned cleanliness classification level",
        example="CLASS_1"  # Other examples: CLASS_2, CLASS_3,  based on cleanliness requirements
    )
    monitoring_regime: str = Field(
        description="Type of monitoring regime applied to the equipment",
        example="ENHANCED"  # Other examples: STANDARD, CRITICAL, BASIC
    )
    technical_passport_link: Optional[str] = Field(
        default=None,
        description="Reference to equipment technical passport document",
        example="DOC-TP-HE101-2024"
    )
    threshold_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Threshold values for different parameters",
        example={
            "pressure_drop": {
                "normal": {"min": 0.2, "max": 0.5, "unit": "bar"},
                "warning": {"min": 0.5, "max": 0.8, "unit": "bar"},
                "critical": {"value": 1.0, "unit": "bar"}
            },
            "heat_transfer_coefficient": {
                "design": 850,
                "minimum_acceptable": 680,
                "unit": "W/m²K",
                "monitoring_frequency": "daily"
            },
            "fouling_factor": {
                "maximum": 0.0002,
                "unit": "m²K/W",
                "action_level": 0.00015
            }
        }
    )
    fouling_tendency: Optional[str] = Field(
        default=None,
        description="Equipment's observed fouling characteristics",
        example="HIGH_SCALING_TENDENCY"  # Other examples: MODERATE_FOULING, LOW_FOULING, SEVERE_BIOFOULING
    )
    deposit_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Results from deposit analysis and characterization",
        example={
            "last_analysis_date": "2024-01-15",
            "composition": {
                "calcium_carbonate": "45%",
                "iron_oxide": "30%",
                "organic_matter": "15%",
                "others": "10%"
            },
            "physical_properties": {
                "thickness": "2.5 mm",
                "hardness": "moderate",
                "adhesion": "strong"
            },
            "chemical_analysis": {
                "pH": 7.8,
                "conductivity": "2500 µS/cm",
                "chlorides": "150 ppm"
            }
        }
    )
    fouling_dynamics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Observed fouling progression patterns",
        example={
            "rate": {"value": 0.1, "unit": "mm/month"},
            "pattern": "linear",  # Other examples: exponential, asymptotic
            "seasonal_factors": ["Summer peak", "Winter slowdown"],
            "contributing_factors": [
                "High inlet temperature",
                "Calcium supersaturation",
                "Low flow periods"
            ]
        }
    )
    cleaning_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Historical cleaning operations and their results",
        example=[
            {
                "date": "2024-01-15",
                "method": "Chemical cleaning - HCl",
                "contractor": "Industrial Cleaning Services Ltd",
                "duration": "8 hours",
                "effectiveness": "90%",
                "cost": 15000,
                "observations": "Heavy scale deposits successfully removed",
                "post_cleaning_inspection": "Passed",
                "next_cleaning_due": "2024-07-15"
            }
        ]
    )
    equipment_cost: Optional[float] = Field(
        default=None,
        description="Current equipment replacement cost for ROI calculations",
        example=250000.00  # Currency in base units
    )
    cleaning_recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended cleaning methods based on fouling history",
        example=[
            "Primary: Chemical cleaning with inhibited HCl",
            "Alternative: High pressure water jetting",
            "Emergency: Mechanical cleaning with soft scrapers",
            "Frequency: Every 6 months or at dP > 0.8 bar",
            "Special considerations: Use corrosion inhibitors during acid cleaning"
        ]
    )
    cleanliness_index: Optional[float] = Field(
        default=None,
        description="Current cleanliness performance index (0-1 scale)",
        example=0.85  # 85% clean relative to design conditions
    )
    target_cleanliness_index: Optional[float] = Field(
        default=None,
        description="Target cleanliness index for optimal operation",
        example=0.95  # 95% clean relative to design conditions
    )
    preventive_measures: List[str] = Field(
        default_factory=list,
        description="Implemented fouling prevention measures",
        example=[
            "Automated chemical dosing system",
            "Online fouling monitoring",
            "Regular water quality monitoring",
            "Flow rate optimization program",
            "Temperature control optimization"
        ]
    )
    last_update: datetime = Field(  # Уточнили тип
        default_factory=lambda: datetime.now(),
        description="Timestamp of last passport update",
        example="2024-01-20T14:30:00"
    )

class MonitoringData(BaseModel):
    """Model for equipment monitoring data"""
    id: str = Field(
        description="Monitoring record identifier",
        example="MON-001"
    )
    equipment_id: str = Field(
        description="Equipment identifier",
        example="E-101"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(),  # Добавили default_factory
        description="Measurement timestamp",
        example="2024-01-15T12:00:00"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,  # Добавили default_factory
        description="Measured parameters",
        example={
            "temperature": 75.5,
            "pressure": 5.2,
            "flow_rate": 100.0
        }
    )
    threshold_violations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Threshold violations",
        example=[{
            "parameter": "temperature",
            "value": 85.0,
            "threshold": 80.0,
            "severity": "high"
        }]
    )
    cleanliness_index: Optional[float] = Field(
        default=None,
        description="Calculated cleanliness index",
        example=0.85
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
        example="Increased fouling rate observed"
    )

    class Config:
        use_enum_values = True

class MonitoringParameter(BaseModel):
    """Model for monitoring parameters"""
    name: str = Field(
        description="Parameter name",
        example="temperature"
    )
    value: float = Field(
        default=0.0,  # Добавили default
        description="Parameter value",
        example=75.5
    )
    unit: str = Field(
        description="Measurement unit",
        example="°C"
    )
    threshold_min: Optional[float] = Field(
        default=None,
        description="Minimum threshold",
        example=70.0
    )
    threshold_max: Optional[float] = Field(
        default=None,
        description="Maximum threshold",
        example=80.0
    )
    critical_min: Optional[float] = Field(
        default=None,
        description="Critical minimum",
        example=60.0
    )
    critical_max: Optional[float] = Field(
        default=None,
        description="Critical maximum",
        example=90.0
    )

class FoulingAnalysis(BaseModel):
    """Model for fouling analysis"""
    id: str = Field(
        description="Analysis identifier",
        example="ANAL-001"
    )
    equipment_id: str = Field(
        description="Equipment identifier",
        example="E-101"
    )
    sample_date: datetime = Field(
        default_factory=lambda: datetime.now(),  # Добавили default_factory
        description="Sample collection date",
        example="2024-01-15T12:00:00"
    )
    location: str = Field(
        description="Sampling location",
        example="Heat exchanger tube inlet"
    )
    
    # Физико-химический анализ
    physical_properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Physical properties",
        example={
            "density": {"value": 1.2, "unit": "g/cm3"},
            "particle_size": {"value": 0.5, "unit": "mm"}
        }
    )
    
    chemical_composition: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chemical composition",
        example={
            "Fe": {"value": 10, "unit": "%"},
            "Ca": {"value": 5, "unit": "%"}
        }
    )
    
    solubility_tests: Dict[str, Any] = Field(
        default_factory=dict,
        description="Solubility test results",
        example={
            "water": "partially soluble",
            "acid": "fully soluble"
        }
    )
    
    thermal_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Thermal analysis results",
        example={
            "decomposition_temp": 400,
            "phase_changes": ["105°C", "400°C", "600°C"]
        }
    )

class FoulingImpactAssessment(BaseModel):
    """Model for fouling impact assessment"""
    id: str = Field(
        description="Assessment identifier",
        example="IMP-001"
    )
    equipment_id: str = Field(
        description="Equipment identifier",
        example="E-101"
    )
    assessment_date: datetime = Field(
        default_factory=lambda: datetime.now(),  # Добавили только default_factory для валидации
        description="Assessment date",
        example="2024-01-15T12:00:00"
    )
    
    # Экономическое влияние
    economic_impact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Economic impact assessment",
        example={
            "production_loss": {"value": 100000, "currency": "USD"},
            "energy_efficiency_loss": {"value": 15, "unit": "%"},
            "cleaning_costs": {"value": 50000, "currency": "USD"}
        }
    )
    
    # Влияние на надежность
    reliability_impact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reliability impact assessment",
        example={
            "equipment_lifetime_reduction": {"value": 20, "unit": "%"},
            "failure_probability_increase": {"value": 30, "unit": "%"},
            "maintenance_frequency_increase": {"value": 2, "unit": "times"}
        }
    )
    
    # Влияние на качество
    quality_impact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quality impact assessment",
        example={
            "product_quality_deviation": {"value": 10, "unit": "%"},
            "off_spec_products": {"value": 5, "unit": "%"}
        }
    )
    
    # Влияние на экологию
    environmental_impact: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Environmental impact assessment",
        example={
            "emissions_increase": {"value": 15, "unit": "%"},
            "waste_generation": {"value": 2000, "unit": "kg/year"}
        }
    )

class FoulingRiskAssessment(BaseModel):
    """Model for fouling risk assessment"""
    id: str = Field(
        description="Risk assessment identifier",
        example="RISK-001"
    )
    equipment_id: str = Field(
        description="Equipment identifier",
        example="E-101"
    )
    assessment_date: datetime = Field(
        default_factory=lambda: datetime.now(),  # Добавили только default_factory для валидации
        description="Assessment date",
        example="2024-01-15T12:00:00"
    )
    
    # Факторы риска
    risk_factors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Risk factors",
        example=[{
            "factor": "temperature_regime",
            "current_value": 75,
            "risk_level": "high",
            "contribution_weight": 0.4
        }]
    )
    
    # Оценка вероятности
    probability_assessment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Probability assessment",
        example={
            "fouling_probability": 0.8,
            "time_to_critical": {"value": 6, "unit": "months"},
            "confidence_level": 0.9
        }
    )
    
    # Меры по снижению рисков
    mitigation_measures: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Risk mitigation measures",
        example=[{
            "measure": "temperature_optimization",
            "effectiveness": 0.7,
            "implementation_cost": 10000,
            "priority": "high"
        }]
    )
    
    # Мониторинг рисков
    monitoring_requirements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Risk monitoring requirements",
        example=[{
            "parameter": "pressure_drop",
            "frequency": "daily",
            "threshold": {"value": 0.5, "unit": "bar"},
            "action_required": "alert"
        }]
    )

class FoulingPrediction(BaseModel):
    """Model for fouling prediction"""
    id: str = Field(
        description="Prediction identifier",
        example="PRED-001"
    )
    equipment_id: str = Field(
        description="Equipment identifier",
        example="E-101"
    )
    prediction_date: datetime = Field(
        default_factory=lambda: datetime.now(),  # Добавили только default_factory для валидации
        description="Prediction date",
        example="2024-01-15T12:00:00"
    )
    
    # Прогнозные модели
    fouling_rate_prediction: Dict[str, Any] = Field(
        default_factory=dict,
        description="Fouling rate prediction",
        example={
            "current_rate": {"value": 0.1, "unit": "mm/month"},
            "predicted_rate": {"value": 0.15, "unit": "mm/month"},
            "confidence_interval": {"min": 0.12, "max": 0.18}
        }
    )
    
    time_predictions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Time-based predictions",
        example={
            "time_to_cleaning": {"value": 6, "unit": "months"},
            "optimal_cleaning_interval": {"value": 8, "unit": "months"}
        }
    )
    
    impact_predictions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Impact predictions",
        example={
            "efficiency_loss": {"value": 20, "unit": "%"},
            "cost_impact": {"value": 100000, "currency": "USD"}
        }
    )

    class Config:
        use_enum_values = True


# ============= Base Functions =============

def get_all_enums() -> List[str]:
    """Get list of all enum names in the module."""
    current_module = sys.modules[__name__]
    return sorted([
        name for name, obj in inspect.getmembers(current_module)
        if inspect.isclass(obj) 
        and issubclass(obj, Enum) 
        and obj != Enum 
        and obj.__module__ == current_module.__name__
    ])

def get_all_models() -> List[str]:
    """Get list of all Pydantic model names in the module."""
    current_module = sys.modules[__name__]
    return sorted([
        name for name, obj in inspect.getmembers(current_module)
        if inspect.isclass(obj) 
        and issubclass(obj, BaseModel) 
        and obj != BaseModel 
        and obj.__module__ == current_module.__name__
    ])

def get_all_classes() -> List[str]:
    """Get list of all class names in the module."""
    current_module = sys.modules[__name__]
    return sorted([
        name for name, obj in inspect.getmembers(current_module)
        if inspect.isclass(obj) 
        and obj.__module__ == current_module.__name__
    ])

def get_classes_with_descriptions() -> Dict[str, Dict[str, Any]]:
    """Get all classes with their descriptions and types."""
    current_module = sys.modules[__name__]
    classes = {}
    
    for name, obj in inspect.getmembers(current_module):
        if (inspect.isclass(obj) and 
            obj.__module__ == current_module.__name__):
            
            class_type = 'class'
            if issubclass(obj, Enum):
                class_type = 'enum'
            elif issubclass(obj, BaseModel):
                class_type = 'pydantic_model'
                
            classes[name] = {
                'type': class_type,
                'description': inspect.getdoc(obj),
                'base_classes': [base.__name__ for base in obj.__bases__ 
                                 if base.__name__ not in ('object', 'BaseModel', 'Enum')]
            }
            
            # Добавляем дополнительную информацию для Pydantic моделей
            if class_type == 'pydantic_model':
                fields_count = len(obj.model_fields) if hasattr(obj, 'model_fields') else 0
                classes[name]['fields_count'] = fields_count
                
            # Добавляем информацию для Enum
            if class_type == 'enum':
                values_count = len(list(obj.__members__)) if hasattr(obj, '__members__') else 0
                classes[name]['values_count'] = values_count
                
    return classes


def _get_class_type(class_obj: type) -> str:
    """Determine the type of class."""
    if issubclass(class_obj, BaseModel):
        return 'pydantic_model'
    elif issubclass(class_obj, Enum):
        return 'enum'
    return 'class'


def _generate_type_example(field_schema: Dict[str, Any]) -> Any:
    """
    Generate example value based on the JSON schema of a single field.
    Дополнительно обрабатываем случаи:
    - enum
    - anyOf
    """
    # Если есть enum, возвращаем первый элемент как пример
    if 'enum' in field_schema:
        enum_values = field_schema['enum']
        if isinstance(enum_values, list) and len(enum_values) > 0:
            return enum_values[0]
        return None

    field_type = field_schema.get('type')
    
    if field_type == 'string':
        # Проверяем на формат дата-время
        if field_schema.get('format') == 'date-time':
            return datetime.now().isoformat()
        return "example_string"
    elif field_type == 'number':
        return 0.0
    elif field_type == 'integer':
        return 0
    elif field_type == 'boolean':
        return False
    elif field_type == 'array':
        items = field_schema.get('items', {})
        return [_generate_type_example(items)]
    elif field_type == 'object':
        if 'properties' in field_schema:
            return {
                prop_key: _generate_type_example(prop_val)
                for prop_key, prop_val in field_schema['properties'].items()
            }
        return {}
    elif field_type is None and 'anyOf' in field_schema:
        # Для полей с anyOf берём первый тип
        return _generate_type_example(field_schema['anyOf'][0])
    
    # fallback если не попали в известные варианты
    return None


def _generate_example(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate example data based on the entire model schema."""
    example = {}
    if 'properties' in schema:
        for prop, details in schema['properties'].items():
            # Если у поля явно указан example - берём его
            if 'example' in details:
                example[prop] = details['example']
            # Иначе пытаемся сформировать из типа
            elif 'default' in details:
                example[prop] = details['default']
            else:
                example[prop] = _generate_type_example(details)
    return example


def serialize(obj, seen=None):
    """Custom serializer for unsupported types in JSON."""
    if seen is None:
        seen = set()
        
    # Получаем id объекта для проверки циклических ссылок
    obj_id = id(obj)
    if obj_id in seen:
        return "Circular reference detected"
    seen.add(obj_id)
    
    try:
        if hasattr(obj, 'annotation') and hasattr(obj, 'description'):
            field_data = {
                'description': obj.description,
                'type': str(obj.annotation).replace('typing.', ''),
                'required': getattr(obj, 'required', None),
                'default': None if obj.default is Ellipsis else obj.default,
            }
            if hasattr(obj, 'json_schema_extra') and obj.json_schema_extra:
                if 'example' in obj.json_schema_extra:
                    field_data['example'] = obj.json_schema_extra['example']
            return field_data
        
        elif isinstance(obj, type) and issubclass(obj, Enum):
            return {
                'type': 'string',
                'enum': [e.value for e in obj],
                'description': obj.__doc__ or ''
            }
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, (list, tuple)):
            return [serialize(item, seen) for item in obj]
        elif isinstance(obj, dict):
            return {k: serialize(v, seen) for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            return {
                k: serialize(v, seen) for k, v in obj.__dict__.items()
                if not k.startswith('_')
            }
        return obj
    except Exception as e:
        logger.error(f"Error serializing object of type {type(obj).__name__}: {str(e)}")
        return str(obj)
    finally:
        seen.discard(obj_id)


def _format_field_info(field_info: Dict[str, Any]) -> Dict[str, Any]:
    """Формируем удобную структуру для отображения информации о поле."""
    formatted = {
        'type': str(field_info.get('type', 'Any')).replace('typing.', ''),
        'required': field_info.get('required', True),
        'description': field_info.get('description'),
    }
    if 'default' in field_info and field_info['default'] is not None:
        formatted['default'] = field_info['default']
    if 'example' in field_info:
        formatted['example'] = field_info['example']
    
    # Добавляем ограничения, если есть
    constraints = {}
    for key in ['gt', 'lt', 'ge', 'le', 'regex', 'max_length', 'min_length']:
        if key in field_info:
            constraints[key] = field_info[key]
    if constraints:
        formatted['constraints'] = constraints
        
    return formatted


def _format_field(name: str, field: Dict, indent: int = 0) -> List[str]:
    """Форматирует информацию по полю для текстового вывода."""
    lines = [f"{'  ' * indent}{name}:"]
    indent += 1
    
    # Основная информация
    for key in ['type', 'description', 'required', 'default']:
        if key in field and field[key] is not None:
            lines.append(f"{'  ' * indent}{key}: {field[key]}")
    
    # Пример
    if 'example' in field:
        if isinstance(field['example'], (dict, list)):
            example_str = json.dumps(field['example'], indent=2)
        else:
            example_str = str(field['example'])
        lines.append(f"{'  ' * indent}example: {example_str}")
    
    # Ограничения
    if 'constraints' in field:
        lines.append(f"{'  ' * indent}constraints:")
        for c_key, c_val in field['constraints'].items():
            lines.append(f"{'  ' * (indent+1)}{c_key}: {c_val}")
    
    return lines


def format_output(data: Any, format: str = 'text', style: str = 'full') -> str:
    """Format output data according to specified format and style."""
    try:
        if format == 'json':
            return json.dumps(data, indent=2, default=serialize)

        # ---- Ниже форматирование в текстовом виде ----
        if isinstance(data, dict):
            # Если это словарь словарей (например, результат describe)
            # и каждый value - тоже dict, форматируем по-своему
            if all(isinstance(v, dict) for v in data.values()):
                lines = []
                for class_name, class_info in data.items():
                    lines.append(f"{class_name}:")
                    for key, value in class_info.items():
                        if isinstance(value, (dict, list)):
                            lines.append(f"  {key}:")
                            formatted_v = format_output(value, format, style)
                            for line in formatted_v.split('\n'):
                                lines.append(f"    {line}")
                        else:
                            lines.append(f"  {key}: {value}")
                    lines.append("")  # пустая строка между записями
                return '\n'.join(lines)

            # Форматирование детальной информации о моделях
            if data.get('type') == 'pydantic_model' and 'fields' in data:
                lines = [
                    f"Class: {data.get('name', 'Unknown')}",
                    f"Type: {data['type']}",
                    f"Description: {data.get('description', 'No description')}",
                ]
                # Выводим поля
                lines.append("\nFields:")
                for name, field in data['fields'].items():
                    formatted_field = _format_field_info(field)
                    lines.extend(_format_field(name, formatted_field, indent=1))
                # Пример
                if 'example' in data:
                    lines.append("\nExample:")
                    lines.append(json.dumps(data['example'], indent=2))
                return '\n'.join(lines)

            # Если просто произвольный словарь
            if style == 'minimal':
                return ', '.join(f"{k}: {v}" for k, v in data.items())
            elif style == 'compact':
                return '\n'.join(f"{k}: {v}" for k, v in data.items())
            else:  # full
                lines = []
                for k, v in data.items():
                    if isinstance(v, (dict, list)):
                        lines.append(f"{k}:")
                        formatted_v = format_output(v, format, style)
                        for line in formatted_v.split('\n'):
                            lines.append(f"  {line}")
                    else:
                        lines.append(f"{k}: {v}")
                return '\n'.join(lines)

        elif isinstance(data, (list, tuple, set)):
            if style == 'minimal':
                return ', '.join(str(item) for item in data)
            else:
                return '\n'.join(f"- {format_output(item, format, style)}" for item in data)

        return str(data)
    except Exception as e:
        return f"Error formatting output: {str(e)}"


def get_class_details(class_name: str) -> Dict[str, Any]:
    """Get detailed information about a class (Enum/Pydantic Model/Plain class)."""
    class_obj = globals().get(class_name)
    if not class_obj:
        raise ValueError(f"Class {class_name} not found")

    details = {
        'name': class_name,
        'type': _get_class_type(class_obj),
        'description': inspect.getdoc(class_obj),
        'base_classes': [
            base.__name__ for base in class_obj.__bases__
            if base.__name__ not in ('object', 'BaseModel', 'Enum')
        ],
    }

    try:
        # Если это Pydantic-модель
        if issubclass(class_obj, BaseModel):
            logger.info(f"Processing Pydantic model: {class_name}")

            fields = {}
            for name, field in class_obj.model_fields.items():
                try:
                    fields[name] = serialize(field)
                except Exception as e:
                    logger.error(f"Error serializing field '{name}' in '{class_name}': {str(e)}")
                    raise

            details['fields'] = fields
            
            try:
                schema = class_obj.model_json_schema()
                details['schema'] = schema
            except Exception as e:
                logger.error(f"Error generating JSON schema for '{class_name}': {str(e)}")
                raise

            try:
                details['example'] = _generate_example(details['schema'])
            except Exception as e:
                logger.error(f"Error generating example for '{class_name}': {str(e)}")
                raise

        # Если это Enum
        elif issubclass(class_obj, Enum):
            details['values'] = {
                e.name: e.value for e in class_obj
            }

    except Exception as e:
        logger.error(f"Error processing class '{class_name}': {str(e)}")
        details['error'] = str(e)

    return details


def main():
    parser = argparse.ArgumentParser(description='Extract and process schema information')
    
    parser.add_argument('command', choices=[
        'list',         # список всех классов
        'info',         # полная информация о классе
        'name',         # только имя класса + тип
        'description',  # только описание класса
        'fields',       # только поля класса
        'schema',       # только схема класса
        'examples',     # только примеры
        'validate',     # проверить данные по схеме
        'all',          # вся информация о модуле
        'describe'      # список классов с описанием
    ], help='Command to execute')
    
    parser.add_argument('--class', dest='class_name',
                       help='Class name to get information about')
    
    parser.add_argument('--type', choices=['all', 'enums', 'models', 'classes'],
                       default='all',
                       help='Type of objects to list')
    
    parser.add_argument('--format', choices=['text', 'json'],
                       default='text',
                       help='Output format')
    
    parser.add_argument('--style', choices=['full', 'minimal', 'compact'],
                       default='full',
                       help='Output style (for text format)')
    
    parser.add_argument('--file',
                       help='Input file for validate command')

    args = parser.parse_args()

    try:
        result = None
        
        if args.command == 'list':
            if args.type == 'all':
                result = {
                    'classes': get_all_classes(),
                    'enums': get_all_enums(),
                    'models': get_all_models()
                }
            elif args.type == 'enums':
                result = get_all_enums()
            elif args.type == 'models':
                result = get_all_models()
            elif args.type == 'classes':
                result = get_all_classes()

        elif args.command == 'describe':
            # Получаем все классы, потом фильтруем
            all_classes = get_classes_with_descriptions()
            if args.type == 'all':
                result = all_classes
            else:
                filtered = {}
                for name, info in all_classes.items():
                    if ((args.type == 'enums' and info['type'] == 'enum') or
                        (args.type == 'models' and info['type'] == 'pydantic_model') or
                        (args.type == 'classes' and info['type'] == 'class')):
                        filtered[name] = info
                result = filtered

        elif args.command in ['info', 'name', 'description', 'fields', 'schema', 'examples']:
            if not args.class_name:
                raise ValueError(f"Class name is required for '{args.command}' command")
            details = get_class_details(args.class_name)
            
            if args.command == 'info':
                result = details
            elif args.command == 'name':
                result = {'name': details['name'], 'type': details['type']}
            elif args.command == 'description':
                result = {'description': details['description']}
            elif args.command == 'fields':
                # Для enum полей не будет, поэтому возвращаем пустой словарь в таком случае
                result = details.get('fields', {})
            elif args.command == 'schema':
                result = details.get('schema', {})
            elif args.command == 'examples':
                # Исправляем ключ с 'json_example' на 'example'
                result = details.get('example', {})

        elif args.command == 'validate':
            if not args.class_name:
                raise ValueError("Class name is required for validate command")
            if not args.file:
                raise ValueError("Input file is required for validate command")
            
            class_obj = globals().get(args.class_name)
            if not class_obj or not issubclass(class_obj, BaseModel):
                raise ValueError(f"{args.class_name} is not a Pydantic model")
            
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            validated = class_obj(**data)
            result = {"validation": "success", "data": validated.model_dump()}

        elif args.command == 'all':
            all_cls = get_all_classes()
            result = {
                'classes': {name: get_class_details(name) for name in all_cls},
                'summary': {
                    'total_classes': len(all_cls),
                    'total_enums': len(get_all_enums()),
                    'total_models': len(get_all_models())
                }
            }

        if result is not None:
            print(format_output(result, format=args.format, style=args.style))

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()