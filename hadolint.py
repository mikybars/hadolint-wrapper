import os,sys
import subprocess
import json
import argparse

parsed_errors = []
color = 'auto'

fore_red = '\033[1;31m'
fore_yellow = '\033[1;33m'
color_reset = '\033[m'

def print_error(err):
    error_line = '{}: {}'.format(err['code'], err['message'])
    if color == 'always' or color == 'auto' and sys.stdout.isatty():
        prefix = fore_red if err['level'] == 'error' else fore_yellow
        suffix = color_reset
    else:
        prefix = '[x] ' if err['level'] == 'error' else '[!] '
        suffix = ''
    print('{}{}{}'.format(prefix, error_line, suffix))

def print_input_line_with_errors((i, line)):
    map(print_error, filter(lambda err: err['line'] == i+1, parsed_errors))
    print(line)

def main():
    global color

    # Setup command line arg parser
    parser = argparse.ArgumentParser(description='Provides a more clear output for hadolint')
    parser.add_argument("Dockerfile")
    parser.add_argument('-c', '--config', metavar='FILENAME', help="Path to the hadolint configuration file")
    parser.add_argument("--docker", help="use the dockerized version of hadolint",
    action="store_true")
    parser.add_argument("--color", choices=['never', 'auto', 'always'], default='auto')

    args = parser.parse_args()
    color = args.color

    try:
        # Read input
        input_ = open(args.Dockerfile) if args.Dockerfile != '-' else sys.stdin
        lines = [line.rstrip('\n') for line in input_]

        # Build command line
        hadolint_args = ["-c", args.config] if args.config else []
        cmd = ["docker", "run", "--rm", "-i", "hadolint/hadolint"] if args.docker else []
        cmd.extend(["hadolint"] + hadolint_args + ["-f", "json", "-"])

        # Exec hadolint and grab the output
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        hadolint_report = process.communicate('\n'.join(lines))[0]

        # Parse errors and merge them with input lines
        global parsed_errors
        parsed_errors = json.loads(hadolint_report)
        if len(parsed_errors) > 0:
            map(print_input_line_with_errors, enumerate(lines))

        # Exit with the exit code of hadolint!
        sys.exit(process.returncode)
    except IOError as err:
        print(err)
        sys.exit(10)
    except ValueError:
        print("Error: Bad output from hadolint")
        sys.exit(20)

if __name__ == '__main__':
    main()
