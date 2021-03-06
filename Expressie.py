import math
import bisection

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces


def tokenize(string, oplist, funclist):
    splitchars = list("+-*/(),")

# surround any splitchar by spaces
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)

    tokenstring = ''.join(tokenstring)

# split on spaces - this gives us our tokens
    tokens = tokenstring.split()

    if tokens[0] == '-':
        tokens[0] = '~'

    for i in range(len(tokens)):
        if tokens[i] == '-' and \
          (tokens[i-1] in oplist or tokens[i-1] in list('()') or
                tokens[i-1] in funclist):
                tokens[i] = '~'

# special casing for **:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans

# special casting for negative numbers (so, numbers starting with -):


def post_tokenize(tokens, funclist, oplist):
    i = 0
    for token in tokens:
        while type(token) == str and len(token) != 1 \
              and token not in oplist and not isnumber(token):
            plaats = infunclist(token, funclist)

            if type(plaats) == list and not type(plaats) == bool:
                if plaats[1] == 0:
                    break
                function_in_token = plaats[0]
                index_from_function = int(plaats[1])

                tokens[i] = token[0:index_from_function]
                tokens.insert(i+1, '*')
                tokens.insert(i+2, function_in_token)
                token = tokens[i]

            else:
                tokens.insert(i+1, '*')
                tokens.insert(i+2, token[-1])
                tokens[i] = token[0:-1]
                token = tokens[i]

# if i= 0, then [i-1] will be the last element of the list, but we want
# subsequent characters. we also do not want * between two ')'
# or between )'and an operator

        if i != 0 and tokens[i-1] == ')' and tokens[i] != ')' and \
           (token in funclist or (len(token) == 1 and type(token) == str)) \
           and token not in oplist:
            tokens.insert(i, '*')

        i += 1
    return tokens


# check if a string represents a numeric value


def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# check if a string represents an integer value


def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

# check if a string represents a variable


def isvariable(string):
    try:
        if len(string) == 1:
            if 97 <= ord(string) and ord(string) <= 123:
                return True
    except ValueError:
        return False

# we sort the funclist and reverse it so that when two functions are partially
# the same from the start, the longest of the two is checked first
# i.e. cosh is checked before cos


def infunclist(string, funclist):
    funclist.sort()
    funclist.reverse()
    for func in funclist:
        if func in string:
            return [func, string.index(func)]
    return False


# making a difference between precedence add/sub, mul/div, pow
# Needed for translating to RPN
# Needed for minimal use of brackets when printing our final expression


def precedence(token):
    if token == '+' or token == '-':
        return(1)
    elif token == '*' or token == '/':
        return(2)
    elif token == '**':
        return(3)
    else:
        return(4)

# checking wether a token is associative or not
# Needed for mininmal use of brackets when printing our final expression


def associativity(token):
    if token == '+' or token == '*':
        return(1)
    if token == '-' or token == '/':
        return(0)


class Expression():
    """A mathematical expression, represented as an expression tree"""
# operator overloading:
# this allows us to perform 'arithmetic' with expressions
# and obtain another expression

    def __add__(self, other):
            return AddNode(self, other)

    def __sub__(self, other):
        return SubstractNode(self, other)

    def __mul__(self, other):
        return MultiplyNode(self, other)

    def __truediv__(self, other):
        return DivideNode(self, other)

    def __pow__(self, other):
        return PowerNode(self, other)

    def abridge(self):
        return self


# basic Shunting-yard algorithm

    def fromString(string):

        # list of operators
        oplist = ['+', '-', '*', '/', '**']

# list of functions
        funclist = ['cos', 'sin', 'tan', 'log', 'sinh', 'cosh', 'tanh', '~']

# split into tokens
        tokens = tokenize(string, oplist, funclist)

# stack used by the Shunting-Yard algorithm
        stack = []
# output of the algorithm: a list representing the formula in RPN
# this will contain Constant's and '+'s
        output = []

        tokens = post_tokenize(tokens, funclist, oplist)

        for token in tokens:
            if isnumber(token):

                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))

            elif isvariable(token):
                output.append(Variable(str(token)))

            elif token in oplist or token in funclist:

                # pop operators from the stack to the output until the top
                # is no longer an operator
                while True:
                    if len(stack) == 0 or \
                       (stack[-1] not in oplist and stack[-1] not in funclist)\
                       or int(precedence(token)) >= int(precedence(stack[-1])):
                        break
                    output.append(stack.pop())
