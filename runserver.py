from sys import argv, stderr, exit
from app import app


def main(argv):
    if len(argv) != 2:
        print("Incorrect number of arguments - specify port only", file=stderr)
        exit(1)

    try:
        port = int(argv[1])
    except Exception:
        print("Port must be an integer", file=stderr)
        exit(1)

    app.run(host="localhost", port=port, debug=True)


if __name__ == "__main__":
    main(argv)
