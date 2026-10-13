import unittest
from unittest.mock import patch, MagicMock
from your_module import Node  # Replace 'your_module' with the actual module name

class TestNode(unittest.TestCase):

    @patch('time.sleep')
    def test_become_follower(self, mock_sleep):
        node = Node(1, [2, 3])
        node.become_follower()
        self.assertEqual(node.state, 'follower')
        self.assertIsNone(node.voted_for)
        self.assertEqual(node.current_term, 1)
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_become_candidate(self, mock_sleep):
        node = Node(1, [2, 3])
        node.become_candidate()
        self.assertEqual(node.state, 'candidate')
        self.assertEqual(node.voted_for, 1)
        self.assertEqual(node.current_term, 1)
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_become_leader(self, mock_sleep):
        node = Node(1, [2, 3])
        node.become_leader()
        self.assertEqual(node.state, 'leader')
        self.assertEqual(node.next_index, {2: 0, 3: 0})
        self.assertEqual(node.match_index, {2: 0, 3: 0})
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    @patch('threading.Thread')
    def test_send_votes(self, mock_thread, mock_sleep):
        node = Node(1, [2, 3])
        node.send_votes()
        self.assertEqual(mock_thread.call_count, 2)
        for call_args, call_kwargs in mock_thread.call_args_list:
            self.assertEqual(call_args[0], node.request_vote)
            self.assertIn(call_args[1], [2, 3])
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_request_vote(self, mock_sleep):
        node = Node(1, [2, 3])
        node.current_term = 1
        node.voted_for = None
        node.request_vote(2)
        self.assertEqual(node.voted_for, 1)
        mock_sleep.assert_called_once()

        node.current_term = 2
        node.request_vote(2)
        self.assertIsNone(node.voted_for)
        mock_sleep.assert_called_once()

        node.state = 'follower'
        node.request_vote(2)
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_send_append_entries(self, mock_sleep):
        node = Node(1, [2, 3])
        node.state = 'leader'
        node.send_append_entries(2)
        mock_sleep.assert_called_once()

        node.state = 'follower'
        node.send_append_entries(2)
        mock_sleep.assert_called_once()

if __name__ == '__main__':
    unittest.main()