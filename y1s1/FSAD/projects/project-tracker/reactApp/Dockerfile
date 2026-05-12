FROM node:22

WORKDIR /app
COPY package*.json ./
RUN npm install
ENV PATH /app/node_modules/.bin:$PATH
COPY . .
EXPOSE 5173

CMD ["npm", "run", "dev"]
