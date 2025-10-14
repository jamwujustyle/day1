start:
    docker compose up --build


stop:
    docker compose down -v


rmvods:
    sudo rm -rf media/videos/*