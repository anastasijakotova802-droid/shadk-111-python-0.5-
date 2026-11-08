"""Выполнение кодовых ячеек .ipynb обычным Python, без Jupyter.

python run_notebook.py tasks/01.ipynb --save
"""

import argparse
import contextlib
import io
import json
from pathlib import Path
import traceback


def run(path, save=False):
    notebook = json.loads(path.read_text(encoding='utf-8-sig'))
    code_cells = [cell for cell in notebook.get('cells', []) if cell.get('cell_type') == 'code']
    if len(code_cells) != 10:
        raise ValueError('В блокноте должно быть ровно десять кодовых ячеек.')
    passed = 0
    for number, cell in enumerate(code_cells, 1):
        text = cell.get('source', '')
        text = ''.join(text) if isinstance(text, list) else text
        stream = io.StringIO()
        error = None
        # Каждая задача работает самостоятельно, без переменных соседних ячеек.
        namespace = {'__name__': '__main__'}
        try:
            with contextlib.redirect_stdout(stream):
                exec(compile(text, f'{path.name}:задача-{number:02d}', 'exec'), namespace)
            passed += 1
        except Exception as exc:
            error = exc
        output = stream.getvalue()
        print(f'Задача {number:02d}')
        if output:
            print(output, end='' if output.endswith('\n') else '\n')
        cell['execution_count'] = number
        cell['outputs'] = []
        if output:
            cell['outputs'].append({'output_type': 'stream', 'name': 'stdout', 'text': output.splitlines(keepends=True)})
        if error is not None:
            print(f'{type(error).__name__}: {error}')
            cell['outputs'].append({'output_type': 'error', 'ename': type(error).__name__, 'evalue': str(error),
                                    'traceback': [f'{type(error).__name__}: {error}']})
    if save:
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('Результаты ячеек сохранены в блокноте.')
    print(f'Выполнено без ошибок: {passed} из 10.')
    return passed == 10


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook', type=Path)
    parser.add_argument('--save', action='store_true', help='Сохранить вывод и номера выполнения в .ipynb')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.notebook.resolve(), args.save) else 1)
