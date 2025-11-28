
# URL Shortener Service

As always like any other interview assessments I made difficult decisions between avoiding over engineering and expose my skills and capabilities.
In the below I try to just mention some decisions and introduce what I have done and hope to have a deep and enjoyable conversation in next days.

I am happy that I should answer scalability questions and issues and I survived from the comparing boundaries between over engineering and must dos.

This is a scalable, asynchronous URL shortening service built with **FastAPI**, **PostgreSQL**, and **Docker**. Designed with performance, data integrity, and clean architecture in mind.

## Features

*   **URL Shortening:** Converts long URLs into short, unique 8-character codes.
*   **Redirects:** Redirection (HTTP 307) to original URLs.
*   **Analytics:** Tracks click counts, user IP, and User-Agent for every access.
*   **Background Processing:** Non-blocking logging of analytics to ensure redirect speed remains unaffected.
*   **Structured Logging:** JSON-formatted logs suitable for Observability stacks (ELK/Datadog).
*   **Containerized:** Fully Dockerized with multi-stage builds for optimization.

---

## Architecture & Design Decisions

* **Contains a little back of envelop calculation!**

### 1. ID Generation Strategy: Base62 Encoding
We utilize a **Database Sequence** combined with **Base62 Encoding** to generate short codes.
To avoiding **over engineering** this way may be the best solution to expose a little system design skills and I ignored **Predictability**.

#### **Why Base62?**
Base62 uses the characters `[a-z]`, `[A-Z]`, and `[0-9]`.
*   **URL Safe:** Unlike Base64, it does not contain special characters (like `/` or `+`) that require escaping in URLs.
*   **Deterministic:** $f(id) = code$. We do not need to store the string "code" in an indexed column (though we can for faster lookups). We can mathematically decode the string back to the Integer ID (`O(1)` complexity).

#### **Capacity Calculation**
With a 7-character limit, the number of unique combinations is $62^7$:
$$62^7 \approx 3,521,614,606,208 \text{ (3.5 Trillion unique URLs)}$$

Even if we generate **1,000 URLs per second**, this system will run for **~111 years** before running out of unique 7-character codes.

#### **Alternatives Considered**
*   **Random Strings:** Requires checking the database for collisions ("Is this code already taken?"). This adds a read operation before every write, slowing down the system as it fills up.
*   **MD5/SHA Hashing:** Produces long strings. Taking just the first 7 characters results in high collision probability (Birthday Paradox).
*   **UUID:** Too long (36 characters) for a URL shortener.

* **Note:** I ignored RandomStrings and Hashing to **reducing DB round-trips**, because our system is a **read heavy** and we do not have consideration about predictability in assessment doc.  
---

### 2. Database Choice: PostgreSQL
I chose PostgreSQL over NoSQL (MongoDB) or Key-Value stores (Redis) as the primary store for the following reasons:

*   **Atomic Sequences:** Postgres `SEQUENCE` objects are highly optimized and thread-safe. They guarantee unique Integer IDs even under heavy concurrent load, which is the backbone of our Base62 strategy.
*   **ACID Compliance:** Essential for the `clicked_count` feature. We use atomic row updates to ensure that if two users click simultaneously, the counter increments correctly by 2, not 1.
*   **Relational Integrity:** We log access details (`URLAccessLog`). A relational model allows us to easily join URL data with logs for complex analytics queries (e.g., "Top 10 users from Germany") in the future.

*Why not Redis?*
While Redis is faster, it is an in-memory store. If the server crashes, we risk losing data (unless strict persistence is configured, which slows it down). We reserve Redis for a future caching layer (e.g., caching hot redirects) rather than the primary source of truth.


### 4. Software Architecture: Repository Pattern
The repository pattern **decouples** business logic from data access, making it straightforward to modify database queries or 
even swap out the underlying database without touching service layer code. API endpoints, services, repositories, and models each live in their own dedicated directories. When adding new features, developers know exactly where each component belongs, reducing cognitive overhead and onboarding time.


---

## Stack

*   **Language:** Python 3
*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy (Async) + Alembic (Migrations)
*   **Validation:** Pydantic
*   **Testing:** Pytest + AsyncPG

---

## Getting Started

### Prerequisites
*   Docker & Docker Compose

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd url-shortener
    ```

2.  **Start Services:**
    ```bash
    docker-compose up --build -d
    ```
    *This starts the PostgreSQL container and the FastAPI application. The app handles database migrations automatically on startup.*

3.  **Access API:**
    *   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running the Tests

All the APIs of the project has test and you can run tests and make sure about they are work with:
```bash

docker compose --profile test run --rm tests

```

---

