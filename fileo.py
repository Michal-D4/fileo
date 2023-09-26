import sys

from src import main

if __name__ == '__main__':
    db = sys.argv[1] if len(sys.argv) > 1 else ''
    main.main(__file__, db)
