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
        return m

    def regex_left(self, re_pairs):
        pos = self.reverse_regex(re_pairs[0], 0, self.cursor)
        if pos is not None:
            pos = self.reverse_regex(
                    re_pairs[0], 0, self.cursor + (pos.end() - pos.start()))
            pos = pos.start(), pos.end()
        rpos = self.cursor, self.cursor + 1

        while pos is not None:
            rpos = self.reverse_regex(re_pairs[1], pos[1], rpos[0])
            if rpos is None:
                break
            else:
                rpos = rpos.start(), rpos.end()
            pos = self.reverse_regex(re_pairs[0], 0, pos[0])
            if pos is not None:
                pos = pos.start(), pos.end()
        return pos

    def regex_right(self, re_pairs):
        pos = re_pairs[1].search(self.text, self.cursor + 1)
        if pos is not None:
            pos = re_pairs[1].search(
                    self.text, self.cursor + 1 - (pos.end() - pos.start()))
            pos = pos.start(), pos.end()
        lpos = self.cursor, self.cursor + 1

        while pos is not None:
            lpos = re_pairs[0].search(self.text, lpos[1], pos[0])
            if lpos is not None:
                lpos = lpos.start(), lpos.end()
            else:
                break
            pos = re_pairs[1].search(self.text, pos[1])
            if pos is not None:
                pos = pos.start(), pos.end()
        return pos

    def regex_closest_pair(self):
        pclosest = None
        lclosest = 0, 0
        rclosest = len(self.text), 0

        # Check if cursor is a pair
        for pair in self.pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            if regex_pair[0].match(self.text, self.cursor) is not None or \
               regex_pair[1].match(self.text, self.cursor) is not None:
                return None, None

        for pair in self.pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            lpos = self.regex_left(regex_pair)
            if lpos is not None and lpos[1] > lclosest[1]:
                rpos = self.regex_right(regex_pair)
                if rpos is not None and rpos[0] < rclosest[0]:
                    pclosest = pair
                    lclosest, rclosest = lpos, rpos

        if pclosest is None:
            return None, None
        return lclosest, rclosest

    def highlight(self, positions):
        cmd = []
        for start, end in positions:
            # +1 as buffer is 0 index, windows are 1 index
            cmd.append('\%{}l\%>{}c\%<{}c'.format(
                start[0] + 1, start[1] - 1, end[1]))
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
        lc = self.bufpos(lc[0]), self.bufpos(lc[1])
        rc = self.bufpos(rc[0]), self.bufpos(rc[1])
        self.highlight([lc, rc])
