import os
import subprocess
import threading

# A dictionary to keep track of bot states and their data for monitoring
bot_data = {}
bots_directory = "./bots"  # Update to your bots folder path

# Function to start bots
def start_bots():
    for file_name in os.listdir(bots_directory):
        if file_name.endswith('.py') and not file_name.startswith('__'):
            bot_path = os.path.join(bots_directory, file_name)
            # Start each bot as a separate subprocess
            subprocess.Popen(["python", bot_path])


def main():
    # Start bots in a separate thread
    bot_thread = threading.Thread(target=start_bots)
    bot_thread.start()


if __name__ == "__main__":
    main()
