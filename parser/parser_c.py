# coding: utf-8
import sys
import string
from lexical_analyzer.analyse_c import AnalyseC


class ParseException(Exception):
    pass


def decorator(func):
    """使用装饰器在方法返回后进行输出
    
    Arguments:
        func {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    func_map = {
        'vn_string_op': '字符串',
        'vn_program_op': '程序',
        'vn_constant_desc_op': '常量说明',
        'vn_constant_define_op': '常量定义',
        'vn_non_sign_integer_op': '无符号整数',
        'vn_integer_op': '整数',
        'vn_declaration_head_op': '声明头部',
        'vn_var_desc_op': '变量说明',
        'vn_var_define_op': '变量定义',
        'vn_return_define_op': '有返回值函数定义',
        'vn_non_return_define_op': '无返回值函数定义',
        'vn_compound_statement_op': '复合语句',
        'vn_parameters_table_op': '参数表',
        'vn_main_func_op': '主函数',
        'vn_expression_op': '表达式',
        'vn_item_op': '项',
        'vn_factor_op': '因子',
        'vn_statement_op': '语句',
        'vn_assignment_statement_op': '赋值语句',
        'vn_conditional_statements_op': '条件语句',
        'vn_condition_op': '条件',
        'vn_loop_statement_op': '循环语句',
        'vn_step_op': '步长',
        'vn_return_call_statement_op': '有返回值函数调用语句',
        'vn_non_return_call_statement_op': '无返回值函数调用语句',
        'vn_value_parameters_table_op': '值参数表',
        'vn_statement_list_op': '语句列',
        'vn_read_statement_op': '读语句',
        'vn_write_statement_op': '写语句',
        'vn_return_statement_op': '返回语句'
    }

    def inner(*args, **kwargs):
        self = args[0]
        func_name = func.__name__
        res = func(*args, **kwargs)
        if func_name in func_map:
            line = '<%s>' % func_map[func_name]
            self.output.append(line)
            if self.debug:
                print(line)
        return res

    return inner


class WordParser:
    """
    字符在输入到语法分析器前加上了 '
    字符串在输入到语法分析器前加上了 "
    """
    def write(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for line in w.output:
                # print(line)
                f.write(line.encode('utf-8').decode('utf-8') +
                        '\n')  # 需要先编码再解码才可以正常输出

    def set_pairs(self, pair: list):
        self._pairs = pair

    def __init__(self, debug):
        self._p = 0  # 当前分析文件的行数
        self._pairs = []  # 分析道第几句文件
        self.output = []
        self.void_identifier = set()
        self.debug = debug

    def get_pair(self):
        return self._pairs[self._p]

    def get_sym(self):
        return self._pairs[self._p][1]

    def get_next_sym(self):
        return self._pairs[self._p + 1][1]

    def get_next_pair(self):
        return self._pairs[self._p + 1]

    def get_offset_pair(self, offset):
        return self._pairs[self._p + offset]

    def get_offset_sym(self, offset):
        return self._pairs[self._p + offset][1]

    def error(self):
        raise ParseException()

    def advance(self):
        pair = self.get_pair()
        if pair[0] in ['CHARCON', 'STRCON']:
            pair[1] = pair[1][1:-1]
        line = ' '.join(pair)
        self.output.append(line)
        if self.debug:
            print(line)
        self._p += 1

    def back(self):
        self.output.pop()
        self._p -= 1

    def go(self, s):
        """支持传入字符串或者可迭代对象

        Arguments:
            s {[str|iterable]} -- [description]
        """
        if isinstance(s, str):
            if self.get_sym() == s:
                self.advance()
            else:
                self.error()
        else:
            if self.get_sym() in s:
                self.advance()
            else:
                self.error()

    def can_go(self, s, sym=None) -> bool:
        """支持传入字符串或者可迭代对象

        Arguments:
            s {[str|iterable]} -- [description]
        """
        if sym is None:
            sym = self.get_sym()
        if isinstance(s, str):
            if sym == s:
                return True
            else:
                return False
        else:
            if sym in s:
                return True
            else:
                return False

    def is_add_op(self, sym=None) -> bool:
        return self.can_go(['-', '+'], sym=sym)

    def is_multi_op(self, sym=None) -> bool:
        return self.can_go(['*', '/'], sym=sym)

    def is_relation_op(self, sym=None):
        return self.can_go(['<', '<=', '>', '>=', '!=', '=='], sym)

    def is_letter_op(self, sym=None) -> bool:
        return self.can_go([
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '_'
        ],
                           sym=sym)

    def is_digit_op(self, sym=None) -> bool:
        if self.can_go('0', sym):
            return True
        return self.is_no_zero_digit_op(sym)

    def is_no_zero_digit_op(self, sym=None) -> bool:
        """
        是否是非零数字
        :return:
        """
        return self.can_go(['1', '2', '3', '4', '5', '6', '7', '8', '9'],
                           sym=sym)

    def is_character_op(self, sym=None) -> bool:
        if sym is None:
            sym = self.get_sym()
        if sym.startswith('\'') and sym.endswith('\''):
            inner_sym = sym[1:-1]
            if self.is_add_op(inner_sym) or self.is_multi_op(
                    inner_sym) or self.is_letter_op(
                        inner_sym) or self.is_digit_op(inner_sym):
                return True
            else:
                return False
        else:
            return False

    def is_string_op(self, sym=None):
        if sym is None:
            sym = self.get_sym()
        if sym.startswith('"') and sym.endswith('"'):
            inner_sym = sym[1:-1]
            for s in inner_sym:
                if ord(s) not in [32, 33] + list(range(35, 127)):
                    return False
            return True
        else:
            return False

    def is_identifier_op(self, sym=None):
        if sym is None:
            sym = self.get_sym()
        assert len(sym) >= 1
        if self.is_letter_op(sym[0]):
            for s in sym[1:]:
                if not (self.is_letter_op(s) or self.is_digit_op(s)):
                    return False
            # 扫描成功
            return True
        else:
            return False

    def is_type_identifier_op(self, sym=None):
        if sym is None:
            sym = self.get_sym()
        return self.can_go('int', sym) or self.can_go('char', sym)

    def vn_add_op(self):
        """
        加法运算符
        :return:
        """
        if self.is_add_op():
            self.advance()
        else:
            self.error()

    def vn_multi_op(self):
        """
        乘法运算符
        :return:
        """
        if self.is_multi_op():
            self.advance()
        else:
            self.error()

    def vn_relation_op(self):
        """
        关系运算符
        :return:
        """
        if self.is_relation_op():
            self.advance()
        else:
            self.error()

    def vn_letter_op(self):
        """
        字母
        :return:
        """
        if self.is_letter_op():
            self.advance()
        else:
            self.error()

    def vn_digit_op(self):
        if self.is_digit_op():
            self.advance()
        else:
            self.error()

    def vn_non_zero_digit_op(self):
        if self.is_no_zero_digit_op():
            self.advance()
        else:
            self.error()

    def vn_character_op(self):
        sym = self.get_sym()
        if sym.startswith('\'') and sym.endswith('\''):
            inner_sym = sym[1:-1]
            if self.is_add_op(inner_sym) or self.is_multi_op(
                    inner_sym) or self.is_letter_op(
                        inner_sym) or self.is_digit_op(inner_sym):
                self.advance()
            else:
                self.error()
        else:
            self.error()

    @decorator
    def vn_string_op(self):
        """
        字符串
        :return:
        """
        if self.is_string_op():
            self.advance()
        else:
            self.error()

    @decorator
    def vn_program_op(self):
        """
        程序
        :return:
        """
        if self.get_sym() == 'const':
            # 常量说明
            self.vn_constant_desc_op()
        if self.get_sym() in ['char', 'int'] and \
                self.is_identifier_op(self.get_next_sym()) and \
                self.get_offset_sym(2) != '(':
            # 变量说明
            self.vn_var_desc_op()
        while True:
            if self.get_sym() == 'void':
                if self.get_next_pair()[0] != 'MAINTK':
                    self.vn_non_return_define_op()
                else:
                    break
            else:
                self.vn_return_define_op()
        self.vn_main_func_op()

    @decorator
    def vn_constant_desc_op(self):
        """
        常量说明
        :return:
        """
        if self.can_go('const'):
            self.go('const')
            self.vn_constant_define_op()
            self.go(';')
            while self.can_go('const'):
                self.go('const')
                self.vn_constant_define_op()
                self.go(';')
        else:
            self.error()

    @decorator
    def vn_constant_define_op(self):
        """
        常量定义
        :return:
        """
        if self.can_go('int'):
            self.go('int')
            self.vn_identifier_op()
            self.go('=')
            self.vn_integer_op()
            while self.can_go(','):
                self.go(',')
                self.vn_identifier_op()
                self.go('=')
                self.vn_integer_op()
        elif self.can_go('char'):
            self.go('char')
            self.vn_identifier_op()
            self.go('=')
            self.vn_character_op()
            while self.can_go(','):
                self.go(',')
                self.vn_identifier_op()
                self.go('=')
                self.vn_character_op()
        else:
            self.error()

    @decorator
    def vn_non_sign_integer_op(self):
        """
        无符号整数
        :return:
        """
        sym = self.get_sym()
        if self.can_go('0', sym):
            self.go('0')
        elif self.is_no_zero_digit_op(sym[0]):
            for s in sym[1:]:
                if not self.is_digit_op(s):
                    self.error()
            # 成功扫描
            self.advance()
        else:
            self.error()

    @decorator
    def vn_integer_op(self):
        """
        整数
        :return:
        """
        if self.can_go(['+', '-']):
            self.advance()
        self.vn_non_sign_integer_op()

    def vn_identifier_op(self):
        """
        标识符  ->  不需要输出，所以不用加装饰器
        :return:
        """
        if self.is_identifier_op():
            self.advance()
        else:
            self.error()

    @decorator
    def vn_declaration_head_op(self):
        """
        声明头部
        :return:
        """
        if self.can_go('char'):
            self.go('char')
            self.vn_identifier_op()
        elif self.can_go('int'):
            self.go('int')
            self.vn_identifier_op()
        else:
            self.error()

    @decorator
    def vn_var_desc_op(self):
        """
        变量说明
        :return:
        """
        self.vn_var_define_op()
        self.go(';')
        # 判断当前单词是否属于＜变量定义＞的FIRST集合，如果属于则执行while循环，否则不执行。执行循环的时候不需要前进
        while self.is_type_identifier_op() and self.is_identifier_op(
        ) and not self.can_go('(', self.get_offset_sym(2)):
            self.vn_var_define_op()
            self.go(';')

    @decorator
    def vn_var_define_op(self):
        """
        变量定义
        :return:
        """
        self.vn_type_identifier_op()
        self.vn_identifier_op()
        if self.can_go('['):
            self.go('[')
            self.vn_non_sign_integer_op()
            self.go(']')
        else:
            # 只识别一个标识符
            pass
        while self.can_go(','):
            self.go(',')
            self.vn_identifier_op()
            if self.can_go('['):
                self.go('[')
                self.vn_non_sign_integer_op()
                self.go(']')
            else:
                # 只识别一个标识符
                pass

    def vn_type_identifier_op(self):
        """
        类型标识符  ->  不需要输出
        :return:
        """
        if self.is_type_identifier_op():
            self.advance()
        else:
            self.error()

    @decorator
    def vn_return_define_op(self):
        """
        有返回值的函数定义
        :return:
        """
        self.vn_declaration_head_op()
        self.go('(')
        self.vn_parameters_table_op()
        self.go(')')
        self.go('{')
        self.vn_compound_statement_op()
        self.go('}')

    @decorator
    def vn_non_return_define_op(self):
        """
        无返回值函数定义
        :return:
        """
        self.go('void')
        self.void_identifier.add(self.get_sym())
        self.vn_identifier_op()
        self.go('(')
        self.vn_parameters_table_op()
        self.go(')')
        self.go('{')
        self.vn_compound_statement_op()
        self.go('}')

    @decorator
    def vn_compound_statement_op(self):
        """
        复合语句
        :return:
        """
        if self.can_go('const'):
            self.vn_constant_desc_op()
        # 首先当前字符是一个类型标识符，且后一个字符是一个标识符
        if self.is_type_identifier_op() and self.is_identifier_op(
                self.get_next_sym()):
            self.vn_var_desc_op()
        self.vn_statement_list_op()

    @decorator
    def vn_parameters_table_op(self):
        """
        参数表
        :return:
        """
        if self.get_sym() == ')':
            # 识别 <空>
            pass
        else:
            self.vn_type_identifier_op()
            self.vn_identifier_op()
            while self.can_go(','):
                self.go(',')
                self.vn_type_identifier_op()
                self.vn_identifier_op()

    @decorator
    def vn_main_func_op(self):
        """
        主函数
        :return:
        """
        self.go('void')
        self.go('main')
        self.go('(')
        self.go(')')
        self.go('{')
        self.vn_compound_statement_op()
        self.go('}')

    @decorator
    def vn_expression_op(self):
        """
        表达式
        :return:
        """
        if self.can_go(['+', '-']):
            self.advance()
        self.vn_item_op()
        while self.is_add_op():
            self.vn_add_op()
            self.vn_item_op()

    @decorator
    def vn_item_op(self):
        """
        项
        :return:
        """
        self.vn_factor_op()
        while self.is_multi_op():
            self.vn_multi_op()
            self.vn_factor_op()

    @decorator
    def vn_factor_op(self):
        """
        因子
        :return:
        """
        # 是否是字符
        if self.is_character_op():
            self.vn_character_op()
        # 表达式
        elif self.can_go('('):
            self.go('(')
            self.vn_expression_op()
            self.go(')')
        # 是否是标识符
        elif self.is_identifier_op():
            if self.can_go('[', self.get_next_sym()):
                # ＜标识符＞'['＜表达式＞']'
                self.vn_identifier_op()
                self.go('[')
                self.vn_expression_op()
                self.go(']')
            elif self.can_go('(', self.get_next_sym()):
                # 有返回值的调用语句
                self.vn_return_call_statement_op()
            else:
                # 只有标识符
                self.advance()
        else:
            # 只能是整数
            self.vn_integer_op()

    @decorator
    def vn_statement_op(self):
        """
        语句
        :return:
        """
        # 条件语句
        if self.can_go('if'):
            self.vn_conditional_statements_op()
        # 循环语句
        elif self.can_go(['do', 'while', 'for']):
            self.vn_loop_statement_op()
        # 语句列
        elif self.can_go('{'):
            self.go('{')
            self.vn_statement_list_op()
            self.go('}')
        # 读语句
        elif self.can_go('scanf'):
            self.vn_read_statement_op()
            self.go(';')
        # 写语句
        elif self.can_go('printf'):
            self.vn_write_statement_op()
            self.go(';')
        # 返回语句
        elif self.can_go('return'):
            self.vn_return_statement_op()
            self.go(';')
        # 空语句
        elif self.can_go(';'):
            self.go(';')
        elif self.is_identifier_op():
            # 赋值语句
            if self.can_go(['=', '['], self.get_next_sym()):
                self.vn_assignment_statement_op()
                self.go(';')
            elif self.can_go('(', self.get_next_sym()):
                # 无返回值函数调用语句
                if self.get_sym() in self.void_identifier:
                    self.vn_non_return_call_statement_op()
                    self.go(';')
                # 有返回值函数调用语句
                else:
                    self.vn_return_call_statement_op()
                    self.go(';')
            else:
                self.error()
        else:
            self.error()

    @decorator
    def vn_assignment_statement_op(self):
        """
        赋值语句
        :return:
        """
        self.vn_identifier_op()
        if self.can_go('='):
            self.go('=')
            self.vn_expression_op()
        elif self.can_go('['):
            self.go('[')
            self.vn_expression_op()
            self.go(']')
            self.go('=')
            self.vn_expression_op()
        else:
            self.error()

    @decorator
    def vn_conditional_statements_op(self):
        """
        条件语句
        :return:
        """
        self.go('if')
        self.go('(')
        self.vn_condition_op()
        self.go(')')
        self.vn_statement_op()
        if self.can_go('else'):
            self.go('else')
            self.vn_statement_op()
        else:
            pass

    @decorator
    def vn_condition_op(self):
        """
        条件
        :return:
        """
        self.vn_expression_op()
        if self.is_relation_op():
            self.vn_relation_op()
            self.vn_expression_op()

    @decorator
    def vn_loop_statement_op(self):
        """
        循环语句
        :return:
        """
        if self.can_go('while'):
            self.go('while')
            self.go('(')
            self.vn_condition_op()
            self.go(')')
            self.vn_statement_op()
        elif self.can_go('do'):
            self.go('do')
            self.vn_statement_op()
            self.go('while')
            self.go('(')
            self.vn_condition_op()
            self.go(')')
        elif self.can_go('for'):
            self.go('for')
            self.go('(')
            # TODO 需要确认是否允许for(int i =0;;)这样的句型
            if self.is_type_identifier_op():
                self.vn_identifier_op()
            self.vn_identifier_op()
            self.go('=')
            self.vn_expression_op()
            self.go(';')
            self.vn_condition_op()
            self.go(';')
            self.vn_identifier_op()
            self.go('=')
            self.vn_identifier_op()
            if self.can_go(['+', '-']):
                self.advance()
            else:
                self.error()
            self.vn_step_op()
            self.go(')')
            self.vn_statement_op()
        else:
            self.error()

    @decorator
    def vn_step_op(self):
        """
        步长
        :return:
        """
        self.vn_non_sign_integer_op()

    @decorator
    def vn_return_call_statement_op(self):
        """
        有返回值函数调用语句
        :return:
        """
        self.vn_identifier_op()
        self.go('(')
        self.vn_value_parameters_table_op()
        self.go(')')

    @decorator
    def vn_non_return_call_statement_op(self):
        """
        无返回值函数调用语句
        :return:
        """
        self.vn_identifier_op()
        self.go('(')
        self.vn_value_parameters_table_op()
        self.go(')')

    @decorator
    def vn_value_parameters_table_op(self):
        """
        值参数表
        :return:
        """
        # FELLOW 集合
        if self.get_sym() == ')':
            pass
        else:
            self.vn_expression_op()
            while self.can_go(','):
                self.go(',')
                self.vn_expression_op()

    @decorator
    def vn_statement_list_op(self):
        """
        语句列
        :return:
        """
        while True:
            self.vn_statement_op()
            if self.can_go('}'):
                break

    @decorator
    def vn_read_statement_op(self):
        """
        读语句
        :return:
        """
        if self.can_go('scanf'):
            self.go('scanf')
            self.go('(')
            self.vn_identifier_op()
            while self.can_go(','):
                self.go(',')
                self.vn_identifier_op()
            self.go(')')
        else:
            self.error()

    @decorator
    def vn_write_statement_op(self):
        """
        写语句
        :return:
        """
        if self.can_go('printf'):
            self.go('printf')
            self.go('(')
            if self.is_string_op():
                self.vn_string_op()
                if self.can_go(','):
                    self.go(',')
                    self.vn_expression_op()
                else:
                    pass
            else:
                self.vn_expression_op()
            self.go(')')

    @decorator
    def vn_return_statement_op(self):
        """
        返回语句
        :return:
        """
        self.go('return')
        if self.can_go('('):
            self.go('(')
            self.vn_expression_op()
            self.go(')')

    def start_from_file(self, filename):
        self.init(file_name=filename)
        self.vn_program_op()

    def start(self):
        self.vn_program_op()

    def init(self, file_name: str) -> None:
        f = open(file_name, 'r')
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            self._pairs.append(line.split(' '))
        f.close()
        # print('加载语法分析生成文件成功！')


if __name__ == '__main__':
    analyse_c = AnalyseC()
    analyse_c.load_content('parser/testfile.txt', encoding='utf-8')
    analyse_c.analyse()
    w = WordParser(debug=False)

    res = []
    for r in analyse_c.result:
        r = list(r)
        if r[0] == 'CHARCON':
            r[1] = '\'' + r[1] + '\''
        elif r[0] == 'STRCON':
            r[1] = '"' + r[1] + '"'
        res.append(r)

    w.set_pairs(res)
    w.start()
    w.write('parser/output.txt')
