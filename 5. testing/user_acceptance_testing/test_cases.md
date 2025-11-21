# User Acceptance Test Cases - ZaNuri

## Test Suite 1: User Onboarding & Registration

### TC-001: New User Registration
**Description:** Test new user account creation
**Preconditions:** User has downloaded the ZaNuri AI app
**Test Steps:**
1. Launch ZaNuri AI application
2. Tap "Get Started" on welcome screen
3. Enter email: testuser@zanuri.co.zm
4. Enter password: SecurePass123
5. Enter phone number: +260123456789
6. Tap "Create Account"

**Expected Results:**
- Account is created successfully
- User receives confirmation message
- User is redirected to onboarding process
- JWT token is generated and stored

**Acceptance Criteria:**
- ✅ Account creation within 5 seconds
- ✅ Input validation for email and password
- ✅ Zambian phone number format accepted
- ✅ Secure password hashing

### TC-002: Health Profile Onboarding
**Description:** Test health and preference data collection
**Preconditions:** User has completed registration
**Test Steps:**
1. Complete health goals selection (Weight Loss, Energy)
2. Select dietary restrictions (Lactose Intolerant)
3. Set budget range (Medium: ZMW 800-1500/week)
4. Add family members (Spouse + 2 children)
5. Set cooking time preferences (30-45 minutes)
6. Complete onboarding

**Expected Results:**
- Profile is saved successfully
- AI processes preferences
- Personalized welcome message shown
- Redirect to main dashboard

**Acceptance Criteria:**
- ✅ All preference data captured accurately
- ✅ Family size affects meal portions
- ✅ Budget constraints respected in meal planning
- ✅ Onboarding completes within 2 minutes

## Test Suite 2: Meal Planning & Recommendations

### TC-003: Weekly Meal Plan Generation
**Description:** Test AI-generated weekly meal plan
**Preconditions:** User has completed onboarding
**Test Steps:**
1. Navigate to Meal Planning section
2. Tap "Generate Weekly Plan"
3. Review 7-day meal plan
4. Check meal details for Monday dinner
5. Verify nutritional information
6. Check total estimated cost

**Expected Results:**
- 7-day plan generated within 10 seconds
- Meals match user's health goals and restrictions
- Zambian staple foods included (nshima, etc.)
- Cost within budget range
- Preparation times appropriate

**Acceptance Criteria:**
- ✅ Plan generation < 10 seconds
- ✅ Cultural relevance maintained
- ✅ Nutritional goals addressed
- ✅ Budget constraints respected

### TC-004: Meal Plan Customization
**Description:** Test meal swapping and plan adjustments
**Preconditions:** Weekly meal plan is generated
**Test Steps:**
1. Tap on Wednesday lunch meal
2. Select "Swap Meal" option
3. Choose alternative from suggestions
4. Apply changes
5. Verify cost impact
6. Save updated plan

**Expected Results:**
- Alternative suggestions are relevant
- Cost changes are calculated
- Nutritional impact shown
- Plan updates immediately

**Acceptance Criteria:**
- ✅ Relevant alternative suggestions
- ✅ Real-time cost calculation
- ✅ Nutritional consistency maintained
- ✅ User preferences preserved

## Test Suite 3: Shopping & Vendor Integration

### TC-005: Smart Shopping List Generation
**Description:** Test automated shopping list creation
**Preconditions:** Weekly meal plan is active
**Test Steps:**
1. Navigate to Shopping section
2. Tap "Generate Shopping List"
3. Review categorized items
4. Check quantities and estimated costs
5. Verify vendor suggestions
6. Share list with family member

**Expected Results:**
- List generated from meal plan ingredients
- Items categorized (Vegetables, Protein, etc.)
- Quantities calculated for family size
- Vendor prices shown where available
- Sharing functionality works

**Acceptance Criteria:**
- ✅ Accurate ingredient aggregation
- ✅ Family-size portion calculations
- ✅ Local vendor price integration
- ✅ List sharing capability

### TC-006: Vendor Price Comparison
**Description:** Test price comparison across vendors
**Preconditions:** Shopping list is generated
**Test Steps:**
1. Tap on "Maize Meal" in shopping list
2. View price comparison across vendors
3. Check Soweto Market vs Supermarket prices
4. View distance and ratings
5. Select preferred vendor
6. Add to cart from chosen vendor

**Expected Results:**
- Price comparison shown for item
- Distance and quality indicators visible
- Vendor selection affects total cost
- Cart updates with vendor-specific items

**Acceptance Criteria:**
- ✅ Accurate price data from multiple vendors
- ✅ Distance calculations correct
- ✅ Vendor ratings displayed
- ✅ Cart management works seamlessly

## Test Suite 4: Progress Tracking & Analytics

### TC-007: Daily Progress Logging
**Description:** Test daily health progress tracking
**Preconditions:** User has active meal plan
**Test Steps:**
1. Navigate to Progress section
2. Log today's weight: 68.5kg
3. Track water intake: 6 glasses
4. Mark completed meals (breakfast, lunch)
5. Add progress photo
6. Save daily log

**Expected Results:**
- Progress data saved successfully
- Water tracking visualization updates
- Meal completion affects weekly analytics
- Photo stored securely

**Acceptance Criteria:**
- ✅ Quick logging (under 30 seconds)
- ✅ Visual feedback for completions
- ✅ Photo upload and storage
- ✅ Data persistence

