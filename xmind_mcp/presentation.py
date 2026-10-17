"""Presentation policy for MCP JSON text results."""
from copy import deepcopy
from pathlib import Path


def public_result(result, *, output=False, success_message=None):
    result = deepcopy(result)
    if output and result.get('status') == 'success':
        data = result.setdefault('data', {})
        path = data.get('output_path') or data.get('output_file') or data.get('absolute_path')
        if path:
            data['filename'] = Path(path).name
            data['absolute_path'] = str(path)
        for key in ('output_path', 'output_file', 'source_file'):
            data.pop(key, None)
        if success_message:
            result['message'] = success_message
    return result
