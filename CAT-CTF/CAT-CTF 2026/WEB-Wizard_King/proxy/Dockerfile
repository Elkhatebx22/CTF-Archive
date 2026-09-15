FROM golang:1.22-alpine AS build

WORKDIR /usr/src/app
COPY go.mod .
COPY server.go .
RUN go build -o server ./server.go

FROM alpine:3.20

ARG USERNAME=app
WORKDIR /usr/src/app
COPY --from=build /usr/src/app/server .
RUN adduser --disabled-password --no-create-home --gecos ${USERNAME} ${USERNAME}

USER ${USERNAME}
EXPOSE 8080
CMD ["/usr/src/app/server"]
