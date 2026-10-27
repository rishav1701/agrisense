"""Software-only tests for Sentinel-2 scene preprocessing."""

import unittest

import numpy as np

from src.data.sentinel2_preprocessing import (
    DEFAULT_EXCLUDED_SCL_CLASSES,
    preprocess_sentinel2_scene,
)


class Sentinel2PreprocessingTests(unittest.TestCase):
    """Check scale, SCL/source masks, and alignment failures."""

    def test_scales_reflectance_and_applies_scl_and_source_masks(self):
        blue = np.array([[1000, 1000, 1000]], dtype=np.uint16)
        red = np.array([[2000, 2000, 2000]], dtype=np.uint16)
        nir = np.array([[6000, 6000, 6000]], dtype=np.uint16)
        scl = np.array([[4, 8, 6]], dtype=np.uint8)
        source_mask = np.array([[True, True, False]], dtype=np.bool_)

        result = preprocess_sentinel2_scene(
            blue_dn=blue,
            red_dn=red,
            nir_dn=nir,
            scl=scl,
            source_valid_mask=source_mask,
        )

        np.testing.assert_allclose(result.blue_reflectance[0, 0], 0.1)
        np.testing.assert_allclose(result.red_reflectance[0, 0], 0.2)
        np.testing.assert_allclose(result.nir_reflectance[0, 0], 0.6)
        np.testing.assert_array_equal(result.validity_mask, [[True, False, False]])
        self.assertTrue(np.isnan(result.indices.ndvi[0, 1:]).all())
        self.assertEqual(result.excluded_scl_classes, DEFAULT_EXCLUDED_SCL_CLASSES)

    def test_aligned_grid_is_required(self):
        band = np.ones((2, 2), dtype=np.uint16)
        with self.assertRaisesRegex(ValueError, "already be aligned"):
            preprocess_sentinel2_scene(
                blue_dn=band,
                red_dn=band,
                nir_dn=band,
                scl=np.ones((1, 1), dtype=np.uint8),
                source_valid_mask=np.ones((2, 2), dtype=np.bool_),
            )

    def test_mask_and_scale_are_validated(self):
        band = np.ones((2, 2), dtype=np.uint16)
        with self.assertRaisesRegex(ValueError, "source_valid_mask"):
            preprocess_sentinel2_scene(
                blue_dn=band,
                red_dn=band,
                nir_dn=band,
                scl=np.ones((2, 2), dtype=np.uint8),
                source_valid_mask=np.ones((2, 2), dtype=np.uint8),
            )
        with self.assertRaisesRegex(ValueError, "scale_factor"):
            preprocess_sentinel2_scene(
                blue_dn=band,
                red_dn=band,
                nir_dn=band,
                scl=np.ones((2, 2), dtype=np.uint8),
                source_valid_mask=np.ones((2, 2), dtype=np.bool_),
                scale_factor=0,
            )


if __name__ == "__main__":
    unittest.main()
