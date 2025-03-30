"""
Main module.
This module provides the CLI interface for the coverage utility script.
"""

import sys
import argparse

from .extraction import extract_coverage, compare_coverage, run_coverage, set_verbose
from .github_api import generate_comment, post_comment, set_github_output
from .workflow import process_coverage_workflow

def main():
    parser = argparse.ArgumentParser(description='Coverage utility script for GitHub Actions workflows')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Helper function to add common arguments
    def add_common_args(parser):
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        return parser
    
    # extract-coverage command - used directly in workflow
    extract_parser = add_common_args(subparsers.add_parser('extract-coverage', help='Extract coverage percentage from a file'))
    extract_parser.add_argument('file_path', help='Path to the coverage report file')
    extract_parser.add_argument('--type', choices=['extension', 'webview'], default='extension',
                               help='Type of coverage report')
    extract_parser.add_argument('--github-output', action='store_true', help='Output in GitHub Actions format')
    
    # compare-coverage command - used by process-workflow
    compare_parser = add_common_args(subparsers.add_parser('compare-coverage', help='Compare coverage percentages'))
    compare_parser.add_argument('base_cov', help='Base branch coverage percentage')
    compare_parser.add_argument('pr_cov', help='PR branch coverage percentage')
    compare_parser.add_argument('--output-prefix', default='', help='Prefix for GitHub Actions output variables')
    compare_parser.add_argument('--github-output', action='store_true', help='Output in GitHub Actions format')
    
    # generate-comment command - used by process-workflow
    comment_parser = add_common_args(subparsers.add_parser('generate-comment', help='Generate PR comment with coverage comparison'))
    comment_parser.add_argument('base_ext_cov', help='Base branch extension coverage')
    comment_parser.add_argument('pr_ext_cov', help='PR branch extension coverage')
    comment_parser.add_argument('ext_decreased', help='Whether extension coverage decreased (true/false)')
    comment_parser.add_argument('ext_diff', help='Extension coverage difference')
    comment_parser.add_argument('base_web_cov', help='Base branch webview coverage')
    comment_parser.add_argument('pr_web_cov', help='PR branch webview coverage')
    comment_parser.add_argument('web_decreased', help='Whether webview coverage decreased (true/false)')
    comment_parser.add_argument('web_diff', help='Webview coverage difference')
    
    # post-comment command - used by process-workflow
    post_parser = add_common_args(subparsers.add_parser('post-comment', help='Post a comment to a GitHub PR'))
    post_parser.add_argument('comment_path', help='Path to the file containing the comment text')
    post_parser.add_argument('pr_number', help='PR number')
    post_parser.add_argument('repo', help='Repository in the format "owner/repo"')
    post_parser.add_argument('--token', help='GitHub token')
    
    # run-coverage command - used by process-workflow
    run_parser = add_common_args(subparsers.add_parser('run-coverage', help='Run a coverage command and extract the coverage percentage'))
    run_parser.add_argument('command', help='Command to run')
    run_parser.add_argument('output_file', help='File to save the output to')
    run_parser.add_argument('--type', choices=['extension', 'webview'], default='extension',
                           help='Type of coverage report')
    run_parser.add_argument('--github-output', action='store_true', help='Output in GitHub Actions format')
    
    # process-workflow command - used directly in workflow
    workflow_parser = add_common_args(subparsers.add_parser('process-workflow', help='Process the entire coverage workflow'))
    workflow_parser.add_argument('--base-branch', required=True, help='Base branch name')
    workflow_parser.add_argument('--pr-number', help='PR number')
    workflow_parser.add_argument('--repo', help='Repository in the format "owner/repo"')
    workflow_parser.add_argument('--token', help='GitHub token')
    
    # set-github-output command - used by process-workflow
    output_parser = add_common_args(subparsers.add_parser('set-github-output', help='Set GitHub Actions output variable'))
    output_parser.add_argument('name', help='Output variable name')
    output_parser.add_argument('value', help='Output variable value')
    
    args = parser.parse_args()
    
    # Set verbose flag - check both the main parser and subparser arguments
    if hasattr(args, 'verbose') and args.verbose:
        set_verbose(True)
        print("Verbose mode enabled")
    
    if args.command == 'extract-coverage':
        coverage_pct = extract_coverage(args.file_path, args.type)
        if args.github_output:
            set_github_output(f"{args.type}_coverage", coverage_pct)
        else:
            print(coverage_pct)
        
    elif args.command == 'compare-coverage':
        decreased, diff = compare_coverage(args.base_cov, args.pr_cov)
        if args.github_output:
            prefix = args.output_prefix
            set_github_output(f"{prefix}decreased", str(decreased).lower())
            set_github_output(f"{prefix}diff", diff)
            print(f"Coverage difference: {diff}%")
            print(f"Coverage decreased: {decreased}")
        else:
            print(f"decreased={str(decreased).lower()}")
            print(f"diff={diff}")
        
    elif args.command == 'generate-comment':
        comment = generate_comment(
            args.base_ext_cov, args.pr_ext_cov, args.ext_decreased, args.ext_diff,
            args.base_web_cov, args.pr_web_cov, args.web_decreased, args.web_diff
        )
        # Output the comment to stdout
        print(comment)
        
    elif args.command == 'post-comment':
        post_comment(args.comment_path, args.pr_number, args.repo, args.token)
        
    elif args.command == 'run-coverage':
        coverage_pct = run_coverage(args.command, args.output_file, args.type)
        if args.github_output:
            set_github_output(f"{args.type}_coverage", coverage_pct)
        else:
            print(coverage_pct)
        
    elif args.command == 'process-workflow':
        process_coverage_workflow(args)
        
    elif args.command == 'set-github-output':
        set_github_output(args.name, args.value)
    
    else:
        parser.print_help()
        sys.exit(1)
