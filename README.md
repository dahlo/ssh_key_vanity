# Vanity SSH Key Generator

This script will generate ssh keys until it finds one that matches the word/pattern you are looking for. It will take exponentially longer time the longer word you are looking for, and even longer time if you have constraints that the key should start/end with the word. A quick test on my own computer showed this time increase when generating about 50 keys per second and requiring the key to end with the word:

```
len   time
1     0.8s
2       3s
3     300s
4    XXXXs
```

I think upto 3-4 characters is feasable for a normal computer.

Run as this:

```bash
usage: ssh_key_vanity.py [-h] [-c] [-f] [-i] [-o OUTPUT_DIR] [-p PASSPHRASE]
                         [-r REGEX] [-w WORDLIST]

Generate SSH key with a specific word at the beginning/end of the public key.

optional arguments:
  -h, --help            show this help message and exit
  -c, --case-sensitive  Used together with --wordlist to make the word match case-sensitive. (much longer running time)
  -f, --front           Used together with --wordlist to make the word match the beginning of the public key.
  -i, --infinite        Run infinitly (otherwise it will end as soon as one matching key has been found).
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Path to where the keys will be saved. (default: ./)
  -p PASSPHRASE, --passphrase PASSPHRASE
                        A passphrase that will be used to protect the private key(s). If the is not set the keys will be unprotected.
  -r REGEX, --regex REGEX
                        The specific regex that should match the public key.
  -w WORDLIST, --wordlist WORDLIST
                        Path to a text file with one word per row that will be matched to the end of the public key.

Using a wordlist will force the words to be either in the beginning or the end of the public key. In the front is probably a bad idea since most keys start with "AAA.."

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
"""
