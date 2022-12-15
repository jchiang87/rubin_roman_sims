import os
import glob
from desc.rubin_roman_sims import omit_existing_ccd_visits

def clean_up_test_dir(test_dir):
    if not os.path.isdir(test_dir):
        return
    for item in glob.glob(os.path.join(test_dir, '*')):
        os.remove(item)
    os.rmdir(test_dir)

def test_omit_existing_ccd_visits():
    orig_ccd_lists = {19031: ['R22_S11', 'R20_S02', 'R03_S10'],
                      823: ['R43_S00', 'R01_S12', 'R13_S22',
                            'R22_S11', 'R20_S02', 'R03_S10']}

    output_dir = 'test_output_dir'
    clean_up_test_dir(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    existing_ccd_visits = ((19031, 'R22_S11'), (19031, 'R20_S02'),
                           (823, 'R03_S10'))
    expected_ccd_visits = ((823, 'R01_S12'), (19031, 'R03_S10'))
    for visit, det_name in existing_ccd_visits:
        file_path = os.path.join(output_dir,
                                 f'amp_{visit:08d}-1-y-{det_name}-detX.fits.fz')
        with open(file_path, 'w'):
            pass

    ccd_lists = omit_existing_ccd_visits(orig_ccd_lists, output_dir)
    for visit, det_name in existing_ccd_visits:
        assert det_name not in ccd_lists[visit]

    for visit, det_name in expected_ccd_visits:
        assert det_name in ccd_lists[visit]
    clean_up_test_dir(output_dir)

if __name__ == '__main__':
    test_omit_existing_ccd_visits()
