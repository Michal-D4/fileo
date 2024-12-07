import sys

from src import main

if __name__ == '__main__':
    if len(sys.argv) == 1:
        db = ''
        first_instance = True
    if len(sys.argv) == 3:
        db = sys.argv[1]
        first_instance = sys.argv[2] == 'True'

    main.main(sys.argv[0], db, first_instance)
