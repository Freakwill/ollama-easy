import inspect
from typing import get_type_hints


def get_func_info(func):
    """Get information of function

    Arguments:
        func: function

    Return:
        dict
    """

    name = func.__name__

    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    param_names = list(sig.parameters.keys())

    type_hints = get_type_hints(func)

    return {
        'name': name,
        'params': [(p.name, p.annotation if p.annotation != inspect.Parameter.empty else None) for p in params],
        'param_names': param_names,
        'type_hints': type_hints,
        'return_annotation': sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None,
        'description': inspect.getdoc(func)
    }


import re
import os
from pathlib import Path


def expand_path(text: str, max_context_chars: int = 100000) -> str:
    """
    Replace @path patterns with file/directory contents, respecting token/context limits
    """
    pattern = r'@([^\s]+\.(yaml|yml|json|txt|md))'
    
    def replacer(match):
        path = match.group(1)
        full_path = Path(path)
        
        if not full_path.exists():
            return text
        
        try:
            if full_path.is_file():
                # Check single file size
                if full_path.stat().st_size > max_context_chars:
                    return f"[ERROR: File exceeds context limit ({max_context_chars} chars) - {path}]"
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) > max_context_chars:
                    return f"[ERROR: File content exceeds context limit - {path}]"
                return f"\n--- Content of {path} ---\n{content}\n--- End ---\n"
            
            elif full_path.is_dir():
                # Process directory with cumulative size tracking
                contents = []
                total_chars = 0
                
                for file_path in sorted(full_path.rglob('*')):
                    if file_path.is_file():
                        if file_path.stat().st_size > max_context_chars:
                            contents.append(f"[SKIPPED: {file_path} - file too large]")
                            continue
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if len(content) > max_context_chars:
                                contents.append(f"[SKIPPED: {file_path} - content exceeds limit]")
                                continue
                            
                            # Check cumulative limit
                            if total_chars + len(content) > max_context_chars:
                                remaining = max_context_chars - total_chars
                                if remaining > 100:  # Only include partial if reasonable
                                    truncated = content[:remaining] + "\n[...TRUNCATED...]"
                                    contents.append(f"\n--- {file_path} (partial) ---\n{truncated}\n--- End ---")
                                else:
                                    contents.append(f"[STOPPED: Reached context limit of {max_context_chars} chars]")
                                break
                            
                            contents.append(f"\n--- {file_path} ---\n{content}\n--- End ---")
                            total_chars += len(content)
                            
                        except Exception as e:
                            contents.append(f"[ERROR reading {file_path}: {e}]")
                
                if not contents:
                    return f"[INFO: Directory is empty or no readable files - {path}]"
                return '\n'.join(contents)
            
        except Exception as e:
            return f"[ERROR: Failed to read {path} - {e}]"
        
        return f"[ERROR: Unsupported path type - {path}]"
    
    # Process replacements and check final length
    result = re.sub(pattern, replacer, text)
    
    # Final context limit check
    if len(result) > max_context_chars:
        result = result[:max_context_chars] + f"\n[...TRUNCATED: Exceeded {max_context_chars} character limit...]"
    
    return result


def get_classmethods(cls):
    return {name:method for name, method in inspect.getmembers(cls, inspect.ismethod)
            if getattr(method, 'as_tool', False)}

