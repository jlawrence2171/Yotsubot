FROM public.ecr.aws/amazonlinux/amazonlinux:latest

# Install dependencies
RUN yum update -y 
RUN dnf install -y nodejs

COPY . ./clown-bot

CMD cd ./clown-bot && npm i && node index.js