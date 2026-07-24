from pathlib import Path
import json
try:
    import yaml
except ModuleNotFoundError:  # lightweight fallback for repository-owned simple YAML
    yaml = None

def _scalar(v: str):
    v=v.strip()
    if v in ('true','false'): return v == 'true'
    if v.startswith('"') and v.endswith('"'): return v[1:-1]
    try: return int(v)
    except ValueError: pass
    try: return float(v)
    except ValueError: return v

def _fallback(text: str):
    lines=[ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith('#')]
    root={}; stack=[(-1, root)]
    for ln in lines:
        indent=len(ln)-len(ln.lstrip()); stripped=ln.strip()
        while stack and indent <= stack[-1][0]: stack.pop()
        parent=stack[-1][1]
        if stripped.startswith('- '):
            item=_scalar(stripped[2:])
            if isinstance(parent, list): parent.append(item)
            continue
        key, _, val=stripped.partition(':')
        if val.strip(): parent[key]=_scalar(val)
        else:
            nxt=[] if any(l.startswith(' '*(indent+2)+'- ') for l in lines[lines.index(ln)+1:lines.index(ln)+3]) else {}
            parent[key]=nxt; stack.append((indent, nxt))
    return root

def load_yaml(path: str | Path) -> dict:
    text=Path(path).read_text(encoding='utf-8')
    if text.lstrip().startswith(("{", "[")):
        return json.loads(text)
    return (yaml.safe_load(text) if yaml else _fallback(text)) or {}
