import math

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # surround any splitchar by spaces
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    
    tokenstring = ''.join(tokenstring)
    
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split()
     
    #special casing for **:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans


    
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

##check if a string represents a variable
def isvariable(string):
    try:
        if 97 <= ord(string) and ord(string) <= 123:
            return True
    except ValueError:
        return False
        
 # making a difference between add/sub and mul/div
def precedence(token):
    if token == '+' or token == '-':
        return(1)
    elif token == '*' or token == '/':
        return(2)

class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """
    # TODO: when adding new methods that should be supported by all subclasses, add them to this list
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
    
    def __sub__(self, other):
        return SubstractNode(self, other)
        
    def __mul__(self, other):
        return MultiplyNode(self,other)
    
    def __truediv__(self, other):
        return DivideNode(self, other)
    
    
    # basic Shunting-yard algorithm
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and '+'s
        output = []
        
        # list of operators
        oplist = ['+','-','*','/']
        
       
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
            elif isvariable(token):
                output.append(Variable(str(token)))                
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    # TODO: when there are more operators, the rules are more complicated
                    # look up the shunting yard-algorithm
                    if len(stack) == 0 or stack[-1] not in oplist or int(precedence(token)) > int(precedence(stack[-1])):
                        break
                    output.append(stack.pop())
                # push the new operator onto the stack
                stack.append(token)
            elif token == '(':
                # left parantheses go to the stack
                stack.append(token)
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
            # TODO: do we need more kinds of tokens?
            else:
                # unknown token
                raise ValueError('Unknown token: %s' % token)
            
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]



    #We use a pass because the expression is evaluated in the subclasses
    #of expression, where we override this method
    def evaluate(self, expression_to_evaluate = dict()):
        pass


    
    
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

    #evaluates the Constant, i.e. returns the Constant as a float
    def evaluate(self, expression_to_evaluate = dict()):
        return float(self)
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        
        # TODO: do we always need parantheses?
        return "(%s %s %s)" % (lstring, self.op_symbol, rstring)

    #A BinaryNode always has a lhs and a rhs which needs to be evaluated
    #this method evaluates the lhs and rhs recursively untill it reaches
    #a function which can be evaluated. I.e. untill it has reaches a leaf.
    def evaluate(self, expression_to_evaluate = dict()):
        operator = self.op_symbol
        f = self.lhs.evaluate(expression_to_evaluate)
        g = self.rhs.evaluate(expression_to_evaluate)


        #If no value is given for a Variable, we want to return it as a Variable
        #hence we have to distinguish if lhs or rhs is still a variable
        if type(f) == str:
            expr = f +' '+ str(operator)+' '+ str(g)
            return expr
        if type(g) == str:
            expr = str(f)+ ' '+str(operator) +' '+ g
            return expr
        else:
            return eval('f' + operator + 'g')
        

class Variable(Constant):
    """represent a variable"""
    
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    #If there is a value given for the Variable when evaluating, this method
    #returns the evaluated value of the Variable. If no value is given for
    #the Variable, the method returns the Variable itself.
    def evaluate(self, expression_to_evaluate = dict()):
        if self.value in expression_to_evaluate:
            return expression_to_evaluate[self.value]
        else:
            return self.value
    
        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubstractNode(BinaryNode):
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs):
        super(SubstractNode, self).__init__(lhs, rhs, '-')
        
class MultiplyNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MultiplyNode, self).__init__(lhs, rhs, '*')

class DivideNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivideNode, self).__init__(lhs, rhs, '/')
        
# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.


