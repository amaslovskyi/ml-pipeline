#!/usr/bin/env python3
"""
🚀 OLLAMA QWEN DEVOPS EVALUATION
Simple and fast evaluation of your qwen-devops model via Ollama

This is the streamlined version - much faster than loading the full PyTorch model!
"""

import subprocess
import time
import json
import statistics
from typing import Dict, List, Any


class OllamaDevOpsEvaluator:
    def __init__(self):
        self.model_name = "qwen-devops:latest"
        self.test_questions = [
            {
                "category": "Kubernetes Deployment",
                "question": "How would you implement a blue-green deployment strategy in Kubernetes?",
                "keywords": [
                    "blue-green",
                    "deployment",
                    "service",
                    "ingress",
                    "traffic",
                    "rollback",
                ],
                "difficulty": "intermediate",
            },
            {
                "category": "Infrastructure as Code",
                "question": "What are the best practices for organizing Terraform modules in a multi-environment setup?",
                "keywords": [
                    "terraform",
                    "modules",
                    "environment",
                    "state",
                    "workspace",
                    "structure",
                ],
                "difficulty": "intermediate",
            },
            {
                "category": "CI/CD Pipeline",
                "question": "How would you set up automated testing and deployment for a microservices architecture?",
                "keywords": [
                    "pipeline",
                    "microservices",
                    "testing",
                    "deployment",
                    "automation",
                    "docker",
                ],
                "difficulty": "advanced",
            },
            {
                "category": "Monitoring & Observability",
                "question": "What metrics would you monitor for a production Kubernetes cluster?",
                "keywords": [
                    "metrics",
                    "monitoring",
                    "prometheus",
                    "grafana",
                    "alerts",
                    "observability",
                ],
                "difficulty": "intermediate",
            },
            {
                "category": "Security & Compliance",
                "question": "How would you implement security scanning in your DevOps pipeline?",
                "keywords": [
                    "security",
                    "scanning",
                    "vulnerability",
                    "compliance",
                    "pipeline",
                    "SAST",
                ],
                "difficulty": "advanced",
            },
            {
                "category": "Troubleshooting",
                "question": "A Kubernetes pod is in CrashLoopBackOff state. How would you troubleshoot this?",
                "keywords": [
                    "crashloopbackoff",
                    "troubleshoot",
                    "logs",
                    "describe",
                    "events",
                    "kubectl",
                ],
                "difficulty": "intermediate",
            },
            {
                "category": "Docker & Containers",
                "question": "How would you optimize a Docker image for production deployment?",
                "keywords": [
                    "docker",
                    "optimize",
                    "image",
                    "production",
                    "multi-stage",
                    "size",
                    "layers",
                ],
                "difficulty": "intermediate",
            },
        ]

    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and self.model_name in result.stdout:
                return True
            return False
        except Exception:
            return False

    def query_ollama(self, question: str) -> Dict[str, Any]:
        """Query the Ollama model"""
        try:
            start_time = time.time()

            result = subprocess.run(
                ["ollama", "run", self.model_name, question],
                capture_output=True,
                text=True,
                timeout=60,
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                return {
                    "response": result.stdout.strip(),
                    "response_time": response_time,
                    "error": None,
                }
            else:
                return {
                    "response": "",
                    "response_time": response_time,
                    "error": f"Ollama error: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {
                "response": "",
                "response_time": 60.0,
                "error": "Timeout after 60 seconds",
            }
        except Exception as e:
            return {
                "response": "",
                "response_time": 0.0,
                "error": f"Exception: {str(e)}",
            }

    def evaluate_response(
        self, response: str, keywords: List[str], difficulty: str
    ) -> Dict[str, Any]:
        """Evaluate response quality"""
        if not response or response.strip() == "":
            return {
                "length_score": 0,
                "keyword_score": 0,
                "technical_score": 0,
                "total_score": 0,
            }

        # Length score (0-30 points)
        length = len(response.split())
        if length >= 100:
            length_score = 30
        elif length >= 60:
            length_score = 25
        elif length >= 30:
            length_score = 20
        elif length >= 15:
            length_score = 10
        else:
            length_score = 5

        # Keyword coverage (0-40 points)
        response_lower = response.lower()
        keywords_found = sum(
            1 for keyword in keywords if keyword.lower() in response_lower
        )
        keyword_score = min(40, (keywords_found / len(keywords)) * 40)

        # Technical depth (0-30 points)
        technical_terms = [
            "steps",
            "process",
            "configuration",
            "setup",
            "deploy",
            "configure",
            "kubectl",
            "yaml",
            "command",
            "script",
            "best practices",
            "production",
            "environment",
            "namespace",
            "container",
            "service",
            "monitoring",
        ]
        tech_found = sum(
            1 for term in technical_terms if term.lower() in response_lower
        )
        technical_score = min(30, (tech_found / 8) * 30)

        # Difficulty adjustment
        difficulty_multiplier = {
            "basic": 1.0,
            "intermediate": 0.95,
            "advanced": 0.9,
        }.get(difficulty, 1.0)
        total_score = (
            length_score + keyword_score + technical_score
        ) * difficulty_multiplier

        return {
            "length_score": length_score,
            "keyword_score": keyword_score,
            "technical_score": technical_score,
            "total_score": total_score,
            "word_count": length,
            "keywords_found": keywords_found,
            "tech_terms_found": tech_found,
        }

    def run_evaluation(self):
        """Run the complete evaluation"""
        print("🚀 OLLAMA QWEN DEVOPS EVALUATION")
        print("=" * 50)
        print(f"Model: {self.model_name}")
        print(f"Questions: {len(self.test_questions)}")
        print()

        # Check if Ollama is available
        if not self.check_ollama_available():
            print("❌ Ollama not available or qwen-devops model not found")
            print("Please ensure Ollama is running and qwen-devops:latest is installed")
            return

        results = []
        total_time = 0

        for i, test in enumerate(self.test_questions, 1):
            print(f"📝 Question {i}/{len(self.test_questions)}: {test['category']}")
            print(f"   {test['question']}")

            # Get response from Ollama
            result = self.query_ollama(test["question"])

            if result["error"]:
                print(f"   ❌ Error: {result['error']}")
                evaluation = {"total_score": 0}
            else:
                evaluation = self.evaluate_response(
                    result["response"], test["keywords"], test["difficulty"]
                )
                print(f"   ✅ Score: {evaluation['total_score']:.1f}/100")
                print(
                    f"   📊 Words: {evaluation['word_count']}, Keywords: {evaluation['keywords_found']}/{len(test['keywords'])}"
                )
                print(f"   ⏱️  Time: {result['response_time']:.1f}s")

                # Show response preview
                if result["response"]:
                    preview = (
                        result["response"][:100] + "..."
                        if len(result["response"]) > 100
                        else result["response"]
                    )
                    print(f"   💬 Preview: {preview}")

            # Store result
            results.append(
                {
                    "question": test["question"],
                    "category": test["category"],
                    "difficulty": test["difficulty"],
                    "response": result["response"],
                    "evaluation": evaluation,
                    "response_time": result["response_time"],
                    "error": result["error"],
                }
            )

            total_time += result["response_time"]
            print()

        # Print summary
        self.print_summary(results, total_time)

        # Save results
        filename = f"ollama_qwen_devops_eval_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to: {filename}")

    def print_summary(self, results: List[Dict], total_time: float):
        """Print evaluation summary"""
        print("🏆 EVALUATION SUMMARY")
        print("=" * 50)

        # Calculate stats
        scores = [
            r["evaluation"]["total_score"]
            for r in results
            if r["evaluation"]["total_score"] > 0
        ]
        response_times = [r["response_time"] for r in results if r["response_time"] > 0]
        errors = [r for r in results if r["error"]]

        if scores:
            avg_score = statistics.mean(scores)
            max_score = max(scores)
            min_score = min(scores)

            print(f"📊 PERFORMANCE:")
            print(f"   Average Score: {avg_score:.1f}/100")
            print(f"   Best Score: {max_score:.1f}/100")
            print(
                f"   Success Rate: {len(scores)}/{len(results)} ({len(scores) / len(results) * 100:.1f}%)"
            )
            print()

            print(f"⏱️  TIMING:")
            print(f"   Average Response Time: {statistics.mean(response_times):.1f}s")
            print(f"   Total Time: {total_time:.1f}s")
            print(f"   Errors: {len(errors)}")
            print()

            # Category breakdown
            print("📋 CATEGORY RESULTS:")
            categories = {}
            for result in results:
                cat = result["category"]
                if cat not in categories:
                    categories[cat] = []
                if result["evaluation"]["total_score"] > 0:
                    categories[cat].append(result["evaluation"]["total_score"])

            for category, cat_scores in categories.items():
                if cat_scores:
                    avg_cat_score = statistics.mean(cat_scores)
                    print(f"   {category:25} | {avg_cat_score:5.1f}")
            print()

            # Overall rating
            if avg_score >= 75:
                print("🌟 RATING: EXCELLENT - Strong DevOps expertise")
            elif avg_score >= 60:
                print("✅ RATING: GOOD - Solid DevOps knowledge")
            elif avg_score >= 45:
                print("⚠️ RATING: FAIR - Basic DevOps understanding")
            else:
                print("❌ RATING: NEEDS IMPROVEMENT")

            print(
                f"\n🎯 Your qwen-devops model via Ollama is {'working well!' if avg_score >= 60 else 'functional but could improve.'}"
            )

        else:
            print("❌ No successful responses. Check Ollama setup.")


def main():
    """Main execution"""
    print("🔧 Starting Ollama-based DevOps model evaluation...")
    print()

    evaluator = OllamaDevOpsEvaluator()

    try:
        evaluator.run_evaluation()
        print("\n✅ Evaluation complete!")
        print("Much faster than the PyTorch version, right? 🚀")

    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
