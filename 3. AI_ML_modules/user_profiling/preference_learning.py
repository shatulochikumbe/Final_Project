import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import json
from collections import defaultdict, Counter

class PreferenceLearner:
    def __init__(self):
        self.preference_models = {}
        self.ingredient_preferences = defaultdict(lambda: defaultdict(int))
        self.cuisine_preferences = defaultdict(lambda: defaultdict(int))
        self.meal_type_preferences = defaultdict(lambda: defaultdict(int))
        
    def learn_from_interactions(self, user_interactions, recipes_df):
        """Learn user preferences from interaction history"""
        user_preferences = {}
        
        for user_id in user_interactions['user_id'].unique():
            user_data = user_interactions[user_interactions['user_id'] == user_id]
            user_preferences[user_id] = self.analyze_user_preferences(user_data, recipes_df)
        
        return user_preferences
    
    def analyze_user_preferences(self, user_interactions, recipes_df):
        """Analyze preferences for a single user"""
        preferences = {
            'preferred_ingredients': defaultdict(int),
            'preferred_cuisines': defaultdict(int),
            'preferred_meal_types': defaultdict(int),
            'avoided_ingredients': defaultdict(int),
            'cooking_time_preference': None,
            'spice_level_preference': None,
            'texture_preferences': []
        }
        
        # Analyze positive interactions (high ratings, repeats)
        positive_interactions = user_interactions[
            (user_interactions['rating'] >= 4) | 
            (user_interactions['repeat_count'] > 0)
        ]
        
        for _, interaction in positive_interactions.iterrows():
            recipe_id = interaction['recipe_id']
            recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
            
            # Analyze ingredients
            for ingredient in recipe.get('ingredients', []):
                ingredient_name = ingredient.get('name', '').lower()
                preferences['preferred_ingredients'][ingredient_name] += 1
            
            # Analyze cuisine types
            cultural_tags = recipe.get('cultural_tags', [])
            for tag in cultural_tags:
                preferences['preferred_cuisines'][tag] += 1
            
            # Analyze meal types
            meal_type = recipe.get('meal_type', '')
            if meal_type:
                preferences['preferred_meal_types'][meal_type] += 1
        
        # Analyze negative interactions (low ratings)
        negative_interactions = user_interactions[user_interactions['rating'] <= 2]
        for _, interaction in negative_interactions.iterrows():
            recipe_id = interaction['recipe_id']
            recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
            
            for ingredient in recipe.get('ingredients', []):
                ingredient_name = ingredient.get('name', '').lower()
                preferences['avoided_ingredients'][ingredient_name] += 1
        
        # Normalize and get top preferences
        preferences['top_ingredients'] = self.get_top_preferences(
            preferences['preferred_ingredients'], top_n=10
        )
        preferences['top_cuisines'] = self.get_top_preferences(
            preferences['preferred_cuisines'], top_n=5
        )
        preferences['top_meal_types'] = self.get_top_preferences(
            preferences['preferred_meal_types'], top_n=3
        )
        preferences['avoided_ingredients'] = self.get_top_preferences(
            preferences['avoided_ingredients'], top_n=5
        )
        
        # Infer cooking time preference
        preferences['cooking_time_preference'] = self.infer_cooking_time_preference(
            user_interactions, recipes_df
        )
        
        return preferences
    
    def get_top_preferences(self, preference_dict, top_n=5):
        """Get top N preferences from a dictionary"""
        return dict(Counter(preference_dict).most_common(top_n))
    
    def infer_cooking_time_preference(self, user_interactions, recipes_df):
        """Infer user's preferred cooking time range"""
        positive_interactions = user_interactions[
            (user_interactions['rating'] >= 4) | 
            (user_interactions['repeat_count'] > 0)
        ]
        
        if len(positive_interactions) == 0:
            return 'medium'  # Default preference
        
        prep_times = []
        for _, interaction in positive_interactions.iterrows():
            recipe_id = interaction['recipe_id']
            recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
            prep_time = recipe.get('preparation_time', 0)
            if prep_time > 0:
                prep_times.append(prep_time)
        
        if not prep_times:
            return 'medium'
        
        avg_prep_time = np.mean(prep_times)
        
        if avg_prep_time <= 30:
            return 'quick'
        elif avg_prep_time <= 60:
            return 'medium'
        else:
            return 'lengthy'
    
    def update_preferences(self, user_id, new_interaction, recipes_df):
        """Update user preferences with new interaction"""
        if user_id not in self.preference_models:
            self.preference_models[user_id] = self.initialize_user_preferences()
        
        recipe_id = new_interaction['recipe_id']
        rating = new_interaction.get('rating', 3)
        recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
        
        # Update based on rating
        weight = 1 if rating >= 4 else -1 if rating <= 2 else 0
        
        if weight != 0:
            self.update_ingredient_preferences(user_id, recipe, weight)
            self.update_cuisine_preferences(user_id, recipe, weight)
            self.update_meal_type_preferences(user_id, recipe, weight)
    
    def update_ingredient_preferences(self, user_id, recipe, weight):
        """Update ingredient preferences for a user"""
        for ingredient in recipe.get('ingredients', []):
            ingredient_name = ingredient.get('name', '').lower()
            self.ingredient_preferences[user_id][ingredient_name] += weight
    
    def update_cuisine_preferences(self, user_id, recipe, weight):
        """Update cuisine preferences for a user"""
        cultural_tags = recipe.get('cultural_tags', [])
        for tag in cultural_tags:
            self.cuisine_preferences[user_id][tag] += weight
    
    def update_meal_type_preferences(self, user_id, recipe, weight):
        """Update meal type preferences for a user"""
        meal_type = recipe.get('meal_type', '')
        if meal_type:
            self.meal_type_preferences[user_id][meal_type] += weight

