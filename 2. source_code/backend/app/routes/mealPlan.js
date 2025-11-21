const express = require('express');
const router = express.Router();
const mealPlanningService = require('../services/meal_planning');
const auth = require('../middleware/auth');

// Generate meal plan for user
router.post('/generate/:userId', auth, async (req, res) => {
  try {
    const { userId } = req.params;
    const userPreferences = req.body;

    const mealPlan = await mealPlanningService.generateWeeklyPlan(userId, userPreferences);
    
    res.json({
      success: true,
      data: mealPlan,
      message: 'Meal plan generated successfully'
    });
  } catch (error) {
    console.error('Meal plan generation error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate meal plan'
    });
  }
});

// Get current meal plan
router.get('/:userId', auth, async (req, res) => {
  try {
    const { userId } = req.params;
    const mealPlan = await mealPlanningService.getCurrentPlan(userId);
    
    res.json({
      success: true,
      data: mealPlan
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch meal plan'
    });
  }
});

module.exports = router;