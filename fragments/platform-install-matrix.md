# Platform Install Matrix

Maintenance reference for `/akka.setup` skill. Documents OS/arch detection logic and install commands for each dependency.

## OS Detection

```bash
# Detect OS
OS=$(uname -s)        # Darwin, Linux, MINGW64_NT-*, MSYS_NT-*
ARCH=$(uname -m)      # x86_64, arm64, aarch64
SHELL_NAME=$(basename "$SHELL")  # bash, zsh, fish

# Linux distro detection
if [ -f /etc/os-release ]; then
  . /etc/os-release
  DISTRO=$ID           # ubuntu, debian, fedora, rhel, arch, etc.
  DISTRO_FAMILY=$ID_LIKE  # debian, rhel fedora, arch, etc.
fi

# Package manager detection
if command -v brew &>/dev/null; then PKG=brew
elif command -v apt &>/dev/null; then PKG=apt
elif command -v dnf &>/dev/null; then PKG=dnf
elif command -v pacman &>/dev/null; then PKG=pacman
elif command -v winget &>/dev/null; then PKG=winget
elif command -v scoop &>/dev/null; then PKG=scoop
elif command -v choco &>/dev/null; then PKG=choco
fi
```

## Java 21+ Installation

| Platform | Preferred | Fallback |
|----------|-----------|----------|
| macOS | `brew install --cask temurin@21` | SDKMAN: `sdk install java 21-tem` |
| Linux (SDKMAN) | `sdk install java 21-tem` | — |
| Linux (apt) | `sudo apt install openjdk-21-jdk` | SDKMAN |
| Linux (dnf) | `sudo dnf install java-21-openjdk-devel` | SDKMAN |
| Linux (pacman) | `sudo pacman -S jdk-openjdk` | SDKMAN |
| Windows | `winget install EclipseAdoptium.Temurin.21.JDK` | `scoop install temurin21-jdk` or `choco install temurin21` |

**SDKMAN install** (user-space, no sudo):
```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 21-tem
```

**Version check:**
```bash
java -version 2>&1 | head -1
# Parse: version "21.x.x" or version "1.x.x" (old format)
```

## Maven 3.9+ Installation

| Platform | Preferred | Fallback |
|----------|-----------|----------|
| macOS | `brew install maven` | SDKMAN: `sdk install maven` |
| Linux (SDKMAN) | `sdk install maven` | — |
| Linux (apt) | `sudo apt install maven` | SDKMAN |
| Linux (dnf) | `sudo dnf install maven` | SDKMAN |
| Linux (pacman) | `sudo pacman -S maven` | SDKMAN |
| Windows | `winget install Apache.Maven` | `scoop install maven` or `choco install maven` |

**Maven wrapper**: If `./mvnw` exists in the project, Maven installation may be skipped.

**Version check:**
```bash
mvn --version | head -1
# Parse: Apache Maven 3.9.x
```

## Akka CLI Installation

| Platform | Method |
|----------|--------|
| macOS | `brew install akka/brew/akka` |
| Linux | Download binary from Akka releases |
| Windows | Download binary from Akka releases |

**Version check:**
```bash
akka version
```

## Docker Installation

| Platform | Preferred | Alternative |
|----------|-----------|-------------|
| macOS | `brew install --cask docker` | Colima: `brew install colima && colima start` |
| Linux (apt) | Official Docker CE repo | Rootless: `dockerd-rootless-setuptool.sh install` |
| Linux (dnf) | Official Docker CE repo | Podman: `sudo dnf install podman` |
| Linux (pacman) | `sudo pacman -S docker` | Podman: `sudo pacman -S podman` |
| Windows | `winget install Docker.DockerDesktop` | — |

**Version check:**
```bash
docker info 2>/dev/null | head -5
# Or: docker --version
```

## Akka Download Token

**Check if configured:**
```bash
grep -q "akka-repository" ~/.m2/settings.xml 2>/dev/null
```

**Configure via CLI:**
```bash
akka code token
# Opens browser to https://account.akka.io for OAuth
# Writes token to ~/.m2/settings.xml
```

## Privilege Escalation Policy

1. Prefer user-space installs: SDKMAN, Homebrew, winget, local binaries
2. If sudo required: show the exact command and ask for confirmation
3. Never run privileged commands silently
4. For SDKMAN: no elevated privileges needed at all
