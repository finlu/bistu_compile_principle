from tkinter.filedialog import LoadFileDialog
from tkinter import *
from tkinter import messagebox

KEY_TABLE = {
    'const': 'CONSTTK',
    'int': 'INTTK',
    'char': 'CHARTK',
    'void': 'VOIDTK',
    'main': 'MAINTK',
    'if': 'IFTK',
    'else': 'ELSETK',
    'do': 'DOTK',
    'while': 'WHILETK',
    'for': 'FORTK',
    'scanf': 'SCANFTK',
    'printf': 'PRINTFTK',
    'return': 'RETURNTK',
}

SINGLE_TABLE = {
    '+': 'PLUS',
    '-': 'MINU',
    '*': 'MULT',
    '/': 'DIV',
    ';': 'SEMICN',
    ',': 'COMMA',
    '(': 'LPARENT',
    ')': 'RPARENT',
    '[': 'LBRACK',
    ']': 'RBRACK',
    '{': 'LBRACE',
    '}': 'RBRACE',
}

SINGLE_TO_DOUBLE_TABLE = {
    '<': 'LSS',
    '>': 'GRE',
    '=': 'ASSIGN',
}

DOUBLE_TABLE = {
    '<=': 'LEQ',
    '>=': 'GEQ',
    '==': 'EQL',
    '!=': 'NEQ',
}


class AnalyseC:
    """
    C语言分析器的python实现
    """
    def __init__(self):
        self.__content = None
        self.__index = -1
        self.result = []

    def load_content(self, filename, encoding=None):
        """
        读取文件中的内容
        :param filename:
        :param encoding:
        :return:
        """
        f = open(filename, encoding=encoding)
        self.__content = f.read()
        f.close()
        return self.__content

    def remove_comment(self):
        pass

    def preform_analyse(self):
        """
        词法分析前的预处理工作
        :return:
        """
        self.remove_comment()

    def get_current_char(self):
        return self.__content[self.__index]

    def get_next_char(self):
        if self.has_char():
            self.__index += 1
            return self.__content[self.__index]
        return ''

    def see_next_char(self):
        if self.has_char():
            return self.__content[self.__index + 1]
        return ''

    def has_char(self):
        return self.__index < len(self.__content) - 1

    def back_char(self):
        self.__index -= 1

    def analyse(self):
        while self.has_char():
            result = self.analyse_one()
            print(result)
            if result is None:
                continue
            self.result.append(result)

    def analyse_one(self):
        value = ''
        cur_char = self.get_next_char()
        while cur_char == ' ' or cur_char == '\n':
            cur_char = self.get_next_char()
        if cur_char.isalpha() or cur_char == '_':
            while cur_char.isalpha() or cur_char.isalnum() or cur_char == '_':
                value += cur_char
                cur_char = self.get_next_char()
            self.back_char()
            # 此时value已经是一个单词了，需要检查合法性
            if value in KEY_TABLE.keys():
                return KEY_TABLE[value], value
            else:
                return 'IDENFR', value
        elif cur_char.isalnum():
            while cur_char.isalnum():
                value += cur_char
                cur_char = self.get_next_char()
            self.back_char()
            return 'INTCON', value
        elif cur_char in SINGLE_TABLE.keys():
            value += cur_char
            return SINGLE_TABLE[value], value
        elif cur_char in SINGLE_TO_DOUBLE_TABLE.keys() or cur_char == '!':
            next_char = self.see_next_char()
            if cur_char + next_char in DOUBLE_TABLE.keys():
                value += cur_char + next_char
                self.get_next_char()
                return DOUBLE_TABLE[value], value
            else:
                value += cur_char
                self.get_next_char()
                return SINGLE_TO_DOUBLE_TABLE[value], value
        elif cur_char == '\'':
            cur_char = self.get_next_char()
            while cur_char != '\'':
                value += cur_char
                cur_char = self.get_next_char()
            return 'CHARCON', value
        elif cur_char == '\"':
            cur_char = self.get_next_char()
            while cur_char != '\"':
                value += cur_char
                cur_char = self.get_next_char()
            return 'STRCON', value

    def print_result(self):
        for r in self.result:
            print('{} {}'.format(r[0], r[1]))

    def write_result(self, filename):
        f = open(filename, 'w')
        for r in self.result:
            f.write('{} {}\n'.format(r[0], r[1]))
        f.close()

    def get_content(self):
        return self.__content


def simple():
    analyse_c = AnalyseC()
    analyse_c.load_content('parser/lexical_analyzer/testfile.txt',
                           encoding='utf-8')
    analyse_c.analyse()
    analyse_c.write_result('parser/lexical_analyzer/output.txt')


def tk():
    def fileloader():
        nonlocal root
        code.delete(1.0, END)
        fd = LoadFileDialog(root)
        filename = fd.go()
        nonlocal analyse_c
        code.insert(1.0, analyse_c.load_content(filename, encoding='utf-8'))

    def apply_analyse():
        if analyse_c.get_content() is None:
            messagebox.showerror('错误', '请先加载代码')
            return
        try:
            analyse_c.analyse()
            value = ''
            for a, b in analyse_c.result:
                value += a + ' ' + b + '\n'
            analysis.insert(1.0, value)
        except Exception as e:
            messagebox.showerror('错误', str(e))

    analyse_c = AnalyseC()
    root = Tk()
    code = Text(root, width=60, height=20, font=15)
    analysis = Text(root, width=60, height=20, font=15)

    t = StringVar()
    t.set('基于Python的C语言词法分析器')
    label = Label(root, textvariable=t, font=15)
    Analysis = Button(root, text='词法分析', command=apply_analyse, font=15)
    load = Button(root, text='载入代码', command=fileloader, font=15)
    root.title("词法分析器")
    label.pack(side=TOP)
    Analysis.pack(side=BOTTOM)
    load.pack(side=BOTTOM)
    code.pack(side=LEFT)
    analysis.pack(side=RIGHT)
    root.mainloop()


if __name__ == '__main__':
    simple()
    # tk()
