# TPS 2017 results

\[[Português](README.pt_BR.md)\] \[**[English](README.md)**\]

During the 2017 edition of the Public Security Tests of the Brazilian voting system, we found vulnerabilities allowing for **arbitrary code execution** in the voting machine.

## Repository contents

### Technical lectures

Slides of technical lectures reporting our results (in Portuguese):

 * [12/2017: Lecture at UFSCar](https://epicleet.github.io/tps2017/slides/2017-12-ufscar.pdf)
 * [04/2018: Lecture at Unicamp](https://epicleet.github.io/tps2017/slides/2018-04-unicamp.pdf)
 * [10/2018: Lecture at SBSeg](https://epicleet.github.io/tps2017/slides/2018-10-sbseg.pdf)

### Encryption and decryption of the file system

The install card uses the custom `ueminix` file system, which obfuscates file contents by encrypting their contents with AES-XTS.

Here we release two tools related to that file system:

 * [encall.py](fs_crypto/encall.py): encrypts original files into the `enc` directory.

 * [decall.py](fs_crypto/decall.py): decrypts files from the `enc` directory into the  `dec` directory.

Please note it is needed to provide the disk image (`dsk.img`), for the following reasons:

 * The cipher padding may not be directly read from userspace, therefore we read it from the disk image.

 * One of the AES-XTS keys is contained in the second sector of the partition. The tools themselves recover this key.

The other AES-XTS key may be recovered from the kernel's `ueminix` code and must be set up directly in the tool's source code (`key1` variable). If access to the source code is not available, one can recover this key by emulating the bootloader, dumping the decrypted kernel and reverse engineering it.

### Tampering with votes

The file [exploit.py](exploit/exploit.py) illustrates the attack to tamper with votes. We infect the [hkdf](exploit/hkdf.cpp) library with code which infects [vota](exploit/gui/infoeleitor.cpp)'s memory space.

Code excerpts from [hkdf](exploit/hkdf.cpp) and [vota](exploit/gui/infoeleitor.cpp) mock the official voting application's structure, allowing to simulate the attack in a simplified model remarkably close to the real system.

Just like the voting machine's official software, our voting software simulator is a 32-bit software. Therefore, if you have a 64-bit system, you need to install the 32-bit libraries to be able to run the simulator. For instance, if you use Debian or Ubuntu, run the following commands:

```bash
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install libqt5multimedia5:i386
```

To execute the voting software simulator, enter directory `exploit` and run `make test_cli` to execute the command line interface (CLI) simulator, or run `make test_gui` to execute the graphical user interface (GUI) simulator.

To infect the library, install [pwntools](https://github.com/Gallopsled/pwntools#installation) and run `make exploit_cli` to compromise the CLI simulator, or run `make exploit_gui` to compromise the GUI simulator.

After that, when the voting simulator is rerun, the malicious code modifies the votes.

To restore the original behaviour, run `make restore`.

### How to carry a real attack

A real attack would follow the following steps:

1. Obtain an image of the install card contents.
2. Reverse engineer the bootloader and the decrypted kernel to obtain the key which ciphers/deciphers other install card's files.
3. Decipher the filesystem.
4. Run the exploit to infect `libhkdf.so`.
5. Cipher the modified file to generate an infected install card.

## About the team

Our team comprises members from [ELT](https://ctftime.org/team/9061), an interinstitutional team which participates in CTF competitions. We also organise an annual competition called [Pwn2Win](https://pwn2win.party).
