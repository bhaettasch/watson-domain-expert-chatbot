# Deploying the Project

## Using Docker

The subprojects include individual Dockerfiles. You can use them to build the images manually and start the containers afterwards.

## Using docker-compose

To automatically build the images and run the containers with appropriate parameters, you can use docker-compose.

```
# bring up the whole application
docker-compose up -d
# once you are done...
docker-compose stop
```
