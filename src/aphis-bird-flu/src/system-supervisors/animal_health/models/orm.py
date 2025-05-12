"""
SQLAlchemy ORM models for the APHIS Bird Flu Tracking System.

This module defines ORM models that map to database tables, providing
a type-safe interface for database operations using SQLAlchemy.
"""

import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey, Date, DateTime, Text,
    Boolean, Table, PrimaryKeyConstraint, Index, Enum, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..config.database import Base
from . import base as domain_models

# Define enums to match database enum types
from enum import Enum as PyEnum

class SiteType(PyEnum):
    COMMERCIAL_POULTRY = "commercial_poultry"
    BACKYARD_POULTRY = "backyard_poultry"
    LIVE_BIRD_MARKET = "live_bird_market"
    WILD_BIRD_HABITAT = "wild_bird_habitat"
    WATERFOWL_REST_AREA = "waterfowl_rest_area"
    POULTRY_EXHIBITION = "poultry_exhibition"
    RENDERING_PLANT = "rendering_plant"
    FEED_MILL = "feed_mill"
    PROCESSING_PLANT = "processing_plant"
    HATCHERY = "hatchery"
    OTHER = "other"

class SiteStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    QUARANTINED = "quarantined"
    INFECTED = "infected"
    CLEANED = "cleaned_disinfected"
    UNKNOWN = "unknown"

class RiskLevel(PyEnum):
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"

class CaseStatus(PyEnum):
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    RECOVERED = "recovered"
    DECEASED = "deceased"
    UNKNOWN = "unknown"

class DetectionMethod(PyEnum):
    PCR_TEST = "pcr_test"
    RAPID_TEST = "rapid_test"
    SEROLOGY = "serology"
    CLINICAL_SIGNS = "clinical_signs"
    NECROPSY = "necropsy"
    SURVEILLANCE = "routine_surveillance"
    OTHER = "other"

class VirusSubtype(PyEnum):
    H5N1 = "h5n1"
    H5N2 = "h5n2"
    H5N8 = "h5n8"
    H7N3 = "h7n3"
    H7N9 = "h7n9"
    H9N2 = "h9n2"
    OTHER = "other"
    UNKNOWN = "unknown"

class PathogenicityLevel(PyEnum):
    HPAI = "highly_pathogenic"
    LPAI = "low_pathogenic"
    UNKNOWN = "unknown"

class SpeciesCategory(PyEnum):
    DOMESTIC_POULTRY = "domestic_poultry"
    DOMESTIC_WATERFOWL = "domestic_waterfowl"
    WILD_WATERFOWL = "wild_waterfowl"
    WILD_GALLINACEOUS = "wild_gallinaceous"
    WILD_OTHER = "wild_other"
    CAPTIVE_WILD = "captive_wild"
    OTHER = "other"

class AllocationStrategy(PyEnum):
    EQUAL = "equal_allocation"
    RISK_BASED = "risk_based"
    RESPONSE_ADAPTIVE = "response_adaptive"
    OPTIMIZED = "optimized"
    MANUAL = "manual"

# Many-to-many relationship tables
related_cases = Table(
    'related_cases',
    Base.metadata,
    Column('case_id', UUID(as_uuid=True), ForeignKey('bird_flu_cases.id', ondelete='CASCADE')),
    Column('related_case_id', UUID(as_uuid=True), ForeignKey('bird_flu_cases.id', ondelete='CASCADE')),
    Column('relationship_type', String(50), default='related'),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    PrimaryKeyConstraint('case_id', 'related_case_id')
)

sampling_plan_sites = Table(
    'sampling_plan_sites',
    Base.metadata,
    Column('plan_id', UUID(as_uuid=True), ForeignKey('adaptive_sampling_plans.id', ondelete='CASCADE')),
    Column('site_id', UUID(as_uuid=True), ForeignKey('surveillance_sites.id', ondelete='CASCADE')),
    Column('allocation_proportion', Float, default=0.0),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now()),
    PrimaryKeyConstraint('plan_id', 'site_id')
)

event_samples = Table(
    'event_samples',
    Base.metadata,
    Column('event_id', UUID(as_uuid=True), ForeignKey('surveillance_events.id', ondelete='CASCADE')),
    Column('sample_id', UUID(as_uuid=True), ForeignKey('laboratory_samples.id', ondelete='CASCADE')),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    PrimaryKeyConstraint('event_id', 'sample_id')
)

