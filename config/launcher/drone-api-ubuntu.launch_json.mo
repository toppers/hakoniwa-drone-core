{
  "version": "0.1",
  "defaults": {
    "cwd": ".",
    "stdout": "logs/${asset}.out",
    "stderr": "logs/${asset}.err",
    "env": {
      "prepend": {
        "lib_path": ["/usr/lib/x86_64-linux-gnu"],
        "PATH": ["/usr/bin"],
        "PYTHONPATH": [
          "{{REPO_ROOT}}/drone_api",
          "{{REPO_ROOT}}/drone_api/assets",
          "{{REPO_ROOT}}/drone_api/assets/lib",
          "{{SYS_DIST}}",
          "{{PYENV_SITE}}"
        ]
      }
    },
    "start_grace_sec": 1,
    "delay_sec": 3
  },
  "assets": [
    {
      "name": "drone",
      "activation_timing": "before_start",
      "command": "lnx/linux-main_hako_drone_service",
      "args": ["config/drone/api", "config/pdudef/webavatar.json"],
      "cwd": "{{REPO_ROOT}}"
    },
    {
      "name": "environment",
      "activation_timing": "before_start",
      "command": "python",
      "args": ["-m","hako_env_event","../config/pdudef/webavatar.json","20","assets/config"],
      "cwd": "{{REPO_ROOT}}/drone_api"
    },
    {
      "name": "webserver",
      "activation_timing": "after_start",
      "command": "python",
      "args": ["-m","server.main","--asset_name","WebServer",
               "--config_path","{{REPO_ROOT}}/config/pdudef/webavatar.json",
               "--delta_time_usec","20000"],
      "cwd": "{{REPO_ROOT}}/../hakoniwa-webserver",
      "depends_on": ["drone"]
    },
    {
      "name": "Unity",
      "activation_timing": "after_start",
      "command": "simulation.exe",
      "args": [],
      "cwd": "{{REPO_ROOT}}/WebAvatar",
      "depends_on": ["webserver"]
    }
  ],
  "notify": {
    "type": "exec",
    "command": "scripts/notify_on_fail.sh",
    "args": ["${asset}","asset_exit","${timestamp}"]
  }
}
