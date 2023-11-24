# -*- coding: utf-8 -*-


import re
import json
import string


class _Template(string.Template):
    PARAMETER_LABEL = r'[_a-z]+[_a-z0-9-]*'

    pattern = r"""
            %(delim)s(?:
              (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
              (?P<named>%(id)s)      |   # delimiter and a Python identifier
              {(?P<braced>%(bid)s)}  |   # delimiter and a braced identifier
              (?P<invalid>)              # Other ill-formed delimiter exprs
            )
            """ % dict(
        delim=re.escape('$'),
        id=r'a^',  # Match Nothing, only match braced tag
        bid=r'(%(label)s\.%(label)s\.%(label)s)' % dict(
            label=PARAMETER_LABEL)
    )


def find_references(params):
    dumps = json.dumps(params)
    references = []
    for match in _Template.pattern.findall(dumps):
        if match and match[2]:
            references.append(match[2])
    return references


def substitute_references(params, **kwargs):
    dumps = json.dumps(params)
    return json.loads(_Template(dumps).safe_substitute(**kwargs))
