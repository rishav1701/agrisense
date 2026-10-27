"""Software-only tests for Sentinel-1 backscatter math."""

import unittest

import numpy as np

from src.data.sentinel1 import compute_dual_pol_features, db_to_linear_power


class Sentinel1BackscatterTests(unittest.TestCase):
    """Check conversions, ratio semantics, and invalid inputs."""

    def test_converts_db_to_linear_power(self):
        values = np.array([-10.0, 0.0, 10.0], dtype=np.float32)
        np.testing.assert_allclose(db_to_linear_power(values), [0.1, 1.0, 10.0])

    def test_ratio_uses_difference_in_db_and_explicit_mask(self):
        vv = np.array([[-10.0, -10.0, np.nan]], dtype=np.float32)
        vh = np.array([[-20.0, -10.0, -20.0]], dtype=np.float32)
        mask = np.array([[True, False, True]], dtype=np.bool_)

        result = compute_dual_pol_features(
            vv_db=vv, vh_db=vh, validity_mask=mask
        )

        np.testing.assert_allclose(result.vh_to_vv_linear_ratio[0, 0], 0.1)
        self.assertFalse(result.valid_mask[0, 1])
        self.assertFalse(result.valid_mask[0, 2])
        self.assertTrue(np.isnan(result.vh_to_vv_linear_ratio[0, 1:]).all())

    def test_rejects_shape_and_mask_mismatches(self):
        vv = np.ones((2, 2), dtype=np.float32)
        with self.assertRaises(ValueError):
            compute_dual_pol_features(
                vv_db=vv,
                vh_db=np.ones((1, 4), dtype=np.float32),
                validity_mask=np.ones((2, 2), dtype=np.bool_),
            )
        with self.assertRaises(ValueError):
            compute_dual_pol_features(
                vv_db=vv,
                vh_db=vv,
                validity_mask=np.ones((2, 2), dtype=np.uint8),
            )


if __name__ == "__main__":
    unittest.main()