# push the new operator onto the stack
                stack.append(token)

            elif token == '(':
                # left parantheses go to the stack
                stack.append(token)

            elif token == ')':
                # right paranthesis: pop everything upto the last left
                # paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
# pop the left paranthesis from the stack (but not to the output)
                stack.pop()
# a ')' will look for a '(' and cancel both, if a function is priliminary to
# those () the function is moved to the output, otherwise operators and
# function will be wrongly placed to the output
# eg. sin(x) + 1 wil be evaluated as sin(x+1)
                if len(stack) > 0 and stack[-1] in funclist:
                    output.append(stack.pop())
            elif token in funclist:
                # functions will be located to the stack (under restrictions)
                while True:
                    if len(stack) == 0 or stack[-1] not in funclist:
                        break
                    output.append(stack.pop())
                stack.append(token)

            else:
                # unknown token
                raise ValueError('Unknown token: %s' % token)


# pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())


# convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring
                # out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
# translocate function from the output to the stack with use of the class of
# the function to ascribe the input to the mathematical function
            elif t in funclist:
                z = stack.pop()
                if t == 'sin':
                    stack.append(sinNode(z))
                elif t == 'cos':
                    stack.append(cosNode(z))
                elif t == 'tan':
                    stack.append(tanNode(z))
                elif t == 'log':
                    stack.append(logNode(z))
                elif t == 'sinh':
                    stack.append(sinhNode(z))
                elif t == 'cosh':
                    stack.append(coshNode(z))
                elif t == 'tanh':
                    stack.append(tanhNode(z))
                elif t == '~':
                    stack.append(negativeNode(z))
            else:
                # a constant, push it to the stack
                stack.append(t)
# the resulting expression tree is what's left on the stack
        return stack[0]


# We use a pass because the expression is evaluated in the subclasses
# of expression, where we override this method
    def evaluate(self, expression_to_evaluate=dict()):
        pass

    def findRoots(self, variable_to_evaluate, a, b, epsilon):
        return bisection.findAllRoots(str(self), variable_to_evaluate,
                                      a, b, epsilon)


class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False

    def __str__(self):
        return str(self.value)

# allow conversion to numerical values
    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

# evaluates the Constant, i.e. returns the Constant as a float
    def evaluate(self, expression_to_evaluate=dict()):
        return float(self)


class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""

    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol

    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False


# We want to simplify our Expression tree, such that evaluating is extra easy
# We want a tree that has the operators of highest precedence at the bottom
# and operators of lower precedence above
    def simplify(self):

        # first we simplify the left hand side of the tree
        def simplify_left(self):
            left = self.lhs
            operator = self.op_symbol
# when we are dealing with a subtree in the left node
            if isinstance(left, BinaryNode):
                # we only want to simplify the expression when the operator
                # above is of higher precedence than the operator below
                if precedence(operator) == precedence(left.op_symbol) + 1:
                    left_side = BinaryNode(left.lhs, self.rhs, self.op_symbol)
                    right_side = BinaryNode(left.rhs, self.rhs, self.op_symbol)
                    new_operator = left.op_symbol
                    # We have to simplify our outcome again
                    # until everything issimplified
                    return BinaryNode(left_side.simplify(),
                                      right_side.simplify(), new_operator)
                else:
                    return self
            else:
                return self

