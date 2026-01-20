match (n)-[e:release]->(m) return id(n),id(m);
match (n)-[e:interactor]->(m) return id(n),id(m);
match (n)-[e:surroundedBy]->(m) return id(n),id(m);
match (n)-[:hasEvent]->(m) return id(n),id(m);
match (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) return id(n),id(m);
match (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) return id(r),id(s);
