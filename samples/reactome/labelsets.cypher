match (n:Drug) return n;
match (n:ProteinDrug) return n;
match (n:Drug,ProteinDrug) return n;
match (n:Taxon)--(m:Species) return n,m;
match (n)--(m:Interaction)--(o) return n,m,o;
