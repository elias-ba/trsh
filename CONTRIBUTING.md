# Contributing to trsh

First off, thank you for considering contributing to trsh! 🎉

It's people like you that make trsh such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

This project adheres to a simple code of conduct:

- **Be kind** - Treat everyone with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Everyone is learning
- **Be inclusive** - Welcome diverse perspectives

---

## 💡 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

**Template:**

```markdown
**Description**
A clear description of the bug

**Steps to Reproduce**

1. Run command: `trsh delete file.txt`
2. See error

**Expected Behavior**
File should be moved to trash

**Actual Behavior**
Program crashes with error

**Environment**

- OS: Ubuntu 22.04
- Python: 3.11.0
- trsh version: 1.0.0

**Additional Context**
Any other relevant information
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- **Use case** - Why is this needed?
- **Proposed solution** - How should it work?
- **Alternatives** - What other approaches exist?
- **Examples** - Show usage examples

**Template:**

````markdown
**Feature Request**
Add compression for old files in trash

**Use Case**
Users with large files in trash waste disk space

**Proposed Solution**
Auto-compress files older than 30 days using gzip

**Example Usage**

```bash
trsh config set auto-compress true
trsh config set compress-after-days 30
```
````

Alternatives Considered

- User manually compresses files
- Use external compression tools

````bash

### Pull Requests

1. **Fork** the repository
2. **Create** a branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** your changes
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

---

## 🔧 Development Setup

### Prerequisites

- Python 3.7+
- Git
- Conda (recommended) or venv

### Setup Steps

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/trsh.git
cd trsh

# 2. Create environment
conda create -n trsh-dev python=3.11 -y
conda activate trsh-dev

# 3. Install dependencies
conda install -y pytest pytest-cov black pylint mypy
pip install rich

# 4. Install in development mode
pip install -e .

# 5. Run tests
python test_trsh.py

# 6. Verify everything works
python trsh.py --help
````

### Project Structure

```
trsh/
├── trsh.py              # Main implementation
├── test_trsh.py         # Test suite
├── README.md            # User documentation
├── CONTRIBUTING.md      # This file
├── setup.py             # Package configuration
└── .github/
    └── workflows/
        └── ci.yml       # CI/CD pipeline
```

---

## 📝 Coding Guidelines

### Style Guide

We follow **PEP 8** with **Black** formatting.

```bash
# Format your code
black trsh.py test_trsh.py

# Check formatting
black --check trsh.py
```

### Code Quality

```bash
# Run linter
pylint trsh.py

# Type checking
mypy trsh.py

# All checks
make check-all
```

### Python Style

```python
# Good: Clear variable names
def delete_file(filepath: str, tags: List[str] = None) -> bool:
    """Delete a file with optional tags."""
    original_path = Path(filepath).resolve()
    file_size = original_path.stat().st_size
    return True

# Bad: Unclear names, no types
def df(f, t=None):
    p = Path(f).resolve()
    s = p.stat().st_size
    return True
```

### Documentation

```python
def restore_file(self, pattern: str, output: Optional[Path] = None) -> int:
    """
    Restore files matching pattern from trash.

    Args:
        pattern: Filename pattern to match (supports wildcards)
        output: Optional output directory (default: original location)

    Returns:
        Number of files successfully restored

    Raises:
        PermissionError: If lacking permissions to restore

    Example:
        >>> trash.restore('*.txt')
        2
        >>> trash.restore('document.pdf', output=Path('/tmp'))
        1
    """
    pass
```

---

## 📦 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### Examples

**Good commits:**

```bash
feat(search): add size filter support

Add --size flag to search command allowing queries like:
- trsh search "*.pdf" --size ">10MB"
- trsh search "image" --size "<1GB"

Closes #42

---

fix(restore): handle missing files gracefully

Previously crashed when trashed file was manually deleted.
Now checks existence and cleans up database entry.

Fixes #38

---

docs(readme): update installation instructions

Add conda installation method and troubleshooting section
```

**Bad commits:**

```bash
# Too vague
update code
fix stuff
changes

# No context
feat: add feature
fix: fix bug
```

### Commit Message Template

Create `~/.git-commit-template`:

```bash
# <type>(<scope>): <subject>
# |<----  Preferably using up to 50 chars  --->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or resources
# Examples: Fixes #123, Closes #456, Related to #789

