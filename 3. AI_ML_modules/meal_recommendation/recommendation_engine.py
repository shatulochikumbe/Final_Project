import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, Concatenate, Dropout
import warnings
warnings.filterwarnings('ignore')

class HybridRecommendationEngine:
    def __init__(self):
        self.content_similarity_matrix = None
        self.collaborative_model = None
        self.recipe_features = None
        self.user_profiles = None
        self.scaler = StandardScaler()
        
    def build_content_based_model(self, recipe_features):
        """Build content-based filtering model"""
        self.recipe_features = recipe_features
        
        # Select numerical features for similarity calculation
        feature_columns = [
            'preparation_time', 'cost_per_serving', 'ingredient_count',
            'calories', 'protein', 'carbs', 'fats', 'fiber',
            'is_traditional', 'is_zambian', 'is_modern'
        ]
        
        # Get available columns
        available_columns = [col for col in feature_columns if col in recipe_features.columns]
        
        if available_columns:
            feature_matrix = recipe_features[available_columns].values
            feature_matrix = self.scaler.fit_transform(feature_matrix)
            
            # Calculate cosine similarity between recipes
            self.content_similarity_matrix = cosine_similarity(feature_matrix)
        
        return self.content_similarity_matrix
    
    def build_collaborative_model(self, num_users, num_recipes, embedding_size=50):
        """Build neural collaborative filtering model"""
        # User input
        user_input = Input(shape=(1,), name='user_input')
        user_embedding = Embedding(num_users, embedding_size, name='user_embedding')(user_input)
        user_vec = Flatten()(user_embedding)
        
        # Recipe input
        recipe_input = Input(shape=(1,), name='recipe_input')
        recipe_embedding = Embedding(num_recipes, embedding_size, name='recipe_embedding')(recipe_input)
        recipe_vec = Flatten()(recipe_embedding)
        
        # Concatenate features
        concat = Concatenate()([user_vec, recipe_vec])
        
        # Add dense layers
        dense1 = Dense(128, activation='relu')(concat)
        dropout1 = Dropout(0.2)(dense1)
        dense2 = Dense(64, activation='relu')(dropout1)
        dropout2 = Dropout(0.2)(dense2)
        output = Dense(1, activation='sigmoid')(dropout2)
        
        # Build model
        self.collaborative_model = Model(
            inputs=[user_input, recipe_input],
            outputs=output
        )
        
        self.collaborative_model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return self.collaborative_model
    
    def content_based_recommendations(self, recipe_id, top_n=10):
        """Get content-based recommendations"""
        if self.content_similarity_matrix is None:
            raise ValueError("Content-based model not built. Call build_content_based_model first.")
        
        # Get similarity scores for the given recipe
        recipe_idx = self.recipe_features[
            self.recipe_features['recipe_id'] == recipe_id
        ].index[0]
        
        similarity_scores = list(enumerate(self.content_similarity_matrix[recipe_idx]))
        
        # Sort by similarity score
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar recipes (excluding the input recipe itself)
        similar_recipes = []
        for i, score in similarity_scores[1:top_n+1]:
            similar_recipe_id = self.recipe_features.iloc[i]['recipe_id']
            similar_recipes.append({
                'recipe_id': similar_recipe_id,
                'similarity_score': score
            })
        
        return similar_recipes
    
    def hybrid_recommendations(self, user_id, user_preferences, top_n=15):
        """Generate hybrid recommendations using both content-based and collaborative filtering"""
        recommendations = []
        
        # Content-based filtering based on user preferences
        if user_preferences.get('preferred_recipes'):
            # If user has preferred recipes, use content-based filtering
            content_recs = []
            for recipe_id in user_preferences['preferred_recipes'][:3]:
                content_recs.extend(self.content_based_recommendations(recipe_id, top_n=5))
            
            # Aggregate and deduplicate content-based recommendations
            content_scores = {}
            for rec in content_recs:
                if rec['recipe_id'] in content_scores:
                    content_scores[rec['recipe_id']] += rec['similarity_score']
                else:
                    content_scores[rec['recipe_id']] = rec['similarity_score']
        
        # Apply user constraints
        filtered_recipes = self.apply_user_constraints(user_preferences)
        
        # Score recipes based on multiple factors
        for recipe in filtered_recipes:
            score = self.calculate_recipe_score(recipe, user_preferences)
            
            recommendations.append({
                'recipe_id': recipe['id'],
                'name': recipe['name'],
                'score': score,
                'meal_type': recipe['meal_type'],
                'preparation_time': recipe['preparation_time'],
                'cost_per_serving': recipe.get('cost_per_serving', 0),
                'nutrition_score': self.calculate_nutrition_score(recipe, user_preferences)
            })
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]
    
    def apply_user_constraints(self, user_preferences):
        """Apply user dietary and budget constraints"""
        # This would filter the recipe database based on user preferences
        # For now, return all recipes (in practice, this would query the database)
        return []  # Placeholder
    
    def calculate_recipe_score(self, recipe, user_preferences):
        """Calculate overall score for a recipe based on user preferences"""
        score = 0.0
        
        # Budget alignment
        user_budget = user_preferences.get('budget_range', 'medium')
        recipe_cost = recipe.get('cost_per_serving', 0)
        
        if user_budget == 'low' and recipe_cost <= 15:
            score += 0.3
        elif user_budget == 'medium' and recipe_cost <= 25:
            score += 0.3
        elif user_budget == 'high':
            score += 0.3
        
        # Health goals alignment
        health_goals = user_preferences.get('health_goals', [])
        nutrition_facts = recipe.get('nutrition_facts', {})
        
        if 'weight_loss' in health_goals and nutrition_facts.get('calories', 0) <= 400:
            score += 0.2
        if 'muscle_gain' in health_goals and nutrition_facts.get('protein', 0) >= 20:
            score += 0.2
        if 'diabetes_management' in health_goals and nutrition_facts.get('sugar', 0) <= 10:
            score += 0.2
        
        # Preparation time alignment
        user_time_preference = user_preferences.get('available_time', 'medium')
        prep_time = recipe.get('preparation_time', 0)
        
        if user_time_preference == 'low' and prep_time <= 30:
            score += 0.1
        elif user_time_preference == 'medium' and prep_time <= 60:
            score += 0.1
        elif user_time_preference == 'high':
            score += 0.1
        
        # Cultural preference
        cultural_tags = recipe.get('cultural_tags', [])
        if 'zambian' in cultural_tags or 'traditional' in cultural_tags:
            score += 0.1
        
        return score
    
    def calculate_nutrition_score(self, recipe, user_preferences):
        """Calculate nutrition score based on user health goals"""
        nutrition_facts = recipe.get('nutrition_facts', {})
        health_goals = user_preferences.get('health_goals', [])
        
        score = 0.0
        max_score = 1.0
        
        # Weight loss goal
        if 'weight_loss' in health_goals:
            calories = nutrition_facts.get('calories', 0)
            if calories <= 400:
                score += 0.25
            elif calories <= 600:
                score += 0.15
        
        # Muscle gain goal
        if 'muscle_gain' in health_goals:
            protein = nutrition_facts.get('protein', 0)
            if protein >= 25:
                score += 0.25
            elif protein >= 15:
                score += 0.15
        
        # Diabetes management
        if 'diabetes_management' in health_goals:
            carbs = nutrition_facts.get('carbs', 0)
            fiber = nutrition_facts.get('fiber', 0)
            if carbs <= 30 and fiber >= 5:
                score += 0.25
            elif carbs <= 50 and fiber >= 3:
                score += 0.15
        
        # General health
        if 'general_health' in health_goals:
            # Balanced nutrition score
            protein = nutrition_facts.get('protein', 0)
            carbs = nutrition_facts.get('carbs', 0)
            fats = nutrition_facts.get('fats', 0)
            fiber = nutrition_facts.get('fiber', 0)
            
            if 10 <= protein <= 30 and 40 <= carbs <= 60 and 20 <= fats <= 40 and fiber >= 5:
                score += 0.25
        
        return min(score, max_score)

