MATCH (n{displayName:"Autophagy"}) RETURN id(n);
MATCH (n{displayName:"Autophagy"})-->(m) RETURN id(m);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN id(p);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN id(q);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN id(r);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN id(s);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN id(t);
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN id(v);
