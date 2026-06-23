import os
import subprocess

def copy_script_directory(remote_user, remote_host, remote_path, port=22):
    local_dir = os.path.dirname(os.path.abspath(__file__))

    cmd = [
        "scp",
        "-P", str(port),
        "-r",  # recursive (for folders)
        f"{remote_user}@{remote_host}:{remote_path}",
        local_dir + "/."
    ]

    print("Copying from:", local_dir)
    print("Running:", " ".join(cmd))

    result = subprocess.run(cmd, text=True, capture_output=True)

    if result.returncode == 0:
        print("✔ Copy successful")
    else:
        print("❌ Error:")
        print(result.stderr)


if __name__ == "__main__":
    copy_script_directory(
        remote_user="jedlikpi",
        remote_host="jedlikpi",
        remote_path="/home/jedlikpi/wro2026/log",
        port=22  # change if needed
    )