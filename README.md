# Vanity SSH Key Generator

This script will generate ssh keys until it finds one that matches the word/pattern you are looking for. It will take exponentially longer time the longer word you are looking for. A quick test on my own computer showed this time increase when generating about 50 keys per second:

```
len   time
1     0.5s
2     0.5s
3       2s
4     115s
```

I think upto 5 characters is feasable for a normal computer.

Run as this:

```bash
python ssh_key_vanity.ph <word/pattern> <n threads>

ex. word
python ssh_key_vanity.ph dahlo 20

ex. regex
python ssh_key_vanity.ph 'dahlo$' 20
```

The word/pattern is passed directly to a `re.search` function so it can be written as any regex you want.
