function! pyparens#setup()
	if &diff
		return
	endif

	if pumvisible()
		return
	endif

	" Default to enable
	if !exists('b:pyparens_enabled')
		call pyparens#init()
		call pyparens#enable()
	endif

endfunction

function! pyparens#init()
	return has('nvim') ? PyParensInit() : pyparens#vim#init()
endfunction

function! pyparens#match()
	return has('nvim') ? PyParensMatch() : pyparens#vim#match()
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

