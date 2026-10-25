"""Software-only tests for Sentinel-2 spectral-index calculations.

All arrays below are invented test values and are not satellite observations.
"""

import unittest

import numpy as np

from src.data.sentinel2 import compute_vegetation_indices


class Sentinel2VegetationIndexTests(unittest.TestCase):
    """Check formulas, explicit masking, and invalid-pixel behavior."""

    def test_computes_indices_from_reflectance_scaled_inputs(self):
        blue = np.array([[0.1, 0.2]], dtype=np.float32)
        red = np.array([[0.2, 0.3]], dtype=np.float32)
        nir = np.array([[0.6, 0.7]], dtype=np.float32)
        mask = np.array([[True, True]], dtype=np.bool_)

        result = compute_vegetation_indices(
            blue=blue, red=red, nir=nir, validity_mask=mask
        )

        expected_ndvi = (nir - red) / (nir + red)
        expected_evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
        np.testing.assert_allclose(result.ndvi, expected_ndvi, rtol=1e-6)
        np.testing.assert_allclose(result.evi, expected_evi, rtol=1e-6)
        self.assertTrue(result.ndvi_valid.all())
        self.assertTrue(result.evi_valid.all())

    def test_applies_only_the_explicit_mask_and_keeps_nan_inputs_invalid(self):
        blue = np.array([[0.1, 0.1, np.nan]], dtype=np.float32)
        red = np.array([[0.2, 0.2, 0.2]], dtype=np.float32)
        nir = np.array([[0.6, 0.6, 0.6]], dtype=np.float32)
        mask = np.array([[True, False, True]], dtype=np.bool_)

        result = compute_vegetation_indices(
            blue=blue, red=red, nir=nir, validity_mask=mask
        )

        np.testing.assert_array_equal(result.ndvi_valid, [[True, False, False]])
        np.testing.assert_array_equal(result.evi_valid, [[True, False, False]])
        self.assertTrue(np.isnan(result.ndvi[0, 1:]).all())
        self.assertTrue(np.isnan(result.evi[0, 1:]).all())

    def test_zero_denominators_are_masked_without_imputation(self):
        # Artificial input chosen to make the NDVI denominator zero.
        blue = np.array([[0.0]], dtype=np.float32)
        red = np.array([[1.0]], dtype=np.float32)
        nir = np.array([[-1.0]], dtype=np.float32)
        mask = np.array([[True]], dtype=np.bool_)

        result = compute_vegetation_indices(
            blue=blue, red=red, nir=nir, validity_mask=mask
        )

        self.assertFalse(result.ndvi_valid[0, 0])
        self.assertTrue(np.isnan(result.ndvi[0, 0]))
        self.assertTrue(result.evi_valid[0, 0])

    def test_rejects_shape_and_mask_mismatches(self):
        base = np.ones((2, 3), dtype=np.float32)
        with self.assertRaises(ValueError):
            compute_vegetation_indices(
                blue=base,
                red=np.ones((3, 2), dtype=np.float32),
                nir=base,
                validity_mask=np.ones((2, 3), dtype=np.bool_),
            )
        with self.assertRaises(ValueError):
            compute_vegetation_indices(
                blue=base,
                red=base,
                nir=base,
                validity_mask=np.ones((2, 3), dtype=np.uint8),
            )


if __name__ == "__main__":
    unittest.main()
