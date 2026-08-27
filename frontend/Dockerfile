# --- Build stage: compile the React app into static assets ---
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# REACT_APP_* vars are baked into the bundle at build time by react-scripts, so this
# has to be a build ARG, not a runtime environment variable. Pass it via
# `docker build --build-arg REACT_APP_GATEWAY_URL=...` or docker-compose `args:`.
ARG REACT_APP_GATEWAY_URL
ENV REACT_APP_GATEWAY_URL=${REACT_APP_GATEWAY_URL}
RUN npm run build

# --- Runtime stage: serve the built static assets instead of the webpack dev server ---
# `npm start` (react-scripts start) is a development server -- unoptimized, not
# hardened for real traffic, and not what should run in a container meant for
# production/staging use.
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
