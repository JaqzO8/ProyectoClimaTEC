#!/usr/bin/env bash
set -xeuo pipefail

# Update packages and install prerequisites
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release amazon-cloudwatch-agent

# Install Docker Engine & Compose plugin
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker ubuntu

# Configure Amazon CloudWatch Agent
cat <<'EOF' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "agent": {
    "metrics_collection_interval": 300,
    "run_as_user": "root"
  },
  "metrics": {
    "namespace": "ProyectoClimatico/PruebaRama",
    "metrics_collected": {
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 300
      },
      "disk": {
        "measurement": [
          "disk_used_percent"
        ],
        "metrics_collection_interval": 300,
        "resources": [
          "/"
        ]
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}",
      "AutoScalingGroupName": "${aws:AutoScalingGroupName}"
    }
  }
}
EOF

systemctl enable amazon-cloudwatch-agent
systemctl restart amazon-cloudwatch-agent || /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Launch a lightweight placeholder/app container on port 80 with / and /health endpoints
cat <<'EOF' > /opt/app-server.py
import http.server
import socketserver
import json

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/health'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "service": "ProyectoClimatico", "branch": "PruebaRama"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", 80), HealthHandler) as httpd:
    httpd.serve_forever()
EOF

cat <<'EOF' > /etc/systemd/system/clima-test-app.service
[Unit]
Description=Clima Test App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/app-server.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable clima-test-app
systemctl start clima-test-app
