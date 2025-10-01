#!/usr/bin/env python3
"""
trsh - Delete with confidence, restore with ease
A world-class trash utility for the command line

Author: Elias W. BA <eliaswalyba@gmail.com>
License: MIT
Version: 1.0.0
"""

import sqlite3
import hashlib
import shutil
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import argparse


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors (for non-TTY output)"""
        Colors.RED = Colors.GREEN = Colors.YELLOW = ''
        Colors.BLUE = Colors.MAGENTA = Colors.CYAN = ''
        Colors.BOLD = Colors.DIM = Colors.RESET = ''


# Disable colors if not in a TTY
if not sys.stdout.isatty():
    Colors.disable()


class TrashItem:
    """Represents an item in the trash"""
    def __init__(self, row: sqlite3.Row):
        self.id = row['id']
        self.original_path = row['original_path']
        self.trashed_path = row['trashed_path']
        self.deletion_time = datetime.fromtimestamp(row['deletion_time'])
        self.file_size = row['file_size']
        self.file_hash = row['file_hash']
        self.mime_type = row['mime_type']
        self.deletion_reason = row['deletion_reason']
        self.tags = json.loads(row['tags']) if row['tags'] else []
        self.restored = bool(row['restored'])
        self.compressed = bool(row.get('compressed', 0))


class Trash:
    """Main trash utility class"""
    
    VERSION = "1.0.0"
    
    def __init__(self, trash_dir: Optional[Path] = None):
        self.trash_dir = trash_dir or Path.home() / '.trashbin'
        self.files_dir = self.trash_dir / 'files'
        self.db_path = self.trash_dir / 'metadata.db'
        
        # Create directories
        self.trash_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database schema"""
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS trash_items (
                id TEXT PRIMARY KEY,
                original_path TEXT NOT NULL,
                trashed_path TEXT NOT NULL,
                deletion_time INTEGER NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT,
                mime_type TEXT,
                deletion_reason TEXT,
                tags TEXT,
                restored INTEGER DEFAULT 0,
                compressed INTEGER DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_original_path 
                ON trash_items(original_path);
            CREATE INDEX IF NOT EXISTS idx_deletion_time 
                ON trash_items(deletion_time);
            CREATE INDEX IF NOT EXISTS idx_hash 
                ON trash_items(file_hash);
            CREATE INDEX IF NOT EXISTS idx_restored
                ON trash_items(restored);
            
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                details TEXT NOT NULL,
                undone INTEGER DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_timestamp
                ON operations(timestamp);
            CREATE INDEX IF NOT EXISTS idx_undone
                ON operations(undone);
            
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        ''')
        self.conn.commit()
    
    def delete(self, filepath: str, tags: List[str] = None, 
               reason: str = None, dry_run: bool = False) -> bool:
        """Delete a file to trash with metadata"""
        path = Path(filepath)
        
        # Validation
        if not path.exists():
            self._print_error(f"File not found: {filepath}")
            return False
        
        if self._is_critical_path(path):
            self._print_error(f"Refusing to delete critical path: {path}")
            return False
        
        # Get file info
        try:
            path = path.resolve()
            file_size = self._get_path_size(path)
            file_hash = self._calculate_hash(path)
        except (OSError, PermissionError) as e:
            self._print_error(f"Cannot access {path}: {e}")
            return False
        
        # Check for deduplication
        existing = self.conn.execute(
            'SELECT id FROM trash_items WHERE file_hash = ? AND restored = 0',
            (file_hash,)
        ).fetchone()
        
        if existing and file_hash.startswith('file_'):
            self._print_info(
                f"File already in trash (saved {self._format_size(file_size)})"
            )
            if not dry_run:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
            return True
        
        # Generate unique ID
        item_id = str(uuid.uuid4())
        timestamp = int(datetime.now().timestamp())
        trash_subdir = self.files_dir / item_id
        trashed_path = trash_subdir / path.name
        
        if dry_run:
            self._print_dry_run(
                f"Would delete: {path} ({self._format_size(file_size)})"
            )
            return True
        
        # Move to trash
        trash_subdir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), str(trashed_path))
        except Exception as e:
            self._print_error(f"Failed to move file: {e}")
            try:
                trash_subdir.rmdir()
            except:
                pass
            return False
        
        # Store metadata
        try:
            self.conn.execute('''
                INSERT INTO trash_items 
                (id, original_path, trashed_path, deletion_time, file_size, 
                 file_hash, deletion_reason, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, str(path), str(trashed_path), timestamp, 
                  file_size, file_hash, reason, json.dumps(tags or [])))
            self.conn.commit()
        except Exception as e:
            self._print_error(f"Failed to store metadata: {e}")
            try:
                shutil.move(str(trashed_path), str(path))
                trash_subdir.rmdir()
            except:
                pass
            return False
        
        # Log operation
        self._log_operation('delete', [item_id])
        
        self._print_success(f"Deleted: {path} ({self._format_size(file_size)})")
        return True
    
    def restore(self, pattern: str = None, output: Optional[Path] = None, 
                dry_run: bool = False, interactive: bool = False) -> int:
        """Restore files matching pattern"""
        
        if interactive:
            self._print_error("Interactive mode requires fzf (not yet implemented)")
            return 0
        
        if not pattern:
            self._print_error("No pattern specified")
            return 0
        
        items = self.conn.execute('''
            SELECT * FROM trash_items 
            WHERE original_path LIKE ? AND restored = 0
            ORDER BY deletion_time DESC
        ''', (f'%{pattern}%',)).fetchall()
        
        if not items:
            self._print_error(f"No matching files found: {pattern}")
            return 0
        
        restored_count = 0
        for row in items:
            item = TrashItem(row)
            original_path = Path(item.original_path)
            trashed_path = Path(item.trashed_path)
            
            target_path = output / original_path.name if output else original_path
            
            if dry_run:
                self._print_dry_run(f"Would restore: {original_path} -> {target_path}")
                continue
            
            if target_path.exists():
                self._print_warning(f"Target already exists: {target_path}")
                continue
            
            if not trashed_path.exists():
                self._print_warning(f"File missing in trash: {trashed_path}")
                self.conn.execute('DELETE FROM trash_items WHERE id = ?', (item.id,))
                self.conn.commit()
                continue
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(trashed_path), str(target_path))
                
                self.conn.execute(
                    'UPDATE trash_items SET restored = 1 WHERE id = ?',
                    (item.id,)
                )
                self.conn.commit()
                
                try:
                    trashed_path.parent.rmdir()
                except:
                    pass
                
                self._print_success(f"Restored: {target_path}")
                restored_count += 1
            except Exception as e:
                self._print_error(f"Failed to restore {original_path}: {e}")
        
        return restored_count
    
    def list_items(self, pattern: Optional[str] = None, 
                   from_path: Optional[str] = None,
                   last_days: Optional[int] = None,
                   verbose: bool = False):
        """List items in trash"""
        query = 'SELECT * FROM trash_items WHERE restored = 0'
        params = []
        
        if pattern:
            query += ' AND original_path LIKE ?'
            params.append(f'%{pattern}%')
        
        if from_path:
            query += ' AND original_path LIKE ?'
            params.append(f'{from_path}%')
        
        if last_days:
            cutoff = int((datetime.now() - timedelta(days=last_days)).timestamp())
            query += ' AND deletion_time > ?'
            params.append(cutoff)
        
        query += ' ORDER BY deletion_time DESC'
        
        rows = self.conn.execute(query, params).fetchall()
        
        if not rows:
            self._print_info("Trash is empty")
            return
        
        items = [TrashItem(row) for row in rows]
        total_size = sum(item.file_size for item in items)
        
        for item in items:
            if verbose:
                print('─' * 80)
                print(f"{Colors.BOLD}ID:{Colors.RESET} {item.id}")
                print(f"{Colors.BOLD}Original Path:{Colors.RESET} {item.original_path}")
                print(f"{Colors.BOLD}Size:{Colors.RESET} {self._format_size(item.file_size)}")
                print(f"{Colors.BOLD}Deleted:{Colors.RESET} {item.deletion_time.strftime('%Y-%m-%d %H:%M:%S')}")
                if item.deletion_reason:
                    print(f"{Colors.BOLD}Reason:{Colors.RESET} {item.deletion_reason}")
                if item.tags:
                    print(f"{Colors.BOLD}Tags:{Colors.RESET} {', '.join(item.tags)}")
            else:
                date_str = item.deletion_time.strftime('%Y-%m-%d %H:%M')
                size_str = self._format_size(item.file_size)
                tag_str = f"{Colors.YELLOW}[{', '.join(item.tags)}]{Colors.RESET}" if item.tags else ""
                
                print(f"{Colors.DIM}{date_str}{Colors.RESET}  "
                      f"{Colors.BLUE}{size_str:>10}{Colors.RESET}  "
                      f"{Colors.GREEN}{item.original_path}{Colors.RESET}  "
                      f"{tag_str}")
        
        print(f"\n{Colors.BLUE}ℹ{Colors.RESET} {len(items)} items, "
              f"{self._format_size(total_size)} total")
    
    def search(self, query: str, from_path: Optional[str] = None,
               last_days: Optional[str] = None, size_filter: Optional[str] = None,
               tags: List[str] = None):
        """Advanced search with filters"""
        sql = 'SELECT * FROM trash_items WHERE restored = 0'
        params = []
        
        if query:
            sql += ' AND original_path LIKE ?'
            params.append(f'%{query}%')
        
        if from_path:
            sql += ' AND original_path LIKE ?'
            params.append(f'{from_path}%')
        
        if last_days:
            days = self._parse_time_expression(last_days)
            if days:
                cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
                sql += ' AND deletion_time > ?'
                params.append(cutoff)
        
        if size_filter:
            operator, size_bytes = self._parse_size_filter(size_filter)
            if operator and size_bytes:
                sql += f' AND file_size {operator} ?'
                params.append(size_bytes)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%"{tag}"%')
        
        sql += ' ORDER BY deletion_time DESC'
        
        rows = self.conn.execute(sql, params).fetchall()
        items = [TrashItem(row) for row in rows]
        
        if not items:
            self._print_info(f"No items found matching: {query}")
            return
        
        print(f"{Colors.BOLD}Found {len(items)} matching items:{Colors.RESET}\n")
        
        for item in items:
            date_str = item.deletion_time.strftime('%Y-%m-%d')
            size_str = self._format_size(item.file_size)
            tag_str = f"[{', '.join(item.tags)}]" if item.tags else ""
            
            print(f"{Colors.DIM}{date_str}{Colors.RESET}  "
                  f"{Colors.BLUE}{size_str:>10}{Colors.RESET}  "
                  f"{Colors.GREEN}{item.original_path}{Colors.RESET}  "
                  f"{Colors.YELLOW}{tag_str}{Colors.RESET}")
    
    def empty(self, force: bool = False, dry_run: bool = False):
        """Empty entire trash"""
        count = self.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        total_size = self.conn.execute(
            'SELECT COALESCE(SUM(file_size), 0) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        if count == 0:
            self._print_info("Trash is already empty")
            return
        
        if dry_run:
            self._print_dry_run(
                f"Would permanently delete {count} items "
                f"({self._format_size(total_size)})"
            )
            return
        
        if not force:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} This will permanently delete "
                  f"{count} items ({self._format_size(total_size)})")
            response = input("Type 'yes' to confirm: ").strip().lower()
            if response != 'yes':
                self._print_info("Cancelled")
                return
        
        try:
            shutil.rmtree(self.files_dir)
            self.files_dir.mkdir()
        except Exception as e:
            self._print_error(f"Failed to delete files: {e}")
            return
        
        self.conn.execute('DELETE FROM trash_items WHERE restored = 0')
        self.conn.commit()
        
        self._print_success(
            f"Trash emptied: {count} items deleted ({self._format_size(total_size)})"
        )
    
    def purge(self, older_than: Optional[int] = None, 
              size_quota: Optional[float] = None,
              dry_run: bool = False):
        """Purge old files based on retention policy"""
        
        items_to_purge = []
        
        if older_than:
            cutoff = int((datetime.now() - timedelta(days=older_than)).timestamp())
            rows = self.conn.execute('''
                SELECT * FROM trash_items 
                WHERE deletion_time < ? AND restored = 0
                ORDER BY deletion_time ASC
            ''', (cutoff,)).fetchall()
            items_to_purge.extend([TrashItem(row) for row in rows])
        
        elif size_quota:
            total_size = self.conn.execute(
                'SELECT COALESCE(SUM(file_size), 0) FROM trash_items WHERE restored = 0'
            ).fetchone()[0]
            
            quota_bytes = int(size_quota * 1024 * 1024 * 1024)
            
            if total_size <= quota_bytes:
                self._print_info(f"Trash size ({self._format_size(total_size)}) "
                               f"is within quota ({size_quota} GB)")
                return
            
            rows = self.conn.execute('''
                SELECT * FROM trash_items WHERE restored = 0
                ORDER BY deletion_time ASC
            ''').fetchall()
            
            current_size = total_size
            for row in rows:
                if current_size <= quota_bytes:
                    break
                item = TrashItem(row)
                items_to_purge.append(item)
                current_size -= item.file_size
        
        else:
            self._print_error("Specify --older-than or --size-quota")
            return
        
        if not items_to_purge:
            self._print_info("No files to purge")
            return
        
        total_size = sum(item.file_size for item in items_to_purge)
        
        if dry_run:
            self._print_dry_run(
                f"Would purge {len(items_to_purge)} items "
                f"({self._format_size(total_size)})"
            )
            for item in items_to_purge[:5]:
                print(f"  - {item.original_path}")
            if len(items_to_purge) > 5:
                print(f"  ... and {len(items_to_purge) - 5} more")
            return
        
        purged_count = 0
        for item in items_to_purge:
            try:
                trashed_path = Path(item.trashed_path)
                if trashed_path.exists():
                    if trashed_path.is_file():
                        trashed_path.unlink()
                    else:
                        shutil.rmtree(trashed_path)
                    
                    try:
                        trashed_path.parent.rmdir()
                    except:
                        pass
                
                self.conn.execute('DELETE FROM trash_items WHERE id = ?', (item.id,))
                purged_count += 1
                
            except Exception as e:
                self._print_warning(f"Failed to purge {item.original_path}: {e}")
        
        self.conn.commit()
        
        self._print_success(
            f"Purged {purged_count} items ({self._format_size(total_size)})"
        )
    
    def stats(self):
        """Show trash statistics"""
        count = self.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        total_size = self.conn.execute(
            'SELECT COALESCE(SUM(file_size), 0) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        restored_count = self.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 1'
        ).fetchone()[0]
        
        print(f"\n{Colors.BOLD}📊 Trash Statistics{Colors.RESET}")
        print("─" * 50)
        print(f"{Colors.BOLD}Items in trash:{Colors.RESET} {count}")
        print(f"{Colors.BOLD}Total space used:{Colors.RESET} {self._format_size(total_size)}")
        print(f"{Colors.BOLD}Items restored (all time):{Colors.RESET} {restored_count}")
        
        if count + restored_count > 0:
            rate = (restored_count / (count + restored_count)) * 100
            print(f"{Colors.BOLD}Restoration rate:{Colors.RESET} {rate:.1f}%")
        
        rows = self.conn.execute('''
            SELECT original_path, file_size FROM trash_items WHERE restored = 0
        ''').fetchall()
        
        if rows:
            extensions = {}
            for row in rows:
                path = Path(row[0])
                ext = path.suffix.lower() or '(no extension)'
                if ext not in extensions:
                    extensions[ext] = {'count': 0, 'size': 0}
                extensions[ext]['count'] += 1
                extensions[ext]['size'] += row[1]
            
            sorted_exts = sorted(extensions.items(), 
                               key=lambda x: x[1]['count'], 
                               reverse=True)[:5]
            
            if sorted_exts:
                print(f"\n{Colors.BOLD}Top file types:{Colors.RESET}")
                for ext, data in sorted_exts:
                    percentage = (data['count'] / count) * 100
                    print(f"  {ext:15} {data['count']:4} files ({percentage:5.1f}%)  "
                          f"{self._format_size(data['size'])}")
        
        print()
    
    def undo(self, count: int = 1):
        """Undo last N operations"""
        operations = self.conn.execute('''
            SELECT * FROM operations 
            WHERE undone = 0 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (count,)).fetchall()
        
        if not operations:
            self._print_info("No operations to undo")
            return
        
        for op in operations:
            op_type = op['operation_type']
            details = json.loads(op['details'])
            
            if op_type == 'delete':
                restored = 0
                for item_id in details:
                    row = self.conn.execute(
                        'SELECT * FROM trash_items WHERE id = ?',
                        (item_id,)
                    ).fetchone()
                    
                    if row:
                        item = TrashItem(row)
                        try:
                            original_path = Path(item.original_path)
                            original_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(item.trashed_path), str(original_path))
                            
                            self.conn.execute(
                                'UPDATE trash_items SET restored = 1 WHERE id = ?',
                                (item_id,)
                            )
                            restored += 1
                        except Exception as e:
                            self._print_warning(f"Failed to restore {item.original_path}: {e}")
                
                self._print_success(f"Undone: Restored {restored} files")
            
            elif op_type in ['purge', 'empty']:
                self._print_warning(f"Cannot undo {op_type} operation (files permanently deleted)")
            
            self.conn.execute(
                'UPDATE operations SET undone = 1 WHERE id = ?',
                (op['id'],)
            )
        
        self.conn.commit()
    
    def history(self, limit: int = 20):
        """Show operation history"""
        operations = self.conn.execute('''
            SELECT * FROM operations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
        
        if not operations:
            self._print_info("No operations in history")
            return
        
        print(f"\n{Colors.BOLD}📜 Operation History{Colors.RESET}")
        print("─" * 80)
        
        for op in operations:
            timestamp = datetime.fromtimestamp(op['timestamp'])
            op_type = op['operation_type']
            undone = " (undone)" if op['undone'] else ""
            
            date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{Colors.DIM}{date_str}{Colors.RESET}  "
                  f"{Colors.CYAN}{op_type}{Colors.RESET}{undone}")
        
        print()
    
    def verify(self, repair: bool = False):
        """Verify trash integrity"""
        print(f"\n{Colors.BOLD}🔍 Verifying trash integrity...{Colors.RESET}\n")
        
        issues = []
        
        print("Checking for orphaned files...")
        db_ids = {row['id'] for row in self.conn.execute(
            'SELECT id FROM trash_items WHERE restored = 0'
        ).fetchall()}
        
        if self.files_dir.exists():
            disk_ids = {d.name for d in self.files_dir.iterdir() if d.is_dir()}
            orphaned = disk_ids - db_ids
            
            for orphan_id in orphaned:
                issues.append(('orphaned', orphan_id))
                print(f"{Colors.YELLOW}⚠{Colors.RESET} Orphaned: {orphan_id}")
                if repair:
                    try:
                        shutil.rmtree(self.files_dir / orphan_id)
                        print(f"  {Colors.GREEN}✓{Colors.RESET} Removed")
                    except Exception as e:
                        print(f"  {Colors.RED}✗{Colors.RESET} Failed: {e}")
        
        print("\nChecking for missing files...")
        for row in self.conn.execute('SELECT * FROM trash_items WHERE restored = 0').fetchall():
            item = TrashItem(row)
            if not Path(item.trashed_path).exists():
                issues.append(('missing', item.id))
                print(f"{Colors.YELLOW}⚠{Colors.RESET} Missing: {item.original_path}")
                if repair:
                    self.conn.execute('DELETE FROM trash_items WHERE id = ?', (item.id,))
                    print(f"  {Colors.GREEN}✓{Colors.RESET} Removed from database")
        
        if repair:
            self.conn.commit()
        
        print()
        if not issues:
            print(f"{Colors.GREEN}✅ No issues found!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ Found {len(issues)} issues{Colors.RESET}")
            if not repair:
                print(f"\nRun with --repair to fix these issues")
        print()
    
    def config_set(self, key: str, value: str):
        """Set configuration value"""
        self.conn.execute(
            'INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)',
            (key, value)
        )
        self.conn.commit()
        self._print_success(f"Configuration updated: {key} = {value}")
    
    def config_get(self, key: str):
        """Get configuration value"""
        row = self.conn.execute(
            'SELECT value FROM config WHERE key = ?',
            (key,)
        ).fetchone()
        
        if row:
            print(row[0])
        else:
            self._print_error(f"Key not found: {key}")
    
    def config_list(self):
        """List all configuration"""
        rows = self.conn.execute('SELECT key, value FROM config').fetchall()
        
        if not rows:
            self._print_info("No configuration set")
            return
        
        print(f"\n{Colors.BOLD}⚙️  Configuration{Colors.RESET}")
        print("─" * 50)
        for row in rows:
            print(f"{Colors.BOLD}{row[0]}:{Colors.RESET} {row[1]}")
        print()
    
    # Helper methods
    
    def _is_critical_path(self, path: Path) -> bool:
        """Check if path is critical system path"""
        critical = ['/', '/bin', '/sbin', '/usr', '/etc', '/var', '/boot', 
                   '/sys', '/proc', '/dev']
        path_str = str(path.resolve())
        return any(path_str == p or path_str.startswith(f"{p}/") for p in critical)
    
    def _get_path_size(self, path: Path) -> int:
        """Get total size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except (OSError, PermissionError):
                    pass
        return total
    
    def _calculate_hash(self, path: Path) -> str:
        """Calculate SHA256 hash of file"""
        if path.is_file():
            hasher = hashlib.sha256()
            try:
                with open(path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        hasher.update(chunk)
                return f"file_{hasher.hexdigest()}"
            except (OSError, PermissionError):
                return f"file_{uuid.uuid4()}"
        return f"dir_{uuid.uuid4()}"
    
    def _format_size(self, size: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{size} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _parse_time_expression(self, expr: str) -> Optional[int]:
        """Parse time expressions like 7d, 2w, 1m to days"""
        try:
            if expr.endswith('d'):
                return int(expr[:-1])
            elif expr.endswith('w'):
                return int(expr[:-1]) * 7
            elif expr.endswith('m'):
                return int(expr[:-1]) * 30
            elif expr.endswith('y'):
                return int(expr[:-1]) * 365
            else:
                return int(expr)
        except ValueError:
            return None
    
    def _parse_size_filter(self, expr: str) -> tuple:
        """Parse size expressions like >10MB, <1GB"""
        import re
        match = re.match(r'([<>]=?)(\d+(?:\.\d+)?)(B|KB|MB|GB|TB)', expr.upper())
        if not match:
            return None, None
        
        operator, value, unit = match.groups()
        value = float(value)
        
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        size_bytes = int(value * units[unit])
        
        return operator, size_bytes
    
    def _log_operation(self, op_type: str, details: List[str]):
        """Log operation for undo functionality"""
        self.conn.execute('''
            INSERT INTO operations (operation_type, timestamp, details)
            VALUES (?, ?, ?)
        ''', (op_type, int(datetime.now().timestamp()), json.dumps(details)))
        self.conn.commit()
    
    def _print_success(self, message: str):
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    
    def _print_error(self, message: str):
        print(f"{Colors.RED}✗{Colors.RESET} {message}", file=sys.stderr)
    
    def _print_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    
    def _print_info(self, message: str):
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
    
    def _print_dry_run(self, message: str):
        print(f"{Colors.YELLOW}→{Colors.RESET} {message}")
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='🗑️  trsh - Delete with confidence, restore with ease',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  trsh delete file.txt                    # Delete a file
  trsh delete *.log --tags temp           # Delete with tags
  trsh restore document.pdf               # Restore a file
  trsh list --last 7                      # List files from last 7 days
  trsh search "report" --from ~/work      # Search with filters
  trsh purge --older-than 30              # Purge files older than 30 days
  trsh stats                              # Show statistics
  trsh undo                               # Undo last operation
'''
    )
    
    parser.add_argument('--version', action='version', 
                       version=f'trsh {Trash.VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete files to trash')
    delete_parser.add_argument('files', nargs='+', help='Files to delete')
    delete_parser.add_argument('-n', '--dry-run', action='store_true',
                              help='Show what would be deleted without doing it')
    delete_parser.add_argument('-r', '--reason', help='Reason for deletion')
    delete_parser.add_argument('-t', '--tags', nargs='*', default=[],
                              help='Tags for organization')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore files from trash')
    restore_parser.add_argument('pattern', nargs='?', help='Pattern to match files')
    restore_parser.add_argument('-i', '--interactive', action='store_true',
                               help='Interactive mode with fuzzy search')
    restore_parser.add_argument('-o', '--output', type=Path,
                               help='Restore to different location')
    restore_parser.add_argument('-n', '--dry-run', action='store_true',
                               help='Show what would be restored')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List items in trash')
    list_parser.add_argument('pattern', nargs='?', help='Filter by pattern')
    list_parser.add_argument('--from', dest='from_path', help='Filter by path')
    list_parser.add_argument('--last', type=int, help='Show items from last N days')
    list_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show detailed information')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search trash with filters')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--from', dest='from_path', help='Filter by path')
    search_parser.add_argument('--last', help='Filter by time (e.g., 7d, 2w, 1m)')
    search_parser.add_argument('--size', help='Filter by size (e.g., >10MB, <1GB)')
    search_parser.add_argument('--tag', action='append', dest='tags',
                              help='Filter by tag (can be used multiple times)')
    
    # Empty command
    empty_parser = subparsers.add_parser('empty', help='Empty entire trash')
    empty_parser.add_argument('-f', '--force', action='store_true',
                             help='Skip confirmation')
    empty_parser.add_argument('-n', '--dry-run', action='store_true',
                             help='Show what would be deleted')
    
    # Purge command
    purge_parser = subparsers.add_parser('purge', help='Purge old files')
    purge_parser.add_argument('--older-than', type=int,
                             help='Delete files older than N days')
    purge_parser.add_argument('--size-quota', type=float,
                             help='Keep only N GB of trash')
    purge_parser.add_argument('-n', '--dry-run', action='store_true',
                             help='Show what would be purged')
    
    # Stats command
    subparsers.add_parser('stats', help='Show trash statistics')
    
    # Undo command
    undo_parser = subparsers.add_parser('undo', help='Undo last operation')
    undo_parser.add_argument('count', nargs='?', type=int, default=1,
                            help='Number of operations to undo')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show operation history')
    history_parser.add_argument('-l', '--limit', type=int, default=20,
                               help='Number of operations to show')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify trash integrity')
    verify_parser.add_argument('-r', '--repair', action='store_true',
                              help='Attempt to repair issues')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_set = config_subparsers.add_parser('set', help='Set configuration value')
    config_set.add_argument('key', help='Configuration key')
    config_set.add_argument('value', help='Configuration value')
    
    config_get = config_subparsers.add_parser('get', help='Get configuration value')
    config_get.add_argument('key', help='Configuration key')
    
    config_subparsers.add_parser('list', help='List all configuration')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create Trash instance
    try:
        trash = Trash()
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.RESET} Failed to initialize trash: {e}", 
              file=sys.stderr)
        return 1
    
    # Execute command
    try:
        if args.command == 'delete':
            success_count = 0
            for file in args.files:
                if trash.delete(file, tags=args.tags, reason=args.reason, 
                              dry_run=args.dry_run):
                    success_count += 1
            return 0 if success_count > 0 else 1
        
        elif args.command == 'restore':
            count = trash.restore(pattern=args.pattern, output=args.output, 
                                dry_run=args.dry_run, interactive=args.interactive)
            return 0 if count > 0 or args.dry_run else 1
        
        elif args.command == 'list':
            trash.list_items(pattern=args.pattern, from_path=args.from_path,
                           last_days=args.last, verbose=args.verbose)
            return 0
        
        elif args.command == 'search':
            trash.search(args.query, from_path=args.from_path, last_days=args.last,
                        size_filter=args.size, tags=args.tags)
            return 0
        
        elif args.command == 'empty':
            trash.empty(force=args.force, dry_run=args.dry_run)
            return 0
        
        elif args.command == 'purge':
            trash.purge(older_than=args.older_than, size_quota=args.size_quota,
                       dry_run=args.dry_run)
            return 0
        
        elif args.command == 'stats':
            trash.stats()
            return 0
        
        elif args.command == 'undo':
            trash.undo(count=args.count)
            return 0
        
        elif args.command == 'history':
            trash.history(limit=args.limit)
            return 0
        
        elif args.command == 'verify':
            trash.verify(repair=args.repair)
            return 0
        
        elif args.command == 'config':
            if args.config_action == 'set':
                trash.config_set(args.key, args.value)
            elif args.config_action == 'get':
                trash.config_get(args.key)
            elif args.config_action == 'list':
                trash.config_list()
            else:
                config_parser.print_help()
            return 0
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}ℹ{Colors.RESET} Cancelled by user")
        return 130
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.RESET} Error: {e}", file=sys.stderr)
        if os.getenv('DEBUG'):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())