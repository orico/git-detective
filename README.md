# Git Repository AI Contribution Detector

This tool analyzes GitHub repositories to determine whether contributions are likely made by humans or AI. It operates on the principle that AI-generated code typically results in larger, out-of-distribution changes compared to human contributions. The analysis is performed by:

1. Cloning the target repository
2. Analyzing commit patterns and statistics
3. Classifying contributions based on size and distribution of changes
4. Providing statistical insights to identify unusual commit patterns

The tool helps identify potential AI-generated code by detecting:
- Unusually large commits (outliers in terms of lines changed)
- Out-of-distribution changes compared to the repository's normal patterns
- Sudden spikes in code volume that deviate from typical human contribution patterns

## Requirements
- Python 3.x
- git (available in your PATH)

## Usage
```bash
python analyze_repo.py <git-repo-url>
```

For example, to analyze the `git-detective` repository:
```bash
python analyze_repo.py https://github.com/orico/git-detective
```

## Understanding the Statistics

### Metrics Explained
- **Changes per commit**: The number of lines changed in each commit
- **Percentage change**: The percentage of lines changed relative to the total lines in the previous commit
- **IQR (Interquartile Range)**: The difference between the 75th (Q3) and 25th (Q1) percentiles of percentage changes. This helps identify the typical range of changes and potential outliers:
  - Values below Q1 - 1.5×IQR: Considered unusually small changes
  - Values above Q3 + 1.5×IQR: Considered unusually large changes
  - Changes within this range are considered typical for the repository

### Example Output
```
+------------+---------------------------+-----------------+------------+---------------+---------------------+
| Commit     | Date                      |   Lines Changed | % Change   |   Total Lines | Contribution Type   |
+============+===========================+=================+============+===============+=====================+
| 3eb8a37d0e | 2025-03-29 06:03:08 +0300 |            1515 | N/A        |          1515 | Likely AI           |
| d19be46e0d | 2025-03-29 06:05:08 +0300 |              16 | 1.06%      |          1515 | Likely Human        |
| 53eb35e125 | 2025-03-29 07:29:38 +0300 |             176 | 11.62%     |          1547 | Possible AI         |
| ad71f2f402 | 2025-03-29 07:42:13 +0300 |            1104 | 71.36%     |          1701 | Likely AI           |
| 9333a02e02 | 2025-07-24 14:03:10 +0300 |            1125 | 66.14%     |          2714 | Likely AI           |
| 521b40141d | 2025-07-24 14:04:46 +0300 |              90 | 3.32%      |          2628 | Likely Human        |
| b2003d6d24 | 2025-07-24 14:08:55 +0300 |             127 | 4.83%      |          2737 | Likely Human        |
| 4182c476bc | 2025-07-24 14:19:27 +0300 |             114 | 4.17%      |          2849 | Likely Human        |
| 2b0fb09ce8 | 2025-07-26 07:28:50 +0300 |            2812 | 95.58%     |          5002 | Likely AI           |
...
```

The output includes:
- **Commit**: The first 10 characters of the commit hash
- **Date**: Timestamp of the commit
- **Lines Changed**: Total number of lines modified in this commit
- **% Change**: Percentage of lines changed relative to previous commit
- **Total Lines**: Total lines of code after this commit
- **Contribution Type**: Classification of the change based on size and patterns:
  - Likely Human: Small to medium changes (typically within IQR range)
  - Possible AI: Larger changes that might be AI-generated
  - Likely AI: Very large changes typical of AI-generated code

### Repository Statistics
```
Changes per commit (mean)        422.44
Changes per commit (median)      93.50
Changes standard deviation       750.84
Percentage change (mean)         16.27%
Percentage change (std)          29.94%
Percentage Q1 (25th percentile)  1.70%
Percentage Q3 (75th percentile)  4.83%
Percentage IQR                   3.13%
```

These statistics help understand the typical size and variability of changes in your repository, making it easier to identify unusual patterns or potential AI-generated contributions.
