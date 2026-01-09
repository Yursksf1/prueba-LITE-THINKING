"""
Helper to import domain package.

This module ensures the domain package is accessible from Django backend code.
The domain layer is a separate Python package managed by Poetry.

NOTE: In production, consider:
1. Installing domain package via pip install -e ../domain
2. Using proper Python packaging with setup.py/pyproject.toml
3. Adding domain to PYTHONPATH environment variable
"""
import sys
import os


def ensure_domain_in_path():
    """
    Add domain package to Python path if not already present.
    
    This is a temporary solution for development. For production,
    the domain package should be properly installed as a dependency.
    """
    domain_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'domain',
        'src'
    )
    domain_path = os.path.abspath(domain_path)
    
    if domain_path not in sys.path:
        sys.path.insert(0, domain_path)


# Auto-configure when this module is imported
ensure_domain_in_path()
