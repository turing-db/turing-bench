MATCH (n)-[e:release]->(m) RETURN id(n),id(m);
MATCH (n)-[e:interactor]->(m) RETURN id(n),id(m);
MATCH (n)-[e:surroundedBy]->(m) RETURN id(n),id(m);
MATCH (n)-[:hasEvent]->(m) RETURN id(n),id(m);
MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN id(n),id(m);
MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN id(r),id(s);
