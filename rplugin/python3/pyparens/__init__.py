from importlib import find_loader

if not find_loader('vim'):
    import neovim
    from pyparens.pyparens import PyParens

    @neovim.plugin
    class PyParensHandler(object):
        def __init__(self, vim):
            self._vim = vim
            self._pyparens = PyParens(self._vim)

        @neovim.function('PyParensMatch', sync=False)
        def match(self, args):
            self._pyparens.match()
