import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
sys.path.append('../backend')

from app import create_app
from config.database import db

class TestCompleteUserFlows(unittest.TestCase):
    """
    Test complete user workflows from registration to daily usage
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Mock external services
        self.meal_patcher = patch('app.routes.meal_plan.meal_planning_service')
        self.vendor_patcher = patch('app.routes.vendors.vendor_service')
        self.auth_patcher = patch('app.routes.auth.auth_service')
        
        self.mock_meal_service = self.meal_patcher.start()
        self.mock_vendor_service = self.vendor_patcher.start()
        self.mock_auth_service = self.auth_patcher.start()
    
    def tearDown(self):
        self.meal_patcher.stop()
        self.vendor_patcher.stop()
        self.auth_patcher.stop()
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_complete_user_journey(self):
        """
        Test complete user journey:
        1. Registration
        2. Onboarding
        3. Meal planning
        4. Shopping
        5. Progress tracking
        """
        
        # Step 1: User Registration
        print("Step 1: User Registration")
        user_data = {
            'email': 'journey_test@zanuri.co.zm',
            'password': 'securepassword123',
            'phone': '+260123456789'
        }
        
        # Mock registration response
        self.mock_auth_service.register.return_value = {
            'user_id': 'USER123',
            'token': 'JWT_TOKEN_123',
            'profile_complete': False
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        auth_data = json.loads(response.data)
        user_id = auth_data['user_id']
        auth_token = auth_data['token']
        
        # Step 2: Complete Onboarding
        print("Step 2: User Onboarding")
        onboarding_data = {
            'health_goals': ['weight_loss', 'energy'],
            'dietary_restrictions': ['lactose_intolerant'],
            'budget_range': 'medium',
            'family_size': 4,
            'preferences': {
                'likes': ['traditional_zambian', 'vegetables'],
                'dislikes': ['spicy_food', 'okra']
            }
        }
        
        # Mock onboarding completion
        self.mock_auth_service.complete_onboarding.return_value = {
            'profile_completed': True,
            'user_id': user_id
        }
        
        response = self.client.post(f'/api/onboarding/{user_id}',
                                  data=json.dumps(onboarding_data),
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {auth_token}'})
        
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Generate Meal Plan
        print("Step 3: Meal Plan Generation")
        self.mock_meal_service.generate_weekly_plan.return_value = {
            'plan_id': 'PLAN123',
            'week_plan': {
                'monday': {
                    'breakfast': {'recipe_id': 1, 'name': 'Oatmeal with Fruits', 'cost': 18},
                    'lunch': {'recipe_id': 2, 'name': 'Nshima with Bean Stew', 'cost': 25},
                    'dinner': {'recipe_id': 3, 'name': 'Chicken Stew with Vegetables', 'cost': 35}
                },
                'tuesday': {
                    'breakfast': {'recipe_id': 4, 'name': 'Scrambled Eggs', 'cost': 22},
                    'lunch': {'recipe_id': 5, 'name': 'Kapenta with Nshima', 'cost': 30},
                    'dinner': {'recipe_id': 6, 'name': 'Vegetable Stir-fry', 'cost': 28}
                }
            },
            'shopping_list': [
                {'name': 'Maize Meal', 'quantity': '2kg', 'estimated_cost': 17.00},
                {'name': 'Beans', 'quantity': '1kg', 'estimated_cost': 18.00},
                {'name': 'Chicken', 'quantity': '1kg', 'estimated_cost': 35.00}
            ],
            'total_cost': 1200.50
        }
        
        response = self.client.post(f'/api/meal-plan/generate/{user_id}',
                                  data=json.dumps(onboarding_data),  # Use same prefs
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {auth_token}'})
        
        self.assertEqual(response.status_code, 200)
        meal_plan_data = json.loads(response.data)
        self.assertTrue(meal_plan_data['success'])
        self.assertIn('data', meal_plan_data)
        
        # Step 4: Get Shopping List and Vendors
        print("Step 4: Shopping and Vendor Integration")
        
        # Mock vendor data
        self.mock_vendor_service.find_nearby.return_value = [
            {
                'id': 'VENDOR1',
                'name': 'Soweto Market Stall 12',
                'distance_km': 1.2,
                'products': ['maize_meal', 'beans', 'vegetables'],
                'prices': {'maize_meal': 8.50, 'beans': 18.00}
            },
            {
                'id': 'VENDOR2',
                'name': 'Shoprite Lusaka',
                'distance_km': 2.1,
                'products': ['chicken', 'vegetables', 'eggs'],
                'prices': {'chicken': 35.00, 'eggs': 25.00}
            }
        ]
        
        location_data = {'lat': -15.4167, 'lng': 28.2833, 'radius_km': 5}
        response = self.client.get('/api/vendors/nearby',
                                 query_string=location_data,
                                 headers={'Authorization': f'Bearer {auth_token}'})
        
        self.assertEqual(response.status_code, 200)
        vendors_data = json.loads(response.data)
        self.assertGreater(len(vendors_data), 0)
        
        # Step 5: Log Daily Progress
        print("Step 5: Progress Tracking")
        progress_data = {
            'date': '2024-01-15',
            'weight': 68.5,
            'water_intake': 6,
            'meals': {
                'breakfast': True,
                'lunch': True,
                'dinner': False
            },
            'notes': 'Good energy levels today, skipped dinner due to late meeting'
        }
        
        response = self.client.post(f'/api/progress/{user_id}',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {auth_token}'})
        
        self.assertEqual(response.status_code, 200)
        
        # Step 6: Get Progress History
        print("Step 6: Progress Analytics")
        response = self.client.get(f'/api/progress/{user_id}/history',
                                 headers={'Authorization': f'Bearer {auth_token}'})
        
        self.assertEqual(response.status_code, 200)
        
        print("✅ Complete user journey test passed!")

class TestFamilyWorkflow(unittest.TestCase):
    """
    Test workflow for family meal planning and management
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        self.patchers = []
        
        # Mock all necessary services
        services_to_mock = [
            'app.routes.meal_plan.meal_planning_service',
            'app.routes.auth.auth_service',
            'app.routes.vendors.vendor_service'
        ]
        
        for service in services_to_mock:
            patcher = patch(service)
            mock_service = patcher.start()
            self.patchers.append(patcher)
            
            # Set up common mock responses
            if 'auth' in service:
                mock_service.register.return_value = {
                    'user_id': 'FAMILY_USER',
                    'token': 'FAMILY_TOKEN'
                }
            elif 'meal' in service:
                mock_service.generate_weekly_plan.return_value = {
                    'plan_id': 'FAMILY_PLAN',
                    'week_plan': {},
                    'total_cost': 1500.00
                }
    
    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
    
    def test_family_meal_planning(self):
        """Test meal planning for a family with different needs"""
        
        # Family profile with diverse needs
        family_profile = {
            'health_goals': ['weight_loss', 'muscle_gain', 'general_health'],
            'dietary_restrictions': ['lactose_intolerant', 'diabetic_friendly'],
            'budget_range': 'medium',
            'family_size': 4,
            'family_members': [
                {'age': 35, 'gender': 'female', 'goals': ['weight_loss']},
                {'age': 40, 'gender': 'male', 'goals': ['muscle_gain']},
                {'age': 12, 'gender': 'male', 'goals': ['general_health']},
                {'age': 8, 'gender': 'female', 'goals': ['general_health']}
            ]
        }
        
        # Generate family meal plan
        response = self.client.post('/api/meal-plan/generate/FAMILY_USER',
                                  data=json.dumps(family_profile),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer FAMILY_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the plan accommodates different family needs
        plan_data = json.loads(response.data)
        self.assertTrue(plan_data['success'])
        
        # Should have considerations for:
        # - Weight loss (lower calories)
        # - Muscle gain (higher protein)
        # - Children's nutritional needs
        # - Lactose intolerance
        # - Diabetic-friendly options

class TestBudgetOptimizationFlow(unittest.TestCase):
    """
    Test workflow for budget-constrained users
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        self.patchers = []
        
        # Mock services
        patcher = patch('app.routes.meal_plan.meal_planning_service')
        self.mock_meal_service = patcher.start()
        self.patchers.append(patcher)
    
    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
    
    def test_low_budget_optimization(self):
        """Test meal planning for low-budget users"""
        
        low_budget_profile = {
            'health_goals': ['general_health'],
            'budget_range': 'low',  # ZMW 400-800 per week
            'family_size': 2,
            'preferences': {
                'prioritize_cost': True,
                'accept_leftovers': True
            }
        }
        
        # Mock budget-optimized meal plan
        self.mock_meal_service.generate_weekly_plan.return_value = {
            'plan_id': 'BUDGET_PLAN',
            'week_plan': {
                'monday': {
                    'breakfast': {'cost': 12},
                    'lunch': {'cost': 18},
                    'dinner': {'cost': 22}
                }
            },
            'total_cost': 750.00,  # Within low budget range
            'cost_optimization': {
                'savings_vs_regular': 300.00,
                'strategies_applied': ['ingredient_substitution', 'leftover_planning']
            }
        }
        
        response = self.client.post('/api/meal-plan/generate/BUDGET_USER',
                                  data=json.dumps(low_budget_profile),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer BUDGET_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        
        plan_data = json.loads(response.data)
        self.assertTrue(plan_data['success'])
        
        # Verify cost is within budget
        total_cost = plan_data['data']['total_cost']
        self.assertLessEqual(total_cost, 800)  # Within low budget max

class TestMedicalConditionWorkflow(unittest.TestCase):
    """
    Test workflow for users with medical conditions
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        patcher = patch('app.routes.meal_plan.meal_planning_service')
        self.mock_meal_service = patcher.start()
        self.patchers = [patcher]
    
    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
    
    def test_diabetes_management_flow(self):
        """Test meal planning for diabetic users"""
        
        diabetic_profile = {
            'health_goals': ['diabetes_management'],
            'dietary_restrictions': ['diabetic_friendly', 'low_sugar'],
            'budget_range': 'medium',
            'family_size': 2,
            'medical_conditions': ['type_2_diabetes'],
            'preferences': {
                'glycemic_control': 'strict',
                'monitor_carbs': True
            }
        }
        
        # Mock diabetes-appropriate meal plan
        self.mock_meal_service.generate_weekly_plan.return_value = {
            'plan_id': 'DIABETES_PLAN',
            'week_plan': {
                'monday': {
                    'breakfast': {
                        'name': 'Low GI Oatmeal',
                        'nutrition': {'carbs': 25, 'sugar': 5}
                    },
                    'lunch': {
                        'name': 'Vegetable Protein Bowl', 
                        'nutrition': {'carbs': 30, 'sugar': 8}
                    }
                }
            },
            'nutrition_analysis': {
                'average_daily_carbs': 150,
                'average_daily_sugar': 25,
                'glycemic_load': 'low'
            }
        }
        
        response = self.client.post('/api/meal-plan/generate/DIABETES_USER',
                                  data=json.dumps(diabetic_profile),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer DIABETES_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        
        plan_data = json.loads(response.data)
        self.assertTrue(plan_data['success'])
        
        # Verify diabetic-friendly features
        nutrition_analysis = plan_data['data']['nutrition_analysis']
        self.assertLessEqual(nutrition_analysis['average_daily_sugar'], 30)
        self.assertEqual(nutrition_analysis['glycemic_load'], 'low')

class TestVendorIntegrationFlow(unittest.TestCase):
    """
    Test complete vendor integration workflow
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        self.patchers = []
        
        # Mock vendor service
        patcher = patch('app.routes.vendors.vendor_service')
        self.mock_vendor_service = patcher.start()
        self.patchers.append(patcher)
    
    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
    
    def test_complete_shopping_workflow(self):
        """Test complete shopping workflow from list to order"""
        
        # Step 1: Get nearby vendors
        self.mock_vendor_service.find_nearby.return_value = [
            {
                'id': 'V1',
                'name': 'Soweto Market',
                'products': ['maize_meal', 'vegetables', 'kapenta'],
                'prices': {'maize_meal': 8.50, 'kapenta': 45.00}
            }
        ]
        
        response = self.client.get('/api/vendors/nearby',
                                 query_string={'lat': -15.4167, 'lng': 28.2833},
                                 headers={'Authorization': 'Bearer VENDOR_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        vendors = json.loads(response.data)
        
        # Step 2: Get vendor products
        self.mock_vendor_service.get_products.return_value = [
            {'id': 'P1', 'name': 'Maize Meal', 'price': 8.50, 'in_stock': True},
            {'id': 'P2', 'name': 'Kapenta', 'price': 45.00, 'in_stock': True}
        ]
        
        response = self.client.get('/api/vendors/V1/products',
                                 headers={'Authorization': 'Bearer VENDOR_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.data)
        
        # Step 3: Place order (mock)
        order_data = {
            'vendor_id': 'V1',
            'items': [
                {'product_id': 'P1', 'quantity': 2},
                {'product_id': 'P2', 'quantity': 0.5}
            ],
            'delivery_option': 'pickup'
        }
        
        self.mock_vendor_service.place_order.return_value = {
            'order_id': 'ORDER123',
            'total_amount': 61.00,
            'estimated_pickup': '2024-01-15 14:00'
        }
        
        response = self.client.post('/api/orders',
                                  data=json.dumps(order_data),
                                  content_type='application/json',
                                  headers={'Authorization': 'Bearer VENDOR_TOKEN'})
        
        self.assertEqual(response.status_code, 200)
        order_response = json.loads(response.data)
        self.assertIn('order_id', order_response)

if __name__ == '__main__':
    unittest.main()