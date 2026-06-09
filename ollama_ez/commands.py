#!/usr/bin/env python3

import pathlib
import yaml
import types


HISTORY = pathlib.Path('history.yaml')


from functools import update_wrapper


class cmdmethod:
    """
    类似 classmethod，但调用时自动传 cls.obj 给原函数。
    """

    is_cmdmethod = True

    def __init__(self, func):
        self.func = func
        self.as_tool = True
        update_wrapper(self, func)

    def __get__(self, instance, owner):
        def bound(*args, **kwargs):
            return self.func(owner.obj, *args, **kwargs)

        update_wrapper(bound, self.func)

        bound.as_tool = True
        bound.is_cmdmethod = True
        bound.__cmdmethod__ = self

        return types.MethodType(bound, owner)


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

    @cmdmethod
    def clear(obj):
        """Clear the history
        """
        obj.history = []
        print(f'💻System: The history is cleared.')

    @cmdmethod
    def pop(obj, k:int):
        """To pop the k-th message in history.
        """
        obj.history.pop(k)
        print(f'💻System: The k-th message in history is poped.')

    @cmdmethod
    def save(obj):
        """save history in `history_file`
        """
        if not HISTORY.exists():     
            print("💻System: The history is stored in {HISTORY}!")
            HISTORY.write_text(yaml.dump(obj.history, allow_unicode=True))
        else:
            print(f"💻System: {HISTORY} is available! The history will not be stored")

    @cmdmethod
    def load(obj):
        if HISTORY.exists():
            print(f'💻System: The history is loaded from {HISTORY}!')
            obj.history = yaml.safe_load(str(HISTORY))
        else:
            print('💻System: No history is loaded!')

    @cmdmethod
    def ollama(obj, cmd:str, *args):
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


