import time
import re


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
        pos = self.text.rfind(pair[0], None, cursor)
        while self.in_word(pair[0], pos) and pos != -1:
            pos = self.text.rfind(pair[0], None, pos)
        rpos = cursor

        while pos != -1:
            rpos = self.text.rfind(pair[1], pos + 1, rpos)
            while self.in_word(pair[0], rpos) and rpos != -1:
                rpos = self.text.rfind(pair[1], pos + 1, rpos)
            if rpos == -1:
                break
            pos = self.text.rfind(pair[0], None, pos)
            while self.in_word(pair[0], pos) and pos != -1:
                pos = self.text.rfind(pair[0], None, pos)
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

    def find_closest_pair(self, cursor):
        pclosest = [0, 0]
        lclosest = 0
        rclosest = len(self.text)

        for pair in self.pairs:
            lpos = self.find_left(pair, cursor)
            if lpos != -1 and lpos > lclosest:
                rpos = self.find_right(pair, cursor)
                if rpos != -1 and rpos < rclosest:
                    pclosest = pair
                    lclosest, rclosest = lpos, rpos

        if pclosest == [0, 0]:
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

        start = time.clock()
        lc, rc = self.find_closest_pair(cursor)
        end = time.clock()

        self.vim.command('echo "{}"'.format(end - start))

        if lc is None or rc is None:
            return
        lc = self.bufpos(lc)
        rc = self.bufpos(rc)
        self.highlight([lc, rc])
