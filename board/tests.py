from unittest.mock import patch
from django.test import SimpleTestCase, Client


class HealthCheckTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    @patch("board.views.connection.cursor")
    def test_health_check_ok_localhost_and_127_0_0_1(self, mock_cursor):
        for host in ("localhost", "127.0.0.1"):
            response = self.client.get("/health/", HTTP_HOST=host)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})
            mock_cursor.return_value.__enter__.return_value.execute.assert_called_with("SELECT 1")

    @patch("board.views.connection.cursor")
    def test_health_check_db_error(self, mock_cursor):
        mock_cursor.side_effect = Exception("Database connection failed")
        response = self.client.get("/health/", HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "error"})

