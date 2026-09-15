FROM golang:1.23.1-alpine AS builder

ENV CGO_ENABLED=1

RUN apk update && apk add --no-cache git gcc musl-dev sqlite-dev

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN go build -o flagguessr .
RUN go build -o makecert ./certgen

FROM alpine:latest

RUN apk --no-cache add ca-certificates chromium nss

WORKDIR /app

COPY --from=builder /app/flagguessr .
COPY --from=builder /app/makecert .
COPY --from=builder /app/flag.txt .
COPY --from=builder /app/templates ./templates

EXPOSE 5555

ENTRYPOINT ["./flagguessr"]