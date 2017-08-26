let s:pyparens_path = expand('<sfile>:p:h:h:h') . '/rplugin/python3'
	python3 << EOF
import sys
import vim
sys.path.insert(0, vim.eval('s:pyparens_path'))
import pyparens.PyParens
import pyparens.rplugin.Neovim
nvim = Neovim(vim)
pyparens = PyParens(nvim)
EOF

function! pyparens#vim#init()
py3 pyparens.init()
endfunction

function! pyparens#vim#match()
py3 pyparens.match()
endfunction
