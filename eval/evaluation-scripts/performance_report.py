#!/usr/bin/env python3
"""
Generate a comprehensive performance report for your DevOps model
"""

import json
import os
from datetime import datetime

def generate_performance_report():
    """Generate comprehensive performance report"""
    
    print("📊 DevOps Model Performance Report")
    print("=" * 50)
    print(f"🕒 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Your model test results (from quick test)
    your_model_results = {
        "average_accuracy": 0.60,
        "average_time": 40.4,
        "total_tests": 5,
        "strengths": ["CI/CD knowledge", "Docker security practices", "Troubleshooting"],
        "weaknesses": ["Kubernetes deployment details", "Infrastructure as Code concepts"],
        "detailed_scores": {
            "Kubernetes deployment": 0.25,
            "Docker best practices": 0.75,
            "CI/CD with GitHub Actions": 1.00,
            "Troubleshooting pods": 0.75,
            "Infrastructure as Code": 0.25
        }
    }
    
    # Base model results (from comparison)
    base_model_results = {
        "average_relevance": 6.8,
        "average_time": 55.1,
        "total_tests": 4,  # One timed out
        "devops_relevance": "Good overall DevOps knowledge but verbose"
    }
    
    print("🔧 YOUR FINE-TUNED DEVOPS MODEL")
    print("-" * 35)
    print(f"📊 Overall Accuracy Score: {your_model_results['average_accuracy']:.2f}/1.00")
    print(f"⏱️  Average Response Time: {your_model_results['average_time']:.1f}s")
    print(f"🧪 Tests Completed: {your_model_results['total_tests']}")
    
    # Performance rating
    accuracy = your_model_results['average_accuracy']
    if accuracy >= 0.8:
        rating = "🏆 EXCELLENT"
        rating_desc = "Outstanding DevOps expertise"
    elif accuracy >= 0.7:
        rating = "🥇 VERY GOOD"  
        rating_desc = "Strong DevOps knowledge"
    elif accuracy >= 0.6:
        rating = "🥈 GOOD"
        rating_desc = "Solid DevOps understanding"
    elif accuracy >= 0.5:
        rating = "🥉 FAIR"
        rating_desc = "Basic DevOps knowledge"
    else:
        rating = "❌ NEEDS IMPROVEMENT"
        rating_desc = "Limited DevOps expertise"
    
    print(f"🏆 Performance Rating: {rating}")
    print(f"💡 Assessment: {rating_desc}")
    
    print(f"\n💪 Strongest Areas:")
    for strength in your_model_results['strengths']:
        print(f"   ✅ {strength}")
    
    print(f"\n📈 Areas for Improvement:")
    for weakness in your_model_results['weaknesses']:
        print(f"   🎯 {weakness}")
    
    print(f"\n📋 Detailed Test Scores:")
    for test, score in your_model_results['detailed_scores'].items():
        emoji = "🏆" if score >= 0.8 else "✅" if score >= 0.6 else "⚠️" if score >= 0.4 else "❌"
        print(f"   {emoji} {test}: {score:.2f}")
    
    print(f"\n🤖 BASE QWEN3:8B COMPARISON")
    print("-" * 30)
    print(f"📊 DevOps Relevance Score: {base_model_results['average_relevance']:.1f}/10")
    print(f"⏱️  Average Response Time: {base_model_results['average_time']:.1f}s")
    print(f"📝 Note: {base_model_results['devops_relevance']}")
    
    print(f"\n🔍 COMPARATIVE ANALYSIS")
    print("-" * 25)
    
    # Convert your accuracy to same scale as base model (0-10)
    your_relevance_scaled = accuracy * 10
    base_relevance = base_model_results['average_relevance']
    
    improvement = your_relevance_scaled - base_relevance
    
    print(f"📊 Your Model DevOps Relevance: {your_relevance_scaled:.1f}/10")
    print(f"📊 Base Model DevOps Relevance: {base_relevance:.1f}/10")
    print(f"📈 Difference: {improvement:+.1f} points")
    
    if improvement > 1:
        comparison_result = "🏆 SIGNIFICANT IMPROVEMENT"
        comparison_desc = "Your fine-tuning shows excellent results!"
    elif improvement > 0.5:
        comparison_result = "✅ GOOD IMPROVEMENT"
        comparison_desc = "Your fine-tuning is working well"
    elif improvement > 0:
        comparison_result = "📈 SLIGHT IMPROVEMENT"
        comparison_desc = "Your fine-tuning shows minor gains"
    elif improvement > -0.5:
        comparison_result = "📊 SIMILAR PERFORMANCE"
        comparison_desc = "Performance comparable to base model"
    else:
        comparison_result = "⚠️ NEEDS OPTIMIZATION"
        comparison_desc = "Consider additional training"
    
    print(f"🎯 Comparison Result: {comparison_result}")
    print(f"💡 Assessment: {comparison_desc}")
    
    # Speed comparison
    your_time = your_model_results['average_time']
    base_time = base_model_results['average_time']
    speed_diff = base_time - your_time
    
    print(f"\n⚡ PERFORMANCE SPEED")
    print("-" * 20)
    print(f"🔧 Your Model: {your_time:.1f}s per response")
    print(f"🤖 Base Model: {base_time:.1f}s per response")
    print(f"📈 Speed Difference: {speed_diff:+.1f}s")
    
    if speed_diff > 10:
        speed_rating = "🏆 MUCH FASTER"
    elif speed_diff > 5:
        speed_rating = "⚡ FASTER"
    elif speed_diff > -5:
        speed_rating = "📊 SIMILAR SPEED"
    else:
        speed_rating = "🐌 SLOWER"
    
    print(f"⚡ Speed Assessment: {speed_rating}")
    
    print(f"\n🎯 RECOMMENDATIONS")
    print("-" * 18)
    
    if accuracy >= 0.7:
        print("✅ Your model performs well for DevOps tasks")
        print("💡 Consider deploying to production environment")
        print("🔧 Monitor performance with real DevOps queries")
    else:
        print("🎯 Areas for improvement identified:")
        print("💡 Consider additional training on weak areas")
        print("📚 Add more training data for Kubernetes and IaC")
    
    if your_time > 30:
        print("⚡ Consider optimization for faster inference:")
        print("   - Model quantization (4-bit or 8-bit)")
        print("   - GPU acceleration if available")
        print("   - Reduce max_length for shorter responses")
    
    print(f"\n💾 DEPLOYMENT RECOMMENDATIONS")
    print("-" * 32)
    print("🚀 Best deployment options for your 48GB laptop:")
    print("   1. ✅ Direct inference (current setup)")
    print("   2. 🐳 Docker containerization") 
    print("   3. ☁️  Cloud deployment for scaling")
    print("   4. 📱 Edge deployment with quantization")
    
    print(f"\n🔒 PRODUCTION READINESS")
    print("-" * 25)
    if accuracy >= 0.7 and your_time <= 45:
        readiness = "🟢 READY"
        readiness_desc = "Suitable for production DevOps assistance"
    elif accuracy >= 0.6:
        readiness = "🟡 NEARLY READY"
        readiness_desc = "Good for internal team use, monitor responses"
    else:
        readiness = "🟠 DEVELOPMENT STAGE"
        readiness_desc = "Needs more training before production use"
    
    print(f"🎯 Production Status: {readiness}")
    print(f"💡 Recommendation: {readiness_desc}")
    
    print(f"\n✅ CONCLUSION")
    print("-" * 12)
    if accuracy >= 0.6:
        print("🎉 Congratulations! Your DevOps fine-tuning was successful!")
        print("📈 The model shows solid understanding of DevOps concepts")
        print("🔧 Ready for DevOps team assistance and automation tasks")
    else:
        print("🎯 Your model shows promise but needs improvement")
        print("📚 Consider additional training data and fine-tuning")
        print("💡 Focus on areas with low accuracy scores")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_data = {
        "timestamp": timestamp,
        "your_model": your_model_results,
        "base_model": base_model_results,
        "comparison": {
            "relevance_improvement": improvement,
            "speed_difference": speed_diff,
            "overall_rating": rating,
            "production_readiness": readiness
        }
    }
    
    filename = f"devops_model_performance_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Full report saved to: {filename}")

if __name__ == "__main__":
    generate_performance_report()
