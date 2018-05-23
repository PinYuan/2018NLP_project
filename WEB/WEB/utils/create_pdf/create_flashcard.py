def create_flashcard(wordlist, filename):
    f = open(filename, 'w')
    title = filename.split('/', 1)
    for key in wordlist:
        f.write(key[0])
        for state in key[1]:
            f.write('\t' + key[1][state])
        f.write('\n')
    f.close()