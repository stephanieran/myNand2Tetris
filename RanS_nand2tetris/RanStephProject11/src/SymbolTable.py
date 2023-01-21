class SymbolTable:

    static_scope = {}

    counts = {
        'static': 0,
        'field':  0,
        'arg':    0,
        'var':    0
    }


    def __init__(self):
        ''' constructor '''
        self.counts['field']  = 0

        self.subroutine_scope = {}
        self.field_scope      = {}

    def startSubroutine(self, className):
        '''
        Starts a new subroutine score (i.e. resets the
        subroutine's symbol table); only reset arg and
        var since static and field are not applicable
        to subroutine
        '''
        self.subroutine_scope = {}
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, type, kind):
        '''
        Defines a new identifier of the given name, type,
        and kind, and assigns it a running index. static and
        field have a class scope, while arg and var identifiers
        have a subroutine scope
        '''
        number = None

        if kind == 'arg' or kind == 'var':
            if kind == 'arg':
                number = self.counts['arg']
                self.counts['arg'] += 1
            elif kind == 'var':
                number = self.counts['var']
                self.counts['var'] += 1

            self.subroutine_scope[name] = (type, kind, number)
        elif kind == 'static' or kind == 'field':
            if kind == 'static':
                number = self.counts['static']
                self.counts['static'] += 1
                self.static_scope[name] = (type, kind, number)
            elif kind == 'field':
                number = self.counts['field']
                self.counts['field'] += 1
                self.field_scope[name] = (type, kind, number)

    def varCount(self, kind):
        '''
        Returns the number of variables of the given kind
        already defined in the current scope.
        '''
        return self.counts[kind]
    
    def kindOf(self, name):
        '''
        Returns the kind of the named identifier in the current
        scope. If the identifier is unknown in the current scope,
        returns NONE
        '''
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][1]
        elif name in self.field_scope.keys():
            return self.field_scope[name][1]
        elif name in self.static_scope.keys():
            return self.static_scope[name][1]
        else:
            return 'NONE'
    
    def typeOf(self, name):
        '''
        Returns the type of the named identifier in the current scope
        '''
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][0]
        elif name in self.field_scope.keys():
            return self.field_scope[name][0]
        elif name in self.static_scope.keys():
            return self.static_scope[name][0]
        else:
            return 'NONE'

    def indexOf(self, name):
        '''
        Returns the index assigned to the named identifier
        '''
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][2]
        elif name in self.field_scope.keys():
            return self.field_scope[name][2]
        elif name in self.static_scope.keys():
            return self.static_scope[name][2]
        else:
            return'NONE'