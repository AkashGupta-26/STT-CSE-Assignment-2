| Definition ID | Variable | Block | Line | Statement |
|---------------|----------|-------|------|-----------|
| D1 | n | B0 | 110 | `int n;` |
| D2 | startVertex | B3 | 121 | `int startVertex;` |
| D3 | n | B3 | 125 | `int n = g.numVertices;` |
| D4 | dist | B3 | 126 | `int dist[MAX_SIZE];` |
| D5 | visited | B3 | 127 | `int visited[MAX_SIZE] = {0};` |
| D6 | u | B7 | 139 | `int u = node.vertex;` |
| D7 | weight | B11 | 145 | `int weight = g.adjMatrix[u][v];` |
| D8 | alt | B13 | 147 | `int alt = dist[u] + weight;` |