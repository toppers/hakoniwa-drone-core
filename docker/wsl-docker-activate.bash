#!/bin/bash

sudo systemctl enable docker
sudo systemctl start docker

sudo chown `whoami` /var/run/docker.sock
