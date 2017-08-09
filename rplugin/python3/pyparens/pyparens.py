import re


class PyParens(object):
    def __init__(self, vim):
        self.vim = vim
        self.pairs = []
        self.group = ""
        self.bounds = [0, 0]
        self.text = ""
        self.cursor = 0

    def init(self):
        self.group = self.vim.vars['pyparens_hl_group']
        filetype = self.vim.current.buffer.options['ft']
        self.pairs = self.vim.vars['pyparens_pairs']
        lang_pairs = self.vim.vars['pyparens_ft_pairs'].get(filetype)
        if lang_pairs:
            self.pairs.extend(lang_pairs)

    def bufpos(self, textpos):
        if textpos is None:
            return None, None
        row = 0
        col = 1
        for c in self.text:
            if textpos == 0:
                break
            col += 1
            if c == '\n':
                row += 1
                col = 1
            textpos -= 1
        # Remember to readd the trimed rows
        return row + self.bounds[0], col

    def textpos(self, bufpos):
        pos = 0
        # Trim rows out of scope
        for i in range(bufpos[0] - self.bounds[0]):
            pos += len(self.buffer[i]) + 1
        return pos + bufpos[1]

    def reverse_regex(self, regex, start, end):
        m = None
        for m in regex.finditer(self.text, start, end):
            pass
        if m is not None:
            return m.start()
        return None

    def regex_left(self, re_pairs):
        pos = self.reverse_regex(re_pairs[0], 0, self.cursor)
        rpos = self.cursor

        while pos is not None:
            rpos = self.reverse_regex(re_pairs[1], pos + 1, rpos)
            if rpos is None:
                break
            pos = self.reverse_regex(re_pairs[0], 0, pos)
        return pos

    def regex_right(self, re_pairs):
        pos = re_pairs[1].search(self.text, self.cursor + 1)
        lpos = self.cursor
        if pos is not None:
            pos = pos.start()

        while pos is not None:
            lpos = re_pairs[0].search(self.text, lpos + 1, pos)
            if lpos is not None:
                lpos = lpos.start()
            else:
                break
            pos = re_pairs[1].search(self.text, pos + 1)
            if pos is not None:
                pos = pos.start()
        return pos

    def regex_closest_pair(self):
        pclosest = None
        lclosest = 0
        rclosest = len(self.text)

        # Check if cursor is a pair
        for pair in self.pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            if regex_pair[0].match(self.text, self.cursor) is not None or \
               regex_pair[1].match(self.text, self.cursor) is not None:
                return None, None

        for pair in self.pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            lpos = self.regex_left(regex_pair)
            if lpos is not None and lpos > lclosest:
                rpos = self.regex_right(regex_pair)
                if rpos is not None and rpos < rclosest:
                    pclosest = pair
                    lclosest, rclosest = lpos, rpos

        if pclosest is None:
            return None, None
        return lclosest, rclosest

    def highlight(self, positions):
        cmd = []
        for pos in positions:
            # +1 as buffer is 0 index, windows are 1 index
            cmd.append('\%{}l\%{}c'.format(pos[0] + 1, pos[1]))
        self.vim.command(
            'match {} /'.format(self.group) + '\|'.join(cmd) + '/')

    def match(self):
        self.vim.command('silent! match clear {}'.format(self.group))
        self.bounds = (int(self.vim.eval("line('w0')")) - 1,
                       int(self.vim.eval("line('w$')")))
        self.buffer = self.vim.current.buffer[self.bounds[0]:self.bounds[1]]
        self.text = '\n'.join(self.buffer)
        cursor = self.vim.current.window.cursor
        self.cursor = self.textpos((cursor[0] - 1, cursor[1]))

        lc, rc = self.regex_closest_pair()
        if lc is None or rc is None:
            return
        self.highlight([self.bufpos(lc), self.bufpos(rc)])
