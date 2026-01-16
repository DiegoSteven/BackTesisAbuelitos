import unittest
import json
import os

# Set testing environment BEFORE importing app
os.environ['FLASK_ENV'] = 'testing'

from app import app, db
from models.user import User
from models.train_game import TrainGameConfig, TrainGameSession

class TestTrainGame(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            # Create test user
            user = User(nombre="TestUser", password="password", edad=70, genero="M")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_initial_config(self):
        """Test 1: Initial config should be Easy (3 colors)"""
        response = self.app.get(f'/train-game/config/{self.user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        config = data['data']['current_config']
        
        self.assertEqual(config['color_count'], 3)
        self.assertEqual(config['difficulty_label'], 'easy')
        print("\n✅ Test 1 Passed: Initial config is Easy (3 colors)")

    def test_level_up_logic(self):
        """Test 2: High accuracy should increase difficulty"""
        # 1. Get initial config
        self.app.get(f'/train-game/config/{self.user_id}')
        
        # 2. Submit perfect results (10/10 correct)
        session_data = {
            "train_speed": 3.0,
            "color_count": 3,
            "spawn_rate": 5.0,
            "total_spawned": 10,
            "correct_routing": 10,
            "wrong_routing": 0,
            "completion_status": "completed"
        }
        
        response = self.app.post('/train-game/submit-results', 
                               json={"user_id": self.user_id, "session_data": session_data})
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        analysis = data['data']['ai_analysis']
        
        # Should decide to increase difficulty
        self.assertEqual(analysis['decision'], 'increase_difficulty')
        
        # Check next config (Priority 1: Speed increase)
        next_config = analysis['next_config']
        self.assertGreater(next_config['train_speed'], 3.0)
        print(f"\n✅ Test 2 Passed: Level Up triggered. New Speed: {next_config['train_speed']}")

    def test_level_down_logic(self):
        """Test 3: Low accuracy should decrease difficulty"""
        # 1. Set difficulty to Medium manually
        with app.app_context():
            config = TrainGameConfig.query.filter_by(user_id=self.user_id).first()
            if not config:
                config = TrainGameConfig(user_id=self.user_id)
                db.session.add(config)
            config.color_count = 4 # Medium
            config.train_speed = 5.0
            db.session.commit()
            
        # 2. Submit bad results (2/10 correct)
        session_data = {
            "train_speed": 5.0,
            "color_count": 4,
            "spawn_rate": 5.0,
            "total_spawned": 10,
            "correct_routing": 2,
            "wrong_routing": 8,
            "completion_status": "completed"
        }
        
        response = self.app.post('/train-game/submit-results', 
                               json={"user_id": self.user_id, "session_data": session_data})
        data = json.loads(response.data)
        
        analysis = data['data']['ai_analysis']
        
        # Should decide to decrease difficulty
        self.assertEqual(analysis['decision'], 'decrease_difficulty')
        
        # Check next config (Priority 1: Decrease colors)
        next_config = analysis['next_config']
        self.assertEqual(next_config['color_count'], 3)
        print(f"\n✅ Test 3 Passed: Level Down triggered. Colors reduced to: {next_config['color_count']}")

if __name__ == '__main__':
    unittest.main()
