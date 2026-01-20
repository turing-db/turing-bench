match (n{displayName:"Autophagy"}) return id(n);
match (n{displayName:"Autophagy"})-->(m) return id(m);
match (n{displayName:"Autophagy"})-->(m)-->(p) return id(p);
match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) return id(q);
match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) return id(r);
match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) return id(s);
match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) return id(t);
match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) return id(v);
