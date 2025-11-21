import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append('../backend')

from app import create_app
from config.database import db

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'OK')
        self.assertEqual(data['service'], 'ZaNuri API')
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            'email': 'test@zanuri.co.zm',
            'password': 'securepassword123',
            'phone': '+260123456789'
        }
        
        response = self.client.post('/api/auth/register', 
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('user_id', data)
        self.assertIn('token', data)
        self.assertFalse(data['profile_complete'])
    
    def test_user_login(self):
        """Test user login endpoint"""
        # First register a user
        user_data = {
            'email': 'login_test@zanuri.co.zm',
            'password': 'securepassword123'
        }
        
        self.client.post('/api/auth/register', 
                        data=json.dumps(user_data),
                        content_type='application/json')
        
        # Then test login
        login_data = {
            'email': 'login_test@zanuri.co.zm',
            'password': 'securepassword123'
        }
        
        response = self.client.post('/api/auth/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user_id', data)
    
    @patch('app.routes.meal_plan.meal_planning_service')
    def test_meal_plan_generation(self, mock_meal_service):
        """Test meal plan generation endpoint"""
        # Mock the meal planning service
        mock_meal_service.generate_weekly_plan.return_value = {
            'plan_id': 1,
            'week_plan': {
                'monday': {
                    'breakfast': {'recipe_id': 1, 'name': 'Oatmeal'},
                    'lunch': {'recipe_id': 2, 'name': 'Nshima with Beans'},
                    'dinner': {'recipe_id': 3, 'name': 'Chicken Stew'}
                }
            },
            'total_cost': 1200.50
        }
        
        user_preferences = {
            'health_goals': ['weight_loss'],
            'budget_range': 'medium',
            'family_size': 4
        }
        
        response = self.client.post('/api/meal-plan/generate/1',
                                  data=json.dumps(user_preferences),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer test_token'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['plan_id'], 1)
    
    @patch('app.routes.vendors.vendor_service')
    def test_nearby_vendors(self, mock_vendor_service):
        """Test nearby vendors endpoint"""
        mock_vendor_service.find_nearby.return_value = [
            {
                'id': 1,
                'name': 'Soweto Market Stall 12',
                'distance_km': 1.2,
                'products': ['maize_meal', 'vegetables']
            }
        ]
        
        location_data = {
            'lat': -15.4167,
            'lng': 28.2833,
            'radius_km': 5
        }
        
        response = self.client.get('/api/vendors/nearby',
                                 query_string=location_data)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['name'], 'Soweto Market Stall 12')
    
    def test_progress_logging(self):
        """Test progress logging endpoint"""
        progress_data = {
            'weight': 68.5,
            'water_intake': 6,
            'meals': {'breakfast': True, 'lunch': True, 'dinner': False},
            'notes': 'Feeling good today'
        }
        
        response = self.client.post('/api/progress/1',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer test_token'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    @patch('app.routes.meal_plan.meal_planning_service')
    def test_meal_plan_retrieval(self, mock_meal_service):
        """Test retrieving existing meal plan"""
        mock_meal_service.get_current_plan.return_value = {
            'id': 1,
            'week_plan': {'monday': {}},
            'total_estimated_cost': 1200.50
        }
        
        response = self.client.get('/api/meal-plan/1',
                                 headers={'Authorization': 'Bearer test_token'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint handling"""
        response = self.client.get('/api/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_authentication_required(self):
        """Test authentication requirement for protected endpoints"""
        response = self.client.get('/api/meal-plan/1')  # No auth header
        
        self.assertEqual(response.status_code, 401)
    
    def test_rate_limiting(self):
        """Test API rate limiting"""
        # Make multiple rapid requests to test rate limiting
        for i in range(10):
            response = self.client.get('/health')
            # Should handle up to reasonable number of requests
    
    @patch('app.routes.vendors.vendor_service')
    def test_vendor_products(self, mock_vendor_service):
        """Test vendor products endpoint"""
        mock_vendor_service.get_products.return_value = [
            {'id': 1, 'name': 'Maize Meal', 'price': 8.50, 'unit': 'kg'},
            {'id': 2, 'name': 'Rape Leaves', 'price': 10.00, 'unit': 'bunch'}
        ]
        
        response = self.client.get('/api/vendors/1/products')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Maize Meal')

class TestErrorHandling(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = self.client.post('/api/auth/register',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        user_data = {
            'email': 'test@zanuri.co.zm'
            # Missing password
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_server_error_handling(self):
        """Test server error handling"""
        with patch('app.routes.auth.User.create') as mock_create:
            mock_create.side_effect = Exception('Database error')
            
            user_data = {
                'email': 'test@zanuri.co.zm',
                'password': 'password123'
            }
            
            response = self.client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()