# ORM Models
class Region(Base):
    """Geographic region model"""
    __tablename__ = 'regions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    region_type = Column(String(50), nullable=False)
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)
    properties = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    sampling_plans = relationship("AdaptiveSamplingPlan", back_populates="region")
    
    def to_domain(self) -> domain_models.GeoRegion:
        """Convert ORM model to domain model"""
        # TODO: Convert PostGIS geometry to GeoLocation list
        # This is a simplified version
        boundary = []
        
        return domain_models.GeoRegion(
            name=self.name,
            region_type=self.region_type,
            boundary=boundary,
            properties=self.properties
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.GeoRegion) -> 'Region':
        """Create ORM model from domain model"""
        # TODO: Convert GeoLocation list to PostGIS geometry
        # This is a simplified version
        
        return cls(
            name=domain_obj.name,
            region_type=domain_obj.region_type,
            # Convert domain boundary to WKT format
            boundary=None,  # Placeholder
            properties=domain_obj.properties
        )


class SurveillanceSite(Base):
    """Surveillance site model"""
    __tablename__ = 'surveillance_sites'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    site_type = Column(Enum(SiteType), nullable=False)
    jurisdiction = Column(String(255), nullable=False)
    population = Column(Integer)
    status = Column(Enum(SiteStatus), nullable=False, default=SiteStatus.ACTIVE)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.UNKNOWN)
    risk_factors = Column(JSONB, default={})
    contact_info = Column(JSONB, default={})
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    cases = relationship("BirdFluCase", back_populates="site")
    surveillance_events = relationship("SurveillanceEvent", back_populates="site")
    sampling_plans = relationship("AdaptiveSamplingPlan", secondary=sampling_plan_sites, back_populates="sample_sites")
    
    def to_domain(self) -> domain_models.SurveillanceSite:
        """Convert ORM model to domain model"""
        # Convert PostGIS point to GeoLocation
        # This is a simplified version
        location = domain_models.GeoLocation(0, 0)  # Placeholder
        
        return domain_models.SurveillanceSite(
            name=self.name,
            location=location,
            site_type=self.site_type.value,
            jurisdiction=self.jurisdiction,
            population=self.population,
            status=self.status.value,
            risk_level=self.risk_level.value,
            risk_factors=self.risk_factors,
            contact_info=self.contact_info,
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.SurveillanceSite) -> 'SurveillanceSite':
        """Create ORM model from domain model"""
        # Convert GeoLocation to PostGIS point
        # This is a simplified version
        
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            name=domain_obj.name,
            location=None,  # Placeholder
            site_type=SiteType(domain_obj.site_type.value if isinstance(domain_obj.site_type, PyEnum) else domain_obj.site_type),
            jurisdiction=domain_obj.jurisdiction,
            population=domain_obj.population,
            status=SiteStatus(domain_obj.status.value if isinstance(domain_obj.status, PyEnum) else domain_obj.status),
            risk_level=RiskLevel(domain_obj.risk_level.value if isinstance(domain_obj.risk_level, PyEnum) else domain_obj.risk_level),
            risk_factors=domain_obj.risk_factors,
            contact_info=domain_obj.contact_info,
            notes=domain_obj.notes
        )


