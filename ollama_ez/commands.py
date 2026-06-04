#!/usr/bin/env python3

import pathlib
import yaml


history_file = pathlib.Path('history.yaml')


from functools import wraps

def cmdmethod(f):
    @classmethod
    @wraps(f)
    def wrapper(cls, *args):
        return f(cls.obj, *args)
    return wrapper


class Commands:

    # the first argument should be the object of AI-chat

    obj = None

    @cmdmethod
    def greet(obj):
        """Greating to the user
        """
        print('💻System: Hello, user.')

    @cmdmethod
    def reset(obj):
        """Reset the settings of the model
        """
        obj.model = obj.__class__.default_model
        obj.description = obj.__class__.default_description
        print('💻System: Reset the settings (except the history).')

    @classmethod
    def clear(cls):
        """Clear the history
        """
        obj.history = []
        print(f'💻System: The history is cleared.')

    @cmdmethod
    def pop(obj, k):
        obj.history.pop(k)
        print(f'💻System: The k-th message in history is poped.')

    @cmdmethod
    def save(obj):
        if not history_file.exists():     
            print("💻System: The history is stored in {history_file}!")
            history_file.write_text(yaml.dump(obj.history, allow_unicode=True))
        else:
            print(f"💻System: {history_file} is available! The history will not be stored")

    @cmdmethod
    def load(obj):
        if history_file.exists():
            print(f'💻System: The history is loaded from {history_file}!')
            obj.history = yaml.safe_load(str(history_file))
        else:
            print('💻System: No history is loaded!')

    @cmdmethod
    def ollama(obj, cmd, *args):
        import ollama
        if cmd == 'search':
            cmd = 'web_search'
        elif cmd == 'fetch':
            cmd = 'web_fetch'
        try:
            getattr(ollama, cmd)(*args)
            print(f'💻System: Run the ollama command `{cmd}`.')
        except:
            print(f'💻System: Fail to run the ollama command `{cmd}`.')

    @classmethod
    def register(cls, name=None):
        def dec(f):
            _name = name or f.__name__
            setattr(cls, _name, f)
        return dec

