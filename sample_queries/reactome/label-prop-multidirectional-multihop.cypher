MATCH (n:DatabaseObject{isChimeric:false}) RETURN n;
MATCH (n:DatabaseObject{isChimeric:true}) RETURN n;
MATCH (b)-->(a:Pathway) RETURN a;
MATCH (c)-->(b)-->(a:Pathway) RETURN a, c;
MATCH (c)-->(b)-->(a:Pathway) RETURN b;
MATCH (c)-->(b)-->(a:Pathway) RETURN c;
MATCH (c)-->(b)-->(a:Pathway) RETURN a;
