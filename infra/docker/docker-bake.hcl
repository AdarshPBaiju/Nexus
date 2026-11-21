group "default" {
  targets = ["api", "worker-go", "web"]
}

target "api" {
  context = "."
  dockerfile = "infra/docker/api.Dockerfile"
  tags = ["nexus-api:latest"]
}

target "worker-go" {
  context = "."
  dockerfile = "infra/docker/worker-go.Dockerfile"
  tags = ["nexus-worker-go:latest"]
}

target "web" {
  context = "."
  dockerfile = "infra/docker/web.Dockerfile"
  tags = ["nexus-web:latest"]
}
