from pathlib import Path
for p in Path('.github/workflows').glob('*.yml'):
    text=p.read_text()
    assert 'jobs:' in text, f'{p} has no jobs'
    assert 'on:' in text and ('schedule:' in text or 'workflow_dispatch:' in text), f'{p} has no trigger'
    print(f'workflow ok: {p}')
