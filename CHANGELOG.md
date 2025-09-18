# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-09-19

### Added 
- Added structured output support with pydantic models in a type safe manner that confines to the constraints

## [0.6.2] - 2025-09-18

### Fixed 
- Fixed returned response not being added to the messages history

## [0.6.1] - 2025-09-14

### Changed
- Removed unnecessary logging statements
- Minor bug fixes and cleanup

## [0.6.0] - 2025-09-14

### Fixed
- Updated system prompt handling in Agent and AgentConfig
- Improved configuration management

### Changed
- Enhanced agent initialization and configuration flow

## [0.5.1] - 2025-09-14

### Changed
- Improved README documentation to reflect actual implementation
- Updated project documentation

## [0.5.0] - 2025-09-14

### Added
- **GitToolKit**: New comprehensive toolkit for git operations
- Enhanced git integration capabilities

### Removed
- Calculator directory and related test files
- Cleaned up unnecessary example code

### Changed
- Expanded toolkit architecture with git capabilities
- Updated project structure

## [0.4.0] - 2025-09-13

### Added
- **Permission callback system**: Function execution now requires user confirmation
- Enhanced security with interactive permission requests

### Changed
- Improved agent execution flow with confirmation prompts
- Updated agent settings configuration

## [0.3.0] - 2025-09-13

### Changed
- Minor version bump with incremental improvements
- Internal refactoring and optimizations

## [0.2.0] - 2025-09-13

### Added
- **User configuration directory**: Proto-agent now creates and uses a dedicated user config directory
- Persistent storage for `.env` and `config.toml` files
- Improved configuration management system

### Changed
- Enhanced configuration persistence and management

## [0.1.0] - 2025-09-13

### Added
- Initial release of proto-agent
- Core agent framework architecture
- Basic toolkit system
- Command-line interface using Click
- Working directory variable option for CLI

### Changed
- Lowered Python version requirement for broader compatibility
- Restructured file hierarchy for proper packaging

### Features
- **LiteLLM Integration**: Switched from google.genai SDK to LiteLLM for broader model support
- **Capability-based toolkit architecture**: Modular design for extensible functionality
- **File operations toolkit**: Basic file manipulation capabilities
- **System info toolkit**: System information gathering tools
- **Interactive CLI**: User-friendly command-line interface with confirmation prompts

---

[0.7.0]: https://github.com/WeismannS/proto-agent/compare/v0.6.3...v0.7.0