class AdaptivePreferenceModel:
    """Model that adapts to changing user preferences over time"""
    
    def __init__(self, decay_factor=0.95):
        self.decay_factor = decay_factor
        self.user_preferences = {}
        self.interaction_history = defaultdict(list)
        
    def add_interaction(self, user_id, recipe_id, rating, timestamp):
        """Add a new interaction with decayed weighting"""
        interaction = {
            'recipe_id': recipe_id,
            'rating': rating,
            'timestamp': timestamp,
            'weight': 1.0  # Initial weight
        }
        
        self.interaction_history[user_id].append(interaction)
        
        # Apply time decay to older interactions
        self.apply_time_decay(user_id, timestamp)
        
        # Update preferences
        self.update_user_preferences(user_id)
    
    def apply_time_decay(self, user_id, current_timestamp):
        """Apply time decay to older interactions"""
        for interaction in self.interaction_history[user_id]:
            time_diff = current_timestamp - interaction['timestamp']
            days_diff = time_diff.days
            
            # Decay weight based on time difference
            interaction['weight'] = self.decay_factor ** days_diff
    
    def update_user_preferences(self, user_id):
        """Update user preferences based on weighted interactions"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'ingredient_weights': defaultdict(float),
                'cuisine_weights': defaultdict(float),
                'meal_type_weights': defaultdict(float)
            }
        
        user_data = self.user_preferences[user_id]
        
        # Reset weights
        for key in user_data:
            user_data[key].clear()
        
        # Recalculate weighted preferences
        for interaction in self.interaction_history[user_id]:
            recipe_id = interaction['recipe_id']
            rating = interaction['rating']
            weight = interaction['weight']
            
            # Get recipe details (this would query the recipe database)
            recipe = self.get_recipe_details(recipe_id)
            if not recipe:
                continue
            
            # Calculate effective score (rating * weight)
            effective_score = (rating - 2.5) * weight  # Center around 0
            
            # Update ingredient preferences
            for ingredient in recipe.get('ingredients', []):
                ingredient_name = ingredient.get('name', '').lower()
                user_data['ingredient_weights'][ingredient_name] += effective_score
            
            # Update cuisine preferences
            cultural_tags = recipe.get('cultural_tags', [])
            for tag in cultural_tags:
                user_data['cuisine_weights'][tag] += effective_score
            
            # Update meal type preferences
            meal_type = recipe.get('meal_type', '')
            if meal_type:
                user_data['meal_type_weights'][meal_type] += effective_score
    
    def get_recipe_details(self, recipe_id):
        """Get recipe details from database (placeholder)"""
        # This would typically query the recipe database
        return None
    
    def get_current_preferences(self, user_id, top_n=10):
        """Get current top preferences for a user"""
        if user_id not in self.user_preferences:
            return {}
        
        user_data = self.user_preferences[user_id]
        
        preferences = {}
        
        for preference_type, weights in user_data.items():
            # Sort by weight and get top N
            sorted_items = sorted(
                weights.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_n]
            
            preferences[preference_type] = dict(sorted_items)
        
        return preferences