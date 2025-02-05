import sys

from src import main

if __name__ == '__main__':
    """
    sys.argv - up to 3 parameters:
    0 - entry_point: str,
    1 - db_name: str,
    2 - first_instanse: bool
    """
    if len(sys.argv) == 1:
        db = ''
        first_instance = True
    if len(sys.argv) == 3:
        db = sys.argv[1]
        first_instance = sys.argv[2] == 'True'

    main.main(sys.argv[0], db, first_instance)
