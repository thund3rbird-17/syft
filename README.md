# Docker Build and Syft Scan Project

This project clones a GitHub repository, builds a Docker image from it (creating a Dockerfile if one does not exist), and scans the image using Syft to generate an SBOM (Software Bill of Materials) report.

## Prerequisites

- **Docker:** Must be installed and running.
- **Git:** Must be installed.
- **Syft:** Install via Homebrew (`brew install syft`) or following the instructions at [Syft GitHub](https://github.com/anchore/syft).
- **Python 3:** Required to run the script.

## Project Structure

