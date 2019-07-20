import copy 


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def read_source(path: str) -> str:
        source = ''
        with open(path, encoding='utf8') as f:
            source = f.read()
        return source



class SYM:
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    LEFT_ROUND = '('
    RIGHT_ROUND = ')'
    NEW_LINE = '\n'
    TAB = '    '
    COLON = ':'
    SEMI_COLON = ';'
    SPACE = ' '
    COMMA = ','
    EQUAL = '='
    UNION = '-'
    DOT = '.'
    AT = '@'

KEYWORDS = (SYM.LEFT_BRACE, SYM.RIGHT_BRACE, SYM.NEW_LINE, SYM.TAB, SYM.COLON, 
    SYM.SEMI_COLON, SYM.SPACE, SYM.RIGHT_ROUND, SYM.LEFT_ROUND, SYM.COMMA, SYM.EQUAL)


class Lexer:
    # https://www.pythonmembers.club/2018/05/01/building-a-lexer-in-python-tutorial/
    def __init__(self, source: str, KEYWORDS: list):
        self.white_space = SYM.SPACE
        self.KEYWORDS = KEYWORDS
        self.lexeme = ''
        self.lexemes = []
        self.string = source

    def get_lexemes(self) -> list:
        for i, char in enumerate(self.string):
            if char != self.white_space and char != SYM.NEW_LINE:
                self.lexeme += char  # adding a char each time
            if (i+1 < len(self.string)):  # prevents error
                if self.string[i+1] == self.white_space or self.string[i+1] in KEYWORDS or self.lexeme in KEYWORDS or self.string[i+1] == SYM.NEW_LINE: # if next char == ' '
                    if self.lexeme != '':
                        self.lexemes.append(self.lexeme)
                        self.lexeme = ''
        self.lexemes.append('') # appending last element to dump values well
        return self.lexemes


class Tree:
    def __init__(self, lexemes: list):
        self.tree = {}
        self.memory = {}
        self.lexemes = lexemes

        self.block_ongoing = False
        self.attribute_ongoing = False
        self.value_ongoing = False
        self.statement_ongoing = False

        self.id_string = ''
        self.last_id_string = ''
        self.last_attribute = ''

        self.current_attribute = ''
        self.current_value = ''

        self.len_lexemes = len(lexemes)

    def gen(self) -> None:
        for i, lex in enumerate(self.lexemes):
            if i+1 < self.len_lexemes:
                next_lexeme = self.lexemes[i+1]
            prev_lexeme = self.lexemes[i-1]

            if lex == SYM.LEFT_BRACE:
                self.block_ongoing = True
                self.attribute_ongoing = True
                continue
            elif lex == SYM.RIGHT_BRACE:
                self.block_ongoing = False
                self.statement_ongoing = False
                self.attribute_ongoing = False
                self.alue_ongoing = False
                continue
            if lex == SYM.COLON:
                self.value_ongoing = True
                self.attribute_ongoing = False
                continue
            elif lex == SYM.SEMI_COLON:
                self.value_ongoing = False
                self.statement_ongoing = False
                self.attribute_ongoing = True
                continue

            if lex == SYM.EQUAL:
                self.memory[prev_lexeme] = next_lexeme
                continue
            elif next_lexeme == SYM.EQUAL or prev_lexeme == SYM.EQUAL:
                continue

            if not self.block_ongoing:
                self.id_string += lex + ' '
            elif self.block_ongoing:
                if self.id_string:
                    self.tree[self.id_string.strip()] = {}
                    self.last_id_string = self.id_string.strip()
                    self.id_string = ''

            if self.attribute_ongoing:
                self.current_attribute += lex
            elif not self.attribute_ongoing:
                if self.current_attribute:
                    self.tree[self.last_id_string][self.current_attribute] = ''
                    self.last_attribute = self.current_attribute
                    self.current_attribute = ''

            if self.value_ongoing:
                self.current_value += lex + ' '
            elif not self.value_ongoing:
                if self.current_value:
                    self.tree[self.last_id_string][self.last_attribute] = self.current_value.strip()
                    self.last_value = self.current_value.strip()
                    self.current_value = ''

    def parseFunc(self, f: str) -> str:
        v = f.split(SYM.LEFT_ROUND)
        name = v[0]
        vals = v[1][:-1].replace(SYM.SPACE, '')
        values = vals.split(SYM.COMMA)
        for i, v in enumerate(values):
            if not v.isnumeric():
                values[i] = self.memory[v]
        return '{}({})'.format(name.strip(), ','.join(values))

    def parse(self) -> None:
        self.ntree = copy.deepcopy(self.tree)

        for block_name in self.ntree:
            properties = self.ntree[block_name]
            if block_name[0] == SYM.AT:
                continue
            for element in properties:
                value = properties[element]
                if SYM.LEFT_ROUND in value:
                    self.tree[block_name][element] = self.parseFunc(value)
                if SYM.DOT in value:
                    self.tree[block_name][element] = self.memory[value.strip(SYM.DOT)]
                if SYM.AT in element:
                    del self.tree[block_name][element]
                    self.tree[block_name].update(self.tree[element])

    def output(self, css_filename: str, mode="compile") -> None:
        if mode == 'compile':
            with open(css_filename, 'w+', encoding='utf8') as f:
                for key in self.tree:
                    if key[0] == SYM.AT:
                        continue
                    f.write('{}{{{}'.format(key, SYM.NEW_LINE))
                    for elem in self.tree[key]:
                        f.write('{}{}: {};{}'.format(SYM.TAB, elem, 
                            self.tree[key][elem], SYM.NEW_LINE))
                    f.write('}}{}'.format(SYM.NEW_LINE*2))


source = Utils.read_source('source.dot')
v = Lexer(source, KEYWORDS)
lexemes = v.get_lexemes()
# print(lexemes)

tree = Tree(lexemes)
tree.gen()
print(tree.tree)
tree.parse()
print(tree.tree)
tree.output('compiled.css')
