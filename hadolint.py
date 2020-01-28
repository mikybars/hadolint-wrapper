import json
import subprocess
import sys
from typing import List, Any
import click

FORE_RED = '\033[1;31m'
FORE_YELLOW = '\033[1;33m'
RESET_COLOR = '\033[m'

parsed_errors: List[Any]
color_setting: str


def should_use_colors():
    return color_setting == 'always' or color_setting == 'auto' and sys.stdout.isatty()


def style_error(e):
    error_msg = f'{e["code"]}: {e["message"]}'
    if should_use_colors():
        prefix = {
            'error': FORE_RED,
            'warning': FORE_YELLOW,
        }.get(e['level'], FORE_RED)
        suffix = RESET_COLOR
    else:
        prefix = {
            'error': '[x] ',
            'warning': '[!] ',
        }.get(e['level'], '[x] ')
        suffix = ''
    return f'{prefix}{error_msg}{suffix}'


def print_errors_if_any(lineno):
    line_errors = [e for e in parsed_errors if e['line'] == lineno]
    for e in line_errors:
        print(style_error(e))


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('Dockerfile', type=click.File())
@click.option('--use-docker', '-d', is_flag=True, help='use the dockerized version of hadolint')
@click.option('--config', '-c', help="path to the hadolint configuration file")
@click.option('--color', type=click.Choice(['never', 'auto', 'always']), default='auto')
def main(dockerfile, use_docker, config, color):
    """
    Provides a more clear output for hadolint
    """
    global color_setting, parsed_errors
    color_setting = color

    try:
        lines = [line.rstrip('\n') for line in dockerfile]

        hadolint_args = ["-c", config] if config else []
        cmd = ["docker", "run", "--rm", "-i", "hadolint/hadolint"] if use_docker else []
        cmd.extend(["hadolint"] + hadolint_args + ["-f", "json", "-"])

        process = subprocess.run(cmd, input='\n'.join(lines).encode(), capture_output=True)
        parsed_errors = json.loads(process.stdout)
        if len(parsed_errors) > 0:
            for n, line in enumerate(lines, start=1):
                print_errors_if_any(n)
                print(line)

        sys.exit(process.returncode)
    except IOError as err:
        print(err)
        sys.exit(10)
    except ValueError:
        print("Error: Bad output from hadolint")
        sys.exit(20)


if __name__ == '__main__':
    main()
