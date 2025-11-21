import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Modal,
  TextInput,
  Alert,
  Image,
  Dimensions
} from 'react-native';
import { BarChart, LineChart, ProgressChart } from 'react-native-chart-kit';
import * as ImagePicker from 'expo-image-picker';
import { logProgress, getProgressHistory } from '../screens/services/api';

const ProgressTracker = ({ userId }) => {
  const [activeTab, setActiveTab] = useState('today');
  const [progressModal, setProgressModal] = useState(false);
  const [progressData, setProgressData] = useState({
    date: new Date().toISOString().split('T')[0],
    weight: '',
    meals: { breakfast: false, lunch: false, dinner: false, snacks: false },
    waterIntake: 0,
    notes: '',
    photos: []
  });
  const [progressHistory, setProgressHistory] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    loadProgressHistory();
  }, []);

  const loadProgressHistory = async () => {
    try {
      const history = await getProgressHistory(userId);
      setProgressHistory(history);
    } catch (error) {
      console.error('Failed to load progress history:', error);
    }
  };

  const handleLogProgress = async () => {
    try {
      await logProgress(userId, progressData);
      Alert.alert('Success', 'Progress logged successfully!');
      setProgressModal(false);
      resetProgressForm();
      loadProgressHistory();
    } catch (error) {
      Alert.alert('Error', 'Failed to log progress');
    }
  };

  const resetProgressForm = () => {
    setProgressData({
      date: new Date().toISOString().split('T')[0],
      weight: '',
      meals: { breakfast: false, lunch: false, dinner: false, snacks: false },
      waterIntake: 0,
      notes: '',
      photos: []
    });
  };

  const takeProgressPhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permission Required', 'Camera access is needed to take progress photos.');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [3, 4],
        quality: 0.7,
      });

      if (!result.canceled) {
        const newPhotos = [...progressData.photos, result.assets[0].uri];
        setProgressData({ ...progressData, photos: newPhotos });
        setSelectedImage(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const toggleMeal = (mealType) => {
    setProgressData({
      ...progressData,
      meals: {
        ...progressData.meals,
        [mealType]: !progressData.meals[mealType]
      }
    });
  };

  const updateWaterIntake = (change) => {
    const newIntake = Math.max(0, progressData.waterIntake + change);
    setProgressData({ ...progressData, waterIntake: newIntake });
  };

  // Calculate weekly progress data for charts
  const getWeeklyData = () => {
    const last7Days = progressHistory.slice(-7);
    return {
      labels: last7Days.map(day => {
        const date = new Date(day.date);
        return date.getDate() + '/' + (date.getMonth() + 1);
      }),
      weightData: last7Days.map(day => day.weight || 0),
      waterData: last7Days.map(day => day.waterIntake || 0),
      mealCompletion: last7Days.map(day => {
        const meals = day.meals || {};
        const completedMeals = Object.values(meals).filter(Boolean).length;
        return completedMeals / 4; // 4 meals per day
      })
    };
  };

  const weeklyData = getWeeklyData();

  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.5,
  };

  const screenWidth = Dimensions.get('window').width;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Progress Tracker</Text>
        <Text style={styles.subtitle}>Track your health journey</Text>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{progressData.waterIntake}</Text>
          <Text style={styles.statLabel}>Glasses Today</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {Object.values(progressData.meals).filter(Boolean).length}/4
          </Text>
          <Text style={styles.statLabel}>Meals Completed</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {progressHistory.filter(day => day.weight).length}
          </Text>
          <Text style={styles.statLabel}>Days Tracked</Text>
        </View>
      </View>

      {/* Navigation Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'today' && styles.activeTab]}
          onPress={() => setActiveTab('today')}
        >
          <Text style={[styles.tabText, activeTab === 'today' && styles.activeTabText]}>
            Today
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'charts' && styles.activeTab]}
          onPress={() => setActiveTab('charts')}
        >
          <Text style={[styles.tabText, activeTab === 'charts' && styles.activeTabText]}>
            Progress
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'history' && styles.activeTab]}
          onPress={() => setActiveTab('history')}
        >
          <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>
            History
          </Text>
        </TouchableOpacity>
      </View>

      {/* Today's Progress */}
      {activeTab === 'today' && (
        <ScrollView style={styles.content}>
          <View style={styles.todaySection}>
            {/* Water Intake */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Water Intake</Text>
              <View style={styles.waterContainer}>
                <Text style={styles.waterCount}>{progressData.waterIntake} glasses</Text>
                <View style={styles.waterButtons}>
                  <TouchableOpacity 
                    style={styles.waterButton} 
                    onPress={() => updateWaterIntake(-1)}
                  >
                    <Text style={styles.waterButtonText}>-</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.waterButton} 
                    onPress={() => updateWaterIntake(1)}
                  >
                    <Text style={styles.waterButtonText}>+</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>

            {/* Meal Completion */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Meals Today</Text>
              <View style={styles.mealsContainer}>
                {Object.entries(progressData.meals).map(([meal, completed]) => (
                  <TouchableOpacity
                    key={meal}
                    style={[styles.mealButton, completed && styles.mealCompleted]}
                    onPress={() => toggleMeal(meal)}
                  >
                    <Text style={[
                      styles.mealText,
                      completed && styles.mealTextCompleted
                    ]}>
                      {meal.charAt(0).toUpperCase() + meal.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Weight Tracking */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Weight Tracking</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter today's weight (kg)"
                value={progressData.weight}
                onChangeText={(text) => setProgressData({ ...progressData, weight: text })}
                keyboardType="numeric"
              />
            </View>

            {/* Progress Photos */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Progress Photos</Text>
              <TouchableOpacity style={styles.photoButton} onPress={takeProgressPhoto}>
                <Text style={styles.photoButtonText}>Take Progress Photo</Text>
              </TouchableOpacity>
              
              {progressData.photos.length > 0 && (
                <ScrollView horizontal style={styles.photosContainer}>
                  {progressData.photos.map((photo, index) => (
                    <TouchableOpacity key={index} onPress={() => setSelectedImage(photo)}>
                      <Image source={{ uri: photo }} style={styles.thumbnail} />
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              )}
            </View>

            {/* Notes */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Daily Notes</Text>
              <TextInput
                style={[styles.input, styles.notesInput]}
                placeholder="How are you feeling today? Any challenges or successes?"
                value={progressData.notes}
                onChangeText={(text) => setProgressData({ ...progressData, notes: text })}
                multiline
                numberOfLines={3}
              />
            </View>

            {/* Save Button */}
            <TouchableOpacity style={styles.saveButton} onPress={handleLogProgress}>
              <Text style={styles.saveButtonText}>Save Today's Progress</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* Progress Charts */}
      {activeTab === 'charts' && (
        <ScrollView style={styles.content}>
          <View style={styles.chartsSection}>
            {/* Weight Progress Chart */}
            {weeklyData.weightData.some(weight => weight > 0) && (
              <View style={styles.chartContainer}>
                <Text style={styles.chartTitle}>Weight Progress (kg)</Text>
                <LineChart
                  data={{
                    labels: weeklyData.labels,
                    datasets: [{ data: weeklyData.weightData }]
                  }}
                  width={screenWidth - 40}
                  height={220}
                  chartConfig={chartConfig}
                  bezier
                  style={styles.chart}
                />
              </View>
            )}

            {/* Water Intake Chart */}
            <View style={styles.chartContainer}>
              <Text style={styles.chartTitle}>Water Intake (glasses per day)</Text>
              <BarChart
                data={{
                  labels: weeklyData.labels,
                  datasets: [{ data: weeklyData.waterData }]
                }}
                width={screenWidth - 40}
                height={220}
                chartConfig={chartConfig}
                style={styles.chart}
              />
            </View>

            {/* Meal Completion Chart */}
            <View style={styles.chartContainer}>
              <Text style={styles.chartTitle}>Meal Completion Rate</Text>
              <ProgressChart
                data={{ data: weeklyData.mealCompletion }}
                width={screenWidth - 40}
                height={220}
                strokeWidth={16}
                radius={32}
                chartConfig={chartConfig}
                hideLegend={false}
                style={styles.chart}
              />
            </View>
          </View>
        </ScrollView>
      )}

      {/* History */}
      {activeTab === 'history' && (
        <ScrollView style={styles.content}>
          <View style={styles.historySection}>
            {progressHistory.length === 0 ? (
              <Text style={styles.noDataText}>No progress data yet. Start tracking today!</Text>
            ) : (
              progressHistory.map((day, index) => (
                <View key={index} style={styles.historyItem}>
                  <Text style={styles.historyDate}>
                    {new Date(day.date).toLocaleDateString()}
                  </Text>
                  <View style={styles.historyDetails}>
                    <Text>Weight: {day.weight || 'Not recorded'} kg</Text>
                    <Text>Water: {day.waterIntake || 0} glasses</Text>
                    <Text>
                      Meals: {Object.values(day.meals || {}).filter(Boolean).length}/4 completed
                    </Text>
                  </View>
                </View>
              ))
            )}
          </View>
        </ScrollView>
      )}

      {/* Progress Photo Modal */}
      <Modal
        visible={!!selectedImage}
        animationType="slide"
        onRequestClose={() => setSelectedImage(null)}
      >
        <View style={styles.modalContainer}>
          <TouchableOpacity 
            style={styles.closeButton}
            onPress={() => setSelectedImage(null)}
          >
            <Text style={styles.closeButtonText}>Close</Text>
          </TouchableOpacity>
          {selectedImage && (
            <Image source={{ uri: selectedImage }} style={styles.fullSizeImage} />
          )}
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#4CAF50',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    textAlign: 'center',
    marginTop: 5,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 15,
    backgroundColor: 'white',
  },
  statCard: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    padding: 15,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    fontSize: 16,
    color: '#666',
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  todaySection: {
    padding: 15,
  },
  section: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  waterContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  waterCount: {
    fontSize: 18,
    fontWeight: '500',
  },
  waterButtons: {
    flexDirection: 'row',
  },
  waterButton: {
    backgroundColor: '#4CAF50',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 10,
  },
  waterButtonText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  mealsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  mealButton: {
    width: '48%',
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  mealCompleted: {
    backgroundColor: '#4CAF50',
  },
  mealText: {
    fontSize: 16,
    color: '#666',
  },
  mealTextCompleted: {
    color: 'white',
    fontWeight: '500',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  notesInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  photoButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  photoButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  photosContainer: {
    flexDirection: 'row',
  },
  thumbnail: {
    width: 80,
    height: 100,
    borderRadius: 8,
    marginRight: 10,
  },
  saveButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  chartsSection: {
    padding: 15,
  },
  chartContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    textAlign: 'center',
  },
  chart: {
    borderRadius: 8,
  },
  historySection: {
    padding: 15,
  },
  historyItem: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  historyDate: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
    color: '#333',
  },
  historyDetails: {
    marginTop: 5,
  },
  noDataText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 16,
    marginTop: 50,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'black',
    justifyContent: 'center',
  },
  closeButton: {
    position: 'absolute',
    top: 40,
    right: 20,
    zIndex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 10,
    borderRadius: 20,
  },
  closeButtonText: {
    color: 'white',
    fontSize: 16,
  },
  fullSizeImage: {
    width: '100%',
    height: '80%',
    resizeMode: 'contain',
  },
});

export default ProgressTracker;