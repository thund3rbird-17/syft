#!/usr/bin/env python3
import os
import subprocess
import sys
import json

def create_dockerfile(target_dir, default_content):
    """
    Check if a Dockerfile exists in target_dir.
    If not, create one using the provided default content.
    """
    dockerfile_path = os.path.join(target_dir, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        print("No Dockerfile found in '{}'. Creating a default Dockerfile...".format(target_dir))
        with open(dockerfile_path, "w") as f:
            f.write(default_content)
    else:
        print("Dockerfile already exists in '{}'.".format(target_dir))

def build_docker_image(target_dir, image_name):
    """
    Build a Docker image from target_dir using the Dockerfile.
    """
    print("Building Docker image '{}' from directory '{}'...".format(image_name, target_dir))
    build_cmd = ["docker", "build", "-t", image_name, target_dir]
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: Docker build failed.")
        print(result.stderr)
        sys.exit(1)
    print("Docker image built successfully.")

def scan_image_with_syft(image_name):
    """
    Scan the Docker image using Syft and return the SBOM as a JSON object.
    """
    print("Scanning Docker image '{}' with Syft...".format(image_name))
    syft_cmd = ["syft", image_name, "-o", "json"]
    result = subprocess.run(syft_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: Syft scan failed.")
        print(result.stderr)
        sys.exit(1)
    try:
        sbom = json.loads(result.stdout)
    except Exception as e:
        print("Error parsing Syft output: {}".format(e))
        sbom = {"raw": result.stdout}
    return sbom

def main():
    print("=== Docker Build and Syft Scan Project ===")
    repo_url = input("Enter the GitHub repository URL (e.g., https://github.com/username/repo): ").strip()
    if not repo_url.startswith("https://github.com/"):
        print("Error: Repository URL must start with 'https://github.com/'")
        sys.exit(1)
    # Append .git if not present
    if not repo_url.endswith(".git"):
        repo_url = repo_url + ".git"
    
    image_name = input("Enter a Docker image name (default: my_image): ").strip() or "my_image"
    target_dir = "cloned_repo"  # Folder where repo will be cloned
    
    # Remove target_dir if it already exists
    if os.path.exists(target_dir):
        print("Removing existing directory '{}'...".format(target_dir))
        subprocess.run(["rm", "-rf", target_dir])
    
    # Clone the repository
    print("Cloning repository from '{}'...".format(repo_url))
    clone_cmd = ["git", "clone", repo_url, target_dir]
    clone_result = subprocess.run(clone_cmd, capture_output=True, text=True)
    if clone_result.returncode != 0:
        print("Error: Git clone failed.")
        print(clone_result.stderr)
        sys.exit(1)
    print("Repository cloned to '{}'.".format(target_dir))
    
    # Create Dockerfile if needed
    default_dockerfile = (
        "FROM python:3.9-slim\n"
        "WORKDIR /app\n"
        "COPY . /app\n"
        "RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi\n"
        "CMD [\"python\", \"app.py\"]\n"
    )
    create_dockerfile(target_dir, default_dockerfile)
    
    # Build Docker image
    build_docker_image(target_dir, image_name)
    
    # Scan the Docker image with Syft
    sbom = scan_image_with_syft(image_name)
    print("Syft scan complete. SBOM report:")
    print(json.dumps(sbom, indent=2))
    print("Process complete.")

if __name__ == "__main__":
    main()
