import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Image,
  TextInput,
  Modal,
  Alert,
  Dimensions,
  ActivityIndicator
} from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { getNearbyVendors, getVendorProducts, placeOrder } from '../services/api';

const VendorMarketplace = ({ userId, userLocation }) => {
  const [vendors, setVendors] = useState([]);
  const [filteredVendors, setFilteredVendors] = useState([]);
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [vendorProducts, setVendorProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [cart, setCart] = useState({});
  const [cartModal, setCartModal] = useState(false);
  const [orderModal, setOrderModal] = useState(false);
  const [orderType, setOrderType] = useState('pickup'); // 'pickup' or 'delivery'

  const categories = [
    { id: 'all', name: 'All Vendors' },
    { id: 'supermarket', name: 'Supermarkets' },
    { id: 'local_market', name: 'Local Markets' },
    { id: 'farm', name: 'Farms' },
    { id: 'butchery', name: 'Butcheries' },
    { id: 'greengrocer', name: 'Green Grocers' }
  ];

  useEffect(() => {
    loadVendors();
  }, []);

  useEffect(() => {
    filterVendors();
  }, [vendors, searchQuery, selectedCategory]);

  const loadVendors = async () => {
    try {
      setLoading(true);
      // Use default Lusaka location if user location not available
      const location = userLocation || { lat: -15.4167, lng: 28.2833, radius_km: 10 };
      const vendorData = await getNearbyVendors(location);
      setVendors(vendorData);
    } catch (error) {
      console.error('Failed to load vendors:', error);
      Alert.alert('Error', 'Failed to load nearby vendors');
    } finally {
      setLoading(false);
    }
  };

  const filterVendors = () => {
    let filtered = vendors;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(vendor =>
        vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vendor.products.some(product =>
          product.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(vendor => vendor.type === selectedCategory);
    }

    setFilteredVendors(filtered);
  };

  const loadVendorDetails = async (vendor) => {
    try {
      setSelectedVendor(vendor);
      const products = await getVendorProducts(vendor.id);
      setVendorProducts(products);
    } catch (error) {
      console.error('Failed to load vendor products:', error);
      Alert.alert('Error', 'Failed to load vendor products');
    }
  };

  const addToCart = (product, vendorId) => {
    setCart(prevCart => {
      const vendorCart = prevCart[vendorId] || {};
      const currentQuantity = vendorCart[product.id]?.quantity || 0;
      
      return {
        ...prevCart,
        [vendorId]: {
          ...vendorCart,
          [product.id]: {
            ...product,
            quantity: currentQuantity + 1,
            totalPrice: (currentQuantity + 1) * product.price
          }
        }
      };
    });
  };

  const removeFromCart = (productId, vendorId) => {
    setCart(prevCart => {
      const vendorCart = { ...prevCart[vendorId] };
      delete vendorCart[productId];
      
      return {
        ...prevCart,
        [vendorId]: vendorCart
      };
    });
  };

  const updateCartQuantity = (productId, vendorId, newQuantity) => {
    if (newQuantity < 1) {
      removeFromCart(productId, vendorId);
      return;
    }

    setCart(prevCart => {
      const vendorCart = { ...prevCart[vendorId] };
      if (vendorCart[productId]) {
        vendorCart[productId] = {
          ...vendorCart[productId],
          quantity: newQuantity,
          totalPrice: newQuantity * vendorCart[productId].price
        };
      }
      
      return {
        ...prevCart,
        [vendorId]: vendorCart
      };
    });
  };

  const getCartTotal = (vendorId) => {
    const vendorCart = cart[vendorId] || {};
    return Object.values(vendorCart).reduce((total, item) => total + item.totalPrice, 0);
  };

  const getCartItemCount = (vendorId) => {
    const vendorCart = cart[vendorId] || {};
    return Object.values(vendorCart).reduce((count, item) => count + item.quantity, 0);
  };

  const placeVendorOrder = async () => {
    if (!selectedVendor) return;

    const vendorCart = cart[selectedVendor.id] || {};
    const orderItems = Object.values(vendorCart);

    if (orderItems.length === 0) {
      Alert.alert('Empty Cart', 'Please add items to your cart before ordering.');
      return;
    }

    try {
      const orderData = {
        userId,
        vendorId: selectedVendor.id,
        items: orderItems,
        totalAmount: getCartTotal(selectedVendor.id),
        orderType,
        deliveryAddress: orderType === 'delivery' ? userLocation?.address : null
      };

      await placeOrder(orderData);
      Alert.alert('Order Placed!', `Your order has been placed with ${selectedVendor.name}`);
      setCart(prevCart => ({ ...prevCart, [selectedVendor.id]: {} }));
      setCartModal(false);
      setOrderModal(false);
    } catch (error) {
      console.error('Failed to place order:', error);
      Alert.alert('Error', 'Failed to place order. Please try again.');
    }
  };

  const renderVendorCard = ({ item: vendor }) => (
    <TouchableOpacity 
      style={styles.vendorCard}
      onPress={() => loadVendorDetails(vendor)}
    >
      <View style={styles.vendorHeader}>
        <View style={styles.vendorImagePlaceholder}>
          <Text style={styles.vendorInitial}>
            {vendor.name.charAt(0).toUpperCase()}
          </Text>
        </View>
        <View style={styles.vendorInfo}>
          <Text style={styles.vendorName}>{vendor.name}</Text>
          <Text style={styles.vendorType}>{vendor.type}</Text>
          <Text style={styles.vendorDistance}>
            {vendor.distance_km} km away • {vendor.rating} ⭐
          </Text>
        </View>
      </View>

      <View style={styles.vendorDetails}>
        <Text style={styles.vendorAddress} numberOfLines={2}>
          📍 {vendor.address}
        </Text>
        {vendor.business_hours && (
          <Text style={styles.businessHours}>
            🕒 {vendor.business_hours}
          </Text>
        )}
      </View>

      <View style={styles.productsPreview}>
        <Text style={styles.productsLabel}>Popular Products:</Text>
        <View style={styles.productTags}>
          {vendor.products.slice(0, 3).map((product, index) => (
            <View key={index} style={styles.productTag}>
              <Text style={styles.productTagText}>{product}</Text>
            </View>
          ))}
          {vendor.products.length > 3 && (
            <Text style={styles.moreProducts}>+{vendor.products.length - 3} more</Text>
          )}
        </View>
      </View>

      {getCartItemCount(vendor.id) > 0 && (
        <View style={styles.cartIndicator}>
          <Text style={styles.cartIndicatorText}>
            {getCartItemCount(vendor.id)} items in cart
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderProductItem = ({ item: product }) => (
    <View style={styles.productCard}>
      <View style={styles.productImagePlaceholder}>
        <Text style={styles.productInitial}>
          {product.name.charAt(0).toUpperCase()}
        </Text>
      </View>
      
      <View style={styles.productInfo}>
        <Text style={styles.productName}>{product.name}</Text>
        <Text style={styles.productCategory}>{product.category}</Text>
        <Text style={styles.productPrice}>ZMW {product.price.toFixed(2)}</Text>
        {product.unit && (
          <Text style={styles.productUnit}>per {product.unit}</Text>
        )}
      </View>

      <View style={styles.productActions}>
        {cart[selectedVendor?.id]?.[product.id] ? (
          <View style={styles.quantityControls}>
            <TouchableOpacity 
              style={styles.quantityButton}
              onPress={() => updateCartQuantity(product.id, selectedVendor.id, 
                cart[selectedVendor.id][product.id].quantity - 1)}
            >
              <Text style={styles.quantityButtonText}>-</Text>
            </TouchableOpacity>
            
            <Text style={styles.quantityText}>
              {cart[selectedVendor.id][product.id].quantity}
            </Text>
            
            <TouchableOpacity 
              style={styles.quantityButton}
              onPress={() => updateCartQuantity(product.id, selectedVendor.id, 
                cart[selectedVendor.id][product.id].quantity + 1)}
            >
              <Text style={styles.quantityButtonText}>+</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity 
            style={styles.addButton}
            onPress={() => addToCart(product, selectedVendor.id)}
          >
            <Text style={styles.addButtonText}>Add</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Finding nearby vendors...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Local Marketplace</Text>
        <Text style={styles.subtitle}>Fresh products from local vendors</Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search vendors or products..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <TouchableOpacity style={styles.filterButton}>
          <Text style={styles.filterButtonText}>🔍</Text>
        </TouchableOpacity>
      </View>

      {/* Category Filter */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesContainer}
      >
        {categories.map(category => (
          <TouchableOpacity
            key={category.id}
            style={[
              styles.categoryButton,
              selectedCategory === category.id && styles.categoryButtonActive
            ]}
            onPress={() => setSelectedCategory(category.id)}
          >
            <Text style={[
              styles.categoryText,
              selectedCategory === category.id && styles.categoryTextActive
            ]}>
              {category.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Vendor List/Map View */}
      {!selectedVendor ? (
        <View style={styles.vendorsContainer}>
          <View style={styles.resultsHeader}>
            <Text style={styles.resultsCount}>
              {filteredVendors.length} vendors found
            </Text>
            <TouchableOpacity style={styles.mapToggle}>
              <Text style={styles.mapToggleText}>📍 Map View</Text>
            </TouchableOpacity>
          </View>

          {filteredVendors.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateTitle}>No vendors found</Text>
              <Text style={styles.emptyStateText}>
                Try adjusting your search or filters to find more vendors in your area.
              </Text>
              <TouchableOpacity style={styles.retryButton} onPress={loadVendors}>
                <Text style={styles.retryButtonText}>Refresh Vendors</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <FlatList
              data={filteredVendors}
              renderItem={renderVendorCard}
              keyExtractor={item => item.id}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.vendorsList}
            />
          )}
        </View>
      ) : (
        /* Vendor Detail View */
        <View style={styles.vendorDetailContainer}>
          <ScrollView>
            {/* Vendor Header */}
            <View style={styles.vendorDetailHeader}>
              <TouchableOpacity 
                style={styles.backButton}
                onPress={() => setSelectedVendor(null)}
              >
                <Text style={styles.backButtonText}>← Back</Text>
              </TouchableOpacity>
              
              <View style={styles.vendorDetailInfo}>
                <Text style={styles.vendorDetailName}>{selectedVendor.name}</Text>
                <Text style={styles.vendorDetailType}>{selectedVendor.type}</Text>
                <Text style={styles.vendorDetailDistance}>
                  {selectedVendor.distance_km} km away • {selectedVendor.rating} ⭐
                </Text>
              </View>

              {getCartItemCount(selectedVendor.id) > 0 && (
                <TouchableOpacity 
                  style={styles.cartButton}
                  onPress={() => setCartModal(true)}
                >
                  <Text style={styles.cartButtonText}>
                    🛒 {getCartItemCount(selectedVendor.id)}
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Vendor Map */}
            <View style={styles.mapContainer}>
              <MapView
                style={styles.map}
                provider={PROVIDER_GOOGLE}
                initialRegion={{
                  latitude: selectedVendor.location?.lat || -15.4167,
                  longitude: selectedVendor.location?.lng || 28.2833,
                  latitudeDelta: 0.01,
                  longitudeDelta: 0.01,
                }}
              >
                <Marker
                  coordinate={{
                    latitude: selectedVendor.location?.lat || -15.4167,
                    longitude: selectedVendor.location?.lng || 28.2833,
                  }}
                  title={selectedVendor.name}
                />
              </MapView>
            </View>

            {/* Vendor Information */}
            <View style={styles.infoSection}>
              <Text style={styles.sectionTitle}>Information</Text>
              <View style={styles.infoGrid}>
                <View style={styles.infoItem}>
                  <Text style={styles.infoLabel}>Address</Text>
                  <Text style={styles.infoValue}>{selectedVendor.address}</Text>
                </View>
                {selectedVendor.contact_phone && (
                  <View style={styles.infoItem}>
                    <Text style={styles.infoLabel}>Phone</Text>
                    <Text style={styles.infoValue}>{selectedVendor.contact_phone}</Text>
                  </View>
                )}
                {selectedVendor.business_hours && (
                  <View style={styles.infoItem}>
                    <Text style={styles.infoLabel}>Business Hours</Text>
                    <Text style={styles.infoValue}>{selectedVendor.business_hours}</Text>
                  </View>
                )}
              </View>
            </View>

            {/* Products List */}
            <View style={styles.productsSection}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Available Products</Text>
                <Text style={styles.productsCount}>
                  {vendorProducts.length} products
                </Text>
              </View>

              {vendorProducts.length === 0 ? (
                <View style={styles.noProducts}>
                  <Text style={styles.noProductsText}>
                    No products available at the moment.
                  </Text>
                </View>
              ) : (
                <FlatList
                  data={vendorProducts}
                  renderItem={renderProductItem}
                  keyExtractor={item => item.id}
                  scrollEnabled={false}
                />
              )}
            </View>
          </ScrollView>

          {/* Checkout Button */}
          {getCartItemCount(selectedVendor.id) > 0 && (
            <View style={styles.checkoutBar}>
              <View style={styles.checkoutInfo}>
                <Text style={styles.checkoutTotal}>
                  ZMW {getCartTotal(selectedVendor.id).toFixed(2)}
                </Text>
                <Text style={styles.checkoutItems}>
                  {getCartItemCount(selectedVendor.id)} items
                </Text>
              </View>
              <TouchableOpacity 
                style={styles.checkoutButton}
                onPress={() => setOrderModal(true)}
              >
                <Text style={styles.checkoutButtonText}>Proceed to Order</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      )}

      {/* Cart Modal */}
      <Modal
        visible={cartModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setCartModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.cartModalContent}>
            <View style={styles.cartHeader}>
              <Text style={styles.cartTitle}>Your Cart</Text>
              <TouchableOpacity onPress={() => setCartModal(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            {!selectedVendor || getCartItemCount(selectedVendor.id) === 0 ? (
              <View style={styles.emptyCart}>
                <Text style={styles.emptyCartText}>Your cart is empty</Text>
                <Text style={styles.emptyCartSubtext}>
                  Add some products from this vendor
                </Text>
              </View>
            ) : (
              <>
                <ScrollView style={styles.cartItems}>
                  {Object.values(cart[selectedVendor.id] || {}).map(item => (
                    <View key={item.id} style={styles.cartItem}>
                      <View style={styles.cartItemInfo}>
                        <Text style={styles.cartItemName}>{item.name}</Text>
                        <Text style={styles.cartItemPrice}>
                          ZMW {item.price.toFixed(2)} each
                        </Text>
                      </View>
                      <View style={styles.cartItemControls}>
                        <TouchableOpacity 
                          style={styles.cartQuantityButton}
                          onPress={() => updateCartQuantity(item.id, selectedVendor.id, item.quantity - 1)}
                        >
                          <Text style={styles.cartQuantityText}>-</Text>
                        </TouchableOpacity>
                        <Text style={styles.cartQuantity}>{item.quantity}</Text>
                        <TouchableOpacity 
                          style={styles.cartQuantityButton}
                          onPress={() => updateCartQuantity(item.id, selectedVendor.id, item.quantity + 1)}
                        >
                          <Text style={styles.cartQuantityText}>+</Text>
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.cartItemTotal}>
                        ZMW {item.totalPrice.toFixed(2)}
                      </Text>
                    </View>
                  ))}
                </ScrollView>

                <View style={styles.cartFooter}>
                  <View style={styles.cartTotal}>
                    <Text style={styles.cartTotalLabel}>Total:</Text>
                    <Text style={styles.cartTotalAmount}>
                      ZMW {getCartTotal(selectedVendor.id).toFixed(2)}
                    </Text>
                  </View>
                  <TouchableOpacity 
                    style={styles.checkoutModalButton}
                    onPress={() => {
                      setCartModal(false);
                      setOrderModal(true);
                    }}
                  >
                    <Text style={styles.checkoutModalButtonText}>Continue to Checkout</Text>
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* Order Modal */}
      <Modal
        visible={orderModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setOrderModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.orderModalContent}>
            <View style={styles.orderHeader}>
              <Text style={styles.orderTitle}>Place Your Order</Text>
              <TouchableOpacity onPress={() => setOrderModal(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.orderTypeSelection}>
              <Text style={styles.orderSectionTitle}>Order Type</Text>
              <View style={styles.orderTypeButtons}>
                <TouchableOpacity 
                  style={[
                    styles.orderTypeButton,
                    orderType === 'pickup' && styles.orderTypeButtonActive
                  ]}
                  onPress={() => setOrderType('pickup')}
                >
                  <Text style={[
                    styles.orderTypeText,
                    orderType === 'pickup' && styles.orderTypeTextActive
                  ]}>
                    🛵 Pickup
                  </Text>
                  <Text style={styles.orderTypeDescription}>
                    Collect from vendor
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={[
                    styles.orderTypeButton,
                    orderType === 'delivery' && styles.orderTypeButtonActive
                  ]}
                  onPress={() => setOrderType('delivery')}
                >
                  <Text style={[
                    styles.orderTypeText,
                    orderType === 'delivery' && styles.orderTypeTextActive
                  ]}>
                    🚚 Delivery
                  </Text>
                  <Text style={styles.orderTypeDescription}>
                    Delivered to your address
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.orderSummary}>
              <Text style={styles.orderSectionTitle}>Order Summary</Text>
              {Object.values(cart[selectedVendor?.id] || {}).map(item => (
                <View key={item.id} style={styles.orderItem}>
                  <Text style={styles.orderItemName}>{item.name}</Text>
                  <Text style={styles.orderItemDetails}>
                    {item.quantity} × ZMW {item.price.toFixed(2)}
                  </Text>
                  <Text style={styles.orderItemTotal}>
                    ZMW {item.totalPrice.toFixed(2)}
                  </Text>
                </View>
              ))}
              
              <View style={styles.orderTotal}>
                <Text style={styles.orderTotalLabel}>Total:</Text>
                <Text style={styles.orderTotalAmount}>
                  ZMW {getCartTotal(selectedVendor?.id).toFixed(2)}
                </Text>
              </View>
            </View>

            <TouchableOpacity 
              style={styles.placeOrderButton}
              onPress={placeVendorOrder}
            >
              <Text style={styles.placeOrderButtonText}>
                Place Order with {selectedVendor?.name}
              </Text>
            </TouchableOpacity>
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
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
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
  searchContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: 'white',
  },
  searchInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginRight: 10,
  },
  filterButton: {
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  filterButtonText: {
    fontSize: 18,
  },
  categoriesContainer: {
    padding: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    marginRight: 10,
  },
  categoryButtonActive: {
    backgroundColor: '#4CAF50',
  },
  categoryText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  categoryTextActive: {
    color: 'white',
  },
  vendorsContainer: {
    flex: 1,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
  },
  resultsCount: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  mapToggle: {
    padding: 8,
  },
  mapToggleText: {
    color: '#2196F3',
    fontWeight: '500',
  },
  vendorsList: {
    padding: 15,
  },
  vendorCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  vendorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  vendorImagePlaceholder: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#e3f2fd',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  vendorInitial: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  vendorInfo: {
    flex: 1,
  },
  vendorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  vendorType: {
    fontSize: 14,
    color: '#666',
    textTransform: 'capitalize',
    marginBottom: 2,
  },
  vendorDistance: {
    fontSize: 12,
    color: '#4CAF50',
  },
  vendorDetails: {
    marginBottom: 10,
  },
  vendorAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  businessHours: {
    fontSize: 12,
    color: '#666',
  },
  productsPreview: {
    marginTop: 10,
  },
  productsLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    color: '#333',
  },
  productTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  productTag: {
    backgroundColor: '#e8f5e8',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  productTagText: {
    fontSize: 12,
    color: '#4CAF50',
  },
  moreProducts: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  cartIndicator: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#FF9800',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  cartIndicatorText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  vendorDetailContainer: {
    flex: 1,
  },
  vendorDetailHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    fontSize: 16,
    color: '#2196F3',
    fontWeight: '500',
  },
  vendorDetailInfo: {
    flex: 1,
  },
  vendorDetailName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  vendorDetailType: {
    fontSize: 14,
    color: '#666',
    textTransform: 'capitalize',
    marginBottom: 2,
  },
  vendorDetailDistance: {
    fontSize: 12,
    color: '#4CAF50',
  },
  cartButton: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  cartButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  mapContainer: {
    height: 200,
    margin: 15,
    borderRadius: 12,
    overflow: 'hidden',
  },
  map: {
    flex: 1,
  },
  infoSection: {
    backgroundColor: 'white',
    padding: 15,
    margin: 15,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoGrid: {
    // Add styles for info grid
  },
  infoItem: {
    marginBottom: 10,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
  },
  productsSection: {
    backgroundColor: 'white',
    margin: 15,
    borderRadius: 12,
    padding: 15,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  productsCount: {
    fontSize: 14,
    color: '#666',
  },
  productCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#fafafa',
    borderRadius: 8,
    marginBottom: 10,
  },
  productImagePlaceholder: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#e8f5e8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  productInitial: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  productInfo: {
    flex: 1,
  },
  productName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  productCategory: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
    marginBottom: 2,
  },
  productPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  productUnit: {
    fontSize: 12,
    color: '#999',
  },
  productActions: {
    marginLeft: 10,
  },
  addButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  addButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  quantityControls: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    padding: 4,
  },
  quantityButton: {
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  quantityText: {
    marginHorizontal: 12,
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  checkoutBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  checkoutInfo: {
    flex: 1,
  },
  checkoutTotal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  checkoutItems: {
    fontSize: 14,
    color: '#666',
  },
  checkoutButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  checkoutButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  cartModalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  cartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  cartTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    fontSize: 20,
    color: '#666',
  },
  emptyCart: {
    padding: 40,
    alignItems: 'center',
  },
  emptyCartText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 8,
  },
  emptyCartSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  cartItems: {
    maxHeight: 300,
  },
  cartItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  cartItemInfo: {
    flex: 1,
  },
  cartItemName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  cartItemPrice: {
    fontSize: 14,
    color: '#666',
  },
  cartItemControls: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 15,
  },
  cartQuantityButton: {
    width: 28,
    height: 28,
    backgroundColor: '#f0f0f0',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cartQuantityText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  cartQuantity: {
    marginHorizontal: 12,
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  cartItemTotal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
    minWidth: 80,
    textAlign: 'right',
  },
  cartFooter: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  cartTotal: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  cartTotalLabel: {
    fontSize: 18,
    fontWeight: '500',
    color: '#333',
  },
  cartTotalAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  checkoutModalButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  checkoutModalButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  orderModalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '90%',
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  orderTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  orderTypeSelection: {
    marginBottom: 20,
  },
  orderSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  orderTypeButtons: {
    flexDirection: 'row',
  },
  orderTypeButton: {
    flex: 1,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  orderTypeButtonActive: {
    backgroundColor: '#e3f2fd',
    borderColor: '#2196F3',
    borderWidth: 2,
  },
  orderTypeText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginBottom: 4,
  },
  orderTypeTextActive: {
    color: '#2196F3',
  },
  orderTypeDescription: {
    fontSize: 12,
    color: '#999',
  },
  orderSummary: {
    marginBottom: 20,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  orderItemName: {
    flex: 1,
    fontSize: 14,
    color: '#333',
  },
  orderItemDetails: {
    fontSize: 12,
    color: '#666',
    marginRight: 10,
  },
  orderItemTotal: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  orderTotal: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 2,
    borderTopColor: '#e0e0e0',
  },
  orderTotalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  orderTotalAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  placeOrderButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
  },
  placeOrderButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
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
  retryButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  noProducts: {
    padding: 20,
    alignItems: 'center',
  },
  noProductsText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});

export default VendorMarketplace;