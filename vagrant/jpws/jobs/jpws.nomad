job "jpws" {
  type = "service"

  datacenters = ["dc1"]

  group "jpws" {
    count = 1

    network {
      port "http" {
        to = 5000
      }
      port "promtail" {}
    }

    task "jpws" {
      driver = "docker"

      config {
        image   = "jpws-app:local"
        ports   = ["http"]
      }

      # TO DO: Move to KV store
      env {
        JPWS_FILE_EXT_URL = "https://www.learningcontainer.com/wp-content/uploads/2020/04/sample-text-file.txt"
        JPWS_REDIS_KEY = "jpws_file"
        JPWS_LOG_LEVEL = "DEBUG"
      }

      template {
  data = <<EOH
# Gets Redis service URL

REDIS_URL="redis://{{ range $i, $s := service "redis" }}{{ if eq $i 0 }}{{.Address}}:{{.Port}}{{end}}{{end}}/0"
EOH

  destination = "local/file.env"
  env         = true
}

      resources {
        cpu    = 50
        memory = 128
      }

      service {
        name = "jpws"
        port = "http"

       # check {
       #   type     = "http"
       ##   path     = "/health"
       #  interval = "3s"
       #   timeout  = "1s"
       # }
      }
    }

    task "promtail" {
      driver = "docker"

      lifecycle {
        hook    = "prestart"
        sidecar = true
      }

      config {
        image = "grafana/promtail:1.5.0"
        ports = ["promtail"]

        args = [
          "-config.file",
          "local/promtail.yaml",
        ]
      }

      template {
        data = <<EOH
server:
  http_listen_port: {{ env "NOMAD_PORT_promtail" }}
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

client:
  url: http://{{ range $i, $s := service "loki" }}{{ if eq $i 0 }}{{.Address}}:{{.Port}}{{end}}{{end}}/api/prom/push

scrape_configs:
- job_name: system
  entry_parser: raw
  static_configs:
  - targets:
      - localhost
    labels:
      task: jpws
      __path__: /alloc/logs/jpws*
  
EOH

        destination = "local/promtail.yaml"
      }

      resources {
        cpu    = 50
        memory = 32
      }

      service {
        name = "promtail"
        port = "promtail"

        check {
          type     = "http"
          path     = "/ready"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
