function! pyparens#setup()
	if &diff
		return
	endif

	if pumvisible()
		return
	endif

	" Default to enable
	if !exists('b:pyparens_enabled')
		call pyparens#enable()
	endif

endfunction

function! pyparens#match()
    let l:mode = mode()
    if l:mode == 'v' || l:mode == 'V' || l:mode == '^V'
        " Clear the highlight groups if visual
        silent! 2match clear g:pyparens_hl_group
        silent! 3match clear g:pyparens_hl_col_group
    else
	    return has('nvim') ? PyParensMatch() : pyparens#vim#match()
    endif
endfunction

function! pyparens#enable()
	let b:pyparens_enabled = 1
	augroup PyParensMatcher
		autocmd! CursorMoved,CursorMovedI,WinEnter <buffer>
					\ call pyparens#match()
    augroup END
endfunction

function! pyparens#disable()
	let b:pyparens_enabled = 0
	autocmd! PyParensMatcher * <buffer>
endfunction

