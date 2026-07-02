# Bootstrap: register all ORM models and association tables with Base.metadata.
#
# Why here?
# ─────────
# SQLAlchemy resolves relationship() string arguments ("ClassName",
# secondary="table_name") at mapper-configuration time, which is triggered
# the first time any mapped class is used in a query.  At that point ALL
# mappers in the same registry are configured together.  If any referenced
# class or Table object has not yet been imported, SQLAlchemy raises:
#
#   InvalidRequestError: expression '<name>' failed to locate a name
#
# Placing *all* imports here guarantees that importing anything from app.db
# (session, enums, mixins) is sufficient to bootstrap the complete metadata
# and mapper graph — regardless of which feature model is imported first and
# regardless of the entrypoint (uvicorn, celery worker, test runner, or an
# interactive shell script).
#
# Import order matters:
#   1. app.db.associations  — plain Table objects only, no relationships.
#   2. Feature models       — reference associations + each other via strings.
#
# Circular-import safety:
#   Each submodule (associations, feature models) imports Base and other
#   symbols from app.db.session / app.db.enums / app.db.mixins, not from
#   app.db itself.  Python resolves those as direct module imports, avoiding
#   any circular reference through this __init__.

# ── 1. Association tables ─────────────────────────────────────────────────────
import app.db.associations  # noqa: F401

# ── 2. Feature ORM models ─────────────────────────────────────────────────────
import app.features.assets.models  # noqa: F401
import app.features.campaigns.models  # noqa: F401
import app.features.feeds.models  # noqa: F401
import app.features.indicators.models  # noqa: F401
import app.features.investigations.models  # noqa: F401
import app.features.malware.models  # noqa: F401
import app.features.mitre.models  # noqa: F401
import app.features.reports.models  # noqa: F401
import app.features.threat_actors.models  # noqa: F401
import app.features.vulnerabilities.models  # noqa: F401
import app.features.watchlists.models  # noqa: F401
import app.features.enrichment.models  # noqa: F401
