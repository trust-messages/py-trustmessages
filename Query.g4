grammar Query;

expr:   FIELD OP VALUE  # comparison
    |   '(' expr ')'    # parenthesis
    |   expr 'AND' expr # and
    |   expr 'OR' expr  # or
    ;

FIELD:  'source' | 'target' | 'service' | 'date' ;
OP:     '!=' | '<=' | '>=' | '<' | '>' | '=' ;
VALUE:  [a-zA-Z0-9@\\.]+ ; // not sure if completely ok..
WS:     [ \t\r\n]+ -> skip ;
