#!/bin/env python3

import os

from desc.rubin_roman_sims import RunImSim, make_visit_tranches


def main(
    tranche: int,
    num_tranches: int,
    n_proc: int,
    pretend: bool,
    opsim_db: str,
    sky_catalog: str,
    output_dir: str,
) -> None:
    assert tranche < num_tranches

    if pretend:

        def _run_imsim(visit, ccds, nproc=1):
            """Function to use for debugging division of ccd lists into tranches"""
            print(visit, len(ccds), nproc)

        run_imsim = _run_imsim
    else:
        run_imsim = RunImSim(
            sky_catalog_file=sky_catalog, opsim_db_file=opsim_db, output_dir=output_dir
        )

    visit_tranches = make_visit_tranches(num_tranches, output_dir)

    for visit, ccds in visit_tranches[tranche].items():
        run_imsim(visit, ccds, nproc=n_proc)


if __name__ == "__main__":
    import argparse

    def existing_path(path: str):
        if not os.path.isfile(path):
            raise argparse.ArgumentTypeError(f"{path} does not exist")
        return path

    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        "-p",
        dest="pretend",
        help="Only print number of CCD's per visist / dont run simulation.",
        action="store_true",
        default=False,
    )
    _parser.add_argument(
        "-o",
        dest="output_dir",
        help="Output directory (default: rubin_roman_sims_y1)",
        default="rubin_roman_sims_y1",
    )
    _parser.add_argument(
        "--n-proc", help="Set number of processes. Default: 64", default=64, type=int
    )
    _parser.add_argument(
        "--opsim-db",
        help="Specify the obsim db to use (default: opsim.db)",
        default="opsim.db",
        type=existing_path,
    )
    _parser.add_argument(
        "--sky-catalog",
        help="Specify the sky catalog to use (default: skyCatalog.yaml)",
        default="skyCatalog.yaml",
        type=existing_path,
    )
    _parser.add_argument("tranche", help="Tranche index", type=int)
    _parser.add_argument("num_tranches", help="Number of tranches", type=int)
    _cmd_args = _parser.parse_args()

    main(**vars(_cmd_args))
