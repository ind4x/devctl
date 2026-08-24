"""
Spring Boot framework generator and scaffolder.
"""

from devctl.generators.spring.generator import (
    download_spring_boilerplate,
    patch_pom_xml,
)
from devctl.generators.spring.scaffolder import generate_spring_resource

__all__ = ["download_spring_boilerplate", "generate_spring_resource", "patch_pom_xml"]
