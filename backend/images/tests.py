from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from images.models import ImageDownloadTask
from images.tools import download_satellite_images
from polygons.models import Polygon


class ImageDownloadTaskModelTests(TestCase):
    def test_task_uses_the_current_date_range_contract(self):
        polygon = Polygon.objects.create(
            name='test-area',
            gcj02_coordinates=[[116.3, 39.9], [116.4, 39.9], [116.4, 40.0]],
            wgs84_coordinates=[[116.29, 39.89], [116.39, 39.89], [116.39, 39.99]],
        )

        task = ImageDownloadTask.objects.create(
            name='Test download',
            polygon=polygon,
            start_day=date(2023, 1, 1),
            end_day=date(2023, 1, 31),
        )

        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.progress, 0)
        self.assertEqual(task.polygon, polygon)


class SatelliteDownloadTests(SimpleTestCase):
    @patch('images.tools.ee.ImageCollection')
    def test_earth_engine_filter_dates_are_iso_strings(self, image_collection):
        collection = MagicMock()
        collection.filterDate.return_value = collection
        collection.filterBounds.return_value = collection
        collection.select.return_value = collection
        collection.size.return_value.getInfo.return_value = 0
        image_collection.return_value = collection
        task = SimpleNamespace(
            id=1,
            name='Online download',
            polygon=SimpleNamespace(id=1),
        )

        result = download_satellite_images(
            task,
            'sentinel-1',
            date(2026, 4, 1),
            date(2026, 9, 15),
            MagicMock(),
            [],
            MagicMock(),
        )

        collection.filterDate.assert_called_once_with('2026-04-01', '2026-09-16')
        self.assertTrue(result['success'])