# Specialized recommendation engines
class ZambianMealRecommender(HybridRecommendationEngine):
    """Specialized recommender for Zambian cuisine"""
    
    def __init__(self):
        super().__init__()
        self.staple_foods = ['nshima', 'maize', 'cassava', 'sweet_potato']
    
    def generate_weekly_plan(self, user_preferences):
        """Generate a weekly meal plan following Zambian eating patterns"""
        weekly_plan = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            day_plan = {
                'breakfast': self.recommend_breakfast(user_preferences),
                'lunch': self.recommend_lunch(user_preferences),
                'dinner': self.recommend_dinner(user_preferences)
            }
            weekly_plan[day] = day_plan
        
        return weekly_plan
    
    def recommend_breakfast(self, user_preferences):
        """Recommend breakfast options"""
        # Zambian breakfast typically lighter, often tea with bread or leftovers
        breakfast_filters = {
            'meal_type': 'breakfast',
            'preparation_time__lte': 20,
            'cultural_tags__contains': ['zambian', 'quick']
        }
        return self.hybrid_recommendations(None, user_preferences, top_n=3)
    
    def recommend_lunch(self, user_preferences):
        """Recommend lunch options"""
        # Lunch often includes nshima with relish
        lunch_filters = {
            'meal_type': 'lunch',
            'cultural_tags__contains': ['zambian', 'traditional']
        }
        return self.hybrid_recommendations(None, user_preferences, top_n=3)
    
    def recommend_dinner(self, user_preferences):
        """Recommend dinner options"""
        # Dinner is typically the main meal with nshima
        dinner_filters = {
            'meal_type': 'dinner',
            'cultural_tags__contains': ['zambian', 'traditional']
        }
        return self.hybrid_recommendations(None, user_preferences, top_n=3)