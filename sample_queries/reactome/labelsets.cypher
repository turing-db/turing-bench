MATCH (n:Drug) RETURN id(n);
MATCH (n:ProteinDrug) RETURN id(n);
MATCH (n:Drug:ProteinDrug) RETURN id(n);
MATCH (n:Taxon)-->(m:Species) RETURN id(n),id(m);
MATCH (n)-->(m:Interaction)-->(o) RETURN id(n),id(m),id(o);
