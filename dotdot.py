import json
import copy 

source = '''

x = 1
y = 5
x-y-z = 6
col-z = berry

@f{
    border: 10px solid black;
    border-radius: 50%;
}

.add{
    color:white;
    background-color: rgb(3, 4, 5);
}

#ad{
    color: rgb(x, 4, 5);
}

.a div a{
    color: ..col-z;
    @f
}
'''


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
        return self.lexemes


v = Lexer(source, KEYWORDS)
lexemes = v.get_lexemes()
# print(lexemes)
lexemes.append('') # appending an unused last element to properly dump all values

tree = {}
memory = {}

block_ongoing = False
attribute_ongoing = False
value_ongoing = False
statement_ongoing = False

id_string = ''
last_id_string = ''
last_attribute = ''

current_attribute = ''
current_value = ''

len_lexemes = len(lexemes)

for i, lex in enumerate(lexemes):

    if i+1 < len_lexemes:
        next_lexeme = lexemes[i+1]
    prev_lexeme = lexemes[i-1]

    if lex == SYM.LEFT_BRACE:
        block_ongoing = True
        attribute_ongoing = True
        continue
    elif lex == SYM.RIGHT_BRACE:
        block_ongoing = False
        statement_ongoing = False
        attribute_ongoing = False
        value_ongoing = False
        continue
    if lex == SYM.COLON:
        value_ongoing = True
        attribute_ongoing = False
        continue
    elif lex == SYM.SEMI_COLON:
        value_ongoing = False
        statement_ongoing = False
        attribute_ongoing = True
        continue

    if lex == SYM.EQUAL:
        memory[prev_lexeme] = next_lexeme
        continue
    elif next_lexeme == SYM.EQUAL or prev_lexeme == SYM.EQUAL:
        continue

    if not block_ongoing:
        id_string += lex + ' '
    elif block_ongoing:
        if id_string:
            tree[id_string.strip()] = {}
            last_id_string = id_string.strip()
            id_string = ''

    if attribute_ongoing:
        current_attribute += lex
    elif not attribute_ongoing:
        if current_attribute:
            tree[last_id_string][current_attribute] = ''
            last_attribute = current_attribute
            current_attribute = ''

    if value_ongoing:
        current_value += lex + ' '
    elif not value_ongoing:
        if current_value:
            tree[last_id_string][last_attribute] = current_value.strip()
            last_value = current_value.strip()
            current_value = ''

    #print(f'''
    #    i:{i}, lex: {lex}
    #    current_id: {id_string}, last: {last_id_string}
    #    current_attribute: {current_attribute}
    #    current_value: {current_value}''')

    
print(tree)
# print(memory)

def parseFunc(f):
    v = f.split(SYM.LEFT_ROUND)
    name = v[0]
    vals = v[1][:-1].replace(SYM.SPACE, '')
    values = vals.split(SYM.COMMA)
    for i, v in enumerate(values):
        if not v.isnumeric():
            values[i] = memory[v]
    return '{}({})'.format(name.strip(), ','.join(values))

ntree = copy.deepcopy(tree)

for block_name in ntree:
    properties = ntree[block_name]
    if block_name[0] == SYM.AT:
        continue
    for element in properties:
        value = properties[element]
        if SYM.LEFT_ROUND in value:
            tree[block_name][element] = parseFunc(value)
        if SYM.DOT in value:
            tree[block_name][element] = memory[value.strip(SYM.DOT)]
        if SYM.AT in element:
            del tree[block_name][element]
            tree[block_name].update(tree[element])


# print(parseFunc('rgb (x-y-z , 4 , 5 )'))
# print(tree)

# display
for key in tree:
    if key[0] == SYM.AT:
        continue
    print(key, '{', sep='')
    for elem in tree[key]:
        print('{}{}: {};'.format(SYM.TAB, elem, tree[key][elem]))
    print('}\n')