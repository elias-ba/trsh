#!/usr/bin/env python3
"""
Comprehensive test suite for trsh
"""

import unittest
import tempfile
import shutil
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from trsh import Trash, Colors

# Disable colors for testing
Colors.disable()


class TestTrash(unittest.TestCase):
    """Test cases for Trash class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.trash_dir = self.test_dir / '.trashbin'
        self.trash = Trash(trash_dir=self.trash_dir)
        
        # Create test files
        self.test_files_dir = self.test_dir / 'test_files'
        self.test_files_dir.mkdir()
        
        self.test_file1 = self.test_files_dir / 'file1.txt'
        self.test_file1.write_text('test content 1')
        
        self.test_file2 = self.test_files_dir / 'file2.txt'
        self.test_file2.write_text('test content 2')
        
        self.test_dir_with_files = self.test_files_dir / 'subdir'
        self.test_dir_with_files.mkdir()
        (self.test_dir_with_files / 'nested.txt').write_text('nested content')
    
    def tearDown(self):
        """Clean up after each test"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    # Basic Operations Tests
    
    def test_delete_file(self):
        """Test deleting a single file"""
        result = self.trash.delete(str(self.test_file1))
        
        self.assertTrue(result)
        self.assertFalse(self.test_file1.exists())
        
        rows = self.trash.conn.execute(
            'SELECT * FROM trash_items WHERE restored = 0'
        ).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertIn('file1.txt', rows[0]['original_path'])
    
    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist"""
        result = self.trash.delete('/nonexistent/file.txt')
        self.assertFalse(result)
    
    def test_delete_multiple_files(self):
        """Test deleting multiple files"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        self.assertEqual(count, 2)
    
    def test_delete_with_tags(self):
        """Test deleting with tags"""
        result = self.trash.delete(
            str(self.test_file1),
            tags=['test', 'important']
        )
        
        self.assertTrue(result)
        
        row = self.trash.conn.execute(
            'SELECT tags FROM trash_items WHERE restored = 0'
        ).fetchone()
        
        import json
        tags = json.loads(row['tags'])
        self.assertIn('test', tags)
        self.assertIn('important', tags)
    
    def test_delete_with_reason(self):
        """Test deleting with a reason"""
        result = self.trash.delete(
            str(self.test_file1),
            reason='cleanup test'
        )
        
        self.assertTrue(result)
        
        row = self.trash.conn.execute(
            'SELECT deletion_reason FROM trash_items WHERE restored = 0'
        ).fetchone()
        
        self.assertEqual(row['deletion_reason'], 'cleanup test')
    
    def test_delete_dry_run(self):
        """Test dry-run mode for delete"""
        result = self.trash.delete(str(self.test_file1), dry_run=True)
        
        self.assertTrue(result)
        self.assertTrue(self.test_file1.exists())
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items'
        ).fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_delete_directory(self):
        """Test deleting a directory"""
        result = self.trash.delete(str(self.test_dir_with_files))
        
        self.assertTrue(result)
        self.assertFalse(self.test_dir_with_files.exists())
        
        rows = self.trash.conn.execute(
            'SELECT * FROM trash_items WHERE restored = 0'
        ).fetchall()
        self.assertEqual(len(rows), 1)
    
    # Restore Tests
    
    def test_restore_file(self):
        """Test restoring a file"""
        self.trash.delete(str(self.test_file1))
        self.assertFalse(self.test_file1.exists())
        
        count = self.trash.restore('file1.txt')
        
        self.assertEqual(count, 1)
        self.assertTrue(self.test_file1.exists())
        self.assertEqual(self.test_file1.read_text(), 'test content 1')
    
    def test_restore_nonexistent(self):
        """Test restoring a file that's not in trash"""
        count = self.trash.restore('nonexistent.txt')
        self.assertEqual(count, 0)
    
    def test_restore_to_different_location(self):
        """Test restoring to a different output directory"""
        self.trash.delete(str(self.test_file1))
        
        output_dir = self.test_dir / 'restored'
        output_dir.mkdir()
        
        count = self.trash.restore('file1.txt', output=output_dir)
        
        self.assertEqual(count, 1)
        restored_file = output_dir / 'file1.txt'
        self.assertTrue(restored_file.exists())
        self.assertEqual(restored_file.read_text(), 'test content 1')
    
    def test_restore_dry_run(self):
        """Test dry-run mode for restore"""
        self.trash.delete(str(self.test_file1))
        
        count = self.trash.restore('file1.txt', dry_run=True)
        
        self.assertEqual(count, 0)
        self.assertFalse(self.test_file1.exists())
    
    def test_restore_directory(self):
        """Test restoring a directory"""
        self.trash.delete(str(self.test_dir_with_files))
        
        count = self.trash.restore('subdir')
        
        self.assertEqual(count, 1)
        self.assertTrue(self.test_dir_with_files.exists())
        self.assertTrue((self.test_dir_with_files / 'nested.txt').exists())
    
    # List Tests
    
    def test_list_empty_trash(self):
        """Test listing empty trash"""
        # Should not raise any errors
        self.trash.list_items()
    
    def test_list_items(self):
        """Test listing trash items"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        rows = self.trash.conn.execute(
            'SELECT * FROM trash_items WHERE restored = 0'
        ).fetchall()
        
        self.assertEqual(len(rows), 2)
    
    def test_list_with_pattern(self):
        """Test listing with pattern filter"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        rows = self.trash.conn.execute(
            "SELECT * FROM trash_items WHERE original_path LIKE ? AND restored = 0",
            ('%file1%',)
        ).fetchall()
        
        self.assertEqual(len(rows), 1)
    
    # Search Tests
    
    def test_search(self):
        """Test search functionality"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        # Just verify it doesn't crash
        self.trash.search('file')
    
    # Empty Tests
    
    def test_empty_trash(self):
        """Test emptying trash"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        self.trash.empty(force=True)
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        self.assertEqual(count, 0)
        self.assertFalse(any(self.trash.files_dir.iterdir()))
    
    def test_empty_trash_dry_run(self):
        """Test dry-run mode for empty"""
        self.trash.delete(str(self.test_file1))
        
        self.trash.empty(dry_run=True)
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        self.assertEqual(count, 1)
    
    # Purge Tests
    
    def test_purge_old_files(self):
        """Test purging files older than N days"""
        self.trash.delete(str(self.test_file1))
        
        # Purge files older than 999 days (nothing should be purged)
        self.trash.purge(older_than=999)
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        self.assertEqual(count, 1)
        
        # Purge files older than 0 days (should purge everything)
        self.trash.purge(older_than=0)
        
        count = self.trash.conn.execute(
            'SELECT COUNT(*) FROM trash_items WHERE restored = 0'
        ).fetchone()[0]
        
        self.assertEqual(count, 0)
    
    # Undo Tests
    
    def test_undo_delete(self):
        """Test undoing a delete operation"""
        self.trash.delete(str(self.test_file1))
        self.assertFalse(self.test_file1.exists())
        
        self.trash.undo()
        
        self.assertTrue(self.test_file1.exists())
        self.assertEqual(self.test_file1.read_text(), 'test content 1')
    
    # Stats Tests
    
    def test_stats(self):
        """Test statistics display"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        # Should not crash
        self.trash.stats()
    
    # Verify Tests
    
    def test_verify_integrity(self):
        """Test trash integrity verification"""
        self.trash.delete(str(self.test_file1))
        
        # Should not find any issues
        self.trash.verify()
    
    # Config Tests
    
    def test_config_set_get(self):
        """Test configuration management"""
        self.trash.config_set('test_key', 'test_value')
        
        row = self.trash.conn.execute(
            'SELECT value FROM config WHERE key = ?',
            ('test_key',)
        ).fetchone()
        
        self.assertEqual(row[0], 'test_value')
    
    # Helper Method Tests
    
    def test_critical_path_protection(self):
        """Test that critical paths are protected"""
        self.assertTrue(self.trash._is_critical_path(Path('/')))
        self.assertTrue(self.trash._is_critical_path(Path('/bin')))
        self.assertFalse(self.trash._is_critical_path(Path('/home/user')))
    
    def test_format_size(self):
        """Test human-readable size formatting"""
        self.assertEqual(self.trash._format_size(100), '100 B')
        self.assertEqual(self.trash._format_size(1024), '1.00 KB')
        self.assertEqual(self.trash._format_size(1024 * 1024), '1.00 MB')
        self.assertEqual(self.trash._format_size(1024 * 1024 * 1024), '1.00 GB')
    
    def test_parse_time_expression(self):
        """Test parsing time expressions"""
        self.assertEqual(self.trash._parse_time_expression('7d'), 7)
        self.assertEqual(self.trash._parse_time_expression('2w'), 14)
        self.assertEqual(self.trash._parse_time_expression('1m'), 30)
        self.assertEqual(self.trash._parse_time_expression('1y'), 365)
    
    def test_parse_size_filter(self):
        """Test parsing size filter expressions"""
        op, size = self.trash._parse_size_filter('>10MB')
        self.assertEqual(op, '>')
        self.assertEqual(size, 10 * 1024 * 1024)
        
        op, size = self.trash._parse_size_filter('<1GB')
        self.assertEqual(op, '<')
        self.assertEqual(size, 1024 * 1024 * 1024)
    
    # Deduplication Tests
    
    def test_deduplication(self):
        """Test file deduplication"""
        # Create two files with same content
        duplicate = self.test_files_dir / 'duplicate.txt'
        duplicate.write_text('test content 1')
        
        # Delete both
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(duplicate))
        
        # Should have 2 metadata entries
        rows = self.trash.conn.execute(
            'SELECT file_hash FROM trash_items WHERE restored = 0'
        ).fetchall()
        
        self.assertEqual(len(rows), 2)
        # Both should have the same hash (starting with 'file_')
        if rows[0]['file_hash'].startswith('file_'):
            self.assertEqual(rows[0]['file_hash'], rows[1]['file_hash'])
    
    # Edge Cases
    
    def test_delete_multiple_files_same_name(self):
        """Test deleting multiple files with same name from different paths"""
        dir1 = self.test_files_dir / 'dir1'
        dir2 = self.test_files_dir / 'dir2'
        dir1.mkdir()
        dir2.mkdir()
        
        file1 = dir1 / 'same_name.txt'
        file2 = dir2 / 'same_name.txt'
        file1.write_text('content 1')
        file2.write_text('content 2')
        
        self.trash.delete(str(file1))
        self.trash.delete(str(file2))
        
        rows = self.trash.conn.execute(
            'SELECT * FROM trash_items WHERE restored = 0'
        ).fetchall()
        self.assertEqual(len(rows), 2)
    
    def test_history(self):
        """Test operation history"""
        self.trash.delete(str(self.test_file1))
        self.trash.delete(str(self.test_file2))
        
        # Should not crash
        self.trash.history()


class TestCLI(unittest.TestCase):
    """Test command-line interface"""
    
    def test_import(self):
        """Test that trsh module can be imported"""
        import trsh
        self.assertIsNotNone(trsh)
        self.assertIsNotNone(trsh.Trash)
        self.assertIsNotNone(trsh.main)


def run_tests():
    """Run all tests"""
    # Disable colors
    Colors.disable()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTrash))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
    