if exists("g:loaded_pyparens")
	finish
endif
let g:loaded_pyparens = 1

let g:pyparens_hl_group =
			\ get(g:, 'pyparens_hl_group',     'MatchParen')
let g:pyparens_pairs =
			\ get(g:, 'pyparens_pairs',
			\ [[ '\(', '\)' ], [ '\[', '\]' ], [ '\{', '\}' ]])
let g:pyparens_ft_pairs = 
			\ get(g:, 'pyparens_ft_pairs', {
			\ 'vim': [['\bif\b','\bendif\b'], ['\bfor\b','\bendfor\b']],
			\})

augroup PyParens
	autocmd! FileType * call pyparens#init()
augroup END
