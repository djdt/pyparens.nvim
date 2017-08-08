if exists("g:loaded_pyparens")
	finish
endif
let g:loaded_pyparens = 1

let g:pyparens_hl_group =
			\ get(g:, 'pyparens_hl_group',     'MatchParen')
let g:pyparens_pairs =
			\ get(g:, 'pyparens_pairs',
			\ [[ '{', '}' ], [ '(', ')' ], [ '[', ']' ]])
let g:pyparens_ft_pairs = 
			\ get(g:, 'pyparens_ft_pairs', {
			\})

augroup PyParens
	autocmd! FileType * call pyparens#init()
augroup END

function! pyparens#init()
	if &diff
		return
	endif
	if pumvisible() || (&t_Co < 8 && !has("gui_running"))
		return
	endif
	call PyParensInit()

	augroup PyParensMatcher
				autocmd! CursorMoved,CursorMovedI <buffer>
							\ call PyParensMatch()
	augroup END
endfunction
