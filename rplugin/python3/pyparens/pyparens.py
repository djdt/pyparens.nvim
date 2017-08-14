import re


class PyParens(object):
    def __init__(self, vim):
        self.vim = vim
        self.pairs = []
        self.group = ""
        self.col_group = ""
        self.bounds = [0, 0]
        self.text = ""
        self.cursor = 0

    def init(self):
        self.group = self.vim.vars['pyparens_hl_group']
        self.col_group = self.vim.vars['pyparens_hl_col_group']
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
        match = None
        for match in regex.finditer(self.text, start, end):
            pass
        return match

    def match_near_cursor_left(self, regex):
        prev = None
        for match in regex.finditer(self.text):
            if match.start() > self.cursor:
                return prev
            prev = match
        if prev and prev.start() <= self.cursor:
            return prev
        return None

    def match_near_cursor_right(self, regex):
        for match in regex.finditer(self.text):
            if match.end() > self.cursor:
                return match
        return None

    def regex_left(self, re_pairs):
        rmost = self.cursor
        pos = self.match_near_cursor_left(re_pairs[0])
        while pos is not None:
            rpos = self.reverse_regex(re_pairs[1], pos.end(), rmost)
            if rpos is None:
                break
            else:
                rmost = rpos.start()
            pos = self.reverse_regex(re_pairs[0], 0, pos.start())
        return pos

    def regex_right(self, re_pairs):
        lmost = self.cursor + 1
        pos = self.match_near_cursor_right(re_pairs[1])
        while pos is not None:
            lpos = re_pairs[0].search(self.text, lmost, pos.start())
            if lpos is None:
                break
            else:
                lmost = lpos.end()
            pos = re_pairs[1].search(self.text, pos.end())
        return pos

    def regex_closest_pair(self):
        pclosest = None
        lclosest, rclosest = 0, len(self.text)
        lmatch, rmatch = None, None

        for pair in self.pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            lpos = self.regex_left(regex_pair)
            if lpos is not None and lpos.end() > lclosest:
                rpos = self.regex_right(regex_pair)
                if rpos is not None and rpos.start() < rclosest:
                    pclosest = pair
                    lmatch, rmatch = lpos, rpos
                    lclosest, rclosest = lpos.end(), rpos.start()

        if pclosest is None:
            return None, None
        return lmatch, rmatch

    def highlight(self, left, right):
        cmd = []
        for start, end in [left, right]:
            # +1 as buffer is 0 index, windows are 1 index
            cmd.append('\%{}l\%>{}c\%<{}c'.format(
                start[0] + 1, start[1] - 1, end[1]))
        self.vim.command(
            'match {} /'.format(self.group) + '\|'.join(cmd) + '/')

        # Highlight column if needed
        if self.col_group != '' and right[1][0] - left[0][0] > 2:
            # cur_line = self.vim.current.window.cursor[0] - 1
            lower = min(right[1][1], left[0][1])
            self.vim.command('2match {} /'.format(self.col_group) +
                             '.\%>{}l\%<{}l\%{}c/'.format(
                                 left[0][0] + 1, right[1][0] + 1, lower))

    def match(self):
        self.vim.command('silent! match clear {}'.format(self.group))
        self.vim.command('silent! 2match clear {}'.format(self.col_group))
        self.bounds = (int(self.vim.eval("line('w0')")) - 1,
                       int(self.vim.eval("line('w$')")))
        self.buffer = self.vim.current.buffer[self.bounds[0]:self.bounds[1]]
        self.text = '\n'.join(self.buffer)
        cursor = self.vim.current.window.cursor
        self.cursor = self.textpos((cursor[0] - 1, cursor[1]))

        lc, rc = self.regex_closest_pair()
        if lc is None or rc is None:
            return
        lc = self.bufpos(lc.start()), self.bufpos(lc.end())
        rc = self.bufpos(rc.start()), self.bufpos(rc.end())
        self.highlight(lc, rc)
