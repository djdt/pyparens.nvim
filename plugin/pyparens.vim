if exists("g:loaded_pyparens")
	finish
endif
let g:loaded_pyparens = 1

" Disbale matchparen
if exists("g:loaded_matchparen")
	exec NoMatchParen
else
	let g:loaded_matchparen = 1
endif

let g:pyparens_hl_group =
			\ get(g:, 'pyparens_hl_group', 'MatchParen')
let g:pyparens_hl_col_group =
			\ get(g:, 'pyparens_hl_col_group', '')
let g:pyparens_pairs =
			\ get(g:, 'pyparens_pairs',
			\ [[ '\(', '\)' ], [ '\[', '\]' ], [ '\{', '\}' ]])
let g:pyparens_ft_pairs =
			\ get(g:, 'pyparens_ft_pairs', {}
			\ )

augroup PyParens
	autocmd! BufEnter * call pyparens#init()
augroup END