class BirdFluCase(Base):
    """Bird flu case model"""
    __tablename__ = 'bird_flu_cases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    detection_date = Column(Date, nullable=False)
    species = Column(String(255), nullable=False)
    species_category = Column(Enum(SpeciesCategory), nullable=False)
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.SUSPECTED)
    subtype = Column(Enum(VirusSubtype), nullable=False, default=VirusSubtype.UNKNOWN)
    pathogenicity = Column(Enum(PathogenicityLevel), nullable=False, default=PathogenicityLevel.UNKNOWN)
    detection_method = Column(Enum(DetectionMethod), nullable=False, default=DetectionMethod.SURVEILLANCE)
    sample_id = Column(UUID(as_uuid=True))
    genetic_sequence_id = Column(UUID(as_uuid=True))
    reported_by = Column(String(255))
    flock_size = Column(Integer)
    mortality_count = Column(Integer)
    site_id = Column(UUID(as_uuid=True), ForeignKey('surveillance_sites.id'))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("SurveillanceSite", back_populates="cases")
    samples = relationship("LaboratorySample", back_populates="case")
    genetic_sequences = relationship("GeneticSequence", back_populates="case")
    related_to = relationship(
        "BirdFluCase",
        secondary=related_cases,
        primaryjoin=id==related_cases.c.case_id,
        secondaryjoin=id==related_cases.c.related_case_id,
        backref="related_from"
    )
    
    def to_domain(self) -> domain_models.case.BirdFluCase:
        """Convert ORM model to domain model"""
        # Convert PostGIS point to GeoLocation
        # This is a simplified version
        location = domain_models.GeoLocation(0, 0)  # Placeholder
        
        return domain_models.case.BirdFluCase(
            location=location,
            detection_date=self.detection_date,
            species=self.species,
            species_category=self.species_category.value,
            status=self.status.value,
            subtype=self.subtype.value,
            pathogenicity=self.pathogenicity.value,
            detection_method=self.detection_method.value,
            sample_id=str(self.sample_id) if self.sample_id else None,
            genetic_sequence_id=str(self.genetic_sequence_id) if self.genetic_sequence_id else None,
            reported_by=self.reported_by,
            related_cases=[str(case.id) for case in self.related_to],
            flock_size=self.flock_size,
            mortality_count=self.mortality_count,
            site_id=str(self.site_id) if self.site_id else None,
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.case.BirdFluCase) -> 'BirdFluCase':
        """Create ORM model from domain model"""
        # Convert GeoLocation to PostGIS point
        # This is a simplified version
        
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            location=None,  # Placeholder
            detection_date=domain_obj.detection_date if isinstance(domain_obj.detection_date, date) else date.fromisoformat(domain_obj.detection_date),
            species=domain_obj.species,
            species_category=SpeciesCategory(domain_obj.species_category.value if isinstance(domain_obj.species_category, PyEnum) else domain_obj.species_category),
            status=CaseStatus(domain_obj.status.value if isinstance(domain_obj.status, PyEnum) else domain_obj.status),
            subtype=VirusSubtype(domain_obj.subtype.value if isinstance(domain_obj.subtype, PyEnum) else domain_obj.subtype),
            pathogenicity=PathogenicityLevel(domain_obj.pathogenicity.value if isinstance(domain_obj.pathogenicity, PyEnum) else domain_obj.pathogenicity),
            detection_method=DetectionMethod(domain_obj.detection_method.value if isinstance(domain_obj.detection_method, PyEnum) else domain_obj.detection_method),
            sample_id=uuid.UUID(domain_obj.sample_id) if domain_obj.sample_id else None,
            genetic_sequence_id=uuid.UUID(domain_obj.genetic_sequence_id) if domain_obj.genetic_sequence_id else None,
            reported_by=domain_obj.reported_by,
            flock_size=domain_obj.flock_size,
            mortality_count=domain_obj.mortality_count,
            site_id=uuid.UUID(domain_obj.site_id) if domain_obj.site_id else None,
            notes=domain_obj.notes
        )


class LaboratorySample(Base):
    """Laboratory sample model"""
    __tablename__ = 'laboratory_samples'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('bird_flu_cases.id', ondelete='CASCADE'))
    collection_date = Column(Date, nullable=False)
    sample_type = Column(String(255), nullable=False)
    collected_by = Column(String(255), nullable=False)
    lab_id = Column(String(255))
    received_date = Column(Date)
    testing_status = Column(String(50), default='pending')
    results = Column(JSONB, default={})
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    case = relationship("BirdFluCase", back_populates="samples")
    genetic_sequences = relationship("GeneticSequence", back_populates="sample")
    events = relationship("SurveillanceEvent", secondary=event_samples, back_populates="samples")
    
    def to_domain(self) -> domain_models.case.LaboratorySample:
        """Convert ORM model to domain model"""
        return domain_models.case.LaboratorySample(
            case_id=str(self.case_id),
            collection_date=self.collection_date,
            sample_type=self.sample_type,
            collected_by=self.collected_by,
            lab_id=self.lab_id,
            received_date=self.received_date,
            testing_status=self.testing_status,
            results=self.results,
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.case.LaboratorySample) -> 'LaboratorySample':
        """Create ORM model from domain model"""
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            case_id=uuid.UUID(domain_obj.case_id),
            collection_date=domain_obj.collection_date if isinstance(domain_obj.collection_date, date) else date.fromisoformat(domain_obj.collection_date),
            sample_type=domain_obj.sample_type,
            collected_by=domain_obj.collected_by,
            lab_id=domain_obj.lab_id,
            received_date=domain_obj.received_date if isinstance(domain_obj.received_date, date) else date.fromisoformat(domain_obj.received_date) if domain_obj.received_date else None,
            testing_status=domain_obj.testing_status,
            results=domain_obj.results,
            notes=domain_obj.notes
        )


