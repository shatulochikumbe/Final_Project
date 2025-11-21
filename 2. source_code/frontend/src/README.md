# ZaNuri - AI-Powered Food Personalization for Zambia

![ZaNuri Logo](https://via.placeholder.com/150x150.png?text=ZaNuri)

## 🎯 Project Overview

ZaNuri is a mobile-based platform that delivers hyper-personalized meal planning and nutritional guidance to Zambian households. Our AI-powered solution addresses the double burden of malnutrition in Zambia by providing culturally relevant, budget-conscious meal plans using locally available ingredients.

**Tagline:** *Your Personal Chef for a Healthier, Happier Zambia*

## 🚀 Key Features

### 1. **AI-Powered Personalization**
- 2-minute onboarding quiz capturing health goals, dietary restrictions, and budget
- Dynamic meal plans tailored to individual preferences and local food availability
- Smart budget optimization for cost-effective nutrition

### 2. **Localized for Zambia**
- Database built around Zambian staple foods (nshima, kapenta, local vegetables)
- Culturally appropriate recipes and meal patterns
- Real-time pricing from Lusaka markets

### 3. **Integrated Ecosystem**
- **Smart Shopping Lists**: Optimized lists organized by vendor/aisle
- **Vendor Marketplace**: Direct connection to local farmers and supermarkets
- **Progress Tracking**: Health monitoring with visual analytics and photo tracking

### 4. **Multi-Platform Accessibility**
- Full-featured mobile app for smartphones
- USSD/SMS service for feature phones
- Low data consumption design

## 🛠 Technical Architecture

### Frontend (React Native)
```
frontend/
├── src/
│   ├── components/
│   │   ├── OnboardingQuiz.js
│   │   ├── MealPlanner.js
│   │   ├── ShoppingList.js
│   │   ├── VendorMarketplace.js
│   │   └── ProgressTracker.js
│   ├── screens/
│   ├── services/
│   └── assets/
```

### Backend (Node.js/Express)
```
backend/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   │   ├── ai_engine/
│   │   ├── meal_planning.py
│   │   └── user_profiling.py
│   └── utils/
```

### Database (PostgreSQL)
- User profiles and preferences
- Zambian food database with nutritional information
- Recipe database with local ingredients
- Vendor and product information

## 📋 Prerequisites

Before running this project, ensure you have the following installed:

- Node.js 16+
- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- Expo CLI (for mobile development)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/zanuri/platform.git
cd zaNuri
```

### 2. Backend Setup
```bash
cd backend
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
npm run migrate

# Start the development server
npm run dev
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Start the Expo development server
npm start
```

### 4. Database Setup
```bash
cd database
psql -U postgres -f schema.sql
psql -U postgres -f sample_data/zambian_foods.sql
```

## 🎯 Usage

### For End Users
1. **Download the App** from Google Play Store or Apple App Store
2. **Complete Onboarding**: 2-minute health and preference assessment
3. **Receive Personalized Meal Plan**: AI-generated weekly plan with local recipes
4. **Shop Smart**: Use optimized shopping lists with vendor integration
5. **Track Progress**: Monitor health goals with visual analytics

### For Developers
```javascript
// Example: Generating a meal plan
const mealPlan = await zaNuriAPI.generateMealPlan(userId, preferences);

// Example: Adding to shopping cart
zaNuriAPI.addToCart(userId, vendorId, product, quantity);
```

## 📊 Data Sources

### Nutritional Database
- Zambia Food and Nutrition Commission data
- USDA FoodData Central
- Local market research in Lusaka
- Traditional Zambian recipe analysis

### Vendor Network
- Supermarkets (Shoprite, Pick n Pay, etc.)
- Local markets (Soweto, Town Centre Market)
- Smallholder farmers
- Local butcheries and green grocers

## 🏗 Project Structure

```
zaNuri-ai/
├── 📁 1. PROJECT_DOCUMENTATION/
├── 📁 2. SOURCE_CODE/
│   ├── 📁 frontend/ (React Native)
│   ├── 📁 backend/ (Node.js/Express)
│   └── 📁 database/ (PostgreSQL)
├── 📁 3. AI_ML_MODULES/
├── 📁 4. DEMONSTRATION/
├── 📁 5. TESTING/
├── 📁 6. DEPLOYMENT/
├── 📁 7. BUSINESS_MATERIALS/
└── 📁 8. REFLECTION_DOCUMENTATION/
```

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🧪 Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run end-to-end tests
npm run test:e2e
```

## 📱 Deployment

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
npm run migrate

# Seed production data
npm run seed:production
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/zanuri
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your_jwt_secret
JWT_EXPIRY=24h

# External APIs
GOOGLE_MAPS_API_KEY=your_key
NUTRITIONIX_APP_ID=your_id
```

## 👥 Team

- **[Your Name]** - CEO & Founder
- **[Co-founder Name]** - CTO & AI Engineer
- **[Co-founder Name]** - Head of Nutrition & Community
- **Advisory Board** - Experts in agribusiness, public health, and Zambian market development

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Zambia Food and Nutrition Commission for nutritional data
- Local farmers and vendors in Lusaka for partnership
- Power Learn Project for incubation support
- Open-source community for tools and libraries

## 📞 Contact & Support

- **Website**: [www.zanuri.zm](https://www.zanuri.zm)
- **Email**: hello@zanuri.ai
- **Business Inquiries**: partnerships@zanuri.zm
- **Technical Support**: support@zanuri.zm

## 🌟 Social Impact

ZaNuri AI is committed to:
- Improving public health through personalized nutrition
- Supporting local economies by connecting consumers with vendors
- Reducing food waste through smart planning
- Making healthy eating accessible to all Zambians

---

<div align="center">

**Built with ❤️ for a healthier Zambia**

*Part of the Power Learn Project Final Project Series*

</div>