# Compilation
This is intended to be cross-compiled on a more powerful linux machine (or in WSL).
Connect to the Pi using `sshfs`:
```bash
mkdir pi_fs
sshfs pi@192.168.50.233: pi_fs
cd pi_fs/traildev-keyboard-driver
code-insiders .
```
To build and run:

On the compilation machine:
```bash
cargo build
```
On the target, via `ssh`:
```bash
./target/arm-unknown-linux-gnueabihf/debug/traildev-keyboard-driver
```