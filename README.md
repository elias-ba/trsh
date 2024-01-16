# trsh 🗑️

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

**trsh** is a lightweight and powerful command-line utility designed to simplify file management on Linux systems. It allows you to confidently delete files, restore them effortlessly, and keep your trash bin clutter-free with automatic purging.

## Features

- **Delete Files:** Securely move files to the trash bin.
- **Restore Files:** Effortlessly restore files to their original locations.
- **List Items:** View the contents of the trash bin.
- **Empty Trash:** Permanently delete all items in the trash bin.
- **Automatic Purging:** Schedule automatic purging of old files beyond a specified grace period.

## Installation

### Debian-based Distributions (e.g., Ubuntu)

```bash
sudo dpkg -i trsh.deb
```

### RPM-based Distributions (e.g., Fedora)

```bash
sudo rpm -i trsh.rpm
```

### Arch Linux

```bash
makepkg -si
```

### macOS (Homebrew)

```bash
brew install ./trsh.rb
```

## Usage

### Delete Files

```bash
trsh delete file1 file2
```

### Restore Files

```bash
trsh restore file1
```

### List Items in Trash

```bash
trsh list
```

### Empty Trash

```bash
trsh empty
```

### Set Retention Period

```bash
trsh config --retention-period 7
```

***This will add a cron job or systemd timer for daily purging.***

## Contributing

If you'd like to contribute to this project, please check out our Contribution Guidelines.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Made with ❤️ by Elias W. BA <eliaswalyba@gmail.com>

If you like this tool please add star on this project, it will help a lot for my motivation to keep maintaining it.

> Delete with Confidence, Restore with Ease! Explore the power of "trsh" for seamless file management on your Linux system.
