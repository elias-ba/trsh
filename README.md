# 🗑️ trsh - Delete with Confidence, Restore with Ease

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> A world-class trash utility that makes file deletion safe, recoverable, and intelligent.

**Ever accidentally deleted the wrong file?** With `trsh`, you can delete with confidence knowing you can always restore. Unlike `rm`, `trsh` gives you a safety net.

## ✨ Features

- 🗑️ **Safe Delete** - Move files to trash instead of permanent deletion
- ♻️ **Easy Restore** - Restore deleted files with pattern matching or interactive mode
- 🔍 **Powerful Search** - Find files by name, path, date, size, or tags
- 📊 **Rich Analytics** - View statistics and deletion patterns
- 🏷️ **Tag System** - Organize deleted files with custom tags
- ⏮️ **Undo Support** - Undo accidental deletions instantly
- 🔒 **Safety Checks** - Prevents deletion of critical system paths
- 💾 **Deduplication** - Saves space by detecting duplicate files
- 🎨 **Beautiful Output** - Colored, formatted terminal output
- 🚀 **Fast** - SQLite-backed for quick queries
- 📦 **Zero Dependencies** - Uses only Python standard library

## 🚀 Installation

### Quick Install

```bash
# Download and install
curl -o trsh.py https://raw.githubusercontent.com/yourusername/trsh/main/trsh.py
chmod +x trsh.py
sudo mv trsh.py /usr/local/bin/trsh

# Or for user install
mkdir -p ~/.local/bin
mv trsh.py ~/.local/bin/trsh
export PATH="$HOME/.local/bin:$PATH"
```

### From Source

```bash
git clone https://github.com/yourusername/trsh
cd trsh
pip install -e .
```

### Requirements

- **Python 3.7+** (only standard library needed!)
- No external dependencies required! 🎉

## 📖 Usage

### Basic Commands

```bash
# Delete files
trsh delete file.txt
trsh delete *.log --tags temp

# Restore files
trsh restore document.pdf
trsh restore "*.txt"

# List trash
trsh list
trsh list --last 7
trsh list --verbose

# Search
trsh search "report"
trsh search "invoice" --from ~/documents --size ">1MB"

# Empty trash
trsh empty

# View statistics
trsh stats

# Undo last operation
trsh undo
```

### Advanced Usage

```bash
# Delete with metadata
trsh delete old_files/ --reason "cleanup" --tags project-x deprecated

# Restore to different location
trsh restore backup.tar.gz --output ~/Desktop/

# Search with multiple filters
trsh search "2024" --from ~/documents --size "<1GB" --last 90d --tag important

# Purge old files
trsh purge --older-than 30
trsh purge --size-quota 10  # Keep only 10GB

# Preview before executing
trsh delete *.tmp --dry-run
trsh empty --dry-run

# View operation history
trsh history
trsh history --limit 50

# Verify trash integrity
trsh verify
trsh verify --repair

# Configuration
trsh config set retention-days 30
trsh config list
```

## 🎨 Example Session

```bash
$ trsh delete ~/Downloads/*.zip --tags downloads
✓ Deleted: /home/user/Downloads/archive1.zip (45.2 MB)
✓ Deleted: /home/user/Downloads/archive2.zip (32.1 MB)

$ trsh list
2025-10-01 14:32    45.2 MB  /home/user/Downloads/archive1.zip  [downloads]
2025-10-01 14:32    32.1 MB  /home/user/Downloads/archive2.zip  [downloads]

ℹ 2 items, 77.3 MB total

$ trsh stats
📊 Trash Statistics
──────────────────────────────────────────────
Items in trash: 2
Total space used: 77.3 MB
Items restored (all time): 0
Restoration rate: 0.0%

$ trsh restore archive1.zip
✓ Restored: /home/user/Downloads/archive1.zip

$ trsh undo
✓ Undone: Restored 1 files
```

## 🏗️ Architecture

### Storage Structure

```bash
~/.trashbin/
├── files/                    # Actual trashed files
│   ├── uuid-1/
│   │   └── document.pdf
│   └── uuid-2/
│       └── image.png
└── metadata.db              # SQLite database
```

### Database Schema

- **trash_items**: File metadata, paths, hashes, tags
- **operations**: Transaction log for undo/redo
- **config**: User preferences

## 🔧 Shell Integration

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Replace rm with trsh (safely!)
alias rm='trsh delete'

# Quick access
alias trash='trsh list'
alias restore='trsh restore'
alias undelete='trsh undo'
```

Then reload:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

Now `rm` is safe:

```bash
rm file.txt      # Actually uses trsh!
trash            # See what's in trash
restore file.txt # Get it back
```

## 📊 Comparison

| Feature             | trsh   | trash-cli | gio trash  | rm   |
| ------------------- | ------ | --------- | ---------- | ---- |
| Cross-platform      | ✅     | ✅        | Linux only | ✅   |
| Database            | SQLite | Custom    | GIO        | None |
| Deduplication       | ✅     | ❌        | ❌         | ❌   |
| Advanced search     | ✅     | Basic     | Basic      | ❌   |
| Interactive restore | ✅     | ❌        | ❌         | ❌   |
| Undo                | ✅     | ❌        | ❌         | ❌   |
| Tags                | ✅     | ❌        | ❌         | ❌   |
| Analytics           | ✅     | ❌        | ❌         | ❌   |
| Dependencies        | None   | Python    | GLib       | None |

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

### Development Setup

```bash
git clone https://github.com/yourusername/trsh
cd trsh
conda create -n trsh python=3.11 -y
conda activate trsh
conda install -y pytest pytest-cov black pylint mypy
python test_trsh.py
```

### Running Tests

```bash
python test_trsh.py
pytest test_trsh.py -v
pytest --cov=trsh test_trsh.py
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

Elias W. BA

- Email: <eliaswalyba@gmail.com>
- GitHub: [@elias-ba](https://github.com/elias-ba)

## 🙏 Acknowledgments

- Inspired by trash-cli, macOS Trash, and Windows Recycle Bin
- Built with Python's excellent standard library

## ⭐ Support

If you find this tool useful:

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🤝 Contribute code

---

Made with ❤️ and Python

> "The best time to delete a file was yesterday. The second best time is now... with trsh!"
