# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Interactive restore mode with fzf integration
- File compression for old items
- Network sync across machines
- GUI interface
- Trash profiles (work/personal)
- Smart purging with ML

---

## [1.0.0] - 2025-10-01

### 🎉 Initial Release

First stable release of trsh - a world-class trash utility for the command line!

### Added

#### Core Features

- **Safe Delete** - Move files to trash instead of permanent deletion
- **Easy Restore** - Restore files by pattern matching
- **Advanced Search** - Search by name, path, date, size, or tags
- **Statistics** - View trash analytics and usage patterns
- **Undo Support** - Undo last delete operation
- **Tag System** - Organize deleted files with custom tags

#### Safety Features

- Critical path protection (prevents deletion of /, /bin, etc.)
- Confirmation prompts for destructive operations
- Dry-run mode for all commands
- Transaction logging for audit trail
- Integrity verification and repair

#### Performance

- SQLite-backed metadata storage
- File deduplication to save disk space
- Indexed queries for fast search
- Efficient hash-based duplicate detection

#### User Experience

- Beautiful colored terminal output
- Clear error messages
- Comprehensive help text
- Progress indicators for batch operations

#### Commands

- `trsh delete` - Move files to trash
- `trsh restore` - Restore files from trash
- `trsh list` - List trash contents
- `trsh search` - Advanced search with filters
- `trsh empty` - Empty entire trash
- `trsh purge` - Purge old files
- `trsh stats` - Show statistics
- `trsh undo` - Undo last operation
- `trsh history` - Show operation history
- `trsh verify` - Verify integrity
- `trsh config` - Manage configuration

#### Developer Features

- Comprehensive test suite (30+ tests)
- > 85% test coverage
- CI/CD with GitHub Actions
- Type hints throughout codebase
- Detailed documentation
- Zero external dependencies (Python stdlib only)

### Technical Details

- Python 3.7+ support
- SQLite for metadata storage
- SHA256 for file hashing
- UUID-based file identification
- Cross-platform compatibility (Linux, macOS, Windows)

### Documentation

- Complete README with examples
- Contributing guidelines
- Development setup guide
- Architecture documentation
- Quick reference card

---

## Version History Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- New features

### Changed

- Changes to existing features

### Deprecated

- Features marked for removal

### Removed

- Removed features

### Fixed

- Bug fixes

### Security

- Security improvements
```

---

## Semantic Versioning Guide

Given a version number MAJOR.MINOR.PATCH:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes

  - API changes
  - Removed features
  - Incompatible changes

- **MINOR** (1.0.0 → 1.1.0): New features (backwards compatible)

  - New commands
  - New options
  - New functionality

- **PATCH** (1.0.0 → 1.0.1): Bug fixes (backwards compatible)
  - Bug fixes
  - Performance improvements
  - Documentation updates

---

## Release Process

### Pre-release Checklist

- [ ] All tests pass
- [ ] Version number updated in:
  - [ ] `trsh.py` (Trash.VERSION)
  - [ ] `setup.py` (version)
  - [ ] This CHANGELOG
- [ ] CHANGELOG updated with changes
- [ ] README updated if needed
- [ ] Documentation reviewed
- [ ] CI/CD passing

### Creating a Release

```bash
# 1. Update version numbers
# 2. Update CHANGELOG.md
# 3. Commit changes
git add .
git commit -m "chore: prepare release v1.1.0"

# 4. Create tag
git tag -a v1.1.0 -m "Release v1.1.0"

# 5. Push
git push origin main
git push origin v1.1.0

# 6. Create GitHub release
# Go to: https://github.com/YOUR_USERNAME/trsh/releases/new
# - Choose tag: v1.1.0
# - Copy changelog entry
# - Publish release
```

---

## Future Versions (Examples)

### [1.1.0] - TBD

#### Planned Features

- Interactive restore mode
- Compression support
- Better progress indicators

### [1.0.1] - TBD

#### Planned Fixes

- Improve error messages
- Fix edge cases in restore
- Performance optimizations

---

## Links

- [Homepage](https://github.com/YOUR_USERNAME/trsh)
- [Issue Tracker](https://github.com/YOUR_USERNAME/trsh/issues)
- [Releases](https://github.com/YOUR_USERNAME/trsh/releases)

---

## Contributors

Thanks to all contributors who have helped make trsh better!

- Elias W. BA ([@YOUR_USERNAME](https://github.com/YOUR_USERNAME)) - Creator & Maintainer

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Note:** This changelog is automatically generated from git commits and release notes.
For detailed changes, see [commit history](https://github.com/YOUR_USERNAME/trsh/commits/main).
