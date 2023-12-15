import sys

from src import main

if __name__ == '__main__':
    db = sys.argv[1] if len(sys.argv) > 1 else '-'
    '''
    "-" - means first instance,
    any next instance is either empty string
    or real db file name
    '''
    main.main(sys.argv[0], db)
