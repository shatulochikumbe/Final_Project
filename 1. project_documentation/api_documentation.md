# ZaNuri API Documentation

## Base URL
`https://api.zanuri.ai/v1`

## Authentication
All endpoints require JWT token in header:
`Authorization: Bearer <token>`

## Endpoints

### 1. User Management

#### POST /auth/register
Register new user
```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword",
  "phone": "+260123456789"
}

Response:
{
  "user_id": "123",
  "token": "jwt_token",
  "profile_complete": false
}

Request:
{
  "user_id": "123",
  "health_goals": ["weight_loss", "energy"],
  "dietary_restrictions": ["lactose"],
  "budget_range": "medium",
  "preferences": {
    "likes": ["vegetables", "chicken"],
    "dislikes": ["fish"]
  }
}

Response:
{
  "week_plan": {
    "monday": {
      "breakfast": {"recipe": "Oatmeal", "ingredients": [...]},
      "lunch": {"recipe": "Vegetable Stir-fry", "ingredients": [...]}
    }
  },
  "shopping_list": {
    "total_estimated_cost": "ZMW 245.50",
    "items": [
      {"name": "Tomatoes", "quantity": "1kg", "estimated_cost": "ZMW 15"}
    ]
  }
}

Request:
{
  "user_id": "123",
  "date": "2024-01-15",
  "meals_consumed": ["breakfast", "lunch"],
  "water_intake": 5,
  "weight": 75.5
}

Request:
{
  "user_location": {"lat": -15.4167, "lng": 28.2833},
  "radius_km": 5
}

Response:
{
  "vendors": [
    {
      "id": "v1",
      "name": "Soweto Market Stall 12",
      "products": ["tomatoes", "onions", "cabbage"],
      "distance_km": 1.2
    }
  ]
}