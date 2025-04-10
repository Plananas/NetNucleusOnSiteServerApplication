import unittest
from unittest.mock import patch, MagicMock
from App.Backend.Server.OverseerHandler import OverseerHandler


class OverseerHandlerTest(unittest.TestCase):

    @patch('App.Backend.Server.OverseerHandler.requests.post')
    @patch.object(OverseerHandler, 'get_clients')
    @patch.object(OverseerHandler, 'get_ip_address')
    @patch.object(OverseerHandler, 'get_mac_address')
    def test_update_overseer_sends_correct_data(self, mock_mac, mock_ip, mock_clients, mock_post):
        mock_mac.return_value = '00:11:22:33:44:55'
        mock_ip.return_value = '192.168.1.123'
        mock_clients.return_value = [
            {'hostname': 'PC1', 'programs': [{'name': 'Chrome', 'version': '120.0'}]}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        handler = OverseerHandler()
        handler.update_overseer()

        mock_post.assert_called_once()
        url, = mock_post.call_args[0]
        data = mock_post.call_args[1]['json']

        self.assertEqual(url, 'http://overseer.local/update')
        self.assertEqual(data['mac_address'], '00:11:22:33:44:55')
        self.assertEqual(data['ip_address'], '192.168.1.123')
        self.assertIn('clients', data)
        self.assertEqual(len(data['clients']), 1)
        self.assertEqual(data['clients'][0]['hostname'], 'PC1')
        self.assertEqual(data['clients'][0]['programs'][0]['name'], 'Chrome')

    @patch('App.Backend.Server.OverseerHandler.ClientRepository')
    def test_get_clients_formats_client_data_with_programs(self, mock_repo_cls):
        # Mock client object
        mock_client = MagicMock()
        mock_client.to_dict.return_value = {'hostname': 'PC1'}

        # Mock programs
        mock_program = MagicMock()
        mock_program.to_json.return_value = {'name': 'Chrome', 'version': '120.0'}
        mock_client.get_installed_programs.return_value = [mock_program]

        # Repository returns one client
        mock_repo = MagicMock()
        mock_repo.get_all_clients.return_value = [mock_client]
        mock_repo_cls.return_value = mock_repo

        handler = OverseerHandler()
        clients = handler.get_clients()

        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['hostname'], 'PC1')
        self.assertEqual(clients[0]['programs'], [{'name': 'Chrome', 'version': '120.0'}])


if __name__ == '__main__':
    unittest.main()
