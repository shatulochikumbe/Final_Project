import unittest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append('../backend/app/services/ai_engine')

from meal_recommender import HybridRecommendationEngine, ZambianMealRecommender
from data_preprocessing import MealDataPreprocessor

class TestHybridRecommendationEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = HybridRecommendationEngine()
        self.recipe_features = [
            {
                'recipe_id': 1,
                'name': 'Nshima with Ifisashi',
                'preparation_time': 45,
                'cost_per_serving': 55.50,
                'calories': 450,
                'protein': 12,
                'is_traditional': 1,
                'is_zambian': 1
            },
            {
                'recipe_id': 2,
                'name': 'Kapenta with Nshima',
                'preparation_time': 30,
                'cost_per_serving': 65.25,
                'calories': 380,
                'protein': 25,
                'is_traditional': 1,
                'is_zambian': 1
            }
        ]
    
    def test_content_based_model_building(self):
        """Test building content-based similarity matrix"""
        similarity_matrix = self.engine.build_content_based_model(
            self.recipe_features
        )
        
        self.assertIsNotNone(similarity_matrix)
        self.assertEqual(
            similarity_matrix.shape[0], 
            len(self.recipe_features)
        )
        self.assertEqual(
            similarity_matrix.shape[1], 
            len(self.recipe_features)
        )
    
    def test_content_based_recommendations(self):
        """Test content-based recipe recommendations"""
        self.engine.build_content_based_model(self.recipe_features)
        
        recommendations = self.engine.content_based_recommendations(
            recipe_id=1, 
            top_n=5
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
        
        for rec in recommendations:
            self.assertIn('recipe_id', rec)
            self.assertIn('similarity_score', rec)
    
    def test_hybrid_recommendations(self):
        """Test hybrid recommendation generation"""
        user_preferences = {
            'health_goals': ['weight_loss'],
            'budget_range': 'medium',
            'dietary_restrictions': [],
            'preferred_recipes': [1]
        }
        
        with patch.object(self.engine, 'apply_user_constraints') as mock_filter:
            mock_filter.return_value = self.recipe_features
            
            recommendations = self.engine.hybrid_recommendations(
                user_id=1,
                user_preferences=user_preferences,
                top_n=10
            )
            
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), 10)
            
            for rec in recommendations:
                self.assertIn('recipe_id', rec)
                self.assertIn('score', rec)
                self.assertIn('nutrition_score', rec)
    
    def test_recipe_scoring(self):
        """Test recipe scoring algorithm"""
        recipe = {
            'name': 'Test Recipe',
            'nutrition_facts': {'calories': 350, 'protein': 20, 'sugar': 5},
            'cost_per_serving': 18,
            'preparation_time': 30,
            'cultural_tags': ['zambian', 'traditional']
        }
        
        user_preferences = {
            'health_goals': ['weight_loss'],
            'budget_range': 'medium',
            'available_time': 'medium'
        }
        
        score = self.engine.calculate_recipe_score(recipe, user_preferences)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
    
    def test_nutrition_score_calculation(self):
        """Test nutrition score calculation"""
        recipe = {
            'nutrition_facts': {
                'calories': 350,
                'protein': 25,
                'carbs': 45,
                'fats': 10,
                'fiber': 8,
                'sugar': 12
            }
        }
        
        user_preferences = {
            'health_goals': ['weight_loss', 'muscle_gain']
        }
        
        nutrition_score = self.engine.calculate_nutrition_score(
            recipe, 
            user_preferences
        )
        
        self.assertIsInstance(nutrition_score, float)
        self.assertGreaterEqual(nutrition_score, 0)
        self.assertLessEqual(nutrition_score, 1)

class TestZambianMealRecommender(unittest.TestCase):
    
    def setUp(self):
        self.zambian_recommender = ZambianMealRecommender()
        self.user_preferences = {
            'health_goals': ['weight_loss'],
            'budget_range': 'medium',
            'family_size': 4
        }
    
    def test_weekly_plan_generation(self):
        """Test Zambian weekly meal plan generation"""
        with patch.object(self.zambian_recommender, 'hybrid_recommendations') as mock_rec:
            mock_rec.side_effect = [
                [{'recipe_id': 1, 'name': 'Oatmeal'}],  # breakfast
                [{'recipe_id': 2, 'name': 'Nshima with Beans'}],  # lunch
                [{'recipe_id': 3, 'name': 'Chicken Stew'}]   # dinner
            ]
            
            weekly_plan = self.zambian_recommender.generate_weekly_plan(
                self.user_preferences
            )
            
            self.assertIsInstance(weekly_plan, dict)
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            for day in days:
                self.assertIn(day, weekly_plan)
                day_plan = weekly_plan[day]
                self.assertIn('breakfast', day_plan)
                self.assertIn('lunch', day_plan)
                self.assertIn('dinner', day_plan)
    
    def test_recipe_filtering_zambian(self):
        """Test filtering recipes for Zambian context"""
        recipes = [
            {
                'id': 1,
                'name': 'Nshima with Ifisashi',
                'cultural_tags': ['zambian', 'traditional'],
                'ingredients': ['maize_meal', 'rape_leaves']
            },
            {
                'id': 2,
                'name': 'Pizza',
                'cultural_tags': ['international'],
                'ingredients': ['flour', 'cheese', 'tomato_sauce']
            },
            {
                'id': 3,
                'name': 'Kapenta with Nshima',
                'cultural_tags': ['zambian'],
                'ingredients': ['kapenta', 'maize_meal']
            }
        ]
        
        filtered = self.zambian_recommender.filter_recipes(
            recipes, 
            ['weight_loss'], 
            [], 
            'medium'
        )
        
        # Should prioritize Zambian recipes
        zambian_recipes = [r for r in filtered if 'zambian' in r.get('cultural_tags', [])]
        self.assertGreater(len(zambian_recipes), 0)

