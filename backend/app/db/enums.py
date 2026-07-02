"""Shared enumeration types used across multiple feature models.

Defined in app.db to avoid circular imports: any feature model can import
from here without depending on another feature's package.
"""

import enum


class IndicatorType(str, enum.Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    ASN = "asn"
    FILE_NAME = "file_name"
    PROCESS_NAME = "process_name"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    CERTIFICATE = "certificate"
    USER_AGENT = "user_agent"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IndicatorStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    FALSE_POSITIVE = "false_positive"
    UNDER_REVIEW = "under_review"


class FeedType(str, enum.Enum):
    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    INTERNAL = "internal"


class FeedStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class FeedRunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class AssetType(str, enum.Enum):
    PUBLIC_IP = "public_ip"
    DOMAIN = "domain"
    EMAIL_DOMAIN = "email_domain"
    CLOUD_ACCOUNT = "cloud_account"
    SUPPLIER = "supplier"
    VPN_GATEWAY = "vpn_gateway"
    PRODUCT = "product"
    MANUFACTURING_PLANT = "manufacturing_plant"
    VEHICLE_PLATFORM = "vehicle_platform"
    REPOSITORY = "repository"


class AssetCriticality(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InvestigationStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    ARCHIVED = "archived"


class InvestigationPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ThreatActorSophistication(str, enum.Enum):
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    NOVICE = "novice"
    UNKNOWN = "unknown"


class CommentEntityType(str, enum.Enum):
    INDICATOR = "indicator"
    THREAT_ACTOR = "threat_actor"
    MALWARE = "malware"
    CAMPAIGN = "campaign"
    VULNERABILITY = "vulnerability"
    INVESTIGATION = "investigation"
    ASSET = "asset"


class EnrichmentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

