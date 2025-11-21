import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { getMealPlan } from '../screens/services/api';

const MealPlanner = ({ userId }) => {
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMealPlan();
  }, []);

  const loadMealPlan = async () => {
    try {
      const plan = await getMealPlan(userId);
      setMealPlan(plan);
    } catch (error) {
      console.error('Failed to load meal plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderDayPlan = ({ item: day }) => (
    <View style={styles.dayContainer}>
      <Text style={styles.dayTitle}>{day.day}</Text>
      <View style={styles.mealsContainer}>
        {Object.entries(day.meals).map(([mealType, meal]) => (
          <View key={mealType} style={styles.meal}>
            <Text style={styles.mealType}>{mealType}</Text>
            <Text style={styles.mealName}>{meal.recipe}</Text>
            <Text style={styles.mealTime}>Prep: {meal.prep_time}</Text>
          </View>
        ))}
      </View>
    </View>
  );

  if (loading) return <Text>Loading your personalized meal plan...</Text>;
  if (!mealPlan) return <Text>No meal plan available</Text>;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Weekly Meal Plan</Text>
      <Text style={styles.subtitle}>Total Estimated Cost: ZMW {mealPlan.total_cost}</Text>
      
      <FlatList
        data={mealPlan.week_plan}
        renderItem={renderDayPlan}
        keyExtractor={item => item.day}
      />
      
      <TouchableOpacity style={styles.regenerateButton} onPress={loadMealPlan}>
        <Text style={styles.regenerateText}>Regenerate Plan</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 15 },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 5 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 20 },
  dayContainer: { marginBottom: 20, padding: 15, backgroundColor: '#f9f9f9', borderRadius: 8 },
  dayTitle: { fontSize: 18, fontWeight: '600', marginBottom: 10 },
  mealsContainer: { marginLeft: 10 },
  meal: { marginBottom: 10 },
  mealType: { fontSize: 14, fontWeight: '500', textTransform: 'capitalize' },
  mealName: { fontSize: 16, color: '#333' },
  mealTime: { fontSize: 12, color: '#666' },
  regenerateButton: { 
    backgroundColor: '#FF9800', 
    padding: 15, 
    borderRadius: 8, 
    alignItems: 'center',
    marginTop: 10
  },
  regenerateText: { color: 'white', fontWeight: 'bold' }
});

export default MealPlanner;