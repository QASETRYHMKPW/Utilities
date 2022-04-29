import pathlib
import random
from argparse import ArgumentParser
from zipfile import ZipFile
import tqdm


def extract_zip(zip_file, pwd, dir) -> bool:
    password = pwd.strip()
    try:
        zip_file.extractall(dir, None, pwd=password.encode())
    except:
        return False
    else:
        return True


def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', nargs='?', required=True, dest='zip_file', metavar='<filename>', type=str,
                        help='path to zip file')
    parser.add_argument('-d', '--dictionary', nargs='?', required=True, dest='dictionary', metavar='<filename>',
                        type=str,
                        help='path to password dictionary file')

    args = parser.parse_args()
    zip_file_path = pathlib.Path(args.zip_file)
    out_dir = pathlib.Path(zip_file_path.parent).joinpath(zip_file_path.stem + str(random.Random().randint(10000, 99999)))
    out_dir.mkdir()
    password_found = None
    with open(args.dictionary) as rainbow_table, ZipFile(zip_file_path) as zip_file:
        for line in tqdm.tqdm(rainbow_table, unit='word'):
            if extract_zip(zip_file, pwd=line, dir=out_dir):
                password_found = line.strip()
                break

    if password_found is not None:
        print(f"Password found: {password_found}")
        print(f"Zip file extracted to {out_dir}")
    else:
        print(f"Password not found")


if __name__ == '__main__':
    main()
