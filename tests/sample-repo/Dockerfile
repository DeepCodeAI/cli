FROM node:10-alpine

# Packaged dependencies
RUN apk add --no-cache \
  --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
  bash

# The /wait command is to wait for an image to load before running the next command
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.2/wait /wait
RUN chmod +x /wait

RUN mkdir -p /home/node/node_modules && mkdir -p /home/node/app && chown -R node:node /home/node
ENV NPM_CONFIG_PREFIX=/home/node/node_modules
ENV PATH="/home/node/node_modules/.bin:${PATH}"

WORKDIR /home/node/app

COPY package*.json ./

USER node

RUN npm install

COPY --chown=node:node . .

EXPOSE 8080

# CMD [ "node", "app.js" ]
CMD /wait && node ./app.js
