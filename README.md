# pyparens.nvim
Neovim / vim8 plugin to highlight surrounding braces.

## Installation

Using [vim-plug](https://github.com/junegunn/vim-plug):
```
Plug 'djdt/pyparens.nvim'
```
Be sure to `:UpdateRemotePlugins` if using Neovim, this can be acheived using Plug:
```
Plug 'djdt/pyparens.nvim', {do: ':UpdateRemotePlugins'}
```

## Options

To set the highlight group use `g:pyparens_hl_group`:
```
let g:pyparens_hl_group = 'MatchParen'
```
The leftmost column of the current block will be highlighted if `g:pyparens_hl_col_group` is set.

Use `g:pyparens_pairs` to set the types of pairs highlighted.
Each pair is a list of [python regexes](https://docs.python.org/3/howto/regex.html#regex-howto) for opening and closing words.

`g:pyparens_ft_pairs` can be used to set pairs used only for specific filetypes.

As an example:
```
let g:pyparens_pairs = [[ '\{', '\}' ], [ '\(', '\)' ], [ '\[', '\]' ]]

let g:pyparens_ft_pairs = {
		\ 'cpp': [['(?<!\<)\<(?!\<)', '\>']],
		\ 'vim': [['\bif\b', '\bendif\b', '\bfor\b', '\bendfor\b']]
		\}
```

Inspired by [matchparenalways.vim](https://github.com/justinmk/vim-matchparenalways) and [MatchTagAlways](https://github.com/Valloric/MatchTagAlways).
