# TIPS


## Ardupilot SITL のセットアップ方法

```
git clone --recursive https://github.com/ArduPilot/ardupilot.git
```

```
cd ardupilot
```

```
./Tools/environment_install/install-prereqs-ubuntu.sh -y
```

```
pip3 install empy==3.3.4 future MAVProxy
```

```
./waf configure --board sitl
```

```
./waf copter
```
