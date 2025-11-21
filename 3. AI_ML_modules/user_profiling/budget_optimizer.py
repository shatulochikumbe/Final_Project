import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class BudgetOptimizer:
    def __init__(self):
        self.cost_models = {}
        self.budget_ranges = {
            'low': {'min': 0, 'max': 150, 'weekly_budget': 1050},  # ZMW 150/day
            'medium': {'min': 150, 'max': 250, 'weekly_budget': 1750},  # ZMW 250/day
            'high': {'min': 250, 'max': 400, 'weekly_budget': 2800}  # ZMW 400/day
        }
    
    def optimize_meal_plan_cost(self, meal_plan, user_budget, family_size=1):
        """Optimize meal plan to fit user's budget"""
        total_cost = self.calculate_meal_plan_cost(meal_plan)
        weekly_budget = self.budget_ranges[user_budget]['weekly_budget'] * family_size
        
        if total_cost <= weekly_budget:
            return meal_plan  # Plan already within budget
        
        # Need to optimize - implement cost reduction strategies
        optimized_plan = self.apply_cost_reduction_strategies(
            meal_plan, total_cost, weekly_budget
        )
        
        return optimized_plan
    
    def calculate_meal_plan_cost(self, meal_plan):
        """Calculate total cost of a meal plan"""
        total_cost = 0
        
        for day, meals in meal_plan.items():
            for meal_type, meal in meals.items():
                if meal and 'cost_per_serving' in meal:
                    total_cost += meal['cost_per_serving']
        
        return total_cost
    
    def apply_cost_reduction_strategies(self, meal_plan, current_cost, target_budget):
        """Apply strategies to reduce meal plan cost"""
        reduction_needed = current_cost - target_budget
        optimized_plan = meal_plan.copy()
        
        strategies = [
            self.substitute_expensive_ingredients,
            self.reduce_meal_complexity,
            self.incorporate_leftovers,
            self.optimize_portions
        ]
        
        # Apply strategies until budget is met
        for strategy in strategies:
            if reduction_needed <= 0:
                break
            
            optimized_plan, cost_reduction = strategy(optimized_plan, reduction_needed)
            reduction_needed -= cost_reduction
        
        return optimized_plan
    
    def substitute_expensive_ingredients(self, meal_plan, max_reduction):
        """Substitute expensive ingredients with cheaper alternatives"""
        cost_reduction = 0
        substitutions_made = []
        
        # Zambian ingredient substitution database
        substitution_map = {
            'imported_chicken': 'local_chicken',
            'imported_rice': 'local_rice',
            'fresh_fish': 'kapenta',
            'imported_oil': 'local_cooking_oil',
            'imported_vegetables': 'local_seasonal_vegetables'
        }
        
        for day, meals in meal_plan.items():
            for meal_type, meal in meals.items():
                if not meal:
                    continue
                
                original_cost = meal.get('cost_per_serving', 0)
                substituted_meal = self.apply_ingredient_substitutions(
                    meal, substitution_map
                )
                
                if substituted_meal != meal:
                    new_cost = substituted_meal.get('cost_per_serving', original_cost)
                    reduction = original_cost - new_cost
                    
                    if reduction > 0 and cost_reduction + reduction <= max_reduction:
                        meal_plan[day][meal_type] = substituted_meal
                        cost_reduction += reduction
                        substitutions_made.append({
                            'day': day,
                            'meal': meal_type,
                            'reduction': reduction
                        })
        
        return meal_plan, cost_reduction
    
    def apply_ingredient_substitutions(self, meal, substitution_map):
        """Apply ingredient substitutions to a meal"""
        # This would modify the recipe ingredients
        # For now, return a modified cost estimate
        substituted_meal = meal.copy()
        
        # Simple cost reduction based on substitution complexity
        cost_reduction_ratio = 0.15  # Average 15% cost reduction
        original_cost = meal.get('cost_per_serving', 0)
        substituted_meal['cost_per_serving'] = original_cost * (1 - cost_reduction_ratio)
        substituted_meal['substituted'] = True
        
        return substituted_meal
    
    def reduce_meal_complexity(self, meal_plan, max_reduction):
        """Reduce meal complexity by simplifying recipes"""
        cost_reduction = 0
        
        for day, meals in meal_plan.items():
            for meal_type, meal in meals.items():
                if not meal or meal.get('simplified', False):
                    continue
                
                # Simple meals typically cost less
                complexity = meal.get('ingredient_count', 0)
                if complexity > 8:  # Complex meal
                    simplified_cost = meal.get('cost_per_serving', 0) * 0.8  # 20% reduction
                    reduction = meal.get('cost_per_serving', 0) - simplified_cost
                    
                    if cost_reduction + reduction <= max_reduction:
                        meal['cost_per_serving'] = simplified_cost
                        meal['simplified'] = True
                        cost_reduction += reduction
        
        return meal_plan, cost_reduction
    
    def incorporate_leftovers(self, meal_plan, max_reduction):
        """Incorporate leftovers to reduce cooking and ingredient costs"""
        cost_reduction = 0
        leftover_plan = meal_plan.copy()
        
        # Strategy: Cook larger portions for dinner and use leftovers for lunch
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            dinner = leftover_plan[day].get('dinner')
            next_day_lunch = leftover_plan.get(self.get_next_day(day), {}).get('lunch')
            
            if dinner and next_day_lunch and not next_day_lunch.get('leftover_based', False):
                # Replace lunch with leftovers from dinner
                leftover_cost = dinner.get('cost_per_serving', 0) * 0.3  # Leftovers cost 30% of original
                original_lunch_cost = next_day_lunch.get('cost_per_serving', 0)
                reduction = original_lunch_cost - leftover_cost
                
                if reduction > 0 and cost_reduction + reduction <= max_reduction:
                    leftover_plan[self.get_next_day(day)]['lunch'] = {
                        **dinner,
                        'cost_per_serving': leftover_cost,
                        'leftover_based': True,
                        'original_meal': dinner['name']
                    }
                    cost_reduction += reduction
        
        return leftover_plan, cost_reduction
    
    def get_next_day(self, current_day):
        """Get the next day of the week"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_index = days.index(current_day)
        return days[(current_index + 1) % 7]
    
    def optimize_portions(self, meal_plan, max_reduction):
        """Optimize portion sizes based on nutritional needs"""
        cost_reduction = 0
        
        for day, meals in meal_plan.items():
            for meal_type, meal in meals.items():
                if not meal:
                    continue
                
                # Adjust portion sizes based on meal type and time of day
                portion_adjustment = self.calculate_portion_adjustment(meal_type)
                original_cost = meal.get('cost_per_serving', 0)
                adjusted_cost = original_cost * portion_adjustment
                reduction = original_cost - adjusted_cost
                
                if reduction > 0 and cost_reduction + reduction <= max_reduction:
                    meal['cost_per_serving'] = adjusted_cost
                    meal['portion_optimized'] = True
                    cost_reduction += reduction
        
        return meal_plan, cost_reduction
    
    def calculate_portion_adjustment(self, meal_type):
        """Calculate portion size adjustment factor"""
        portion_factors = {
            'breakfast': 0.9,  # Slightly smaller breakfast portions
            'lunch': 1.0,      # Standard lunch portions
            'dinner': 1.1,     # Slightly larger dinner portions
            'snacks': 0.5      # Half portions for snacks
        }
        
        return portion_factors.get(meal_type, 1.0)

class CostPredictor:
    """Predict food costs based on seasonal and market factors"""
    
    def __init__(self):
        self.seasonal_adjustments = self.load_seasonal_data()
        self.market_trends = self.load_market_trends()
    
    def load_seasonal_data(self):
        """Load seasonal adjustment factors for Zambian foods"""
        return {
            'rainy_season': {  # November to April
                'vegetables': 0.8,  # 20% cheaper
                'fruits': 0.9,      # 10% cheaper
                'grains': 1.1,      # 10% more expensive
                'protein': 1.0      # No change
            },
            'dry_season': {    # May to October
                'vegetables': 1.2,  # 20% more expensive
                'fruits': 1.1,      # 10% more expensive
                'grains': 0.9,      # 10% cheaper
                'protein': 1.0      # No change
            }
        }
    
    def load_market_trends(self):
        """Load historical market price trends"""
        # This would connect to market data APIs
        return {
            'inflation_rate': 0.10,  # 10% annual inflation
            'seasonal_variation': 0.15  # 15% seasonal variation
        }
    
    def predict_ingredient_cost(self, ingredient_name, category, quantity, date):
        """Predict cost of an ingredient considering seasonal and market factors"""
        base_cost = self.get_base_cost(ingredient_name, category)
        seasonal_factor = self.get_seasonal_factor(category, date)
        inflation_factor = self.get_inflation_factor(date)
        
        predicted_cost = base_cost * seasonal_factor * inflation_factor * quantity
        
        return predicted_cost
    
    def get_base_cost(self, ingredient_name, category):
        """Get base cost for an ingredient"""
        # This would query the food cost database
        base_costs = {
            'maize_meal': 8.5,
            'cassava': 6.0,
            'sweet_potato': 12.0,
            'beans': 18.0,
            'kapenta': 45.0,
            'chicken': 35.0,
            'rape_leaves': 10.0,
            'tomatoes': 15.0,
            'onions': 12.0
        }
        
        return base_costs.get(ingredient_name, 10.0)  # Default cost
    
    def get_seasonal_factor(self, category, date):
        """Get seasonal adjustment factor"""
        month = date.month
        season = 'rainy_season' if 11 <= month <= 4 else 'dry_season'
        
        return self.seasonal_adjustments[season].get(category, 1.0)
    
    def get_inflation_factor(self, date):
        """Get inflation adjustment factor"""
        # Simple linear inflation model
        months_from_base = (date.year - 2024) * 12 + (date.month - 1)
        monthly_inflation = self.market_trends['inflation_rate'] / 12
        
        return (1 + monthly_inflation) ** months_from_base