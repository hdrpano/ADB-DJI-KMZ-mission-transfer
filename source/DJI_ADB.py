import subprocess
import os
import shutil
import re
import sys

# path to your ADB tools
ADB_PATH = r".../platform-tools/adb.exe"

# local file to be uploaded
LOCAL_KMZ = "mission.kmz"

# remote-path for DJI Fly
WAYPOINT_PATH = "/sdcard/Android/data/dji.go.v5/files/waypoint/"

# UUID-RegEx
UUID_PATTERN = re.compile(
    r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$",
    re.IGNORECASE
)


def adb(cmd):
    """Run ADB command with full path"""
    proc = subprocess.run(
        [ADB_PATH] + cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return proc.stdout.strip()


def check_device():
    print("→ Check ADB connection …")
    out = adb("devices")
    print(out)

    if "device" not in out.splitlines()[-1]:
        raise Exception("❌ No ADB device connected or debugging not allowed!")


def get_latest_uuid():
    print("→ Determine latest mission UUID …")

    out = adb(f"shell ls -t {WAYPOINT_PATH}")
    dirs = out.splitlines()

    uuids = [d.strip() for d in dirs if UUID_PATTERN.match(d.strip())]
    if not uuids:
        raise Exception("❌ No valid mission folders found!")

    uuid = uuids[0]
    print("✔ Newest UUID:", uuid)
    return uuid


def upload_kmz(uuid):
    remote_folder = f"{WAYPOINT_PATH}{uuid}"
    remote_file = f"{remote_folder}/{uuid}.kmz"

    print("→ Remote-Target:", remote_file)

    # create temp file
    temp_local = uuid + ".kmz"
    shutil.copy(LOCAL_KMZ, temp_local)

    print("→ Delete old KMZ files if present …")
    adb(f"shell rm {remote_file}")

    print("→ Upload new KMZ files …")
    out = adb(f"push {temp_local} {remote_file}")
    print(out)

    print("→ Clean up temporary file …")
    os.remove(temp_local)

    print("✓ Upload finished!")
    print("→ DJI Fly will automatically synchronise the mission.")


def main():
    try:
        check_device()
        uuid = get_latest_uuid()
        upload_kmz(uuid)
        print("✓ Finished!")
    except Exception as e:
        print("\n❌ ERROR:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
