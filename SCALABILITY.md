## Scalability

### Architectural Philosophy

Our design relies on the distinct characteristics of a URL Shortener: **Read-Heavy**, requiring low-latency redirection but tolerating eventual consistency for analytics.

*   **Storage Engine:** **PostgreSQL with B-Tree Indexing**.
    *   *Decision:* I prefer standard B-Tree indexes over LSM Trees (like Cassandra/RocksDB) for the core mapping table.
    *   *Reasoning:* Since our primary workload is lookups (Reads), B-Trees provide predictable $O(\log n)$ read performance without the read-amplification penalties often associated with LSM compaction cycles.
*   **Replication Strategy:** **Single Leader Replication**.
    *   *Writes:* All URL creations go to the **Master** node to ensure uniqueness and prevent collision in the Base62 namespace.
    *   *Reads:* Millions of redirection lookups are distributed across **Read Replicas**. I accept *Eventual Consistency* for the replicas to maximize throughput.
*   **Partitioning:** **Consistent Hashing**.
    *   Used to shard data across multiple nodes if the dataset exceeds single-node capacity, minimizing data movement when scaling the cluster.

---

### 1. High-Volume Analytics (The "Fire-and-Forget" Pattern)

**Solution:** Async Event Streaming with Kafka & Batch Processing.

Instead of treating a click as a Database operation, I treat it as an **Event**.

1.  **Producer (API Layer):** The application publishes a lightweight event to a Kafka Topic (`url.accessed`). This is a non-blocking operation (< 2ms).
2.  **Broker (Kafka):** Chosen for its log-based storage, allowing massive throughput and replayability.
3.  **Consumer (Worker Layer):** A separate Python service consumes these events.
4.  **Optimization (Batching):** The consumer buffers events (e.g., 1000 clicks) and performs a bulk `INSERT` into the database.

** Engineering THOUGHTS:**
*   **Decoupling:** If the Analytics DB requires maintenance, the Redirect API continues to function without error. Kafka acts as a buffer.
*   **Peak Smoothing:** During traffic spikes, the Kafka queue depth increases, but the Database write rate remains constant and safe.

---

### 2. Distributed Systems & Stateless Architecture

**The Challenge:** Scaling from a single Docker container to a Kubernetes Cluster requires the application to be completely stateless.

**The Solution:**

*   **Session/Memory:** No local memory storage for counters or rate limits.
*   **Connection Pooling (PgBouncer):** Python's `asyncpg` or `SQLAlchemy` are fast, but opening thousands of connections is expensive. I use **PgBouncer** as a sidecar/middleware to pool connections, preventing app instances from exhausting the DB connection limit.
*   **Distributed Cache (Redis Cluster):**
    *   Rate limiting counters (Leaky Bucket algorithm) are stored here.
    *   Ensures that if User A hits *Pod 1*, their rate limit is respected when they subsequently hit *Pod 2*.

**Risk: Race Conditions**
*   **Risk:** The "Counting Problem" (Two servers read `clicks=100`, both write `101`).
*   **Mitigation:** **Atomic Increments**. I never read-then-write. I use Redis `INCR` for real-time stats and SQL `UPDATE ... SET count = count + 1` for persistence.

---

### 3. Viral Campaign Traffic Spikes


#### A. Aggressive Read-Ahead Caching (LRU)
I implement a Read-Through Cache using Redis with an **LRU (Least Recently Used)** eviction policy.
*   **Pareto Principle:** In a viral campaign, ~90% of traffic hits ~1% of URLs.
*   **Mechanism:** The first request hits the DB and populates Redis. The next 100,000 requests are served entirely from RAM (sub-millisecond latency).

#### B. Idempotency & Exactly-Once Processing
To handle network retries (e.g., mobile clients losing signal) without corrupting analytics data, I implement application-level idempotency in our Kafka consumers.

*   **Logic:** The consumer checks if the `idempotency_key` has been processed in the last window (stored in Redis with a TTL) before incrementing the permanent DB counter.

#### C. Handling Replication Lag
**Risk:** A user creates a short link and immediately clicks it. If the Replica hasn't synced with the Master, they get a 404.
**Solution:**
1.  **Write-through Cache:** Upon creation, populate Redis immediately. Replicas are bypassed for the first few seconds.
2.  **Fallback:** If a Replica returns 404, the application makes a fallback query to the Master (or returns a `Retry-After` header).