import neovim

from pyparens.pyparens import PyParens


@neovim.plugin
class PyParensHandler(object):
    def __init__(self, vim):
        self._vim = vim
        self._pyparens = PyParens(self._vim)

    @neovim.function('PyParensInit', sync=False)
    def init(self, args):
        self._pyparens.init()

    @neovim.function('PyParensMatch', sync=True)
    def match(self, args):
        self._pyparens.match()
