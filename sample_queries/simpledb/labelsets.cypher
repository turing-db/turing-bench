MATCH (n:Person) RETURN n, n.name;
MATCH (n:Person), (m:Interest) RETURN n, m, n.name, m.name;
