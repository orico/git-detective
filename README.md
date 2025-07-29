# Git Repository Line Change Analyzer

This tool clones a GitHub repository in a temporary directory and reports the number of lines changed per commit,
along with the percentage change relative to the previous commit and the cumulative total lines of code.

## Requirements
- Python 3.x
- git (available in your PATH)

## Usage
```bash
python analyze_repo.py <git-repo-url>
```

For example, to analyze the `agent-annotation-team` repository:
```bash
python analyze_repo.py https://github.com/orico/agent-annotation-team
```
