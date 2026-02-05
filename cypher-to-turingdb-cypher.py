import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, metavar="input-file")
    parser.add_argument("--output-file", type=str, default="/tmp/output.tdbcypher")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    node_count = 0
    with open(args.input_file, "r") as inp:
        with open(args.output_file, "w") as out:
            out.write("CREATE\n")

            i = 0
            for line in inp:
                line = line.strip()
                print(line)
