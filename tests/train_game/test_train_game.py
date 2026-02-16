import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root and app directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'app'))

from app.services.train_game.train_game_service import TrainGameService

class TestTrainGameService(unittest.TestCase):
    def setUp(self):
        # Mock the AI adapter before instantiating the service to avoid import issues or side effects
        self.ai_adapter_patcher = patch('app.services.train_game.train_game_service.TrainAIAdapter')
        self.mock_ai_adapter_class = self.ai_adapter_patcher.start()
        self.mock_ai_adapter = self.mock_ai_adapter_class.return_value
        
        self.service = TrainGameService()
        # Ensure the service uses our mock
        self.service.ai_adapter = self.mock_ai_adapter
        
        # Mock database session
        self.db_patcher = patch('app.services.train_game.train_game_service.db')
        self.mock_db = self.db_patcher.start()
        
        # Mock models
        self.config_patcher = patch('app.services.train_game.train_game_service.TrainGameConfig')
        self.mock_config_model = self.config_patcher.start()
        
        self.session_patcher = patch('app.services.train_game.train_game_service.TrainGameSession')
        self.mock_session_model = self.session_patcher.start()

    def tearDown(self):
        self.ai_adapter_patcher.stop()
        self.db_patcher.stop()
        self.config_patcher.stop()
        self.session_patcher.stop()

    def test_get_config_existing(self):
        # Setup
        user_id = 1
        mock_config = MagicMock()
        mock_config.to_dict.return_value = {"some": "config"}
        self.mock_config_model.query.filter_by.return_value.first.return_value = mock_config
        
        # Execute
        result = self.service.get_config(user_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['current_config'], {"some": "config"})
        self.mock_config_model.query.filter_by.assert_called_with(user_id=user_id)

    def test_get_config_new(self):
        # Setup
        user_id = 1
        self.mock_config_model.query.filter_by.return_value.first.return_value = None
        
        initial_config = {
            'train_speed': 1.0,
            'spawn_rate': 2.0,
            'total_trains': 5,
            'color_count': 2,
            'time_limit': 60,
            'difficulty_label': 'Easy'
        }
        self.mock_ai_adapter.get_initial_config.return_value = initial_config
        
        # Execute
        result = self.service.get_config(user_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_db.session.add.assert_called()
        self.mock_db.session.commit.assert_called()

    def test_submit_results(self):
        # Setup
        user_id = 1
        session_data = {
            'total_spawned': 10,
            'correct_routing': 8,
            'wrong_routing': 2,
            'crash_count': 0,
            'completion_status': 'completed'
        }
        
        mock_config = MagicMock()
        mock_config.to_dict.return_value = {'current': 'config'}
        self.mock_config_model.query.filter_by.return_value.first.return_value = mock_config
        
        next_config = {
            'train_speed': 1.5,
            'spawn_rate': 2.5,
            'total_trains': 6,
            'color_count': 3,
            'time_limit': 55,
            'difficulty_label': 'Medium'
        }
        self.mock_ai_adapter.analyze_performance.return_value = {'next_config': next_config}
        
        # Execute
        result = self.service.submit_results(user_id, session_data)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_db.session.add.assert_called() # Should add session
        self.mock_db.session.commit.assert_called()
        
        # Verify config update
        self.assertEqual(mock_config.train_speed, next_config['train_speed'])
        self.assertEqual(mock_config.difficulty_label, next_config['difficulty_label'])

    def test_get_stats_empty(self):
        # Setup
        user_id = 1
        self.mock_session_model.query.filter_by.return_value.all.return_value = []
        
        # Execute
        result = self.service.get_stats(user_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['total_sessions'], 0)

    def test_get_stats_with_data(self):
        # Setup
        user_id = 1
        s1 = MagicMock()
        s1.correct_routing = 10
        s1.wrong_routing = 0
        s1.to_dict.return_value = {'id': 1}
        
        s2 = MagicMock()
        s2.correct_routing = 5
        s2.wrong_routing = 5
        s2.to_dict.return_value = {'id': 2}
        
        self.mock_session_model.query.filter_by.return_value.all.return_value = [s1, s2]
        
        # Execute
        result = self.service.get_stats(user_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['total_sessions'], 2)
        self.assertEqual(result['data']['total_trains_routed'], 15)
        self.assertEqual(result['data']['average_accuracy'], 75.0)

if __name__ == '__main__':
    unittest.main()
