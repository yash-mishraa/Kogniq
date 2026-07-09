# Shared Configuration Contracts

Contains immutable base settings, runtime environment classification, safe constants, and an injectable environment-backed provider. The provider reads generic `ENVIRONMENT` and `LOG_LEVEL` names by default and accepts an explicit prefix for composed applications.

The public surface is exported from `shared.config`. Business settings, secret values, service credentials, provider clients, and deployment policy do not belong here.
