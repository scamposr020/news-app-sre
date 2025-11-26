CRHoy News Monitor -
A small web app that keeps an eye on CRHoy news headlines. It spots when new headlines show up and shares that info as Prometheus metrics. It treats headline changes like “events” you can monitor.

### What’s Inside:

- Scrapes CRHoy for the newest headlines
- Figures out which ones are new compared to what’s already saved
- Keeps a list in titulares.txt

### Prometheus metrics:
- Counter for total new headlines
- Histogram for request latency

### How It Works:
Flask app grabs HTML from crhoy.com

Uses BeautifulSoup to pull out headlines

Reads titulares.txt to see what’s old

Spots headlines that weren’t there before

Updates the file with the latest ones


### Endpoints:

/ → shows headlines in HTML

/nuevos → JSON with new headlines

/metrics → Prometheus metrics

### Project structure:

Code
/
```
├── app/
│   └── app.py            
│   └── requirements.txt  
├── k8s/
    └── deployment.yaml
    └── grafana-datasource.yaml
    └── news-app-alerts.yaml
    └── news-app-dashboard.json
    └── newsapp-dashboard.yaml  
    └── service.yaml
    └── servicemonitor.yaml    
├── Dockerfile            
└── CONTRIBUTING.md
├── LICENSE.md            
└── README.md               
```
### Architecture:

Deployment: 3 replicas of the news-app pod for availability.

Service: Exposes port 5000 inside the monitoring namespace.

ServiceMonitor: Tells Prometheus to scrape /metrics every 15s.

ConfigMaps: Used to load Grafana dashboards and Prometheus datasource.

Prometheus + Grafana: Handle scraping and visualization.

### Observability:
The app exposes Prometheus metrics so you can track what’s happening:

nuevas_noticias_total → Counter of new headlines detected 

latencia_peticion_seconds → Histogram of request latency 

### Alerts
Prometheus rules are set up to notify when something unusual happens:

  NewsFound → Triggers when at least one new headline is detected in the last minute.

    Severity: info

    Message: “New headline detected”

  NewsAppHighLatency → Triggers if average latency for /nuevos goes above 2 seconds for more than 2 minutes.

    Severity: warning

    Message: “High latency on /nuevos endpoint”


### Notes:
This project was built as a showcase of what I learned in the SRE Academy.

The goal wasn’t just to write code, but to practice the SRE way of thinking: keep things observable, reliable, and easy to improve.
