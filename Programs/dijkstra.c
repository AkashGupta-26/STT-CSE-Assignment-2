#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define MAX_SIZE 100

// -----------------------------
// Priority Queue Implementation
// -----------------------------
typedef struct {
    int vertex;
    int priority;  // Smaller value = higher priority
} Node;

typedef struct {
    Node data[MAX_SIZE];
    int size;
} PriorityQueue;

void initQueue(PriorityQueue *pq) {
    pq->size = 0;
}

int isEmpty(PriorityQueue *pq) {
    return pq->size == 0;
}

int isFull(PriorityQueue *pq) {
    return pq->size >= MAX_SIZE;
}

void swap(Node *a, Node *b) {
    Node temp = *a;
    *a = *b;
    *b = temp;
}

void heapifyUp(PriorityQueue *pq, int index) {
    while (index > 0) {
        int parent = (index - 1) / 2;
        if (pq->data[index].priority < pq->data[parent].priority) {
            swap(&pq->data[index], &pq->data[parent]);
            index = parent;
        } else break;
    }
}

void heapifyDown(PriorityQueue *pq, int index) {
    while (1) {
        int left = 2 * index + 1;
        int right = 2 * index + 2;
        int smallest = index;

        if (left < pq->size && pq->data[left].priority < pq->data[smallest].priority)
            smallest = left;
        if (right < pq->size && pq->data[right].priority < pq->data[smallest].priority)
            smallest = right;

        if (smallest != index) {
            swap(&pq->data[index], &pq->data[smallest]);
            index = smallest;
        } else break;
    }
}

void insert(PriorityQueue *pq, int vertex, int priority) {
    if (isFull(pq)) {
        printf("Queue full, cannot insert vertex %d\n", vertex);
        return;
    }
    pq->data[pq->size].vertex = vertex;
    pq->data[pq->size].priority = priority;
    pq->size++;
    heapifyUp(pq, pq->size - 1);
}

Node extractMin(PriorityQueue *pq) {
    Node minNode = pq->data[0];
    pq->data[0] = pq->data[pq->size - 1];
    pq->size--;
    heapifyDown(pq, 0);
    return minNode;
}

// -----------------------------
// Graph + Dijkstra’s Algorithm
// -----------------------------
typedef struct {
    int numVertices;
    int adjMatrix[MAX_SIZE][MAX_SIZE];
} Graph;

void initGraph(Graph *g, int n) {
    g->numVertices = n;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            g->adjMatrix[i][j] = 0;
}

void addEdge(Graph *g, int u, int v, int w) {
    g->adjMatrix[u][v] = w;
    g->adjMatrix[v][u] = w;  // For undirected graph
}

// -----------------------------
// Main Function
// -----------------------------
int main() {
    Graph g;
    int n;
    printf("Enter number of vertices: ");
    scanf("%d", &n);

    initGraph(&g, n);

    printf("Enter adjacency matrix (0 for no edge):\n");
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            scanf("%d", &g.adjMatrix[i][j]);

    int startVertex;
    printf("Enter start vertex: ");
    scanf("%d", &startVertex);

    int n = g.numVertices;
    int dist[MAX_SIZE];
    int visited[MAX_SIZE] = {0};

    for (int i = 0; i < n; i++)
        dist[i] = INT_MAX;
    dist[startVertex] = 0;

    PriorityQueue pq;
    initQueue(&pq);
    insert(&pq, startVertex, 0);

    while (!isEmpty(&pq)) {
        Node node = extractMin(&pq);
        int u = node.vertex;

        if (visited[u]) continue;
        visited[u] = 1;

        for (int v = 0; v < n; v++) {
            int weight = g.adjMatrix[u][v];
            if (weight && !visited[v]) {
                int alt = dist[u] + weight;
                if (alt < dist[v]) {
                    dist[v] = alt;
                    insert(&pq, v, alt);
                }
            }
        }
    }

    printf("\nShortest distances from vertex %d:\n", startVertex);
    for (int i = 0; i < n; i++) {
        if (dist[i] == INT_MAX)
            printf("%d -> INF\n", i);
        else
            printf("%d -> %d\n", i, dist[i]);
    }

    return 0;
}
