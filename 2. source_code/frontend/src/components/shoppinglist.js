import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  TextInput,
  Alert,
  Share,
  Modal,
  Animated
} from 'react-native';
import { getShoppingList, updateShoppingList, getNearbyVendors } from '../services/api';

const ShoppingList = ({ userId, mealPlanId }) => {
  const [shoppingList, setShoppingList] = useState([]);
  const [groupedItems, setGroupedItems] = useState({});
  const [loading, setLoading] = useState(true);
  const [totalCost, setTotalCost] = useState(0);
  const [vendorModal, setVendorModal] = useState(false);
  const [nearbyVendors, setNearbyVendors] = useState([]);
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [newItem, setNewItem] = useState({ name: '', quantity: '', category: '' });
  const [addItemModal, setAddItemModal] = useState(false);
  const [checkAnimations] = useState({});

  useEffect(() => {
    loadShoppingList();
    loadNearbyVendors();
  }, [mealPlanId]);

  const loadShoppingList = async () => {
    try {
      const list = await getShoppingList(userId, mealPlanId);
      setShoppingList(list.items || []);
      setTotalCost(list.total_cost || 0);
      groupItemsByCategory(list.items || []);
    } catch (error) {
      console.error('Failed to load shopping list:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadNearbyVendors = async () => {
    try {
      // In a real app, get user's actual location
      const location = { lat: -15.4167, lng: 28.2833 }; // Lusaka coordinates
      const vendors = await getNearbyVendors(location);
      setNearbyVendors(vendors);
    } catch (error) {
      console.error('Failed to load vendors:', error);
    }
  };

  const groupItemsByCategory = (items) => {
    const grouped = items.reduce((acc, item) => {
      const category = item.category || 'Other';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(item);
      return acc;
    }, {});

    // Sort categories by typical shopping order
    const categoryOrder = ['Vegetables', 'Fruits', 'Protein', 'Grains', 'Dairy', 'Spices', 'Other'];
    const sortedGrouped = {};
    categoryOrder.forEach(category => {
      if (grouped[category]) {
        sortedGrouped[category] = grouped[category];
      }
    });

    // Add any remaining categories
    Object.keys(grouped).forEach(category => {
      if (!sortedGrouped[category]) {
        sortedGrouped[category] = grouped[category];
      }
    });

    setGroupedItems(sortedGrouped);
  };

  const toggleItemPurchased = async (itemId) => {
    const updatedList = shoppingList.map(item => 
      item.id === itemId ? { ...item, purchased: !item.purchased } : item
    );

    setShoppingList(updatedList);
    groupItemsByCategory(updatedList);

    // Update animation
    if (!checkAnimations[itemId]) {
      checkAnimations[itemId] = new Animated.Value(0);
    }

    Animated.spring(checkAnimations[itemId], {
      toValue: updatedList.find(item => item.id === itemId)?.purchased ? 1 : 0,
      useNativeDriver: true,
    }).start();

    try {
      await updateShoppingList(userId, { items: updatedList });
    } catch (error) {
      console.error('Failed to update shopping list:', error);
      // Revert on error
      loadShoppingList();
    }
  };

  const addCustomItem = async () => {
    if (!newItem.name.trim()) {
      Alert.alert('Error', 'Please enter an item name');
      return;
    }

    const customItem = {
      id: Date.now().toString(),
      name: newItem.name.trim(),
      quantity: newItem.quantity || '1',
      category: newItem.category || 'Other',
      estimated_cost: 0,
      purchased: false,
      custom: true
    };

    const updatedList = [...shoppingList, customItem];
    setShoppingList(updatedList);
    groupItemsByCategory(updatedList);
    setNewItem({ name: '', quantity: '', category: '' });
    setAddItemModal(false);

    try {
      await updateShoppingList(userId, { items: updatedList });
    } catch (error) {
      console.error('Failed to add custom item:', error);
    }
  };

  const removeItem = async (itemId) => {
    const updatedList = shoppingList.filter(item => item.id !== itemId);
    setShoppingList(updatedList);
    groupItemsByCategory(updatedList);

    try {
      await updateShoppingList(userId, { items: updatedList });
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  const shareShoppingList = async () => {
    try {
      const listText = shoppingList.map(item => 
        `- ${item.name}: ${item.quantity} ${item.purchased ? '✅' : ''}`
      ).join('\n');

      const message = `ZaNuri Shopping List\n\n${listText}\n\nTotal Estimated Cost: ZMW ${totalCost.toFixed(2)}`;

      await Share.share({
        message,
        title: 'My Shopping List'
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to share shopping list');
    }
  };

  const clearPurchasedItems = async () => {
    const remainingItems = shoppingList.filter(item => !item.purchased);
    setShoppingList(remainingItems);
    groupItemsByCategory(remainingItems);

    try {
      await updateShoppingList(userId, { items: remainingItems });
    } catch (error) {
      console.error('Failed to clear purchased items:', error);
    }
  };

  const getVendorsForItem = (itemName) => {
    return nearbyVendors.filter(vendor => 
      vendor.products.some(product => 
        product.toLowerCase().includes(itemName.toLowerCase())
      )
    );
  };

  const renderShoppingItem = ({ item }) => {
    const vendors = getVendorsForItem(item.name);
    
    return (
      <TouchableOpacity 
        style={[styles.itemContainer, item.purchased && styles.itemPurchased]}
        onPress={() => toggleItemPurchased(item.id)}
        onLongPress={() => removeItem(item.id)}
      >
        <View style={styles.itemContent}>
          <View style={styles.itemCheckbox}>
            <Animated.View 
              style={[
                styles.checkbox,
                item.purchased && styles.checkboxChecked,
                {
                  transform: [{
                    scale: checkAnimations[item.id]?.interpolate({
                      inputRange: [0, 1],
                      outputRange: [0.8, 1.2]
                    }) || 1
                  }]
                }
              ]}
            >
              {item.purchased && <Text style={styles.checkmark}>✓</Text>}
            </Animated.View>
          </View>
          
          <View style={styles.itemDetails}>
            <Text style={[styles.itemName, item.purchased && styles.itemNamePurchased]}>
              {item.name}
            </Text>
            <Text style={styles.itemQuantity}>
              {item.quantity} {item.unit || ''}
            </Text>
            {item.estimated_cost > 0 && (
              <Text style={styles.itemCost}>
                ZMW {item.estimated_cost.toFixed(2)}
              </Text>
            )}
          </View>

          {vendors.length > 0 && (
            <TouchableOpacity 
              style={styles.vendorIndicator}
              onPress={() => {
                setSelectedVendor(vendors[0]);
                setVendorModal(true);
              }}
            >
              <Text style={styles.vendorIndicatorText}>📍</Text>
            </TouchableOpacity>
          )}
        </View>

        {item.custom && (
          <View style={styles.customBadge}>
            <Text style={styles.customBadgeText}>Custom</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const renderCategorySection = (category, items) => (
    <View key={category} style={styles.categorySection}>
      <View style={styles.categoryHeader}>
        <Text style={styles.categoryTitle}>{category}</Text>
        <Text style={styles.categoryCount}>
          {items.filter(item => !item.purchased).length}/{items.length} remaining
        </Text>
      </View>
      
      <FlatList
        data={items}
        renderItem={renderShoppingItem}
        keyExtractor={item => item.id}
        scrollEnabled={false}
        style={styles.itemsList}
      />
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading your shopping list...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header with Summary */}
      <View style={styles.header}>
        <View style={styles.summaryCard}>
          <Text style={styles.totalCost}>ZMW {totalCost.toFixed(2)}</Text>
          <Text style={styles.summaryLabel}>Total Estimated Cost</Text>
          
          <View style={styles.summaryStats}>
            <Text style={styles.stat}>
              {shoppingList.filter(item => !item.purchased).length} items left
            </Text>
            <Text style={styles.stat}>
              {shoppingList.filter(item => item.purchased).length} purchased
            </Text>
          </View>
        </View>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionBar}>
        <TouchableOpacity style={styles.actionButton} onPress={shareShoppingList}>
          <Text style={styles.actionButtonText}>Share List</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton} onPress={clearPurchasedItems}>
          <Text style={styles.actionButtonText}>Clear Purchased</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.actionButton, styles.addItemButton]}
          onPress={() => setAddItemModal(true)}
        >
          <Text style={styles.addItemButtonText}>+ Add Item</Text>
        </TouchableOpacity>
      </View>

      {/* Shopping List Content */}
      <ScrollView style={styles.content}>
        {Object.keys(groupedItems).length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateTitle}>Your shopping list is empty</Text>
            <Text style={styles.emptyStateText}>
              Generate a meal plan first or add custom items to get started.
            </Text>
            <TouchableOpacity 
              style={styles.addFirstItemButton}
              onPress={() => setAddItemModal(true)}
            >
              <Text style={styles.addFirstItemButtonText}>Add Your First Item</Text>
            </TouchableOpacity>
          </View>
        ) : (
          Object.entries(groupedItems).map(([category, items]) => 
            renderCategorySection(category, items)
          )
        )}
      </ScrollView>

      {/* Add Item Modal */}
      <Modal
        visible={addItemModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setAddItemModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Custom Item</Text>
            
            <TextInput
              style={styles.modalInput}
              placeholder="Item name (e.g., Tomatoes)"
              value={newItem.name}
              onChangeText={(text) => setNewItem({ ...newItem, name: text })}
            />
            
            <TextInput
              style={styles.modalInput}
              placeholder="Quantity (e.g., 1kg, 2 pieces)"
              value={newItem.quantity}
              onChangeText={(text) => setNewItem({ ...newItem, quantity: text })}
            />
            
            <TextInput
              style={styles.modalInput}
              placeholder="Category (e.g., Vegetables)"
              value={newItem.category}
              onChangeText={(text) => setNewItem({ ...newItem, category: text })}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity 
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setAddItemModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.modalButton, styles.saveButton]}
                onPress={addCustomItem}
              >
                <Text style={styles.saveButtonText}>Add Item</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Vendor Modal */}
      <Modal
        visible={vendorModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setVendorModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedVendor && (
              <>
                <Text style={styles.modalTitle}>{selectedVendor.name}</Text>
                
                <View style={styles.vendorInfo}>
                  <Text style={styles.vendorType}>{selectedVendor.type}</Text>
                  <Text style={styles.vendorDistance}>
                    {selectedVendor.distance_km} km away
                  </Text>
                  <Text style={styles.vendorAddress}>{selectedVendor.address}</Text>
                  
                  {selectedVendor.business_hours && (
                    <View style={styles.businessHours}>
                      <Text style={styles.sectionLabel}>Business Hours:</Text>
                      <Text>{selectedVendor.business_hours}</Text>
                    </View>
                  )}
                  
                  <View style={styles.availableProducts}>
                    <Text style={styles.sectionLabel}>Available Products:</Text>
                    {selectedVendor.products.slice(0, 5).map((product, index) => (
                      <Text key={index} style={styles.productItem}>• {product}</Text>
                    ))}
                    {selectedVendor.products.length > 5 && (
                      <Text style={styles.moreProducts}>
                        ...and {selectedVendor.products.length - 5} more
                      </Text>
                    )}
                  </View>
                </View>

                <View style={styles.modalButtons}>
                  <TouchableOpacity 
                    style={[styles.modalButton, styles.cancelButton]}
                    onPress={() => setVendorModal(false)}
                  >
                    <Text style={styles.cancelButtonText}>Close</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity 
                    style={[styles.modalButton, styles.directionsButton]}
                    onPress={() => {
                      // In a real app, this would open maps with directions
                      Alert.alert('Directions', `Opening directions to ${selectedVendor.name}`);
                    }}
                  >
                    <Text style={styles.directionsButtonText}>Get Directions</Text>
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 20,
    backgroundColor: '#4CAF50',
  },
  summaryCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  totalCost: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 5,
  },
  summaryLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  stat: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  actionBar: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  actionButton: {
    flex: 1,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  actionButtonText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  addItemButton: {
    backgroundColor: '#2196F3',
  },
  addItemButtonText: {
    color: 'white',
    fontWeight: '500',
  },
  content: {
    flex: 1,
    padding: 15,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 22,
  },
  addFirstItemButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
  },
  addFirstItemButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  categorySection: {
    marginBottom: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  categoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  categoryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  categoryCount: {
    fontSize: 14,
    color: '#666',
  },
  itemsList: {
    marginTop: 5,
  },
  itemContainer: {
    backgroundColor: '#fafafa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  itemPurchased: {
    backgroundColor: '#f0f0f0',
    borderLeftColor: '#9E9E9E',
  },
  itemContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemCheckbox: {
    marginRight: 15,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  checkmark: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  itemDetails: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  itemNamePurchased: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  itemQuantity: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  itemCost: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '500',
  },
  vendorIndicator: {
    padding: 8,
  },
  vendorIndicatorText: {
    fontSize: 18,
  },
  customBadge: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#FF9800',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  customBadgeText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  modalInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 15,
    fontSize: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  modalButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  cancelButton: {
    backgroundColor: '#f0f0f0',
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: '500',
  },
  saveButton: {
    backgroundColor: '#4CAF50',
  },
  saveButtonText: {
    color: 'white',
    fontWeight: '500',
  },
  directionsButton: {
    backgroundColor: '#2196F3',
  },
  directionsButtonText: {
    color: 'white',
    fontWeight: '500',
  },
  vendorInfo: {
    marginBottom: 20,
  },
  vendorType: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  vendorDistance: {
    fontSize: 14,
    color: '#4CAF50',
    marginBottom: 10,
  },
  vendorAddress: {
    fontSize: 14,
    color: '#333',
    marginBottom: 15,
    lineHeight: 20,
  },
  businessHours: {
    marginBottom: 15,
  },
  availableProducts: {
    marginBottom: 10,
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  productItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  moreProducts: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
});

export default ShoppingList;