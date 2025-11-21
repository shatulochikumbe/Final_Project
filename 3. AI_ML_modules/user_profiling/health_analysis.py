import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json

class HealthProfileAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.health_clusters = None
        
    def analyze_user_health(self, user_data, health_goals):
        """Analyze user health profile and generate insights"""
        analysis = {
            'bmi_category': self.calculate_bmi_category(user_data),
            'nutritional_needs': self.calculate_nutritional_needs(user_data),
            'health_risks': self.assess_health_risks(user_data),
            'goal_alignment': self.assess_goal_alignment(user_data, health_goals),
            'personalized_recommendations': []
        }
        
        # Generate personalized recommendations
        analysis['personalized_recommendations'] = self.generate_health_recommendations(
            analysis, health_goals
        )
        
        return analysis
    
    def calculate_bmi_category(self, user_data):
        """Calculate BMI and category"""
        weight = user_data.get('weight', 0)
        height = user_data.get('height', 0)
        
        if weight > 0 and height > 0:
            height_m = height / 100  # Convert cm to meters
            bmi = weight / (height_m ** 2)
            
            if bmi < 18.5:
                return {'bmi': bmi, 'category': 'underweight', 'risk': 'high'}
            elif 18.5 <= bmi < 25:
                return {'bmi': bmi, 'category': 'normal', 'risk': 'low'}
            elif 25 <= bmi < 30:
                return {'bmi': bmi, 'category': 'overweight', 'risk': 'medium'}
            else:
                return {'bmi': bmi, 'category': 'obese', 'risk': 'high'}
        
        return {'bmi': None, 'category': 'unknown', 'risk': 'unknown'}
    
    def calculate_nutritional_needs(self, user_data):
        """Calculate daily nutritional requirements based on user profile"""
        weight = user_data.get('weight', 70)
        height = user_data.get('height', 170)
        age = user_data.get('age', 30)
        activity_level = user_data.get('activity_level', 'moderate')
        gender = user_data.get('gender', 'male')
        
        # Basal Metabolic Rate (BMR) calculation
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        # Macronutrient breakdown
        protein_g = weight * 1.8  # Higher protein for satiety and muscle maintenance
        fat_g = (tdee * 0.25) / 9  # 25% of calories from fat
        carbs_g = (tdee - (protein_g * 4 + fat_g * 9)) / 4  # Remaining calories from carbs
        
        return {
            'daily_calories': round(tdee),
            'protein_grams': round(protein_g),
            'carbs_grams': round(carbs_g),
            'fat_grams': round(fat_g),
            'fiber_grams': 25,  # Standard recommendation
            'water_liters': 2.0  # Standard recommendation
        }
    
    def assess_health_risks(self, user_data):
        """Assess potential health risks based on user profile"""
        risks = []
        
        bmi_info = self.calculate_bmi_category(user_data)
        if bmi_info['risk'] == 'high':
            risks.append({
                'risk': 'Weight-related health issues',
                'severity': 'high',
                'recommendation': 'Consult healthcare provider for weight management'
            })
        
        age = user_data.get('age', 0)
        if age > 50:
            risks.append({
                'risk': 'Age-related nutritional deficiencies',
                'severity': 'medium',
                'recommendation': 'Increase calcium and vitamin D intake'
            })
        
        # Add more risk assessments based on available data
        if user_data.get('has_diabetes', False):
            risks.append({
                'risk': 'Blood sugar management',
                'severity': 'high',
                'recommendation': 'Monitor carbohydrate intake and choose low GI foods'
            })
        
        return risks
    
    def assess_goal_alignment(self, user_data, health_goals):
        """Assess how well current profile aligns with health goals"""
        alignment = {}
        bmi_info = self.calculate_bmi_category(user_data)
        
        for goal in health_goals:
            if goal == 'weight_loss':
                if bmi_info['category'] in ['overweight', 'obese']:
                    alignment[goal] = {
                        'alignment': 'high',
                        'reason': 'Current BMI supports weight loss goal'
                    }
                else:
                    alignment[goal] = {
                        'alignment': 'low',
                        'reason': 'Current BMI may not require weight loss'
                    }
            
            elif goal == 'muscle_gain':
                alignment[goal] = {
                    'alignment': 'medium',
                    'reason': 'Focus on protein intake and strength training'
                }
            
            elif goal == 'diabetes_management':
                alignment[goal] = {
                    'alignment': 'high' if user_data.get('has_diabetes') else 'medium',
                    'reason': 'Focus on blood sugar control through diet'
                }
        
        return alignment
    
    def generate_health_recommendations(self, analysis, health_goals):
        """Generate personalized health recommendations"""
        recommendations = []
        
        # BMI-based recommendations
        bmi_category = analysis['bmi_category']['category']
        if bmi_category == 'underweight':
            recommendations.append(
                "Focus on nutrient-dense foods to support healthy weight gain"
            )
        elif bmi_category in ['overweight', 'obese']:
            recommendations.append(
                "Incorporate more vegetables and lean proteins for sustainable weight management"
            )
        
        # Goal-specific recommendations
        for goal in health_goals:
            if goal == 'weight_loss':
                recommendations.extend([
                    "Aim for a 300-500 calorie deficit daily",
                    "Include protein with every meal to maintain muscle mass",
                    "Choose high-fiber foods to stay full longer"
                ])
            elif goal == 'muscle_gain':
                recommendations.extend([
                    "Consume 1.6-2.2g of protein per kg of body weight",
                    "Time carbohydrate intake around workouts",
                    "Ensure adequate calorie surplus for muscle growth"
                ])
            elif goal == 'diabetes_management':
                recommendations.extend([
                    "Choose low glycemic index carbohydrates",
                    "Spread carbohydrate intake evenly throughout the day",
                    "Include fiber-rich foods to slow sugar absorption"
                ])
        
        return recommendations

