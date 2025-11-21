import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import re

class MealDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    def load_zambian_foods(self, file_path):
        """Load and preprocess Zambian food nutritional data"""
        with open(file_path, 'r') as f:
            food_data = json.load(f)
        
        foods_df = pd.DataFrame(food_data['foods'])
        
        # Expand nutrients into separate columns
        nutrient_cols = {}
        for food in foods_df.itertuples():
            nutrients = food.nutrients_per_100g
            for nutrient, value in nutrients.items():
                if nutrient not in nutrient_cols:
                    nutrient_cols[nutrient] = []
                nutrient_cols[nutrient].append(value)
        
        for nutrient, values in nutrient_cols.items():
            foods_df[f'nutrient_{nutrient}'] = values
        
        return foods_df
    
    def load_recipes(self, file_path):
        """Load and preprocess recipe data"""
        with open(file_path, 'r') as f:
            recipes = json.load(f)
        
        recipes_df = pd.DataFrame(recipes)
        
        # Extract features from ingredients
        recipes_df['ingredient_count'] = recipes_df['ingredients'].apply(len)
        recipes_df['total_prep_time'] = recipes_df['preparation_time']
        recipes_df['cost_per_serving'] = recipes_df['ingredients'].apply(
            lambda x: sum([ing.get('estimated_cost', 0) for ing in x])
        )
        
        return recipes_df
    
    def preprocess_user_data(self, users_df):
        """Preprocess user profile data"""
        # Encode categorical variables
        categorical_columns = ['budget_range', 'health_goals', 'dietary_restrictions']
        
        for col in categorical_columns:
            if col in users_df.columns:
                self.label_encoders[col] = LabelEncoder()
                users_df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(
                    users_df[col].astype(str)
                )
        
        # Normalize numerical features
        numerical_columns = ['family_size', 'age', 'weight', 'height']
        numerical_columns = [col for col in numerical_columns if col in users_df.columns]
        
        if numerical_columns:
            users_df[numerical_columns] = self.scaler.fit_transform(
                users_df[numerical_columns]
            )
        
        return users_df
    
    def create_meal_features(self, recipes_df):
        """Create feature matrix for meal recommendations"""
        features = []
        
        for recipe in recipes_df.itertuples():
            feature_vector = {
                'recipe_id': recipe.id,
                'meal_type': recipe.meal_type,
                'preparation_time': recipe.preparation_time,
                'difficulty_level': recipe.difficulty_level,
                'cost_per_serving': getattr(recipe, 'cost_per_serving', 0),
                'ingredient_count': getattr(recipe, 'ingredient_count', 0),
                'calories': recipe.nutrition_facts.get('calories', 0),
                'protein': recipe.nutrition_facts.get('protein', 0),
                'carbs': recipe.nutrition_facts.get('carbs', 0),
                'fats': recipe.nutrition_facts.get('fats', 0),
                'fiber': recipe.nutrition_facts.get('fiber', 0)
            }
            
            # Add cultural tags as binary features
            cultural_tags = getattr(recipe, 'cultural_tags', [])
            feature_vector['is_traditional'] = 1 if 'traditional' in cultural_tags else 0
            feature_vector['is_zambian'] = 1 if 'zambian' in cultural_tags else 0
            feature_vector['is_modern'] = 1 if 'modern' in cultural_tags else 0
            
            features.append(feature_vector)
        
        return pd.DataFrame(features)
    
    def prepare_training_data(self, user_profiles, recipe_features, interactions):
        """Prepare training data for recommendation model"""
        # Merge user profiles with interactions
        training_data = interactions.merge(
            user_profiles, on='user_id', how='left'
        ).merge(
            recipe_features, on='recipe_id', how='left'
        )
        
        # Handle missing values
        training_data = training_data.fillna(0)
        
        return training_data

if __name__ == "__main__":
    preprocessor = MealDataPreprocessor()
    
    # Example usage
    foods_df = preprocessor.load_zambian_foods('../data/raw/nutritional_data.json')
    recipes_df = preprocessor.load_recipes('../data/raw/local_recipes.json')
    
    print(f"Loaded {len(foods_df)} Zambian foods")
    print(f"Loaded {len(recipes_df)} local recipes")