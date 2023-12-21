#!/usr/bin/env python3

import paramiko
import base64
import re
import threading
import os
import argparse
import pdb
import time

# Shared flag
key_found = False

class KeyGenThread(threading.Thread):
    def __init__(self, threadID, args):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.args = args

    def set_permissions(self, file_name):
        os.chmod(file_name, 0o700)

    def run(self):

        # init
        wordlist = []

        # read the wordlist if one is provided
        if self.args.wordlist:
            # if the words should match the front of the key
            if self.args.front:
                wordlist += [ f"^{word}" for word in self.args.wordlist ]

            else:
                wordlist += [ f"{word}$" for word in self.args.wordlist ]

        # add regex to wordlist if one is provided
        if self.args.regex:
            wordlist.append(self.args.regex)

        # set option to be case-sensitive if ordered
        case_flag = re.IGNORECASE
        if self.args.case_sensitive:
            case_flag = re.NOFLAG


        global key_found
        while not key_found or self.args.infinite:
            key = paramiko.RSAKey.generate(2048)
            public_key = key.get_base64()

            for word in wordlist:
                match = re.search(word, public_key, case_flag)

                if match:
                    key_found = True
                    now = time.time()
                    private_key_file = f'{self.args.output_dir}/id_rsa_{match.group()}_{now}'
                    public_key_file  = f'{self.args.output_dir}/id_rsa_{match.group()}_{now}.pub'
                    if self.args.passphrase:
                        key.write_private_key_file(private_key_file, password=self.args.passphrase)
                    else:
                        key.write_private_key_file(private_key_file)
                    with open(public_key_file, 'w') as f:
                        f.write(f'ssh-rsa {public_key}')
                    self.set_permissions(private_key_file)
                    self.set_permissions(public_key_file)
                    print(f"Key found: {match.group()}\t(id_rsa_{match.group()}_{now})")

def main():
    parser = argparse.ArgumentParser(description='Generate SSH key with a specific word at the beginning/end of the public key.',
                                     epilog="""Using a wordlist will force the words to be either in the beginning or the end of the public key. In the front is probably a bad idea since most keys start with "AAA.."

Using '--regex' will add a regex that will be matched together with the words from the wordlist (if one was provided), and it can be written as any python compatible regex.

Examples:

# running until any word (case-insensitive) from the BIP 39 word list is found at the end of the public key, then terminate
python3 ssh_key_vanity.py -w bip39.txt

# running infinitly and find any word (case-insensitive) from the BIP 39 word list is found at the end of the public key
python3 ssh_key_vanity.py -w bip39.txt -i

# running until a regex is found, case-sensitive
python3 ssh_key_vanity.py -r "(dahlo|github)$" -c

# running infinitly and find any word from the BIP 39 word list or matching a specified regex (case-insensitive) and save the keys in a folder called 'passphrase' and protect the private keys with the password 'hunter2'
python3 ssh_key_vanity.py -w bip39.txt -r "(dahlo|github)$" -i -o passphrase/ -p hunter2
                                     """)
    parser.add_argument('-c', '--case-sensitive', action='store_true',  help='Used together with --wordlist to make the word match case-sensitive. (much longer running time)')
    parser.add_argument('-f', '--front',          action='store_true',  help='Used together with --wordlist to make the word match the beginning of the public key.')
    parser.add_argument('-i', '--infinite',       action='store_true',  help='Run infinitly (otherwise it will end as soon as one matching key has been found).')
    parser.add_argument('-o', '--output-dir',     type=str,             help='Path to where the keys will be saved. (default: ./)', default='./')
    parser.add_argument('-p', '--passphrase',     type=str,             help='A passphrase that will be used to protect the private key(s). If the is not set the keys will be unprotected.')
    parser.add_argument('-r', '--regex',          type=str,             help='The specific regex that should match the public key.')
    parser.add_argument('-w', '--wordlist',       type=str,             help='Path to a text file with one word per row that will be matched to the end of the public key.')
#    parser.add_argument('-t', '--threads',        type=int,             help='The number of threads to be used.') # not using threads as it scales really bad. Run multiple instances of the script instread. Will remove everything with Threads later on.
    args = parser.parse_args()

    # Load word list
    if args.wordlist:
        with open(args.wordlist, 'r') as f:
            wordlist = f.read().splitlines()
        args.wordlist = wordlist

    # Create new threads
    args.threads = 1 # for some reason it scales horribly when using threads. Start multiple instances of the script instead.
    threads = []
    for i in range(args.threads):  
        threads.append(KeyGenThread(i, args))

    # Start new Threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()




