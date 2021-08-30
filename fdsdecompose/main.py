import argparse
import os

from .mesh import *


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("in_filepath")
    parser.add_argument("out_filepath")
    parser.add_argument("--decomposition")
    args = parser.parse_args()

    decomposition = list()
    if args.decomposition:
        decomposition = [int(dim) for dim in args.decomposition.split(",")]

    logging.info(f"Parsing input file '{args.in_filepath}'")

    append_next = False
    current_mesh = ""
    with open(args.in_filepath, 'r') as infile, open(args.out_filepath + ".tmp", 'w') as outfile:
        # Iterate over all lines in file and look for "MESH" namelists
        for line in infile:
            # We check for the "MESH" identifier by splitting the line and checking if the line got actually split
            # somewhere. We skip non-active lines (ones that do not start with a "&")
            mesh_split = line.split("MESH", maxsplit=1)
            if len(mesh_split) > 1 and "&" in mesh_split[0]:
                # Remove all whitespace from string to make subsequent parsing easier
                current_mesh = "".join(mesh_split[1].split())
                # Although not common, it might be possible that meshes are defined over multiple lines, we therefore
                # have to check if the line does actually end here
                if "/" not in line:
                    append_next = True
            # If the last mesh-line did not end with a "/" we concatenate this line and the previous one
            elif append_next:
                current_mesh += ", " + "".join(line.split())
                if "/" in line:
                    append_next = False
            else:
                outfile.write(line)
            if current_mesh != "" and not append_next:
                mesh = parse_mesh(current_mesh)
                logging.info("Found " + str(mesh))

                multimesh = ""
                if len(decomposition) > 0:
                    # Try to apply given decomposition to mesh
                    multimesh = mesh.decompose(decomposition)
                else:
                    # Use decomposition heuristic
                    multimesh = mesh.decompose_heuristic()

                if multimesh == "":
                    multimesh = current_mesh
                outfile.write(multimesh)
                current_mesh = ""

    # If everything worked without producing any errors, we rename the temporary output file to the real output name
    # If the output filename does already exist, we remove it prior to renaming
    if os.path.exists(args.out_filepath):
        os.remove(args.out_filepath)
    os.rename(args.out_filepath + ".tmp", args.out_filepath)
    logging.info("Wrote output file to " + args.out_filepath)


if __name__ == "__main__":
    main()
