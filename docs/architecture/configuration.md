# Configuration

Configuration priority:

CLI arguments

↓

Environment variables

↓

Configuration file

↓

Defaults

Configuration file:

~/.config/opspilot/config.yaml

Project-local configuration:

.opspilot/config.yaml

Project configuration overrides user configuration.

Secrets are never stored inside configuration files.

Secrets are resolved through SecretProvider.
