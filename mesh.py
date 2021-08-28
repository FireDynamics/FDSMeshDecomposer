import re
from typing import Sequence
import logging


class Mesh:
    def __init__(self, name: str, ijk: Sequence, xb: Sequence):
        self.name = name.strip()

        self.i = int(ijk[0])
        self.j = int(ijk[1])
        self.k = int(ijk[2])

        self.x = (float(xb[0]), float(xb[1]))
        self.y = (float(xb[2]), float(xb[3]))
        self.z = (float(xb[4]), float(xb[5]))

    def __str__(self):
        return f"{self.name}: i={self.i}, j={self.j}, k={self.k} - x={self.x[0]},{self.x[1]}, " \
               f"y={self.y[0]},{self.y[1]}, z={self.z[0]},{self.z[1]}"

    def decompose(self, dec: Sequence[int]) -> str:
        if all(d == 1 for d in dec):
            logging.warning(f"Decomposition {dec[0]},{dec[1]},{dec[2]} does not decompose the mesh, skipping mesh")
            return ""

        logging.info(f"Starting to decompose mesh using decomposition {dec[0]},{dec[1]},{dec[2]}")

        lx = self.x[1] - self.x[0]
        dx = lx / self.i
        di = self.i // dec[0]
        di_frac = self.i % dec[0]
        if di_frac != 0:
            logging.warning(f"x-decomposition will cause an unbalanced load distribution:"
                            f" {di} * {dec[0]} = {di * dec[0]} != {self.i}")

        ly = self.y[1] - self.y[0]
        dy = ly / self.j
        dj = self.j // dec[1]
        dj_frac = self.j % dec[1]
        if dj_frac != 0:
            logging.warning(f"y-decomposition will cause an unbalanced load distribution:"
                            f" {dj} * {dec[1]} = {dj * dec[1]} != {self.j}")

        lz = self.z[1] - self.z[0]
        dz = lz / self.k
        dk = self.k // dec[2]
        dk_frac = self.k % dec[2]
        if dk_frac != 0:
            logging.warning(f"z-decomposition will cause an unbalanced load distribution:"
                            f" {dk} * {dec[2]} = {dk * dec[2]} != {self.k}")

        out_str = f"&MESH IJK={di},{dj},{dk}, XB={self.x[0]},{self.x[0] + dx * di},{self.y[0]}," \
                  f"{self.y[0] + dy * dj},{self.z[0]},{self.z[0] + dz * dk}, MULT_ID='{self.name}' /\n" \
                  f"&MULT ID='{self.name}'"
        if dec[0] > 1:
            out_str += f", DX={dx * di}, I_UPPER={dec[0] - 1}"
        if dec[1] > 1:
            out_str += f", DY={dy * dj}, J_UPPER={dec[1] - 1}"
        if dec[2] > 1:
            out_str += f", DZ={dz * dk}, K_UPPER={dec[2] - 1}"
        out_str += " /\n"

        x0 = self.x[0] + di * dx
        y0 = self.z[0] + dj * dz
        z0 = self.z[0] + dk * dz
        name_frac = self.name + "_frac_"
        if di_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={x0},{x0 + dx * di_frac},{self.y[0]}," \
                       f"{self.y[0] + dy * dj},{self.z[0]},{self.z[0] + dz * dk}, MULT_ID='{name_frac + 'i'}' /\n" \
                       f"&MULT ID='{name_frac + 'i'}', DY={dy * dj_frac}, J_UPPER={dec[1] - 1}, DZ={dz * dk_frac}, " \
                       f"K_UPPER={dec[2] - 1} /\n"
        if dj_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={self.x[0]},{self.x[0] + dx * di},{y0}," \
                       f"{y0 + dy * dj_frac},{self.z[0]},{self.z[0] + dz * dk}, MULT_ID='{name_frac + 'j'}' /\n" \
                       f"&MULT ID='{name_frac + 'j'}', DX={dx * di_frac}, I_UPPER={dec[0] - 1}, DZ={dz * dk_frac}, " \
                       f"K_UPPER={dec[2] - 1} /\n"
        if dk_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={self.x[0]},{self.x[0] + dx * di},{self.y[0]}," \
                       f"{self.y[0] + dy * dj},{z0},{z0 + dz * dk_frac}, MULT_ID='{name_frac + 'k'}' /\n" \
                       f"&MULT ID='{name_frac + 'k'}', DX={dx * di_frac}, I_UPPER={dec[0] - 1}, DY={dy * dj_frac}, " \
                       f"J_UPPER={dec[1] - 1} /\n"
        if di_frac != 0 and dj_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={x0},{x0 + dx * di_frac},{y0}," \
                       f"{y0 + dy * dj_frac},{self.z[0]},{self.z[0] + dz * dk}, MULT_ID='{name_frac + 'ij'}' /\n" \
                       f"&MULT ID='{name_frac + 'ij'}', DZ={dz * dk_frac}, K_UPPER={dec[2] - 1} /\n"
        if di_frac != 0 and dk_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={x0},{x0 + dx * di_frac},{self.y[0]}," \
                       f"{self.y[0] + dy * dj},{z0},{z0 + dz * dk_frac}, MULT_ID='{name_frac + 'ik'}' /\n" \
                       f"&MULT ID='{name_frac + 'ik'}', DY={dy * dj_frac}, J_UPPER={dec[1] - 1} /\n"
        if dj_frac != 0 and dk_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={self.x[0]},{self.x[0] + dx * di},{y0}," \
                       f"{y0 + dy * dj_frac},{z0},{z0 + dz * dk_frac}, MULT_ID='{name_frac + 'jk'}' /\n" \
                       f"&MULT ID='{name_frac + 'jk'}', DX={dx * di_frac}, I_UPPER={dec[0] - 1} /\n"
        if di_frac != 0 and dj_frac != 0 and dk_frac != 0:
            out_str += f"&MESH IJK={di},{dj},{dk}, XB={x0},{x0 + di_frac * dx},{y0},{y0 + dy * dj_frac}," \
                       f"{z0},{z0 + dz * dk_frac}, ID='{name_frac + 'ijk'}' /\n"

        return out_str

    def decompose_heuristic(self) -> str:
        # TODO: Add heuristic

        return self.decompose([2, 2, 2])


MESH_COUNT = 0


def parse_mesh(mesh: str) -> Mesh:
    mesh_id_results = re.findall(r"ID=\S*", mesh, flags=re.IGNORECASE)
    if len(mesh_id_results) == 0:
        global MESH_COUNT
        MESH_COUNT += 1
        mesh_id = f"MESH_{MESH_COUNT:05d}"
    else:
        mesh_id = mesh_id_results[0].strip()

    raw_ijk = re.findall(r"IJK=\d+,\d+,\d+", mesh, flags=re.IGNORECASE)[0]
    ijk_str = re.findall(r"\d+", raw_ijk)
    ijk = (int(ijk_str[0]), int(ijk_str[1]), int(ijk_str[2]))

    re_float = r"[-+]?[0-9]*\.?[0-9]+"
    raw_xb = re.findall(r"XB={0},{0},{0},{0},{0},{0}".format(re_float), mesh)[0]
    xb = re.findall(re_float, raw_xb)

    return Mesh(mesh_id, ijk, xb)
