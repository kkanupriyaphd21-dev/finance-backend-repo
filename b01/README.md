# Core Service (Java)

Scaffolded Spring Boot backend with neutral naming.

Quick start (build and run):

```bash
cd backend-core
mvn package
java -jar target/core-service-0.1.0-SNAPSHOT.jar
```

Endpoints:
- `GET /api/status` -> health check
- `GET /api/entries` -> list entries
- `POST /api/entries` -> create entry

Notes:
- Edit `src/main/resources/application.yml` to set your database credentials.
- Uses Flyway for migrations (add SQL files under `src/main/resources/db/migration`).
