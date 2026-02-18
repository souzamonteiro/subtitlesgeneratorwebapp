#!/usr/bin/env python3
"""
Script to rename all files in a directory by replacing spaces with underscores.

This script processes all files in a specified directory and renames them
by replacing space characters with underscore characters in their filenames.
"""

import os
import argparse
import sys
from pathlib import Path

def rename_files_with_underscores(directory, dry_run=False):
    """
    Rename all files in directory replacing spaces with underscores.
    
    Args:
        directory (str): Path to the directory containing files to rename
        dry_run (bool): If True, only show what would be renamed without actually renaming
        
    Returns:
        tuple: (count_renamed, count_errors)
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")
    
    if not directory_path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a directory")
    
    renamed_count = 0
    error_count = 0
    
    # Get all items in directory
    items = list(directory_path.iterdir())
    
    if not items:
        print("No files found in directory.")
        return 0, 0
    
    print(f"{'Preview' if dry_run else 'Renaming'} files in: {directory_path.absolute()}")
    print("-" * 50)
    
    for item in items:
        # Skip directories, only process files
        if item.is_dir():
            continue
            
        # Check if filename contains spaces
        if ' ' in item.name:
            # Create new filename with underscores
            new_name = item.name.replace(' ', '_')
            new_path = item.parent / new_name
            
            # Check if target filename already exists
            if new_path.exists():
                print(f"SKIP: {item.name} -> {new_name} (target already exists)")
                error_count += 1
                continue
            
            try:
                if dry_run:
                    print(f"DRY RUN: {item.name} -> {new_name}")
                else:
                    item.rename(new_path)
                    print(f"RENAMED: {item.name} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"ERROR: Could not rename '{item.name}': {e}")
                error_count += 1
        else:
            # No spaces in filename, skip it
            if not dry_run:
                print(f"SKIPPED: {item.name} (no spaces)")
    
    print("-" * 50)
    if dry_run:
        print(f"Dry run complete. Would rename {renamed_count} files, {error_count} errors.")
    else:
        print(f"Renaming complete. Renamed {renamed_count} files, {error_count} errors.")
    
    return renamed_count, error_count

def main():
    """Main function to parse arguments and execute renaming."""
    parser = argparse.ArgumentParser(
        description="Rename files in a directory by replacing spaces with underscores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/directory
  %(prog)s ./my_folder --dry-run
  %(prog)s -d /home/user/documents
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory containing files to rename'
    )
    
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Show what would be renamed without actually renaming files'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    try:
        renamed_count, error_count = rename_files_with_underscores(
            args.directory, 
            dry_run=args.dry_run
        )
        
        if args.verbose:
            print(f"\nSummary:")
            print(f"  Files processed: {renamed_count + error_count}")
            print(f"  Successfully renamed: {renamed_count}")
            print(f"  Errors: {error_count}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