class GeneticSequence(Base):
    """Genetic sequence model"""
    __tablename__ = 'genetic_sequences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('bird_flu_cases.id', ondelete='CASCADE'))
    sample_id = Column(UUID(as_uuid=True), ForeignKey('laboratory_samples.id', ondelete='CASCADE'))
    sequence_data = Column(Text, nullable=False)
    sequencing_method = Column(String(255), nullable=False)
    sequencing_date = Column(Date, nullable=False)
    gene_segments = Column(JSONB, nullable=False)
    sequence_quality = Column(Float, nullable=False)
    external_database_ids = Column(JSONB, default={})
    analysis_results = Column(JSONB, default={})
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    case = relationship("BirdFluCase", back_populates="genetic_sequences")
    sample = relationship("LaboratorySample", back_populates="genetic_sequences")
    
    def to_domain(self) -> domain_models.case.GeneticSequence:
        """Convert ORM model to domain model"""
        return domain_models.case.GeneticSequence(
            case_id=str(self.case_id),
            sample_id=str(self.sample_id),
            sequence_data=self.sequence_data,
            sequencing_method=self.sequencing_method,
            sequencing_date=self.sequencing_date,
            gene_segments=self.gene_segments,
            sequence_quality=self.sequence_quality,
            external_database_ids=self.external_database_ids,
            analysis_results=self.analysis_results,
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.case.GeneticSequence) -> 'GeneticSequence':
        """Create ORM model from domain model"""
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            case_id=uuid.UUID(domain_obj.case_id),
            sample_id=uuid.UUID(domain_obj.sample_id),
            sequence_data=domain_obj.sequence_data,
            sequencing_method=domain_obj.sequencing_method,
            sequencing_date=domain_obj.sequencing_date if isinstance(domain_obj.sequencing_date, date) else date.fromisoformat(domain_obj.sequencing_date),
            gene_segments=domain_obj.gene_segments,
            sequence_quality=domain_obj.sequence_quality,
            external_database_ids=domain_obj.external_database_ids,
            analysis_results=domain_obj.analysis_results,
            notes=domain_obj.notes
        )


class AdaptiveSamplingPlan(Base):
    """Adaptive sampling plan model"""
    __tablename__ = 'adaptive_sampling_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    region_id = Column(UUID(as_uuid=True), ForeignKey('regions.id', ondelete='CASCADE'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    allocation_strategy = Column(Enum(AllocationStrategy), nullable=False, default=AllocationStrategy.RISK_BASED)
    current_stage = Column(Integer, nullable=False, default=0)
    max_stages = Column(Integer, nullable=False, default=3)
    total_resources = Column(JSONB, default={})
    stage_results = Column(JSONB, default=[])
    adaptation_rules = Column(JSONB, default={})
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    region = relationship("Region", back_populates="sampling_plans")
    sample_sites = relationship("SurveillanceSite", secondary=sampling_plan_sites, back_populates="sampling_plans")
    surveillance_events = relationship("SurveillanceEvent", back_populates="plan")
    
    def to_domain(self) -> domain_models.surveillance.AdaptiveSamplingPlan:
        """Convert ORM model to domain model"""
        return domain_models.surveillance.AdaptiveSamplingPlan(
            name=self.name,
            region={},  # This would be converted from region relationship
            start_date=self.start_date,
            end_date=self.end_date,
            allocation_strategy=self.allocation_strategy.value,
            sample_sites=[str(site.id) for site in self.sample_sites],
            current_stage=self.current_stage,
            max_stages=self.max_stages,
            total_resources=self.total_resources,
            stage_results=self.stage_results,
            adaptation_rules=self.adaptation_rules,
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.surveillance.AdaptiveSamplingPlan) -> 'AdaptiveSamplingPlan':
        """Create ORM model from domain model"""
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            name=domain_obj.name,
            region_id=None,  # This would be set from the region relationship
            start_date=domain_obj.start_date if isinstance(domain_obj.start_date, date) else date.fromisoformat(domain_obj.start_date),
            end_date=domain_obj.end_date if isinstance(domain_obj.end_date, date) else date.fromisoformat(domain_obj.end_date),
            allocation_strategy=AllocationStrategy(domain_obj.allocation_strategy.value if isinstance(domain_obj.allocation_strategy, PyEnum) else domain_obj.allocation_strategy),
            current_stage=domain_obj.current_stage,
            max_stages=domain_obj.max_stages,
            total_resources=domain_obj.total_resources,
            stage_results=domain_obj.stage_results,
            adaptation_rules=domain_obj.adaptation_rules,
            notes=domain_obj.notes
        )


