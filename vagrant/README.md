# JPWS Service

This simple service (jpws.py) exposes an HTTP endpoint.

In order to run it please install:
  * [Vagrant 2.2.0+](https://www.vagrantup.com/docs/installation)
  * [VirtualBox 6.1.0+](https://www.virtualbox.org/)

## Features and technology stack:
  * Nomad - Manages different services/jobs inclusing the jpws.nomad job
  * Consul - Provides service discovery
  * Redis - In Memory caching
  * Prometheus - Collects metrics from targets by scraping metrics HTTP endpoint
  * Loki - Log aggregation system to provide logging to Grafana dashboard
  * Grafana - Dashboard
  * Haproxy - provides load balancing 
  
## How to run:

From the directory where Vagrantfile is located run:
  `vagrant up`

Vagrant will create and configure the environment. It will also dockerize the service and run the different nomad jobs.

The following ports are exposed to the host:

  * [http://127.0.0.1:5000](http://127.0.0.1:5000) - JPWS service
  * [http://127.0.0.1:4646](http://127.0.0.1:4646) - Nomad
  * [http://127.0.0.1:8500](http://127.0.0.1:8500) - Consul UI
  * [http://127.0.0.1:1936](http://127.0.0.1:1936) - HAProxy stats
  * [http://127.0.0.1:9090](http://127.0.0.1:9090) - Prometheus
  * [http://127.0.0.1:3000](http://127.0.0.1:3000) - Grafana

  ## How to test it:

  Send multiple requests to the service, for example:

  `curl -d '{"action": "download"}' -H 'Content-Type: application/json' -v http://127.0.0.1:5000/manage_file/`

  Open Grafana and under the Nomad folder select the JPWS dashboard.

  In this dashboard you can see metrics and logging, for example:

  * [Dashboard](https://github.com/rc407/jpws-service/blob/main/vagrant/jpws/images/JPWS_dashboard.png)
  * [Logging showing cache hit or missed](https://github.com/rc407/jpws-service/blob/main/vagrant/jpws/images/JPWS_logging.png)