# now we simplify the right hand side. The method is similar
        def simplify_right(self):
            right = self.rhs
            operator = self.op_symbol
            if isinstance(right, BinaryNode):
                if precedence(operator) == precedence(right.op_symbol) + 1:
                    left_side = BinaryNode(self.lhs, right.lhs, self.op_symbol)
                    right_side = BinaryNode(self.lhs, right.rhs,
                                            self.op_symbol)
                    new_operator = right.op_symbol
                    return BinaryNode(left_side.simplify(),
                                      right_side.simplify(), new_operator)
                else:
                    return self
            else:
                return self

    def __str__(self):
        """Printing our final expression while determining when
    we need brackets"""

        def left_result(self):
            # Do we need brackets on the left hand side?
            lstring = str(self.lhs)
            left_res = ''

            if isinstance(self.lhs, BinaryNode):
                # Defining when the precedence of operators tells us
                # to use brackets on the left hand side
                left_prec = (precedence(self.lhs.op_symbol) <
                             precedence(self.op_symbol))
                if left_prec:
                    left_res += "(%s) %s" % (lstring, self.op_symbol)
                else:
                    left_res += "%s %s" % (lstring, self.op_symbol)
            else:
                left_res += "%s %s" % (lstring, self.op_symbol)

            return left_res

        def right_result(self):
            # Do we need brackets on the right hand side?
            rstring = str(self.rhs)
            right_res = ''

            if isinstance(self.rhs, BinaryNode):
                # Defining when the precedence of operators tells us
                # to use brackets on the right hand side
                right_prec = (precedence(self.rhs.op_symbol) <
                              precedence(self.op_symbol))
                # Defining when the associativity of operators tells us
                # to use brackets on the right hand side
                right_ass = (precedence(self.rhs.op_symbol) ==
                             precedence(self.op_symbol) and
                             associativity(self.rhs.op_symbol) >
                             associativity(self.op_symbol))

                if right_prec or right_ass:
                    right_res += " (%s)" % (rstring)
                else:
                    right_res += " %s" % (rstring)
            else:
                right_res += " %s" % (rstring)

            return right_res

# And now the total result
        return str(left_result(self))+str(right_result(self))

# A BinaryNode always has a lhs and a rhs which needs to be evaluated
# this method evaluates the lhs and rhs recursively untill it reaches
# a function which can be evaluated. I.e. untill it has reaches a leaf.

    def evaluate(self, expression_to_evaluate=dict()):
        operator = self.op_symbol
        f = self.lhs.evaluate(expression_to_evaluate)
        g = self.rhs.evaluate(expression_to_evaluate)


# If no value is given for a Variable, we want to return it as a Variable
# hence we have to distinguish if lhs or rhs is still a variable
        if type(f) == str:
            expr = f + ' ' + str(operator) + ' ' + str(g)
            return expr

        if type(g) == str:
            expr = str(f) + ' ' + str(operator) + ' ' + g
            return expr

        else:
            return eval(str(f) + operator + str(g))

# class for notBinaryNodes in the expressiontree (i.e. functions with input)


class UnaryNode(Expression):
    "Nodes with one incoming edge"

# only one incoming node (function input)
    def __init__(self, node, function):
        self.node = node
        self.function = function

# same def as in BinaryNode to control if two trees are the same
    def __eq__(self, other):
        if type(self) == type(other):
            return self.node == other.node
        else:
            return False

# returns a function f with input x as f(x)
    def __str__(self):
        return self.function + '(' + str(self.node) + ')'

    def evaluate(self, expression_to_evaluate=dict()):
        fun = self.function
        h = self.node.evaluate(expression_to_evaluate)

# If no value is given for a Variable, we want to return it as a Variable
# hence we have to distinguish if node is still a variable
        if type(h) == str:
            expr = fun + '(' + h + ')'
            return expr
        else:
            return eval('math.' + fun + '(' + str(h) + ')')


