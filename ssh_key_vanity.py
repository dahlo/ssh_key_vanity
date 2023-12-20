#!/usr/bin/env python3

import paramiko
import base64
import re
import threading
import os
import argparse

# Shared flag
key_found = False

class KeyGenThread(threading.Thread):
    def __init__(self, threadID, word):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.word = word

    def set_permissions(self, file_name):
        os.chmod(file_name, 0o700)

    def run(self):
        global key_found
        while not key_found:
            key = paramiko.RSAKey.generate(2048)
            public_key = key.get_base64()
            match = re.search(self.word, public_key, re.IGNORECASE)

            if match and not key_found:
                key_found = True
                private_key_file = f'id_rsa_{self.threadID}'
                public_key_file = f'id_rsa_{self.threadID}.pub'
                key.write_private_key_file(private_key_file)
                with open(public_key_file, 'w') as f:
                    f.write(f'ssh-rsa {public_key}')
                self.set_permissions(private_key_file)
                self.set_permissions(public_key_file)
                print(f"Key found by thread {self.threadID}")
                break

def main():
    parser = argparse.ArgumentParser(description='Generate SSH key with a specific word at the end of the public key.')
    parser.add_argument('word', type=str, help='The specific word to be included at the end of the public key.')
    parser.add_argument('threads', type=int, help='The number of threads to be used.')
    args = parser.parse_args()

    # Create new threads
    threads = []
    for i in range(args.threads):  
        threads.append(KeyGenThread(i, args.word))

    # Start new Threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()