### TC-008: Progress Analytics & Insights
**Description:** Test health analytics and recommendations
**Preconditions:** 2+ weeks of progress data logged
**Test Steps:**
1. Navigate to Analytics dashboard
2. Review weight trend chart
3. Check nutrition analysis
4. Read AI-generated insights
5. View achievement badges
6. Share progress with healthcare provider

**Expected Results:**
- Trend charts show progress over time
- Nutritional analysis matches logged data
- Personalized insights provided
- Achievement system motivates continued use

**Acceptance Criteria:**
- ✅ Accurate trend calculations
- ✅ Meaningful insights generated
- ✅ Achievement system functional
- ✅ Data export capability

## Test Suite 5: Zambian Cultural Relevance

### TC-009: Local Recipe Database
**Description:** Test Zambian recipe authenticity
**Preconditions:** User profile indicates Zambian preferences
**Test Steps:**
1. Search for "nshima" in recipes
2. Verify traditional preparation methods
3. Check local ingredient availability
4. Review cultural context notes
5. Test recipe scaling for family size

**Expected Results:**
- Authentic Zambian recipes returned
- Local cooking methods described
- Ingredients available in Zambian markets
- Cultural context provided

**Acceptance Criteria:**
- ✅ Recipe authenticity maintained
- ✅ Local ingredient focus
- ✅ Cultural context included
- ✅ Family scaling accurate

### TC-010: Local Market Integration
**Description:** Test integration with Zambian markets
**Preconditions:** User location set to Lusaka
**Test Steps:**
1. View nearby vendors map
2. Check Soweto Market stall information
3. Verify local product availability
4. Test price accuracy for local goods
5. Check seasonal availability indicators

**Expected Results:**
- Local markets shown on map
- Accurate stall and product information
- Realistic local pricing
- Seasonal availability noted

**Acceptance Criteria:**
- ✅ Zambian market data accuracy
- ✅ Local price realism
- ✅ Seasonal considerations
- ✅ Vendor reliability indicators

## Test Suite 6: Performance & Usability

### TC-011: App Performance
**Description:** Test application performance standards
**Preconditions:** App installed on mid-range Android device
**Test Steps:**
1. Measure app launch time
2. Test meal plan generation speed
3. Check shopping list loading time
4. Verify offline functionality
5. Test battery usage during typical session

**Expected Results:**
- App launches within 3 seconds
- Meal plans generate within 10 seconds
- Shopping lists load within 2 seconds
- Core features work offline
- Reasonable battery consumption

**Acceptance Criteria:**
- ✅ Performance benchmarks met
- ✅ Offline functionality maintained
- ✅ Battery efficient
- ✅ Low data consumption

### TC-012: Accessibility & Localization
**Description:** Test accessibility for diverse users
**Preconditions:** App installed with default settings
**Test Steps:**
1. Test font size adjustments
2. Verify color contrast ratios
3. Check screen reader compatibility
4. Test local language support (Bemba/Nyanja)
5. Verify low-literacy user experience

**Expected Results:**
- Accessible to users with visual impairments
- Local language options available
- Simple, intuitive interface
- Clear visual hierarchy

**Acceptance Criteria:**
- ✅ WCAG 2.1 AA compliance
- ✅ Local language support
- ✅ Simple navigation
- ✅ Clear visual design

## Test Suite 7: Error Handling & Edge Cases

### TC-013: Network Connectivity Issues
**Description:** Test app behavior with poor connectivity
**Preconditions:** App has cached data
**Test Steps:**
1. Disable network connectivity
2. Attempt to generate new meal plan
3. Try to view vendor prices
4. Test progress logging
5. Reconnect and verify sync

**Expected Results:**
- Graceful offline handling
- Clear connectivity status indicators
- Data sync when reconnected
- No data loss

**Acceptance Criteria:**
- ✅ Offline functionality
- ✅ Clear error messages
- ✅ Data synchronization
- ✅ No data corruption

### TC-014: Extreme User Scenarios
**Description:** Test edge cases and boundary conditions
**Preconditions:** Test environment setup
**Test Steps:**
1. Test with very low budget (ZMW 200/week)
2. Test with large family (8+ members)
3. Test with multiple medical conditions
4. Test with all dietary restrictions
5. Verify system stability

**Expected Results:**
- System handles edge cases gracefully
- Appropriate recommendations provided
- No crashes or data corruption
- Helpful guidance for extreme scenarios

**Acceptance Criteria:**
- ✅ System stability maintained
- ✅ Helpful user guidance
- ✅ No catastrophic failures
- ✅ Appropriate fallbacks

## Test Execution Checklist

### Pre-Test Setup
- [ ] Test accounts created
- [ ] Test data prepared
- [ ] Testing environment configured
- [ ] Network conditions simulated
- [ ] Device variety prepared

### Post-Test Validation
- [ ] All test cases executed
- [ ] Results documented
- [ ] Bugs logged and prioritized
- [ ] Performance metrics recorded
- [ ] User feedback incorporated

### Success Metrics
- **Performance:** 95% of operations under 5 seconds
- **Reliability:** 99% uptime, no data loss
- **User Satisfaction:** 90%+ positive feedback
- **Cultural Relevance:** 100% Zambian recipe authenticity
- **Accessibility:** Full WCAG 2.1 AA compliance