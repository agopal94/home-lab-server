from fastapi import FastAPI
import psutil
import shutil
import docker
from pydantic import BaseModel

app = FastAPI()
client = docker.from_env()

class DockerContainer(BaseModel):
    id: str
    image: str
    labels: dict
    name: str
    status: str


@app.get("/")
async def root():
    return {"message": "Welcome to home-lab-server"}

@app.get("/sysStats")
async def get_sys_stats():
    stats = {}
    stats["cpu"] = psutil.cpu_percent()
    stats["used_mem"] = psutil.virtual_memory().percent
    stats["free_mem"] = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
    total, used, free = shutil.disk_usage("/")
    stats["total_disk"] = (total // (2**30))
    stats["used_disk"] = (used // (2**30))
    stats["free_disk"] = (free // (2**30))
    return stats

@app.get("/listServices")
async def get_running_services() -> list[DockerContainer]:
    containersList = client.containers.list(True)
    responseContainers = []
    for container in containersList:
        responseContainers.append(DockerContainer(id=container.id, image=",".join(container.image.tags), labels=container.labels, name=container.name, status=container.status))
    return responseContainers
