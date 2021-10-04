job "redis" {
  datacenters = ["dc1"]

  group "cache" {
    network {
      port "db" {
        to = 6379
      }
    }

    task "redis" {
      driver = "docker"

      config {
        image = "redis:3.2"

        ports = ["db"]
      }

      service {
        name = "redis"
        port = "db"

       # check {
       #   type     = "http"
       ##   path     = "/health"
       #  interval = "3s"
       #   timeout  = "1s"
       # }
      }

      resources {
        cpu    = 500
        memory = 256
      }
    }
  }
}