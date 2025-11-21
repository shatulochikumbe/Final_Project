import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, ndcg_score
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self, recommendation_engine, test_data):
        self.engine = recommendation_engine
        self.test_data = test_data
        
    def evaluate_precision_recall(self, k=10):
        """Evaluate precision and recall at K"""
        precisions = []
        recalls = []
        
        for user_id in self.test_data['user_id'].unique():
            user_data = self.test_data[self.test_data['user_id'] == user_id]
            actual_interactions = set(user_data['recipe_id'].tolist())
            
            # Get recommendations
            user_preferences = self.get_user_preferences(user_id)
            recommendations = self.engine.hybrid_recommendations(
                user_id, user_preferences, top_n=k
            )
            recommended_ids = set([rec['recipe_id'] for rec in recommendations])
            
            # Calculate metrics
            if len(actual_interactions) > 0:
                true_positives = len(actual_interactions.intersection(recommended_ids))
                precision = true_positives / len(recommended_ids) if recommended_ids else 0
                recall = true_positives / len(actual_interactions) if actual_interactions else 0
                
                precisions.append(precision)
                recalls.append(recall)
        
        return {
            'precision@k': np.mean(precisions),
            'recall@k': np.mean(recalls),
            'f1@k': 2 * (np.mean(precisions) * np.mean(recalls)) / 
                    (np.mean(precisions) + np.mean(recalls)) if (np.mean(precisions) + np.mean(recalls)) > 0 else 0
        }
    
    def evaluate_ndcg(self, k=10):
        """Evaluate Normalized Discounted Cumulative Gain"""
        ndcg_scores = []
        
        for user_id in self.test_data['user_id'].unique():
            user_data = self.test_data[self.test_data['user_id'] == user_id]
            
            # Create relevance scores (1 for interacted, 0 for not)
            actual_relevance = np.zeros(k)
            for i, recipe_id in enumerate(user_data['recipe_id'].head(k)):
                if i < k:
                    actual_relevance[i] = 1
            
            # Get predicted scores
            user_preferences = self.get_user_preferences(user_id)
            recommendations = self.engine.hybrid_recommendations(
                user_id, user_preferences, top_n=k
            )
            predicted_scores = [rec['score'] for rec in recommendations]
            
            if len(predicted_scores) > 0:
                ndcg = ndcg_score([actual_relevance], [predicted_scores])
                ndcg_scores.append(ndcg)
        
        return np.mean(ndcg_scores)
    
    def get_user_preferences(self, user_id):
        """Get user preferences for evaluation"""
        # This would typically query the user database
        # For evaluation, we use test data to simulate user preferences
        user_data = self.test_data[self.test_data['user_id'] == user_id]
        
        return {
            'health_goals': ['general_health'],  # Default
            'budget_range': 'medium',  # Default
            'dietary_restrictions': [],
            'preferred_recipes': user_data['recipe_id'].tolist()[:5]
        }
    
    def plot_metrics_comparison(self, models_metrics):
        """Plot comparison of different models"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Precision comparison
        models = list(models_metrics.keys())
        precisions = [metrics['precision@10'] for metrics in models_metrics.values()]
        
        axes[0, 0].bar(models, precisions, color='skyblue')
        axes[0, 0].set_title('Precision@10 Comparison')
        axes[0, 0].set_ylabel('Precision')
        
        # Recall comparison
        recalls = [metrics['recall@10'] for metrics in models_metrics.values()]
        axes[0, 1].bar(models, recalls, color='lightcoral')
        axes[0, 1].set_title('Recall@10 Comparison')
        axes[0, 1].set_ylabel('Recall')
        
        # F1-score comparison
        f1_scores = [metrics['f1@10'] for metrics in models_metrics.values()]
        axes[1, 0].bar(models, f1_scores, color='lightgreen')
        axes[1, 0].set_title('F1-Score@10 Comparison')
        axes[1, 0].set_ylabel('F1-Score')
        
        # NDCG comparison
        ndcg_scores = [metrics.get('ndcg@10', 0) for metrics in models_metrics.values()]
        axes[1, 1].bar(models, ndcg_scores, color='gold')
        axes[1, 1].set_title('NDCG@10 Comparison')
        axes[1, 1].set_ylabel('NDCG')
        
        plt.tight_layout()
        plt.savefig('../reports/model_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.performance_log = []
    
    def log_performance(self, timestamp, model_name, metrics):
        """Log model performance metrics"""
        log_entry = {
            'timestamp': timestamp,
            'model_name': model_name,
            **metrics
        }
        self.performance_log.append(log_entry)
    
    def generate_performance_report(self):
        """Generate performance report"""
        if not self.performance_log:
            return "No performance data available"
        
        df = pd.DataFrame(self.performance_log)
        
        report = {
            'latest_metrics': df.iloc[-1].to_dict(),
            'trend_analysis': self.analyze_trends(df),
            'recommendations': self.generate_recommendations(df)
        }
        
        return report
    
    def analyze_trends(self, df):
        """Analyze performance trends over time"""
        trends = {}
        
        for metric in ['precision@10', 'recall@10', 'f1@10']:
            if metric in df.columns:
                trend = df[metric].pct_change().mean()  # Average percentage change
                trends[metric] = trend
        
        return trends
    
    def generate_recommendations(self, df):
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Check if precision is declining
        if 'precision@10' in df.columns and len(df) > 5:
            recent_precision = df['precision@10'].tail(5).mean()
            older_precision = df['precision@10'].head(5).mean()
            
            if recent_precision < older_precision * 0.9:  # 10% decline
                recommendations.append(
                    "Precision has declined by more than 10%. Consider retraining the model."
                )
        
        # Check for data drift
        if len(df) > 10:
            precision_std = df['precision@10'].std()
            if precision_std > 0.1:  # High variability
                recommendations.append(
                    "High variability in precision detected. Investigate potential data drift."
                )
        
        return recommendations if recommendations else ["Model performance is stable."]