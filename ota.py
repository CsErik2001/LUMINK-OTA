import urequests
import os
import json
import machine
import time


class OTAUpdater:
    """ This class handles OTA updates. It connects to the Wi-Fi, checks for updates, downloads and installs them."""

    def __init__(self, repo_url, filenames, branch="main"):
        self.filenames = filenames
        self.repo_url = repo_url
        self.branch = branch
        if "www.github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent")
            self.repo_url = self.repo_url.replace("www.github", "raw.githubusercontent")
        elif "github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent'")
            self.repo_url = self.repo_url.replace("github", "raw.githubusercontent")
        self.version_url = self.repo_url + self.branch + '/version.json'
        print(f"version url is: {self.version_url}")

        # get the current version (stored in version.json)
        if 'version.json' in os.listdir():
            with open('version.json') as f:
                self.current_version = int(json.load(f)['version'])
            print(f"Current device firmware version is '{self.current_version}'")

        else:
            self.current_version = 0
            # save the current version
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)

    def fetch_latest_code(self) -> bool:
        """ Fetch the latest code from the repo, returns False if not found."""

        # Fetch the latest code from the repo.
        for filename in self.filenames:
            firmware_url = self.repo_url + self.branch + '/' + filename

            response = None
            max_retries = 3
            for i in range(max_retries):
                try:
                    response = urequests.get(firmware_url)
                    break
                except OSError as e:
                    print(f"Error fetching {filename}: {e}, retrying {i+1}/{max_retries}...")
                    time.sleep(2)

            if response is None:
                print(f"Failed to fetch {filename} after retries.")
                return False

            if response.status_code == 200:
                print(f'Fetched latest firmware code for {filename}, status: {response.status_code}')

                # Save the fetched code to memory
                with open('latest_' + filename, 'w') as f:
                    f.write(response.text)

            elif response.status_code == 404:
                print(f'Firmware not found - {firmware_url}.')
                return False

        return True

    def update_no_reset(self):
        """ Update the code without resetting the device."""

        # update the version in memory
        self.current_version = self.latest_version

        # save the current version
        with open('version.json', 'w') as f:
            json.dump({'version': self.current_version}, f)

    def update_and_reset(self):
        """ Update the code and reset the device."""

        print(f"Updating device...", end="")

        # Overwrite the old code.
        for filename in self.filenames:
            os.rename('latest_' + filename, filename)

        # Restart the device to run the new code.
        print('Restarting device...')
        machine.reset()  # Reset the device to run the new code.

    def check_for_updates(self):
        """ Check if updates are available."""

        # Connect to Wi-Fi
        # self.connect_wifi()

        print(f'Checking for latest version... on {self.version_url}')

        response = None
        max_retries = 3
        for i in range(max_retries):
            try:
                response = urequests.get(self.version_url)
                break
            except OSError as e:
                print(f"Error checking for updates: {e}, retrying {i+1}/{max_retries}...")
                time.sleep(2)

        if response is None:
            print("Failed to check for updates after retries.")
            return False

        data = json.loads(response.text)

        print(f"data is: {data}, url is: {self.version_url}")
        print(f"data version is: {data['version']}")
        # Turn list to dict using dictionary comprehension
        #         my_dict = {data[i]: data[i + 1] for i in range(0, len(data), 2)}

        self.latest_version = int(data['version'])
        print(f'latest version is: {self.latest_version}')

        # compare versions
        newer_version_available = True if self.current_version < self.latest_version else False

        print(f'Newer version available: {newer_version_available}')
        return newer_version_available

    def download_and_install_update_if_available(self):
        """ Check for updates, download and install them."""
        if self.check_for_updates():
            if self.fetch_latest_code():
                self.update_no_reset()
                self.update_and_reset()
        else:
            print('No new updates available.')