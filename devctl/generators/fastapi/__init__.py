"""
FastAPI framework generator and scaffolder.
"""

from devctl.generators.fastapi.generator import generate_fastapi_boilerplate
from devctl.generators.fastapi.scaffolder import generate_fastapi_resource

__all__ = ["generate_fastapi_boilerplate", "generate_fastapi_resource"]
