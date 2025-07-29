#!/usr/bin/env python3
"""
analyze_repo.py: Clone a GitHub repository and report line change statistics per commit.
Includes statistical analysis and potential AI contribution detection.

Usage:
    python analyze_repo.py <repo_url>
"""
import argparse
import subprocess
import sys
import os
import numpy as np
from tempfile import TemporaryDirectory
from tabulate import tabulate
from datetime import datetime
from statistics import mean, median, stdev


def run_git(cmd, cwd=None):
    return subprocess.check_output(['git'] + cmd, cwd=cwd)


def parse_numstat(output):
    added = 0
    deleted = 0
    for line in output.splitlines():
        parts = line.decode('utf-8', errors='ignore').split('\t')
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            deleted += int(parts[1])
    return added, deleted


def detect_ai_contribution(changes, total_lines, stats):
    """
    Detect if a commit might be AI-generated based on statistical distribution:
    Uses Interquartile Range (IQR) method to detect outliers in the percentage changes.
    - Beyond 3*IQR from Q3: Likely AI
    - Beyond 1.5*IQR from Q3: Possible AI
    - Within normal distribution: Likely Human
    """
    if not stats['pct_changes']:  # Skip for first commit
        return "N/A"
    
    pct_change = (changes / total_lines * 100) if total_lines > 0 else 0
    
    # Use IQR method for outlier detection
    q3 = stats['pct_q3']
    iqr = stats['pct_iqr']
    
    if iqr > 0:
        # Calculate how many IQRs above Q3
        iqrs_above_q3 = (pct_change - q3) / iqr
        
        if iqrs_above_q3 > 3:  # Strong outlier
            return "Likely AI"
        elif iqrs_above_q3 > 1.5:  # Mild outlier
            return "Possible AI"
    
    return "Likely Human"


def calculate_statistics(data):
    """Calculate statistics for the commit data"""
    if not data:
        return {}
    
    changes = [d['changes'] for d in data]
    pct_changes = [d['pct'] for d in data if d['pct'] is not None]
    
    # Calculate quartiles for percentage changes
    pct_array = np.array(pct_changes)
    q1 = np.percentile(pct_array, 25) if len(pct_changes) > 0 else 0
    q3 = np.percentile(pct_array, 75) if len(pct_changes) > 0 else 0
    iqr = q3 - q1
    
    stats = {
        'changes_mean': mean(changes) if changes else 0,
        'changes_median': median(changes) if changes else 0,
        'changes_std': stdev(changes) if len(changes) > 1 else 0,
        'pct_mean': mean(pct_changes) if pct_changes else 0,
        'pct_std': stdev(pct_changes) if len(pct_changes) > 1 else 0,
        'pct_changes': pct_changes,
        'pct_q1': q1,
        'pct_q3': q3,
        'pct_iqr': iqr
    }
    return stats


def print_statistics(stats):
    """Print statistical summary"""
    print("\nRepository Statistics:")
    print("-" * 50)
    stats_table = [
        ["Changes per commit (mean)", f"{stats['changes_mean']:.2f}"],
        ["Changes per commit (median)", f"{stats['changes_median']:.2f}"],
        ["Changes standard deviation", f"{stats['changes_std']:.2f}"],
        ["Percentage change (mean)", f"{stats['pct_mean']:.2f}%"],
        ["Percentage change (std)", f"{stats['pct_std']:.2f}%"],
        ["Percentage Q1 (25th percentile)", f"{stats['pct_q1']:.2f}%"],
        ["Percentage Q3 (75th percentile)", f"{stats['pct_q3']:.2f}%"],
        ["Percentage IQR", f"{stats['pct_iqr']:.2f}%"],
    ]
    print(tabulate(stats_table, tablefmt='simple'))


def analyze(repo_url):
    with TemporaryDirectory() as tmpdir:
        print(f'Cloning {repo_url} into temporary directory...')
        run_git(['clone', '--quiet', repo_url, tmpdir])
        # get all commits in chronological order
        commits = run_git(['rev-list', '--reverse', 'HEAD'], cwd=tmpdir).splitlines()
        prev_total = None
        prev_commit = None
        print(f"Found {len(commits)} commits.\n")
        
        # prepare table data
        headers = ['Commit', 'Date', 'Lines Changed', '% Change', 'Total Lines', 'Contribution Type']
        table_data = []
        commit_data = []
        
        for c in commits:
            commit = c.decode('utf-8')
            # get commit date
            date = run_git(['show', '-s', '--format=%ci', commit], cwd=tmpdir).decode().strip()
            if prev_commit is None:
                # initial commit: show numstat for the commit
                out = run_git(['show', '--numstat', commit], cwd=tmpdir)
                added, deleted = parse_numstat(out)
                total = added
                pct = None
                changed = added + deleted
            else:
                out = run_git(['diff', '--numstat', prev_commit, commit], cwd=tmpdir)
                added, deleted = parse_numstat(out)
                changed = added + deleted
                total = prev_total + added - deleted
                pct = (changed / prev_total * 100) if prev_total and prev_total > 0 else None
            
            commit_data.append({
                'commit': commit[:10],
                'date': date,
                'changes': changed,
                'pct': pct,
                'total': total
            })
            
            prev_total = total
            prev_commit = commit
        
        # Calculate statistics
        stats = calculate_statistics(commit_data)
        
        # Generate table with AI detection
        for data in commit_data:
            pct_str = f"{data['pct']:.2f}%" if data['pct'] is not None else 'N/A'
            ai_detection = detect_ai_contribution(data['changes'], data['total'], stats)
            
            table_data.append([
                data['commit'],
                data['date'],
                data['changes'],
                pct_str,
                data['total'],
                ai_detection
            ])
        
        # print the table using tabulate
        print(tabulate(table_data, headers=headers, tablefmt='grid', numalign='right'))
        
        # print statistics
        print_statistics(stats)


def main():
    parser = argparse.ArgumentParser(description='Analyze GitHub repo line change stats per commit')
    parser.add_argument('repo', help='Git URL of the repository to analyze')
    args = parser.parse_args()
    try:
        analyze(args.repo)
    except subprocess.CalledProcessError as e:
        print(f"Error running git: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
