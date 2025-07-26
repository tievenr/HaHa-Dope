# Stop and remove all containers, networks, and volumes for this compose file
docker compose down --volumes --remove-orphans

# Remove the images built for your services
docker rmi haha-dope-namenode haha-dope-datanode

# Remove any unused Docker data (containers, images, networks, volumes)
docker system prune -a --volumes --force