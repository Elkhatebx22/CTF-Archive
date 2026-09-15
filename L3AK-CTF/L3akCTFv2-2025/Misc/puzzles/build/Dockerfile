FROM golang:1.23.1-alpine AS builder

RUN apk update && apk add --no-cache git

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN go build -o puzzles .

FROM alpine:latest

RUN apk --no-cache add ca-certificates chromium nss

WORKDIR /app

COPY . .
COPY --from=builder /app/puzzles .


EXPOSE 1353

CMD ["./puzzles"]