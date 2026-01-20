match (n:DatabaseObject{isChimeric:false}) return n;
match (n:DatabaseObject{isChimeric:true}) return n;
match (b)-->(a:Pathway) return a;
match (c)-->(b)-->(a:Pathway) return a, c;
match (c)-->(b)-->(a:Pathway) return b;
match (c)-->(b)-->(a:Pathway) return c;
match (c)-->(b)-->(a:Pathway) return a;
