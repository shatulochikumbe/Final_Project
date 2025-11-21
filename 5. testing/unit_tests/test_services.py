import unittest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append('../backend/app')

from services.meal_planning import MealPlanningService
from services.user_profiling import HealthProfileAnalyzer
from services.budget_optimizer import BudgetOptimizer

class TestMealPlanningService(unittest.TestCase):
    
    def setUp(self):
        self.meal_service = MealPlanningService()
        self.user_preferences = {
            'health_goals': ['weight_loss'],
            'dietary_restrictions': ['lactose_intolerant'],
            'budget_range': 'medium',
            'family_size': 4,
            'preferred_cuisines': ['zambian']
        }
    
    @patch('services.meal_planning.Recipe')
    @patch('services.meal_planning.MealPlan')
    def test_generate_weekly_plan(self, mock_mealplan, mock_recipe):
        """Test generating weekly meal plan"""
        # Mock recipe data
        mock_recipe.filter.return_value = [
            Mock(id=1, name='Nshima with Ifisashi', meal_type='dinner'),
            Mock(id=2, name='Oatmeal', meal_type='breakfast'),
            Mock(id=3, name='Bean Stew', meal_type='lunch')
        ]
        
        # Mock meal plan creation
        mock_mealplan.create.return_value = Mock(id=1, total_estimated_cost=1200.50)
        
        plan = self.meal_service.generate_weekly_plan(
            user_id=1, 
            preferences=self.user_preferences
        )
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan['plan_id'], 1)
        self.assertIn('week_plan', plan)
        self.assertIn('shopping_list', plan)
    
    def test_apply_user_constraints(self):
        """Test applying user constraints to recipes"""
        test_recipes = [
            {
                'id': 1,
                'name': 'Nshima with Milk',
                'ingredients': [{'name': 'maize_meal'}, {'name': 'milk'}],
                'nutrition_facts': {'calories': 500},
                'cost_per_serving': 20
            },
            {
                'id': 2,
                'name': 'Vegetable Stir-fry',
                'ingredients': [{'name': 'vegetables'}],
                'nutrition_facts': {'calories': 300},
                'cost_per_serving': 15
            }
        ]
        
        filtered = self.meal_service.apply_user_constraints(
            test_recipes, 
            self.user_preferences
        )
        
        # Should filter out lactose-containing recipes
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['name'], 'Vegetable Stir-fry')
    
    def test_calculate_recipe_score(self):
        """Test recipe scoring algorithm"""
        recipe = {
            'name': 'Test Recipe',
            'nutrition_facts': {'calories': 350, 'protein': 20},
            'cost_per_serving': 18,
            'preparation_time': 30
        }
        
        score = self.meal_service.calculate_recipe_score(
            recipe, 
            self.user_preferences
        )
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

class TestHealthProfileAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = HealthProfileAnalyzer()
        self.user_data = {
            'weight': 68,
            'height': 165,
            'age': 32,
            'gender': 'female',
            'activity_level': 'moderate'
        }
    
    def test_bmi_calculation(self):
        """Test BMI calculation and categorization"""
        bmi_info = self.analyzer.calculate_bmi_category(self.user_data)
        
        self.assertIn('bmi', bmi_info)
        self.assertIn('category', bmi_info)
        self.assertIn('risk', bmi_info)
        
        self.assertAlmostEqual(bmi_info['bmi'], 24.98, places=2)
        self.assertEqual(bmi_info['category'], 'normal')
    
    def test_nutritional_needs_calculation(self):
        """Test daily nutritional requirements calculation"""
        needs = self.analyzer.calculate_nutritional_needs(self.user_data)
        
        self.assertIn('daily_calories', needs)
        self.assertIn('protein_grams', needs)
        self.assertIn('carbs_grams', needs)
        self.assertIn('fat_grams', needs)
        
        self.assertIsInstance(needs['daily_calories'], int)
        self.assertIsInstance(needs['protein_grams'], int)
    
    def test_health_risk_assessment(self):
        """Test health risk assessment"""
        user_with_risks = {
            'weight': 95,
            'height': 165,
            'age': 62,
            'has_diabetes': True
        }
        
        risks = self.analyzer.assess_health_risks(user_with_risks)
        
        self.assertIsInstance(risks, list)
        self.assertGreater(len(risks), 0)
    
    def test_goal_alignment_assessment(self):
        """Test health goal alignment assessment"""
        health_goals = ['weight_loss', 'muscle_gain']
        alignment = self.analyzer.assess_goal_alignment(
            self.user_data, 
            health_goals
        )
        
        self.assertIsInstance(alignment, dict)
        self.assertIn('weight_loss', alignment)
        self.assertIn('muscle_gain', alignment)

class TestBudgetOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.optimizer = BudgetOptimizer()
        self.meal_plan = {
            'monday': {
                'breakfast': {'cost_per_serving': 15},
                'lunch': {'cost_per_serving': 25},
                'dinner': {'cost_per_serving': 35}
            },
            'tuesday': {
                'breakfast': {'cost_per_serving': 12},
                'lunch': {'cost_per_serving': 28},
                'dinner': {'cost_per_serving': 32}
            }
        }
    
    def test_meal_plan_cost_calculation(self):
        """Test total meal plan cost calculation"""
        total_cost = self.optimizer.calculate_meal_plan_cost(self.meal_plan)
        
        expected_cost = (15+25+35 + 12+28+32)
        self.assertEqual(total_cost, expected_cost)
    
    def test_budget_optimization(self):
        """Test meal plan budget optimization"""
        user_budget = 'medium'  # ZMW 1750 weekly
        family_size = 4
        current_cost = 2000  # Over budget
        
        optimized_plan = self.optimizer.optimize_meal_plan_cost(
            self.meal_plan, 
            user_budget, 
            family_size
        )
        
        self.assertIsNotNone(optimized_plan)
        # Should apply cost reduction strategies
    
    def test_ingredient_substitution(self):
        """Test expensive ingredient substitution"""
        meal = {
            'name': 'Test Meal',
            'ingredients': [
                {'name': 'imported_chicken', 'cost': 45},
                {'name': 'local_vegetables', 'cost': 10}
            ],
            'cost_per_serving': 55
        }
        
        substituted_meal, cost_reduction = self.optimizer.substitute_expensive_ingredients(
            [meal], 
            max_reduction=20
        )
        
        self.assertGreater(cost_reduction, 0)
        self.assertLess(substituted_meal[0]['cost_per_serving'], 55)
    
    def test_cost_prediction(self):
        """Test ingredient cost prediction"""
        from datetime import datetime
        
        predicted_cost = self.optimizer.predict_ingredient_cost(
            ingredient_name='maize_meal',
            category='grains',
            quantity=5,
            date=datetime(2024, 6, 1)  # Dry season
        )
        
        self.assertIsInstance(predicted_cost, float)
        self.assertGreater(predicted_cost, 0)

class TestPreferenceLearning(unittest.TestCase):
    
    def setUp(self):
        from services.preference_learning import PreferenceLearner
        self.learner = PreferenceLearner()
        
        self.user_interactions = [
            {
                'user_id': 1,
                'recipe_id': 1,
                'rating': 5,
                'recipe': {
                    'ingredients': ['maize_meal', 'rape_leaves'],
                    'cultural_tags': ['zambian', 'traditional'],
                    'meal_type': 'dinner'
                }
            },
            {
                'user_id': 1,
                'recipe_id': 2,
                'rating': 2,
                'recipe': {
                    'ingredients': ['imported_pasta', 'cheese'],
                    'cultural_tags': ['international'],
                    'meal_type': 'dinner'
                }
            }
        ]
    
    def test_preference_learning(self):
        """Test learning user preferences from interactions"""
        preferences = self.learner.learn_from_interactions(
            self.user_interactions, 
            recipes_df=Mock()
        )
        
        self.assertIn(1, preferences)
        user_prefs = preferences[1]
        
        self.assertIn('preferred_ingredients', user_prefs)
        self.assertIn('preferred_cuisines', user_prefs)
        self.assertIn('avoided_ingredients', user_prefs)
    
    def test_preference_updating(self):
        """Test updating preferences with new interactions"""
        new_interaction = {
            'user_id': 1,
            'recipe_id': 3,
            'rating': 4,
            'recipe': {
                'ingredients': ['beans', 'tomatoes'],
                'cultural_tags': ['zambian'],
                'meal_type': 'lunch'
            }
        }
        
        self.learner.update_preferences(1, new_interaction, Mock())
        
        # Should update preference weights for Zambian cuisine and ingredients

if __name__ == '__main__':
    unittest.main()