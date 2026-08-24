"""
NodeJS framework generator and scaffolder.
"""

from devctl.generators.nodejs.generator import generate_nodejs_boilerplate
from devctl.generators.nodejs.scaffolder import generate_nodejs_resource

__all__ = ["generate_nodejs_boilerplate", "generate_nodejs_resource"]
