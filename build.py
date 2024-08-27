import subprocess
import os


def build_css():
    subprocess.run(["npm", "run", "build"], check=True)


if __name__ == "__main__":
    build_css()
