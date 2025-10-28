import docker

def get_docker_containers():
    client = docker.from_env()
    containers = []
    for c in client.containers.list(all=True):
        containers.append({
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "unknown"
        })
    return containers
