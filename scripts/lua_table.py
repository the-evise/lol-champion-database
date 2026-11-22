"""Parse data-only Lua tables; never execute downloaded Lua."""
import re, ast, operator
TOKEN = re.compile(r'\s+|--\[\[[\s\S]*?\]\]|--[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|[A-Za-z_]\w*|.', re.M)

def parse(text):
    tokens=[m.group() for m in TOKEN.finditer(text) if not m.group().isspace() and not m.group().startswith('--')]
    i=0
    if tokens[0]=='return':i=1
    def value():
        nonlocal i
        t=tokens[i];i+=1
        if t=='{':
            result={}; seq=1
            while tokens[i]!='}':
                if tokens[i]=='[':
                    i+=1;k=value();assert tokens[i]==']';i+=1;assert tokens[i]=='=';i+=1;v=value()
                elif re.match(r'^[A-Za-z_]\w*$',tokens[i]) and tokens[i+1]=='=':
                    k=tokens[i];i+=2;v=value()
                else:k=seq;seq+=1;v=value()
                result[k]=v
                if tokens[i] in (',',';'):i+=1
                else:assert tokens[i]=='}',tokens[i:i+5]
            i+=1
            if result and list(result)==list(range(1,len(result)+1)):return list(result.values())
            return result
        if t[0] in ('"',"'"):
            # Lua strings in the source use the same simple escapes as Python.
            return ast.literal_eval(t)
        if t=='true':return True
        if t=='false':return False
        if t=='nil':return None
        try:
            expression=t
            while i<len(tokens) and tokens[i] in ('+','-','*','/'):
                expression+=tokens[i]+tokens[i+1];i+=2
            def arithmetic(node):
                if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -arithmetic(node.operand)
                if isinstance(node,ast.Constant) and type(node.value) in (int,float):return node.value
                if isinstance(node,ast.BinOp) and type(node.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div):
                    op={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}[type(node.op)]
                    return op(arithmetic(node.left),arithmetic(node.right))
                raise ValueError('Unsupported expression')
            return arithmetic(ast.parse(expression,mode='eval').body)
        except ValueError:raise ValueError('Unsupported Lua token: '+t)
    out=value()
    if i!=len(tokens):raise ValueError('Unexpected trailing tokens')
    return out
