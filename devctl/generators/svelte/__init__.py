"""
Svelte framework generator and scaffolder.
"""

from devctl.generators.svelte.generator import generate_svelte_boilerplate
from devctl.generators.svelte.scaffolder import generate_svelte_resource

__all__ = ["generate_svelte_boilerplate", "generate_svelte_resource"]
