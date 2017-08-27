function! pyparens#setup()
	if &diff
		return
	endif

	if pumvisible()
		return
	endif

		call pyparens#init()

		augroup PyParensMatcher
					autocmd! CursorMoved,CursorMovedI,WinEnter <buffer>
								\ call pyparens#match()
		augroup END
endfunction

function! pyparens#init()
	return has('nvim') ? PyParensInit() : pyparens#vim#init()
endfunction

function! pyparens#match()
	return has('nvim') ? PyParensMatch() : pyparens#vim#match()
endfunction
