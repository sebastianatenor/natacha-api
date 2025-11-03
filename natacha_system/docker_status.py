import docker


def get_docker_status():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    data = []
    for c in containers:
        data.append(
            {
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else "sin etiqueta",
            }
        )
    return data
