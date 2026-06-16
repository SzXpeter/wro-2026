# WSL
szükséges csomagok telepítése
```bash
sudo apt-get update
sudo apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf cmake
sudo apt-get install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
sudo apt-get install -y sshpass openssh-client rsync

sudo dpkg --add-architecture arm64
sudo apt-get install libpigpio-dev:arm64

```

# PI
szükséges csomagok telepítése
```bash
sudo apt-get update
sudo apt install python3-pip -y
python3 -m pip install opencv-python-headless --break-system-packages
```



        self.left_motor_pins = [13, 19, 12, (16, 17, 20)]  # dir_pin, step_pin, enable_pin
        self.right_motor_pins = [24, 26, 4, (21, 22, 27)]
