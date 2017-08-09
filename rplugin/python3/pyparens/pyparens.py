import re
import time


def re_reverse_search(re, text, start, end):
    m = None
    for m in re.finditer(text, start, end):
        pass
    if m is not None:
        return m.start()
    return None
    # rtext = text[end - 1 if end else None:start - 1 if start else None:-1]
    # pos = re.search(rtext)
    # if pos is not None:
    #     pos = len(rtext) - pos.end()
    # return pos


class PyParens(object):
    def __init__(self, vim):
        self.vim = vim
        self.pairs = []
        self.group = ""
        self.bounds = [0, 0]
        self.text = ""

    def init(self):
        self.group = self.vim.vars['pyparens_hl_group']
        filetype = self.vim.current.buffer.options['ft']
        self.pairs = self.vim.vars['pyparens_pairs']
        lang_pairs = self.vim.vars['pyparens_ft_pairs'].get(filetype)
        if lang_pairs:
            self.pairs.extend(lang_pairs)

    def in_word(self, word, pos):
        if len(word) == 1:
            return False
        bounds = ' \t\n'
        if pos > 0 and self.text[pos - 1] in bounds:
            if self.text[pos + len(word)] in bounds:
                return False
        return True

    def find_left(self, pair, cursor):
        pos = self.text.rfind(pair[0], 0, cursor)
        while self.in_word(pair[0], pos) and pos != -1:
            pos = self.text.rfind(pair[0], 0, pos)
        rpos = cursor

        while pos != -1:
            rpos = self.text.rfind(pair[1], pos + 1, rpos)
            while self.in_word(pair[0], rpos) and rpos != -1:
                rpos = self.text.rfind(pair[1], pos + 1, rpos)
            if rpos == -1:
                break
            pos = self.text.rfind(pair[0], 0, pos)
            while self.in_word(pair[0], pos) and pos != -1:
                pos = self.text.rfind(pair[0], 0, pos)
        return pos

    def regex_left(self, re_pairs, cursor):
        pos = re_reverse_search(re_pairs[0], self.text, 0, cursor)
        rpos = cursor

        while pos is not None:
            rpos = re_reverse_search(re_pairs[1], self.text, pos + 1, rpos)
            if rpos is None:
                break
            pos = re_reverse_search(re_pairs[0], self.text, 0, pos)
        return pos

    def regex_right(self, re_pairs, cursor):
        pos = re_pairs[1].search(self.text, cursor + 1)
        lpos = cursor
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

    def find_right(self, pair, cursor):
        pos = self.text.find(pair[1], cursor + 1)
        while self.in_word(pair[1], pos) and pos != -1:
            pos = self.text.find(pair[1], pos + 1)
        lpos = cursor

        while pos != -1:
            lpos = self.text.find(pair[0], lpos + 1, pos)
            while self.in_word(pair[0], lpos) and lpos != -1:
                lpos = self.text.find(pair[0], lpos + 1, pos)
            if lpos == -1:
                break
            pos = self.text.find(pair[1], pos + 1)
            while self.in_word(pair[1], pos) and pos != -1:
                pos = self.text.find(pair[1], pos + 1)

        return pos

    def regex_closest_pair(self, cursor):
        pclosest = None
        lclosest = 0
        rclosest = len(self.text)

        for pair in self.pairs:
            re_pairs = [re.compile(pair[0]), re.compile(pair[1])]
            lpos = self.regex_left(re_pairs, cursor)
            if lpos is not None and lpos > lclosest:
                rpos = self.regex_right(re_pairs, cursor)
                if rpos is not None and rpos < rclosest:
                    pclosest = pair
                    lclosest, rclosest = lpos, rpos

        if pclosest is None:
            return None, None

        return lclosest, rclosest

    def find_closest_pair(self, cursor):
        pclosest = None
        lclosest = 0
        rclosest = len(self.text)

        for pair in [['(', ')']]:
            lpos = self.find_left(pair, cursor)
            if lpos != -1 and lpos > lclosest:
                rpos = self.find_right(pair, cursor)
                if rpos != -1 and rpos < rclosest:
                    pclosest = pair
                    lclosest, rclosest = lpos, rpos

        if pclosest is None:
            return None, None

        return lclosest, rclosest

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
        return row + self.bounds[0], col

    def textpos(self, bufpos):
        pos = 0
        for i in range(bufpos[0] - self.bounds[0]):
            pos += len(self.buffer[i]) + 1
        return pos + bufpos[1]

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
                       int(self.vim.eval("line('w$')") - 1))

        self.buffer = self.vim.current.buffer[self.bounds[0]:self.bounds[1]]
        self.text = '\n'.join(self.buffer)
        cursor = self.vim.current.window.cursor
        cursor = self.textpos((cursor[0] - 1, cursor[1]))
        self.cur_char = self.text[cursor]

        lc, rc = self.regex_closest_pair(cursor)

        if lc is None or rc is None:
            return
        lc = self.bufpos(lc)
        rc = self.bufpos(rc)
        self.highlight([lc, rc])
