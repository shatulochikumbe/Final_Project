import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';

const OnboardingQuiz = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [userProfile, setUserProfile] = useState({
    healthGoals: [],
    dietaryRestrictions: [],
    budget: 'medium',
    preferences: { likes: [], dislikes: [] },
    familySize: 1
  });

  const healthGoals = [
    { id: 'weight_loss', label: 'Lose Weight' },
    { id: 'muscle_gain', label: 'Gain Muscle' },
    { id: 'energy', label: 'More Energy' },
    { id: 'diabetes_management', label: 'Manage Diabetes' },
    { id: 'general_health', label: 'General Health' }
  ];

  const handleGoalSelect = (goalId) => {
    const updatedGoals = userProfile.healthGoals.includes(goalId)
      ? userProfile.healthGoals.filter(g => g !== goalId)
      : [...userProfile.healthGoals, goalId];
    
    setUserProfile({ ...userProfile, healthGoals: updatedGoals });
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(userProfile);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Welcome to ZaNuri AI!</Text>
      <Text style={styles.subtitle}>Let's personalize your experience</Text>
      
      {currentStep === 0 && (
        <View style={styles.step}>
          <Text style={styles.question}>What are your health goals?</Text>
          {healthGoals.map(goal => (
            <TouchableOpacity
              key={goal.id}
              style={[
                styles.option,
                userProfile.healthGoals.includes(goal.id) && styles.selectedOption
              ]}
              onPress={() => handleGoalSelect(goal.id)}
            >
              <Text style={styles.optionText}>{goal.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
      
      {/* Add more steps for dietary restrictions, budget, preferences, family size */}
      
      <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
        <Text style={styles.nextButtonText}>
          {currentStep === 4 ? 'Complete Setup' : 'Next'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginBottom: 10 },
  subtitle: { fontSize: 16, textAlign: 'center', marginBottom: 30, color: '#666' },
  step: { marginBottom: 30 },
  question: { fontSize: 18, fontWeight: '600', marginBottom: 20 },
  option: { 
    padding: 15, 
    borderWidth: 1, 
    borderColor: '#ddd', 
    borderRadius: 8, 
    marginBottom: 10 
  },
  selectedOption: { 
    backgroundColor: '#e3f2fd', 
    borderColor: '#2196f3' 
  },
  optionText: { fontSize: 16 },
  nextButton: { 
    backgroundColor: '#4CAF50', 
    padding: 15, 
    borderRadius: 8, 
    alignItems: 'center' 
  },
  nextButtonText: { 
    color: 'white', 
    fontSize: 18, 
    fontWeight: 'bold' 
  }
});

export default OnboardingQuiz;