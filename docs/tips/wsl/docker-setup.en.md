English | [日本語](docker-setup.md)

# TIPS

## How to set up a WSL/docker environment

You will be able to install and use docker directly in your WSL2/Ubuntu environment without using Docker Desktop for Windows.

Advantages of this environment:

-   You can avoid the license issue of Docker Desktop for Windows.
-   No waiting time for Docker Desktop for Windows to start up.
-   Development in a Linux environment becomes easier because you can use docker directly in the WSL2/Ubuntu environment.

### docker installation

Please execute the following.

```bash
bash docker/wsl-docker-install.bash
```

You will be asked for your password in the middle, so please enter your Ubuntu user password.

### Starting docker

Please execute the following.

```bash
bash docker/wsl-docker-activate.bash
```

### Getting the docker image

Please execute the following.

```bash
bash docker/pull-image.bash
```

If successful, it will look like this.

```bash
$ docker images
REPOSITORY                      TAG       IMAGE ID       CREATED        SIZE
toppersjp/hakoniwa-drone-core   v1.0.0    cb5d12d6b7ba   17 hours ago   1.28GB
```


### Starting the docker container
Please execute the following.

```bash
bash docker/run.bash
```

If successful, you will log in to the container and it will look like this.

```bash
$ bash docker/run.bash 
x86_64
wsl2
root@WinHako:~/workspace# ls
README.md  config  docker  docs  drone_api  drone_log0  include  mavlink  sample  src  thirdparty  tools
```

### Logging into a running container

Please execute the following.

```bash
bash docker/attach.bash
```

### Stopping the docker container

Stop the container with the `exit` command.

```bash
root@WinHako:~/workspace# exit
exit
```