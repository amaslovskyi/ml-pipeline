#!/usr/bin/env python3
"""
Comprehensive DevOps Model Performance and Accuracy Testing Suite
Tests your fine-tuned Qwen3 DevOps model against various DevOps scenarios
"""

import os
import json
import time
import torch
import requests
from typing import Dict, List, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import re

class DevOpsModelEvaluator:
    def __init__(self, local_model_path: str = None, use_api: bool = False):
        self.local_model_path = local_model_path or os.path.expanduser("~/Downloads/qwen-devops-model")
        self.use_api = use_api
        self.model = None
        self.tokenizer = None
        self.api_base = "http://localhost:8000"
        
        # Test categories
        self.test_categories = {
            "kubernetes": "Kubernetes & Container Orchestration",
            "docker": "Docker & Containerization", 
            "cicd": "CI/CD Pipelines",
            "iac": "Infrastructure as Code",
            "monitoring": "Monitoring & Observability",
            "security": "Security & Compliance",
            "troubleshooting": "Troubleshooting & Debugging"
        }
        
        # Evaluation metrics
        self.results = {
            "performance": {},
            "accuracy": {},
            "detailed_responses": []
        }
    
    def load_model_local(self):
        """Load the model locally for testing"""
        print("🚀 Loading DevOps Foundation Model Locally...")
        
        try:
            # Load base model on CPU to avoid MPS issues
            print("📥 Loading base model...")
            base_model = AutoModelForCausalLM.from_pretrained(
                "Qwen/Qwen3-8B",
                torch_dtype=torch.float16,
                device_map="cpu",
                trust_remote_code=True
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load LoRA adapter
            print(f"📥 Loading LoRA adapter from: {self.local_model_path}")
            self.model = PeftModel.from_pretrained(base_model, self.local_model_path)
            
            print("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            return False
    
    def check_api_server(self):
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ API server is healthy: {health}")
                return True
            else:
                print(f"❌ API server unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API server not available: {str(e)}")
            return False
    
    def generate_response_local(self, prompt: str, max_length: int = 512) -> Tuple[str, float, int]:
        """Generate response using local model"""
        start_time = time.time()
        
        # Format prompt for Qwen3
        formatted_prompt = f"<|im_start|>system\nYou are a DevOps expert assistant. Provide practical, actionable advice with code examples when applicable.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        input_length = inputs.input_ids.shape[1]
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=min(max_length + input_length, 2048),
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.05
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = full_response[len(formatted_prompt):].strip()
        
        # Clean up response
        if response_text.endswith("<|im_end|>"):
            response_text = response_text[:-10].strip()
        
        generation_time = time.time() - start_time
        tokens_generated = outputs[0].shape[0] - input_length
        
        return response_text, generation_time, tokens_generated
    
    def generate_response_api(self, prompt: str, max_length: int = 512) -> Tuple[str, float, int]:
        """Generate response using API"""
        start_time = time.time()
        
        payload = {
            "message": prompt,
            "max_length": max_length,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(f"{self.api_base}/chat", json=payload, timeout=60)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return result['response'], result['generation_time'], result['tokens_generated']
            else:
                return f"API Error: {response.status_code}", generation_time, 0
                
        except Exception as e:
            return f"API Error: {str(e)}", time.time() - start_time, 0
    
    def generate_response(self, prompt: str, max_length: int = 512) -> Tuple[str, float, int]:
        """Generate response using the appropriate method"""
        if self.use_api:
            return self.generate_response_api(prompt, max_length)
        else:
            return self.generate_response_local(prompt, max_length)
    
    def get_devops_test_questions(self) -> Dict[str, List[Dict]]:
        """Get comprehensive DevOps test questions"""
        return {
            "kubernetes": [
                {
                    "question": "How do I deploy a simple web application to Kubernetes with auto-scaling?",
                    "expected_keywords": ["deployment", "service", "hpa", "replicas", "kubectl"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "My Kubernetes pod is stuck in Pending state. How do I troubleshoot this?",
                    "expected_keywords": ["describe", "events", "resources", "node", "scheduling"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I set up ingress controller with SSL termination?",
                    "expected_keywords": ["ingress", "nginx", "tls", "certificate", "secret"],
                    "difficulty": "advanced"
                }
            ],
            "docker": [
                {
                    "question": "How do I create a multi-stage Docker build for a Node.js application?",
                    "expected_keywords": ["FROM", "COPY", "npm install", "multi-stage", "alpine"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "What are Docker security best practices for production?",
                    "expected_keywords": ["non-root", "minimal", "scan", "secrets", "read-only"],
                    "difficulty": "advanced"
                },
                {
                    "question": "How do I optimize Docker image size?",
                    "expected_keywords": ["alpine", "multi-stage", "cache", "layers", ".dockerignore"],
                    "difficulty": "beginner"
                }
            ],
            "cicd": [
                {
                    "question": "How do I set up a CI/CD pipeline with GitHub Actions for a microservice?",
                    "expected_keywords": ["workflow", "build", "test", "deploy", "artifact"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I implement blue-green deployment strategy?",
                    "expected_keywords": ["blue-green", "traffic", "switch", "rollback", "zero-downtime"],
                    "difficulty": "advanced"
                },
                {
                    "question": "What are the stages of a typical CI/CD pipeline?",
                    "expected_keywords": ["build", "test", "security", "deploy", "monitor"],
                    "difficulty": "beginner"
                }
            ],
            "iac": [
                {
                    "question": "How do I create an AWS VPC with public and private subnets using Terraform?",
                    "expected_keywords": ["vpc", "subnet", "route", "gateway", "terraform"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I manage Terraform state securely?",
                    "expected_keywords": ["backend", "s3", "dynamodb", "encryption", "locking"],
                    "difficulty": "advanced"
                },
                {
                    "question": "What is Infrastructure as Code and why is it important?",
                    "expected_keywords": ["version control", "reproducible", "automation", "consistency"],
                    "difficulty": "beginner"
                }
            ],
            "monitoring": [
                {
                    "question": "How do I set up Prometheus and Grafana for Kubernetes monitoring?",
                    "expected_keywords": ["prometheus", "grafana", "metrics", "scrape", "dashboard"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I create effective alerts for my application?",
                    "expected_keywords": ["sli", "slo", "threshold", "alert", "runbook"],
                    "difficulty": "advanced"
                },
                {
                    "question": "What metrics should I monitor for a web application?",
                    "expected_keywords": ["latency", "error rate", "throughput", "saturation"],
                    "difficulty": "beginner"
                }
            ],
            "security": [
                {
                    "question": "How do I implement security scanning in my CI/CD pipeline?",
                    "expected_keywords": ["sast", "dast", "dependency", "container", "vulnerability"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I secure secrets management in Kubernetes?",
                    "expected_keywords": ["secrets", "vault", "encryption", "rbac", "service account"],
                    "difficulty": "advanced"
                },
                {
                    "question": "What are container security best practices?",
                    "expected_keywords": ["scan", "minimal", "non-root", "read-only", "network"],
                    "difficulty": "beginner"
                }
            ],
            "troubleshooting": [
                {
                    "question": "My application is running slowly. How do I diagnose performance issues?",
                    "expected_keywords": ["profiling", "metrics", "logs", "bottleneck", "monitoring"],
                    "difficulty": "intermediate"
                },
                {
                    "question": "How do I debug network connectivity issues in Kubernetes?",
                    "expected_keywords": ["dns", "service", "network policy", "trace", "connectivity"],
                    "difficulty": "advanced"
                },
                {
                    "question": "My deployment failed. What are the first steps to troubleshoot?",
                    "expected_keywords": ["logs", "events", "status", "describe", "rollback"],
                    "difficulty": "beginner"
                }
            ]
        }
    
    def evaluate_response_accuracy(self, response: str, expected_keywords: List[str], difficulty: str) -> Dict:
        """Evaluate response accuracy based on expected keywords and quality"""
        response_lower = response.lower()
        
        # Check keyword coverage
        keywords_found = [kw for kw in expected_keywords if kw.lower() in response_lower]
        keyword_score = len(keywords_found) / len(expected_keywords) if expected_keywords else 0
        
        # Check response quality indicators
        quality_indicators = {
            "has_code_example": bool(re.search(r'```|`[^`]+`', response)),
            "has_steps": bool(re.search(r'\d+\.|step \d+|first|second|then|next', response_lower)),
            "mentions_best_practices": "best practice" in response_lower or "recommendation" in response_lower,
            "provides_explanation": len(response.split()) > 50,
            "mentions_security": "security" in response_lower or "secure" in response_lower,
            "actionable": any(word in response_lower for word in ["run", "execute", "create", "configure", "set up"])
        }
        
        quality_score = sum(quality_indicators.values()) / len(quality_indicators)
        
        # Difficulty-adjusted scoring
        difficulty_weights = {"beginner": 0.8, "intermediate": 1.0, "advanced": 1.2}
        weight = difficulty_weights.get(difficulty, 1.0)
        
        overall_score = (keyword_score * 0.6 + quality_score * 0.4) * weight
        
        return {
            "keyword_score": keyword_score,
            "keywords_found": keywords_found,
            "keywords_missed": [kw for kw in expected_keywords if kw not in keywords_found],
            "quality_score": quality_score,
            "quality_indicators": quality_indicators,
            "overall_score": min(overall_score, 1.0),  # Cap at 1.0
            "difficulty": difficulty
        }
    
    def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation of the DevOps model"""
        print("🧪 Starting Comprehensive DevOps Model Evaluation")
        print("=" * 55)
        
        # Initialize
        if self.use_api:
            if not self.check_api_server():
                print("❌ API server not available, switching to local mode")
                self.use_api = False
        
        if not self.use_api:
            if not self.load_model_local():
                print("❌ Cannot load model locally either")
                return
        
        test_questions = self.get_devops_test_questions()
        
        category_results = {}
        all_scores = []
        
        # Test each category
        for category, category_name in self.test_categories.items():
            print(f"\n📋 Testing Category: {category_name}")
            print("-" * 40)
            
            if category not in test_questions:
                print(f"⚠️  No test questions for {category}")
                continue
            
            category_scores = []
            category_times = []
            category_tokens = []
            
            for i, test_case in enumerate(test_questions[category], 1):
                question = test_case["question"]
                expected_keywords = test_case["expected_keywords"]
                difficulty = test_case["difficulty"]
                
                print(f"\n🔍 Test {i}/{len(test_questions[category])}: {difficulty.title()}")
                print(f"❓ {question}")
                
                # Generate response
                try:
                    response, gen_time, tokens = self.generate_response(question, max_length=400)
                    
                    # Evaluate accuracy
                    accuracy = self.evaluate_response_accuracy(response, expected_keywords, difficulty)
                    
                    # Store results
                    category_scores.append(accuracy["overall_score"])
                    category_times.append(gen_time)
                    category_tokens.append(tokens)
                    all_scores.append(accuracy["overall_score"])
                    
                    # Display results
                    print(f"✅ Generated {tokens} tokens in {gen_time:.1f}s")
                    print(f"📊 Accuracy Score: {accuracy['overall_score']:.2f}")
                    print(f"🎯 Keywords Found: {accuracy['keywords_found']}")
                    if accuracy['keywords_missed']:
                        print(f"❌ Keywords Missed: {accuracy['keywords_missed']}")
                    print(f"💬 Response Preview: {response[:150]}...")
                    
                    # Store detailed results
                    self.results["detailed_responses"].append({
                        "category": category,
                        "question": question,
                        "response": response,
                        "accuracy": accuracy,
                        "performance": {
                            "generation_time": gen_time,
                            "tokens_generated": tokens,
                            "tokens_per_second": tokens / gen_time if gen_time > 0 else 0
                        }
                    })
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    continue
            
            # Category summary
            if category_scores:
                avg_score = sum(category_scores) / len(category_scores)
                avg_time = sum(category_times) / len(category_times)
                avg_tokens = sum(category_tokens) / len(category_tokens)
                
                category_results[category] = {
                    "average_score": avg_score,
                    "average_time": avg_time,
                    "average_tokens": avg_tokens,
                    "total_tests": len(category_scores)
                }
                
                print(f"\n📊 {category_name} Summary:")
                print(f"   Average Accuracy: {avg_score:.2f}")
                print(f"   Average Time: {avg_time:.1f}s")
                print(f"   Average Tokens: {avg_tokens:.0f}")
        
        # Overall results
        self.results["performance"] = category_results
        if all_scores:
            self.results["accuracy"]["overall_average"] = sum(all_scores) / len(all_scores)
            self.results["accuracy"]["total_tests"] = len(all_scores)
        
        self.print_final_report()
        self.save_results()
    
    def print_final_report(self):
        """Print final evaluation report"""
        print("\n" + "=" * 60)
        print("🎯 FINAL DEVOPS MODEL EVALUATION REPORT")
        print("=" * 60)
        
        if "overall_average" in self.results["accuracy"]:
            overall_score = self.results["accuracy"]["overall_average"]
            total_tests = self.results["accuracy"]["total_tests"]
            
            print(f"📊 Overall Accuracy Score: {overall_score:.2f}/1.00")
            print(f"🧪 Total Tests Completed: {total_tests}")
            
            # Performance rating
            if overall_score >= 0.8:
                rating = "🏆 EXCELLENT"
            elif overall_score >= 0.7:
                rating = "🥇 VERY GOOD"
            elif overall_score >= 0.6:
                rating = "🥈 GOOD"
            elif overall_score >= 0.5:
                rating = "🥉 FAIR"
            else:
                rating = "❌ NEEDS IMPROVEMENT"
            
            print(f"🏆 Performance Rating: {rating}")
        
        print("\n📋 Category Breakdown:")
        for category, results in self.results["performance"].items():
            category_name = self.test_categories[category]
            score = results["average_score"]
            tests = results["total_tests"]
            time = results["average_time"]
            
            print(f"   {category_name}:")
            print(f"      Score: {score:.2f} ({tests} tests, avg {time:.1f}s)")
        
        print("\n🔧 Recommendations:")
        category_scores = [(cat, res["average_score"]) for cat, res in self.results["performance"].items()]
        category_scores.sort(key=lambda x: x[1])
        
        if category_scores:
            weakest = category_scores[0]
            strongest = category_scores[-1]
            
            print(f"   💪 Strongest Area: {self.test_categories[strongest[0]]} ({strongest[1]:.2f})")
            print(f"   📈 Area for Improvement: {self.test_categories[weakest[0]]} ({weakest[1]:.2f})")
            
            if weakest[1] < 0.6:
                print(f"   🎯 Consider additional training data for {self.test_categories[weakest[0]]}")
    
    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"devops_model_evaluation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main evaluation function"""
    print("🚀 DevOps Model Performance & Accuracy Evaluation")
    print("=" * 50)
    
    print("Choose evaluation mode:")
    print("1. Use API server (recommended if running)")
    print("2. Load model locally")
    print("3. Auto-detect (try API first, fallback to local)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        evaluator = DevOpsModelEvaluator(use_api=True)
    elif choice == "2":
        evaluator = DevOpsModelEvaluator(use_api=False)
    else:  # choice == "3" or default
        evaluator = DevOpsModelEvaluator(use_api=True)  # Will fallback if API fails
    
    evaluator.run_comprehensive_evaluation()

if __name__ == "__main__":
    main()