# --- COMMIT END ---
# Type can be
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring code)
#    style    (formatting, missing semicolons, etc; no code change)
#    docs     (changes to documentation)
#    test     (adding or refactoring tests; no production code change)
#    chore    (updating build tasks, etc; no production code change)
# --------------------
```

Enable:

```bash
git config --global commit.template ~/.git-commit-template
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Update tests** - Add tests for new features
2. **Run all tests** - Ensure nothing breaks
3. **Update docs** - Update README if needed
4. **Format code** - Run `black`
5. **Check quality** - Run `pylint` and `mypy`

```bash
# Pre-submission checklist
black trsh.py test_trsh.py
pylint trsh.py
python test_trsh.py
# All should pass!
```

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?

- [ ] Test A
- [ ] Test B

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed my code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] Added tests that prove fix/feature works
- [ ] New and existing tests pass locally
- [ ] No new warnings generated

## Related Issues

Fixes #(issue number)
```

### Review Process

1. **Submit PR** - Create pull request
2. **CI runs** - Automated tests run
3. **Code review** - Maintainer reviews code
4. **Address feedback** - Make requested changes
5. **Approval** - PR gets approved
6. **Merge** - Code merged to main

### What Reviewers Look For

- ✅ Tests pass
- ✅ Code is well-documented
- ✅ Follows style guidelines
- ✅ No breaking changes (or properly documented)
- ✅ Clear commit messages
- ✅ Addresses a real need

---

## 🧪 Testing Guidelines

### Writing Tests

```python
def test_new_feature(self):
    """Test description - what are we testing?"""
    # Arrange - Set up test data
    test_file = self.test_files_dir / 'test.txt'
    test_file.write_text('content')

    # Act - Perform the operation
    result = self.trash.delete(str(test_file))

    # Assert - Verify the result
    self.assertTrue(result)
    self.assertFalse(test_file.exists())
```

### Test Coverage

Aim for **>80% coverage**:

```bash
# Run with coverage
pytest --cov=trsh --cov-report=html test_trsh.py

# View report
open htmlcov/index.html
```

### Test Categories

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test feature workflows
3. **Edge Cases** - Test error conditions

### Running Tests

```bash
# All tests
python test_trsh.py

# Specific test
pytest test_trsh.py::TestTrash::test_delete_file -v

# With verbose output
python test_trsh.py -v

# Watch mode (requires pytest-watch)
ptw test_trsh.py -- -v
```

---

## 📚 Documentation

### Code Documentation

```python
# Good: Clear docstring with examples
def search(self, query: str, from_path: Optional[str] = None) -> List[TrashItem]:
    """
    Search trash items with optional filters.

    Args:
        query: Search term to match in file paths
        from_path: Optional path prefix to filter results

    Returns:
        List of TrashItem objects matching criteria

    Example:
        >>> items = trash.search("document", from_path="~/work")
        >>> len(items)
        5
    """
    pass
```

### README Updates

When adding features, update:

- Feature list
- Usage examples
- Command documentation

### Inline Comments

```python
# Good: Explain WHY, not WHAT
# Use deduplication to save disk space when same file deleted multiple times
if self._file_exists_in_trash(file_hash):
    return self._create_reference(file_hash)

# Bad: Obvious what code does
# Check if file hash exists
if self._file_exists_in_trash(file_hash):
    return self._create_reference(file_hash)
```

---

## 🎯 Areas for Contribution

### Good First Issues

Perfect for new contributors:

- Documentation improvements
- Adding examples
- Writing tests
- Fixing typos
- Improving error messages

### Feature Ideas

- Interactive mode with fzf integration
- File compression for old items
- Network trash (sync across machines)
- GUI interface
- Trash profiles (work/personal)
- Smart purging with ML
- File encryption
- Trash analytics dashboard

### Performance Improvements

- Parallel file hashing
- Optimize database queries
- Batch operations
- Caching

---

## 🐛 Debugging Tips

### Enable Debug Mode

```bash
DEBUG=1 python trsh.py delete file.txt
```

### Inspect Database

```bash
sqlite3 ~/.trashbin/metadata.db
.tables
SELECT * FROM trash_items;
.quit
```

### Common Issues

**Import errors:**

```bash
pip install -e .
```

**Test failures:**

```bash
python test_trsh.py -v  # Verbose output
pytest test_trsh.py -v --tb=short  # Short traceback
```

**Formatting:**

```bash
black --diff trsh.py  # See what would change
black trsh.py  # Apply changes
```

---

## 📞 Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: <eliaswalyba@gmail.com>

---

## 🏆 Recognition

Contributors will be:

- Listed in README
- Mentioned in release notes
- Added to CONTRIBUTORS file (if created)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to trsh!** 🚀

Every contribution, no matter how small, makes trsh better for everyone.

Happy coding! 💻✨
