const db = require('../../config/database');

class User {
  static async create(userData) {
    const { email, password_hash, phone } = userData;
    const result = await db('users')
      .insert({
        email,
        password_hash,
        phone,
        created_at: new Date()
      })
      .returning('*');
    
    return result[0];
  }

  static async findByEmail(email) {
    return db('users').where({ email }).first();
  }

  static async findById(id) {
    return db('users').where({ id }).first();
  }

  static async updateProfile(userId, profileData) {
    const result = await db('users')
      .where({ id: userId })
      .update({
        ...profileData,
        profile_completed: true,
        updated_at: new Date()
      })
      .returning('*');
    
    return result[0];
  }
}

module.exports = User;