class SurveillanceEvent(Base):
    """Surveillance event model"""
    __tablename__ = 'surveillance_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey('surveillance_sites.id', ondelete='CASCADE'), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('adaptive_sampling_plans.id', ondelete='SET NULL'))
    event_date = Column(Date, nullable=False)
    collector = Column(String(255), nullable=False)
    samples_collected = Column(Integer, nullable=False, default=0)
    sample_types = Column(JSONB, nullable=False)
    target_species = Column(JSONB, nullable=False)
    weather_conditions = Column(JSONB, default={})
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("SurveillanceSite", back_populates="surveillance_events")
    plan = relationship("AdaptiveSamplingPlan", back_populates="surveillance_events")
    samples = relationship("LaboratorySample", secondary=event_samples, back_populates="events")
    
    def to_domain(self) -> domain_models.surveillance.SurveillanceEvent:
        """Convert ORM model to domain model"""
        return domain_models.surveillance.SurveillanceEvent(
            site_id=str(self.site_id),
            plan_id=str(self.plan_id) if self.plan_id else None,
            event_date=self.event_date,
            collector=self.collector,
            samples_collected=self.samples_collected,
            sample_types=self.sample_types,
            target_species=self.target_species,
            weather_conditions=self.weather_conditions,
            samples=[str(sample.id) for sample in self.samples],
            notes=self.notes,
            id=str(self.id),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
    
    @classmethod
    def from_domain(cls, domain_obj: domain_models.surveillance.SurveillanceEvent) -> 'SurveillanceEvent':
        """Create ORM model from domain model"""
        return cls(
            id=uuid.UUID(domain_obj.id) if hasattr(domain_obj, 'id') and domain_obj.id else uuid.uuid4(),
            site_id=uuid.UUID(domain_obj.site_id),
            plan_id=uuid.UUID(domain_obj.plan_id) if domain_obj.plan_id else None,
            event_date=domain_obj.event_date if isinstance(domain_obj.event_date, date) else date.fromisoformat(domain_obj.event_date),
            collector=domain_obj.collector,
            samples_collected=domain_obj.samples_collected,
            sample_types=domain_obj.sample_types,
            target_species=domain_obj.target_species,
            weather_conditions=domain_obj.weather_conditions,
            notes=domain_obj.notes
        )


class Forecast(Base):
    """Forecast model"""
    __tablename__ = 'forecasts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_date = Column(Date, nullable=False)
    days_ahead = Column(Integer, nullable=False, default=7)
    model_info = Column(JSONB, nullable=False)
    risk_by_region = Column(JSONB, nullable=False)
    predicted_case_count = Column(JSONB, nullable=False)
    confidence_intervals = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())


class Notification(Base):
    """Notification model"""
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False)
    content = Column(JSONB, nullable=False)
    recipients = Column(JSONB, nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    source_id = Column(UUID(as_uuid=True))
    source_type = Column(String(50))
    delivery_stats = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    sent_at = Column(DateTime(timezone=True))


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    role = Column(String(50), nullable=False, default='viewer')
    organization = Column(String(255))
    notification_preferences = Column(JSONB, default={})
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = 'audit_log'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    action = Column(String(255), nullable=False)
    entity_type = Column(String(255), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")