const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const config = require('./config');

// Route imports
const authRoutes = require('./app/routes/auth');
const mealPlanRoutes = require('./app/routes/mealPlan');
const userRoutes = require('./app/routes/users');
const vendorRoutes = require('./app/routes/vendors');

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/meal-plan', mealPlanRoutes);
app.use('/api/users', userRoutes);
app.use('/api/vendors', vendorRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    service: 'ZaNuri'
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

const PORT = config.port || 3000;
app.listen(PORT, () => {
  console.log(`ZaNuri API server running on port ${PORT}`);
});

module.exports = app;