class HealthClusterAnalyzer:
    """Cluster users based on health profiles for targeted recommendations"""
    
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        
    def fit(self, users_df):
        """Fit clustering model to user data"""
        # Select features for clustering
        features = ['age', 'weight', 'height', 'bmi']
        features = [f for f in features if f in users_df.columns]
        
        if features:
            X = users_df[features].fillna(users_df[features].mean())
            X_scaled = self.scaler.fit_transform(X)
            
            self.kmeans.fit(X_scaled)
            users_df['health_cluster'] = self.kmeans.labels_
            
            # Analyze cluster characteristics
            self.cluster_profiles = self.analyze_clusters(users_df, features)
        
        return users_df
    
    def analyze_clusters(self, users_df, features):
        """Analyze characteristics of each cluster"""
        cluster_profiles = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_data = users_df[users_df['health_cluster'] == cluster_id]
            
            profile = {
                'size': len(cluster_data),
                'characteristics': {},
                'common_goals': [],
                'recommendations': []
            }
            
            # Calculate cluster characteristics
            for feature in features:
                profile['characteristics'][feature] = {
                    'mean': cluster_data[feature].mean(),
                    'std': cluster_data[feature].std()
                }
            
            # Identify common health goals in cluster
            if 'health_goals' in cluster_data.columns:
                all_goals = []
                for goals in cluster_data['health_goals']:
                    if isinstance(goals, list):
                        all_goals.extend(goals)
                
                goal_counts = pd.Series(all_goals).value_counts()
                profile['common_goals'] = goal_counts.head(3).index.tolist()
            
            # Generate cluster-specific recommendations
            profile['recommendations'] = self.generate_cluster_recommendations(profile)
            
            cluster_profiles[cluster_id] = profile
        
        return cluster_profiles
    
    def generate_cluster_recommendations(self, cluster_profile):
        """Generate recommendations for a cluster"""
        recommendations = []
        characteristics = cluster_profile['characteristics']
        
        # Age-based recommendations
        avg_age = characteristics.get('age', {}).get('mean', 35)
        if avg_age > 50:
            recommendations.append("Focus on bone health with calcium-rich foods")
        elif avg_age < 25:
            recommendations.append("Build healthy eating habits for long-term health")
        
        # BMI-based recommendations
        avg_bmi = characteristics.get('bmi', {}).get('mean', 25)
        if avg_bmi > 28:
            recommendations.extend([
                "Emphasize portion control and mindful eating",
                "Incorporate daily physical activity"
            ])
        elif avg_bmi < 19:
            recommendations.append("Focus on nutrient-dense weight gain strategies")
        
        return recommendations