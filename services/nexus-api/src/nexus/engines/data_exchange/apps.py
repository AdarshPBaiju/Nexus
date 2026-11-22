"""
nexus.engines.data_exchange.apps - Data exchange application configuration.
"""

from django.apps import AppConfig


class DataExchangeConfig(AppConfig):
    name = "nexus.engines.data_exchange"
    label = "data_exchange"
    verbose_name = "Data Exchange & Dynamic Mapping Engine"
