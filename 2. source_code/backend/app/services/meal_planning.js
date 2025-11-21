const db = require('../../config/database');
const aiEngine = require('./ai_engine/meal_recommender');

class MealPlanningService {
  async generateWeeklyPlan(userId, preferences) {
    try {
      // Get user profile
      const user = await db('users').where({ id: userId }).first();
      if (!user) throw new Error('User not found');

      // Generate plan using AI engine
      const weeklyPlan = await aiEngine.generatePlan(user, preferences);
      
      // Save to database
      const savedPlan = await db('meal_plans')
        .insert({
          user_id: userId,
          week_plan: JSON.stringify(weeklyPlan.days),
          shopping_list: JSON.stringify(weeklyPlan.shopping_list),
          total_estimated_cost: weeklyPlan.total_cost,
          generated_at: new Date()
        })
        .returning('*');

      return {
        plan_id: savedPlan[0].id,
        week_plan: weeklyPlan.days,
        shopping_list: weeklyPlan.shopping_list,
        total_cost: weeklyPlan.total_cost,
        nutritional_summary: weeklyPlan.nutritional_summary
      };
    } catch (error) {
      console.error('Meal planning service error:', error);
      throw error;
    }
  }

  async getCurrentPlan(userId) {
    return db('meal_plans')
      .where({ user_id: userId })
      .orderBy('generated_at', 'desc')
      .first();
  }
}

module.exports = new MealPlanningService();