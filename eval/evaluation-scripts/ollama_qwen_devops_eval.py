#!/usr/bin/env python3
"""
🚀 OLLAMA QWEN DEVOPS EVALUATION (ENHANCED)
Advanced evaluation of DevOps model responses via Ollama

IMPROVEMENTS MADE:
- Enhanced scoring system that values comprehensive, practical responses
- Better recognition of DevOps concepts, synonyms, and related terms
- Rewards implementation depth with code examples and YAML configs
- Evaluates best practices, security, monitoring, and production readiness
- Structured approach assessment (step-by-step guides, checklists)
- Removed arbitrary length caps that penalized detailed explanations

This addresses issues where quality responses were undervalued due to:
- Simple keyword matching vs. conceptual understanding
- Length penalties for comprehensive guides
- Missing recognition of advanced DevOps terminology
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
        """
        Enhanced response evaluation focusing on practical DevOps expertise
        Prioritizes implementation depth, best practices, and real-world applicability
        """
        if not response or response.strip() == "":
            return {
                "structure_score": 0,
                "concept_coverage": 0,
                "implementation_depth": 0,
                "best_practices_score": 0,
                "total_score": 0,
                "word_count": 0,
                "concepts_found": 0,
                "implementation_indicators": 0,
                "best_practices_found": 0,
            }

        response_lower = response.lower()
        length = len(response.split())

        # 1. Structure & Organization (0-25 points)
        # Rewards well-structured, step-by-step approaches
        structure_indicators = [
            "step",
            "first",
            "next",
            "then",
            "finally",
            "overview",
            "summary",
            "checklist",
            "process",
            "workflow",
            "strategy",
            "approach",
            "1.",
            "2.",
            "3.",
            "•",
            "-",
            "phase",
            "stage",
        ]
        structure_score = min(
            25,
            sum(3 for indicator in structure_indicators if indicator in response_lower),
        )

        # 2. Concept Coverage (0-25 points) - Enhanced keyword matching
        # Include synonyms and related concepts
        enhanced_keywords = set(keywords)
        keyword_expansions = {
            "blue-green": [
                "blue green",
                "deployment strategy",
                "zero-downtime",
                "switch traffic",
            ],
            "service": ["load balancer", "ingress", "traffic routing", "endpoint"],
            "rollback": ["revert", "fallback", "recovery", "previous version"],
            "deployment": ["rollout", "release", "deploy"],
            "monitoring": [
                "observability",
                "metrics",
                "alerts",
                "prometheus",
                "grafana",
            ],
            "security": ["rbac", "network policy", "least privilege", "encryption"],
            "terraform": ["infrastructure as code", "iac", "state management"],
            "pipeline": [
                "ci/cd",
                "automation",
                "workflow",
                "github actions",
                "jenkins",
            ],
        }

        all_concepts = set(enhanced_keywords)
        for key in keywords:
            if key.lower() in keyword_expansions:
                all_concepts.update(keyword_expansions[key.lower()])

        concepts_found = sum(
            1 for concept in all_concepts if concept.lower() in response_lower
        )
        concept_coverage = min(25, (concepts_found / max(len(all_concepts), 1)) * 25)

        # 3. Implementation Depth (0-30 points)
        # Rewards practical examples, code snippets, and detailed explanations
        implementation_indicators = [
            "yaml",
            "kubectl",
            "docker",
            "helm",
            "terraform",
            "ansible",
            "apiversion",
            "metadata",
            "spec",
            "selector",
            "template",
            "deployment.yaml",
            "service.yaml",
            "ingress.yaml",
            "configmap",
            "apply -f",
            "patch",
            "create",
            "delete",
            "get pods",
            "describe",
            "namespace",
            "labels",
            "annotations",
            "resources",
            "limits",
            "replicas",
            "strategy",
            "rollingupdate",
            "recreate",
            "probe",
            "readiness",
            "liveness",
            "healthcheck",
            "secret",
            "volume",
            "persistent",
            "statefulset",
            "daemonset",
        ]
        impl_found = sum(
            1 for indicator in implementation_indicators if indicator in response_lower
        )
        implementation_depth = min(30, (impl_found / 15) * 30)

        # 4. Best Practices & Production Readiness (0-20 points)
        # Rewards security, monitoring, and production considerations
        best_practices = [
            "security",
            "rbac",
            "network policy",
            "encryption",
            "tls",
            "monitoring",
            "logging",
            "alerts",
            "prometheus",
            "grafana",
            "backup",
            "disaster recovery",
            "high availability",
            "sla",
            "resource limits",
            "requests",
            "quotas",
            "autoscaling",
            "testing",
            "validation",
            "smoke test",
            "health check",
            "gitops",
            "version control",
            "semantic versioning",
            "least privilege",
            "zero trust",
            "compliance",
            "audit",
            "observability",
            "tracing",
            "metrics",
            "error handling",
        ]
        practices_found = sum(
            1 for practice in best_practices if practice in response_lower
        )
        best_practices_score = min(20, (practices_found / 10) * 20)

        # Enhanced scoring for comprehensive responses
        # Bonus for length when it indicates thoroughness (not just verbosity)
        length_bonus = 0
        if length >= 200 and implementation_depth >= 20:  # Long + practical
            length_bonus = 5
        elif length >= 100 and concept_coverage >= 15:  # Medium + conceptual
            length_bonus = 3

        # Difficulty adjustment - reward complexity for harder questions
        difficulty_multiplier = {
            "basic": 1.0,
            "intermediate": 1.05,  # Slightly bonus for handling complexity
            "advanced": 1.10,  # More bonus for advanced topics
        }.get(difficulty, 1.0)

        raw_score = (
            structure_score
            + concept_coverage
            + implementation_depth
            + best_practices_score
            + length_bonus
        )
        total_score = min(100, raw_score * difficulty_multiplier)

        return {
            "structure_score": structure_score,
            "concept_coverage": concept_coverage,
            "implementation_depth": implementation_depth,
            "best_practices_score": best_practices_score,
            "length_bonus": length_bonus,
            "total_score": total_score,
            "word_count": length,
            "concepts_found": concepts_found,
            "implementation_indicators": impl_found,
            "best_practices_found": practices_found,
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
                    f"   📊 Words: {evaluation['word_count']}, Concepts: {evaluation['concepts_found']}"
                )
                print(
                    f"   🔧 Implementation: {evaluation['implementation_indicators']}, Best Practices: {evaluation['best_practices_found']}"
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

            print("📊 PERFORMANCE:")
            print(f"   Average Score: {avg_score:.1f}/100")
            print(f"   Best Score: {max_score:.1f}/100")
            print(
                f"   Success Rate: {len(scores)}/{len(results)} ({len(scores) / len(results) * 100:.1f}%)"
            )
            print()

            print("⏱️  TIMING:")
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