class TestMealDataPreprocessor(unittest.TestCase):
    
    def setUp(self):
        self.preprocessor = MealDataPreprocessor()
    
    def test_zambian_foods_loading(self):
        """Test loading and processing Zambian food data"""
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            with patch('json.load') as mock_json:
                mock_json.return_value = {
                    'foods': [
                        {
                            'id': 'ZM001',
                            'name': 'Maize Meal',
                            'nutrients_per_100g': {
                                'calories': 365,
                                'protein': 7.0,
                                'carbs': 79.0
                            }
                        }
                    ]
                }
                
                foods_df = self.preprocessor.load_zambian_foods('dummy_path.json')
                
                self.assertIsNotNone(foods_df)
                self.assertIn('nutrient_calories', foods_df.columns)
                self.assertIn('nutrient_protein', foods_df.columns)
                self.assertIn('nutrient_carbs', foods_df.columns)
    
    def test_recipe_feature_creation(self):
        """Test creating feature matrix from recipes"""
        recipes_df = Mock()
        recipes_df.itertuples.return_value = [
            Mock(
                id=1,
                meal_type='dinner',
                preparation_time=45,
                difficulty_level='easy',
                cost_per_serving=55.50,
                ingredient_count=5,
                nutrition_facts={'calories': 450, 'protein': 12, 'carbs': 75, 'fats': 10, 'fiber': 8},
                cultural_tags=['traditional', 'zambian']
            )
        ]
        
        features_df = self.preprocessor.create_meal_features(recipes_df)
        
        self.assertIsNotNone(features_df)
        self.assertIn('recipe_id', features_df.columns)
        self.assertIn('calories', features_df.columns)
        self.assertIn('is_traditional', features_df.columns)
        self.assertIn('is_zambian', features_df.columns)
    
    def test_user_data_preprocessing(self):
        """Test preprocessing user profile data"""
        users_df = Mock()
        users_df.columns = ['budget_range', 'health_goals', 'family_size']
        users_df.__getitem__.return_value = Mock()
        
        processed_users = self.preprocessor.preprocess_user_data(users_df)
        
        self.assertIsNotNone(processed_users)
        # Should have encoded categorical variables and normalized numerical ones

class TestAIModelEvaluation(unittest.TestCase):
    
    def setUp(self):
        from model_evaluation import ModelEvaluator
        
        self.mock_engine = Mock()
        self.test_data = Mock()
        self.evaluator = ModelEvaluator(self.mock_engine, self.test_data)
    
    def test_precision_recall_evaluation(self):
        """Test precision and recall evaluation"""
        self.test_data.__getitem__.return_value = Mock()
        self.test_data['user_id'].unique.return_value = [1]
        
        self.mock_engine.hybrid_recommendations.return_value = [
            {'recipe_id': 1, 'score': 0.8},
            {'recipe_id': 2, 'score': 0.7}
        ]
        
        self.evaluator.get_user_preferences = Mock(return_value={
            'health_goals': ['weight_loss'],
            'preferred_recipes': [1, 3]
        })
        
        metrics = self.evaluator.evaluate_precision_recall(k=5)
        
        self.assertIn('precision@k', metrics)
        self.assertIn('recall@k', metrics)
        self.assertIn('f1@k', metrics)
        
        self.assertIsInstance(metrics['precision@k'], float)
        self.assertIsInstance(metrics['recall@k'], float)
    
    def test_ndcg_evaluation(self):
        """Test NDCG evaluation"""
        self.test_data.__getitem__.return_value = Mock()
        self.test_data['user_id'].unique.return_value = [1]
        
        self.mock_engine.hybrid_recommendations.return_value = [
            {'recipe_id': 1, 'score': 0.9},
            {'recipe_id': 2, 'score': 0.8},
            {'recipe_id': 3, 'score': 0.7}
        ]
        
        self.evaluator.get_user_preferences = Mock(return_value={
            'health_goals': ['weight_loss']
        })
        
        ndcg_score = self.evaluator.evaluate_ndcg(k=5)
        
        self.assertIsInstance(ndcg_score, float)
        self.assertGreaterEqual(ndcg_score, 0)
        self.assertLessEqual(ndcg_score, 1)

if __name__ == '__main__':
    unittest.main()