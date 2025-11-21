const zambianRecipes = require('../../../data/zambian_recipes.json');

class MealRecommender {
  async generatePlan(user, preferences) {
    const { healthGoals, dietaryRestrictions, budget, familySize } = preferences;
    
    // Filter recipes based on user preferences
    let filteredRecipes = this.filterRecipes(
      zambianRecipes, 
      healthGoals, 
      dietaryRestrictions, 
      budget
    );

    // Generate weekly plan
    const weeklyPlan = this.createWeeklySchedule(filteredRecipes, familySize);
    
    // Generate shopping list
    const shoppingList = this.generateShoppingList(weeklyPlan);
    
    // Calculate total cost
    const totalCost = this.calculateTotalCost(shoppingList);

    return {
      days: weeklyPlan,
      shopping_list: shoppingList,
      total_cost: totalCost,
      nutritional_summary: this.calculateNutritionalSummary(weeklyPlan)
    };
  }

  filterRecipes(recipes, healthGoals, restrictions, budget) {
    return recipes.filter(recipe => {
      // Filter by health goals
      if (healthGoals.includes('weight_loss') && recipe.calories > 500) return false;
      if (healthGoals.includes('diabetes_management') && recipe.sugar > 20) return false;
      
      // Filter by dietary restrictions
      if (restrictions.includes('vegetarian') && recipe.contains_meat) return false;
      if (restrictions.includes('lactose') && recipe.contains_dairy) return false;
      
      // Filter by budget
      if (budget === 'low' && recipe.cost_per_serving > 15) return false;
      if (budget === 'medium' && recipe.cost_per_serving > 25) return false;
      
      return true;
    });
  }

  createWeeklySchedule(recipes, familySize) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const weeklyPlan = [];

    for (const day of days) {
      const dayPlan = {
        day,
        meals: {
          breakfast: this.selectRandomRecipe(recipes.filter(r => r.meal_type === 'breakfast')),
          lunch: this.selectRandomRecipe(recipes.filter(r => r.meal_type === 'lunch')),
          dinner: this.selectRandomRecipe(recipes.filter(r => r.meal_type === 'dinner'))
        }
      };
      weeklyPlan.push(dayPlan);
    }

    return weeklyPlan;
  }

  selectRandomRecipe(recipes) {
    const randomIndex = Math.floor(Math.random() * recipes.length);
    return recipes[randomIndex];
  }

  generateShoppingList(weeklyPlan) {
    const ingredientMap = new Map();

    weeklyPlan.forEach(day => {
      Object.values(day.meals).forEach(meal => {
        meal.ingredients.forEach(ingredient => {
          const existing = ingredientMap.get(ingredient.name) || { quantity: 0, unit: ingredient.unit };
          ingredientMap.set(ingredient.name, {
            quantity: existing.quantity + (ingredient.quantity * ingredient.unit),
            unit: ingredient.unit,
            estimated_cost: ingredient.estimated_cost
          });
        });
      });
    });

    return Array.from(ingredientMap, ([name, details]) => ({
      name,
      quantity: details.quantity,
      unit: details.unit,
      estimated_cost: details.estimated_cost
    }));
  }

  calculateTotalCost(shoppingList) {
    return shoppingList.reduce((total, item) => total + (item.estimated_cost || 0), 0);
  }

  calculateNutritionalSummary(weeklyPlan) {
    // Implementation for nutritional calculation
    return {
      total_calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0
    };
  }
}

module.exports = new MealRecommender();