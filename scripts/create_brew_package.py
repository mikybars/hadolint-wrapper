#!/usr/bin/env python

import io
import re
import sys
import tarfile

import toml


class TarFilePatcher:
    def __init__(self, in_filename, out_filename):
        self._in_tarfile = tarfile.open(in_filename, 'r:gz')
        self._out_filename = out_filename
        self._rules = {}

    def with_rule(self, match_fn, patch_fn):
        self._rules[match_fn] = patch_fn
        return self

    def patch(self):
        with tarfile.open(self._out_filename, 'w:gz') as out_tarfile:
            for file in self._in_tarfile:
                original_file = self._in_tarfile.extractfile(file).read()
                patch_fn = self._match_rule(file.name)
                if patch_fn:
                    patched_file = patch_fn(original_file)
                    file.size = len(patched_file)
                    out_tarfile.addfile(file, io.BytesIO(patched_file))
                else:
                    out_tarfile.addfile(file, io.BytesIO(original_file))

    def _match_rule(self, filename):
        for match_fn in self._rules:
            if match_fn(filename):
                return self._rules[match_fn]
        return None


def filename_with_suffix(filename, ext, suffix):
    return re.sub(f"{ext}$", f"{suffix}{ext}", filename)


def toml_remove_section(in_bytes, section_name):
    parsed_toml = toml.loads(str(in_bytes, 'utf-8'))
    if section_name in parsed_toml:
        del(parsed_toml[section_name])
    return bytes(toml.dumps(parsed_toml), 'utf-8')


def main():
    if len(sys.argv) < 2:
        print("Please provide a input tar filename")
        sys.exit(1)

    in_filename = sys.argv[1]

    out_filename = filename_with_suffix(in_filename, '.tar.gz', '-brew')
    TarFilePatcher(in_filename, out_filename).with_rule(
        lambda filename: filename.endswith('/pyproject.toml'),
        lambda in_bytes: toml_remove_section(in_bytes, 'build-system')
    ).patch()

    print(f'Created {out_filename}')


if __name__ == '__main__':
    main()
