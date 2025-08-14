match (n:Drug) return id(n);
match (n:ProteinDrug) return id(n);
match (n:Drug:ProteinDrug) return id(n);
match (n:Taxon)-->(m:Species) return id(n),id(m);
match (n)-->(m:Interaction)-->(o) return id(n),id(m),id(o);
