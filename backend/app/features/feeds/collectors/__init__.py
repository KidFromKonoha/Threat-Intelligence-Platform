"""Collector implementations.

Every module in this package that contains a class decorated with
@registry.register is automatically discovered when the framework calls
registry.autodiscover() at startup.

To add a new feed:
  1. Create a new .py file here.
  2. Subclass BaseCollector, set feed_name, implement fetch/validate/normalize.
  3. Decorate with @registry.register.
  4. No other file needs to change.
"""
