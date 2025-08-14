match (n)-[e:release]-(m) return n,m;
match (n)-[e:interactor]-(m) return n,m;
match (n)-[e:surroundedBy]-(m) return n,m;
match (n)-[:hasEvent]-(m) return n,m;
match (n:Pathway)-[:hasEvent]-(m:ReactionLikeEvent) return n,m;
match (r:ReactionLikeEvent)-[:output]-(s:PhysicalEntity) return r,s;
