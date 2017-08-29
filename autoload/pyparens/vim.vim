let s:pyparens_path = expand('<sfile>:p:h:h:h') . '/rplugin/python3'
	python3 << EOF
import sys
import vim
sys.path.insert(0, vim.eval('s:pyparens_path'))
from pyparens.pyparens import PyParens
import pyparens.rplugin
nvim = pyparens.rplugin.Neovim(vim)
pyparens = PyParens(nvim)
EOF

function! pyparens#vim#match()
py3 pyparens.match()
endfunction
