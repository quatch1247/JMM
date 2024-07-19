uvicorn main:app --host 127.0.0.1 --port 8000 --reload
docker-compose up --build

export PYTHONPATH=/Users/igeon/Desktop/Projects/JMM/app

##ecr
docker build -t new-fastapi-project .
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag new-fastapi-project:latest 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com/new-fastapi-project:latest
docker push 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com/new-fastapi-project:latest

#ecs 
#task-definitions 먼저 정의

docker buildx create --use
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64,linux/arm64 -t 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com/gun-suggest-fastapi-fargate:latest --push .
docker buildx build --platform linux/amd64,linux/arm64 -t 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com/gun-suggest-fastapi-fargate:latest --push .
docker buildx build --platform linux/amd64,linux/arm64 -t 360814036500.dkr.ecr.ap-northeast-2.amazonaws.com/gun-eclipse-ui/gun_ui:latest --push .


docker build -t myapp:v1.2 .
docker run -d -p 8080:8080 --name myapp_container myapp:v1.2

#링크
http://localhost:8080/gun_ui-0.0.1-SNAPSHOT/