class Variable(Constant):
    """Represents a variable"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

# If there is a value given for the Variable when evaluating, this method
# returns the evaluated value of the Variable. If no value is given for
# the Variable, the method returns the Variable itself.
    def evaluate(self, expression_to_evaluate=dict()):
        if self.value in expression_to_evaluate:
            return expression_to_evaluate[self.value]
        else:
            return self.value


class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

    def abridge(self):
        # We overwrite abridge such that c+0=c and 0+c=c for all
        # Constants&Variables c. We also calculate the sum of two Constants
        lhs = self.lhs.abridge()
        rhs = self.rhs.abridge()
        if lhs == Constant(0):
            return rhs
        elif rhs == Constant(0):
            return lhs
        elif type(lhs) == Constant and type(rhs) == Constant:
            return Constant(eval(str(lhs+rhs)))
        else:
            return AddNode(lhs, rhs)


class SubstractNode(BinaryNode):
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs):
        super(SubstractNode, self).__init__(lhs, rhs, '-')

    def abridge(self):
        # We overwrite abridge s.t. c-0=c and 0-c=-c for all Constants and
        # Variables c We also Calculate the difference between two Constants
        lhs = self.lhs.abridge()
        rhs = self.rhs.abridge()
        if lhs == Constant(0):
            return -rhs
        elif rhs == Constant(0):
            return lhs
        elif type(lhs) == Constant and type(rhs) == Constant:
            return Constant(eval(str(lhs - rhs)))
        else:
            return SubstractNode(lhs, rhs)


class MultiplyNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MultiplyNode, self).__init__(lhs, rhs, '*')

    def abridge(self):
        # We overwrite abridge such that c*0=0*c=0 and c*1=1*c=c and
        # c*-1=-1*c=-c for all Constants and Variables c
        # We also calculate the multiplication of two Constants
        lhs = self.lhs.abridge()
        rhs = self.rhs.abridge()
        if lhs == Constant(0) or rhs == Constant(0):
            return(Constant(0))
        elif lhs == Constant(1):
            return rhs
        elif rhs == Constant(1):
            return lhs
        elif lhs == Constant(-1):
            return -rhs
        elif rhs == Constant(-1):
            return -lhs
        elif type(lhs) == Constant and type(rhs) == Constant:
            return Constant(eval(str(lhs*rhs)))
        else:
            return MultiplyNode(lhs, rhs)


class DivideNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivideNode, self).__init__(lhs, rhs, '/')

    def abridge(self):
        # We overwrite abridge such that c/0='Error' and 0/c=0 and
        # c/1=c for all Constants and Variables c. We do not calculate here
        # we think it is nicer to show fractions than to show floats
        lhs = self.lhs.abridge()
        rhs = self.rhs.abridge()
        if lhs == Constant(0):
            return Constant(0)
        elif rhs == Constant(0):
            return('Delen door nul is flauwekul!')
        elif rhs == Constant(1):
            return lhs
        else:
            return DivideNode(self, rhs)


class PowerNode(BinaryNode):
    """Represents the power operator"""
    def __init__(self, lhs, rhs):
        super(PowerNode, self).__init__(lhs, rhs, '**')

    def abridge(self):
        # We overwrite abridge such that c**0=1, c**1=c, 0**c=0 and 1**c=1
        # for all Constants and Variables c. We calculate the power of
        # two Constants
        lhs = self.lhs.abridge()
        rhs = self.rhs.abridge()
        if lhs == Constant(0):
            return Constant(0)
        elif lhs == Constant(1):
            return Constant(1)
        elif rhs == Constant(0):
            return Constant(1)
        elif rhs == Constant(1):
            return lhs
        elif type(lhs) == Constant and type(rhs) == Constant:
            return Constant(eval(str(lhs**rhs)))
        else:
            return PowerNode(lhs, rhs)


class sinNode(UnaryNode):
    """Represents the math.sin function"""
    def __init__(self, node):
        super(sinNode, self).__init__(node, 'sin')


class cosNode(UnaryNode):
    """Represents the math.cos function"""
    def __init__(self, node):
        super(cosNode, self).__init__(node, 'cos')


class tanNode(UnaryNode):
    """Represents the math.tan function"""
    def __init__(self, node):
        super(tanNode, self).__init__(node, 'tan')


class logNode(UnaryNode):
    """Represents the math.log function"""
    def __init__(self, node):
        super(logNode, self).__init__(node, 'log')


class sinhNode(UnaryNode):
    """Represents the math.sinh function"""
    def __init__(self, node):
        super(sinhNode, self).__init__(node, 'sinh')


class coshNode(UnaryNode):
    """Represents the math.cosh function"""
    def __init__(self, node):
        super(coshNode, self).__init__(node, 'cosh')


class tanhNode(UnaryNode):
    """Represents the math.tanh function"""
    def __init__(self, node):
        super(tanhNode, self).__init__(node, 'tanh')


class negativeNode(UnaryNode):
    """Represents a *(-1) function"""
    def __init__(self, node):
        super(negativeNode, self).__init__(node, '-')

    def evaluate(self, dictionary=dict()):
        if type(self.node) == str:
            print('-' + self.node)
        else:
            return eval('-' + str(self.node.evaluate(dictionary)))

    def __str__(self):
        return '-' + str(self.node)
