#!/usr/bin/env python3
import argparse
import sys

if __package__:
    from .server import serve
    from .lib import osmsm
    from .utils import get_argparser
else:
    from server import serve
    from lib import osmsm
    from utils import get_argparser


def main():
    parser = get_argparser()
    args = parser.parse_args()

    #print(args)

    if "help" in args and args.help:
        print(parser.format_help())
        actions = [ action for action in parser._actions if isinstance(action, argparse._SubParsersAction) ]
        if actions:
            print("commands:")
            for action in actions:
                for choice, subparser in action.choices.items():
                    print(f"  {choice} [options]\n")
                    for line in subparser.format_help().splitlines()[1:]:
                        print(f"  {line}")

        print("\nExamples:\n")
        print("""$ osmsm -g '{"type":"Point","coordinates":[-105.01621,39.57422]}'""")
        print("""$ osmsm -g '[{"type":"Feature","properties":{"party":"Republican"},"geometry":{"type":"Polygon","coordinates":[[[-104.05,48.99],[-97.22,48.98],[-96.58,45.94],[-104.03,45.94],[-104.05,48.99]]]}},{"type":"Feature","properties":{"party":"Democrat"},"geometry":{"type":"Polygon","coordinates":[[[-109.05,41.00],[-102.06,40.99],[-102.03,36.99],[-109.04,36.99],[-109.05,41.00]]]}}]' --height=300 --width=300""")
        print("""$ osmsm -f /path/to/my_file.json""")
        print("""$ program_with_geojson_on_stdout | osmsm -f -""")

        exit()

    if args.command == "serve":
        exit(serve(args))

    data = osmsm(vars(args))
    if isinstance(data, str):
        sys.stdout.write(data)
    else:
        sys.stdout.buffer.write(data)


if __name__ == '__main__':
    main()
