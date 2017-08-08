# pyparens.nvim
Neovim plugin to highlight surrounding braces.

## Installation

Using Plug:
```
Plug 'djdt/pyparens.nvim', {'do': 'UpdateRemotePlugins'}
```

## Options

Set the highlight group used
```
let g:pyparens_hl_group = 'MatchParen'
```
Set the pairs detected. `g:pyparens_ft_pairs` can be used to set filetype specific pairs.
```
let g:pyparens_pairs = [[ '{', '}' ], [ '(', ')' ], [ '[', ']' ]]

let g:pyparens_ft_pairs = {'cpp': [['<', '>']]}
```

Inspired by [matchparenalways.vim](https://github.com/justinmk/vim-matchparenalways) and [MatchTagAlways](https://github.com/Valloric/MatchTagAlways).
