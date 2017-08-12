function! pyparens#init()
	if &diff
		return
	endif

	if pumvisible()
		return
	endif

	call PyParensInit()

	augroup PyParensMatcher
				autocmd! CursorMoved,CursorMovedI <buffer>
							\ call PyParensMatch()
	augroup END
endfunction
