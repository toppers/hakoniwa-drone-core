  "mcpServers": {
          "hakoniwa_drone": {
                  "command": "{{PYTHON_EXEC}}",
                  "args": [
                          "-m",
                          "hakoniwa_pdu.apps.mcp.server"
                  ],
                  "env": {
                          "PDU_CONFIG_PATH": "{{REPO_ROOT}}/config/pdudef/webavatar.json",
                          "SERVICE_CONFIG_PATH": "{{REPO_ROOT}}/config/launcher/drone_service.json",
                          "HAKO_BINARY_PATH": "/usr/share/hakoniwa/offset"
                  }
          }
  }
