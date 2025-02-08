import os
import subprocess
import glob
import shutil
import re


class ScoopFunctions:

    @staticmethod
    def download_installer(name="notepadplusplus", version=None):
        try:
            print(f"Downloading package: {name}")

            # Run Scoop download command
            scoop_command = f"scoop download {name}"
            if version:
                scoop_command += f" {version}"

            subprocess.run(scoop_command, shell=True, check=True, capture_output=True, text=True)

            # Locate the installer ZIP file in Scoop's cache directory
            scoop_cache_dir = os.path.expanduser("~\\scoop\\cache")

            # Find the cache file matching the format package#version#hash.zip
            cache_files = glob.glob(os.path.join(scoop_cache_dir, f"{name}#*.zip"))

            if not cache_files:
                print(f"No cache ZIP file found for {name}.")
                return None

            # Use the most recent cache file
            cache_files.sort(key=os.path.getmtime, reverse=True)
            cache_zip_path = cache_files[0]

            # Move the ZIP to the local 'installers' directory
            installers_dir = os.path.join(os.getcwd(), "installers")
            os.makedirs(installers_dir, exist_ok=True)

            final_zip_path = os.path.join(installers_dir, os.path.basename(cache_zip_path))
            shutil.move(cache_zip_path, final_zip_path)

            print(f"Cache ZIP file saved to: {final_zip_path}")
            return final_zip_path

        except subprocess.CalledProcessError as e:
            print(f"Error downloading package: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    @staticmethod
    def getSoftwareVersionNumber(software_name):
        version_number = ""

        try:
            # Run 'scoop info <package>' as a string command
            command = f'scoop info {software_name}'
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,  # ✅ Ensures it never waits for input
                text=True
            )

            # Read the output and error streams
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error running scoop command: {stderr.strip()}")
                return ""

            ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

            for line in stdout.splitlines():
                cleaned_line = ANSI_ESCAPE_PATTERN.sub("", line)  # ✅ Remove colors
                #print(f"DEBUG: {repr(cleaned_line)}")  # See exact processed output

                if cleaned_line.startswith("Version"):  # ✅ Now works!
                    version_number = cleaned_line.split(":", 1)[1].strip()
                    #print(f"Detected Version: {version_number}")

        except FileNotFoundError:
            print("Error: Scoop is not installed or not in PATH.")
        print(version_number)
        return version_number


    @staticmethod
    def ensure_scoop_installed():
        """
        Checks if Scoop is installed on the system. If it is not installed,
        installs it using a PowerShell script.
        """

        #TODO this function needs to change for the client program as scoop cannot be downloaded online


        # Step 1: Check if Scoop is installed
        try:
            # "scoop --version" will throw FileNotFoundError if `scoop` is not on PATH
            # or CalledProcessError if there's another execution problem
            subprocess.run("scoop --version", shell=True, check=True, capture_output=True, text=True)
            print("Scoop is already installed.")
            return
        except FileNotFoundError:
            print("Scoop not found.")
        except subprocess.CalledProcessError:
            # We got a return code != 0; this may mean Scoop is not properly installed
            print("Scoop detected but could not run. Attempting to reinstall.")

        # Step 2: Install Scoop using PowerShell
        print("Installing Scoop. This may take a few moments...")

        install_cmd = (
            r"Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; "
            r"[System.Net.ServicePointManager]::SecurityProtocol = "
            r"[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
            r"iex ((New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh'))"
        )

        try:
            subprocess.run(["powershell", "-Command", install_cmd], check=True)
        except subprocess.CalledProcessError as e:
            print("Installation of Scoop failed with an error:")
            print(e)
            return

        # Step 3: Verify installation
        try:
            subprocess.run(["scoop", "--version"], check=True, capture_output=True)
            print("Scoop installation successful.")
        except Exception as e:
            print("Scoop installation was attempted but verification failed.")
            print(e)


#For testing purposes
if __name__ == "__main__":
    package_name = "notepadplusplus"  # Change this for testing
    version = None

    zip_path = ScoopFunctions.download_installer(package_name, version)

    if zip_path:
        print(f"Success! ZIP file saved at: {zip_path}")
    else:
        print("Download failed.")
