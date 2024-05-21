# Development
This is intended to be cross-compiled on a more powerful linux machine (or in WSL).
Connect to the Pi using `sshfs`:
```bash
mkdir pi_fs
sshfs traildev@192.168.50.233: pi_fs
cd pi_fs/traildev-keyboard-driver
code-insiders .
```