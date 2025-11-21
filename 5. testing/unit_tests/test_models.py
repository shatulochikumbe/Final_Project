import unittest
import sys
import os
sys.path.append('../backend/app')

from models import User, Recipe, MealPlan, Vendor
from config.database import db

class TestUserModel(unittest.TestCase):
    
    def setUp(self):
        """Set up test database and sample data"""
        self.user_data = {
            'email': 'test@zanuri.co.zm',
            'password_hash': 'hashed_password_123',
            'phone': '+260123456789',
            'health_goals': ['weight_loss', 'energy'],
            'dietary_restrictions': ['lactose_intolerant'],
            'budget_range': 'medium',
            'family_size': 4
        }
    
    def test_user_creation(self):
        """Test creating a new user"""
        user = User.create(**self.user_data)
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'test@zanuri.co.zm')
        self.assertEqual(user.budget_range, 'medium')
        self.assertEqual(user.family_size, 4)
    
    def test_user_find_by_email(self):
        """Test finding user by email"""
        user = User.create(**self.user_data)
        found_user = User.find_by_email('test@zanuri.co.zm')
        
        self.assertEqual(found_user.id, user.id)
        self.assertEqual(found_user.email, user.email)
    
    def test_user_profile_completion(self):
        """Test user profile completion"""
        user = User.create(**self.user_data)
        updated_user = User.update_profile(user.id, {
            'health_goals': ['weight_loss', 'energy', 'muscle_gain'],
            'profile_completed': True
        })
        
        self.assertTrue(updated_user.profile_completed)
        self.assertEqual(len(updated_user.health_goals), 3)
    
    def test_user_authentication(self):
        """Test user password verification"""
        from werkzeug.security import check_password_hash
        
        user = User.create(**self.user_data)
        self.assertTrue(check_password_hash(user.password_hash, 'hashed_password_123'))

class TestRecipeModel(unittest.TestCase):
    
    def setUp(self):
        self.recipe_data = {
            'name': 'Test Nshima with Ifisashi',
            'ingredients': [
                {'name': 'maize_meal', 'quantity': 2, 'unit': 'cups'},
                {'name': 'rape_leaves', 'quantity': 1, 'unit': 'bunch'}
            ],
            'nutrition_facts': {
                'calories': 450,
                'protein': 12,
                'carbs': 75
            },
            'meal_type': 'dinner',
            'preparation_time': 45
        }
    
    def test_recipe_creation(self):
        """Test creating a new recipe"""
        recipe = Recipe.create(**self.recipe_data)
        
        self.assertIsNotNone(recipe.id)
        self.assertEqual(recipe.name, 'Test Nshima with Ifisashi')
        self.assertEqual(recipe.meal_type, 'dinner')
        self.assertEqual(len(recipe.ingredients), 2)
    
    def test_recipe_nutrition_calculation(self):
        """Test recipe nutrition calculations"""
        recipe = Recipe.create(**self.recipe_data)
        
        self.assertEqual(recipe.nutrition_facts['calories'], 450)
        self.assertEqual(recipe.nutrition_facts['protein'], 12)
    
    def test_recipe_search_by_ingredients(self):
        """Test searching recipes by ingredients"""
        recipe = Recipe.create(**self.recipe_data)
        
        # Test search for recipes with maize_meal
        recipes_with_maize = Recipe.search_by_ingredients(['maize_meal'])
        self.assertGreaterEqual(len(recipes_with_maize), 1)
        
        # Test search for non-existent ingredient
        recipes_with_beef = Recipe.search_by_ingredients(['beef'])
        self.assertEqual(len(recipes_with_beef), 0)

class TestMealPlanModel(unittest.TestCase):
    
    def setUp(self):
        self.user = User.create({
            'email': 'mealplan_test@zanuri.co.zm',
            'password_hash': 'test_hash'
        })
        
        self.meal_plan_data = {
            'user_id': self.user.id,
            'week_plan': {
                'monday': {
                    'breakfast': {'recipe_id': 1, 'recipe_name': 'Oatmeal'},
                    'lunch': {'recipe_id': 2, 'recipe_name': 'Nshima with Beans'},
                    'dinner': {'recipe_id': 3, 'recipe_name': 'Chicken Stew'}
                }
            },
            'total_estimated_cost': 1200.50
        }
    
    def test_meal_plan_creation(self):
        """Test creating a meal plan"""
        meal_plan = MealPlan.create(**self.meal_plan_data)
        
        self.assertIsNotNone(meal_plan.id)
        self.assertEqual(meal_plan.user_id, self.user.id)
        self.assertEqual(meal_plan.total_estimated_cost, 1200.50)
        self.assertIn('monday', meal_plan.week_plan)
    
    def test_meal_plan_cost_calculation(self):
        """Test meal plan cost calculations"""
        meal_plan = MealPlan.create(**self.meal_plan_data)
        
        # Test cost per day calculation
        cost_per_day = meal_plan.calculate_cost_per_day()
        self.assertIsInstance(cost_per_day, dict)
        self.assertIn('monday', cost_per_day)
    
    def test_meal_plan_shopping_list(self):
        """Test shopping list generation from meal plan"""
        meal_plan = MealPlan.create(**self.meal_plan_data)
        shopping_list = meal_plan.generate_shopping_list()
        
        self.assertIsInstance(shopping_list, list)
        # Should contain aggregated ingredients from all recipes

class TestVendorModel(unittest.TestCase):
    
    def setUp(self):
        self.vendor_data = {
            'name': 'Soweto Market Stall 12',
            'type': 'local_market',
            'location': 'POINT(28.2833 -15.4167)',
            'products': ['maize_meal', 'vegetables', 'kapenta'],
            'rating': 4.5
        }
    
    def test_vendor_creation(self):
        """Test creating a vendor"""
        vendor = Vendor.create(**self.vendor_data)
        
        self.assertIsNotNone(vendor.id)
        self.assertEqual(vendor.name, 'Soweto Market Stall 12')
        self.assertEqual(vendor.type, 'local_market')
        self.assertEqual(vendor.rating, 4.5)
    
    def test_vendor_nearby_search(self):
        """Test finding nearby vendors"""
        vendor = Vendor.create(**self.vendor_data)
        
        # Test search with Lusaka coordinates
        nearby_vendors = Vendor.find_nearby(
            lat=-15.4167, 
            lng=28.2833, 
            radius_km=5
        )
        
        self.assertGreaterEqual(len(nearby_vendors), 1)
    
    def test_vendor_product_search(self):
        """Test searching vendors by products"""
        vendor = Vendor.create(**self.vendor_data)
        
        vendors_with_maize = Vendor.search_by_products(['maize_meal'])
        self.assertGreaterEqual(len(vendors_with_maize), 1)

if __name__ == '__main__':
    unittest.main()