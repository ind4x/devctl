"""
NestJS framework generator and scaffolder.
"""

from devctl.generators.nestjs.generator import generate_nest_boilerplate
from devctl.generators.nestjs.scaffolder import generate_nest_resource

__all__ = ["generate_nest_boilerplate", "generate_nest_resource"]
