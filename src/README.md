# Deploying the Project

Before deploying the project, take a look at the README files of the subprojects and make sure you completed the configuration.

Also copy the file `docker.sample.env` to `docker.env` and modify according to your needs.

## Using Docker

The subprojects include individual Dockerfiles. You can use them to build the images manually and start the containers afterwards.

## Using docker-compose

To automatically build the images and run the containers with appropriate parameters, you can use docker-compose.

```
# bring up the whole application
docker-compose up -d
# once you are done and want to remove containers
docker-compose down

# to stop and start again without removing everything
docker-compose stop
docker-compose start
```
