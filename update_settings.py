import sys

with open('apps/api/src/apps/api/app/config/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('log_level: str = DEFAULT_LOG_LEVEL', 'log_level: str = DEFAULT_LOG_LEVEL\n    log_format: str = "TEXT"', 1)

with open('apps/api/src/apps/api/app/config/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('apps/api/src/apps/api/app/main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

main_content = main_content.replace(
    'configure_logging(LoggingConfig(level=effective_settings.log_level))',
    'configure_logging(LoggingConfig(level=effective_settings.log_level, format_type=effective_settings.log_format))',
    1
)

with open('apps/api/src/apps/api/app/main.py', 'w', encoding='utf-8') as f:
    f.write(main_content)
