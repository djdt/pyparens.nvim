import re


class PyParens(object):
    def __init__(self, vim):
        self.vim = vim
        self.pairs = []
        self.bounds = [0, 0]
        self.text = ""
        self.cursor = 0
        self.last_pair_pos = [None, None]

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
        # Remember to read the trimed rows
        return row + self.bounds[0], col

    def textpos(self, bufpos):
        cline = 1
        textpos = 0
        # # Trim rows out of scope
        for c in self.text:
            textpos += 1
            if c == '\n':
                cline += 1
            if cline > bufpos[0] - self.bounds[0]:
                break

        return textpos + bufpos[1]

    def reverse_regex(self, regex, start, end):
        match = None
        for match in regex.finditer(self.text, start, end):
            pass
        return match

    def find_in_cursor_left(self, regex):
        # Matches even when inside cursor
        prev = None
        for match in regex.finditer(self.text):
            if match.start() > self.cursor:
                return prev
            prev = match
        if prev and prev.start() <= self.cursor:
            return prev
        return None

    def find_in_cursor_right(self, regex):
        for match in regex.finditer(self.text):
            if match.end() > self.cursor:
                return match
        return None

    def find_pair_left(self, re_pairs):
        rmost = self.cursor
        # Get the nearest match to cursor
        pos = self.find_in_cursor_left(re_pairs[0])
        while pos is not None:
            # Check if pair end between match and cursor
            rpos = self.reverse_regex(re_pairs[1], pos.end(), rmost)
            if rpos is None:
                break
            else:
                rmost = rpos.start()
            # If found, retry search with next closest pair start
            pos = self.reverse_regex(re_pairs[0], 0, pos.start())
        return pos

    def find_pair_right(self, re_pairs):
        lmost = self.cursor + 1
        pos = self.find_in_cursor_right(re_pairs[1])
        while pos is not None:
            lpos = re_pairs[0].search(self.text, lmost, pos.start())
            if lpos is None:
                break
            else:
                lmost = lpos.end()
            pos = re_pairs[1].search(self.text, pos.end())
        return pos

    def find_closest_pair(self):
        pclosest = None
        lclosest, rclosest = 0, len(self.text)
        lmatch, rmatch = None, None

        # Build pairs
        filetype = self.vim.current.buffer.options['ft']
        pairs = self.vim.vars['pyparens_pairs']
        lang_pairs = self.vim.vars['pyparens_ft_pairs'].get(filetype)
        if lang_pairs:
            pairs.extend(lang_pairs)

        # Search the text for matches
        for pair in pairs:
            regex_pair = [re.compile(pair[0]), re.compile(pair[1])]
            lpos = self.find_pair_left(regex_pair)
            if lpos is not None and lpos.end() > lclosest:
                rpos = self.find_pair_right(regex_pair)
                if rpos is not None and rpos.start() < rclosest:
                    pclosest = pair
                    lmatch, rmatch = lpos, rpos
                    lclosest, rclosest = lpos.end(), rpos.start()

        if pclosest is None:
            return None, None
        return lmatch, rmatch

    def highlight(self, left, right):
        cmd = "2match {} /{}\|{}/"
        pattern = "\%{}l\%>{}c\%<{}c"
        self.vim.command(cmd.format(
            self.vim.vars['pyparens_hl_group'],
            pattern.format(left[0][0] + 1, left[0][1] - 1, left[1][1]),
            pattern.format(right[0][0] + 1, right[0][1] - 1, right[1][1]))
        )

    def highlight_col(self, left, right):
        lower = min(left[0][1], right[0][1])
        # Return if no column to highlight
        if lower < 1:
            return
        self.vim.command('3match {} /'.format(
            self.vim.vars['pyparens_hl_col_group']) +
            '.\%>{}l\%<{}l\%{}c/'.format(
                left[0][0] + 1, right[0][0] + 1, lower + 1))

    def clear_highlight(self):
        self.vim.command('silent! 2match clear {}'.format(
            self.vim.vars['pyparens_hl_group']))
        self.vim.command('silent! 3match clear {}'.format(
            self.vim.vars['pyparens_hl_col_group']))

    def match(self):
        # Get any changes to buffer since init
        # Bounds -1 as lines are 1 indexed
        self.bounds = (int(self.vim.eval("line('w0')")) - 1,
                       int(self.vim.eval("line('w$')")))
        self.text = '\n'.join(
                self.vim.current.buffer[self.bounds[0]:self.bounds[1]])
        cursor = self.vim.current.window.cursor
        self.cursor = self.textpos((cursor[0] - 1, cursor[1]))

        # Find the closest mathcing pair
        left, right = self.find_closest_pair()

        # If empty return
        if left is None or right is None:
            self.last_pair_pos = [None, None]
            self.clear_highlight()
            return
        left = self.bufpos(left.start()), self.bufpos(left.end())
        right = self.bufpos(right.start()), self.bufpos(right.end())

        # Return if match hasn't changed
        if self.last_pair_pos == [left, right]:
            return
        self.last_pair_pos = [left, right]

        # Clear old match groups
        self.clear_highlight()
        # Highlight matches
        self.highlight(left, right)
        # Highlight column if needed
        if self.vim.vars['pyparens_hl_col_group'] != '' and \
                right[1][0] - left[0][0] > 2:
            self.highlight_col(left, right)
