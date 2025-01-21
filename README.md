```bash
docker run -d -p 5001:5000 --name registry registry:2.7
./build_and_push.sh
docker compose up -d
docker compose down -v
```