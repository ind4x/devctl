"""
Go Fiber framework generator and scaffolder.
"""

from devctl.generators.go_fiber.generator import generate_go_boilerplate
from devctl.generators.go_fiber.scaffolder import generate_go_resource

__all__ = ["generate_go_boilerplate", "generate_go_resource"]
