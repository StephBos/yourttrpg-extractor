APP_NAME=yourttrpg-extractor
CONTAINER_NAME=$(APP_NAME)-container
PORT=8000

build:
	docker build -t $(APP_NAME) .

stop:
	-docker stop $(CONTAINER_NAME)

remove:
	-docker rm $(CONTAINER_NAME)

run:
	docker run -d \
		-p $(PORT):8000 \
		--name $(CONTAINER_NAME) \
		$(APP_NAME)

dev: stop remove build run

login: docker login

push: login
	docker push $(APP_NAME)
    
pull: login
	docker pull $(APP_NAME)
