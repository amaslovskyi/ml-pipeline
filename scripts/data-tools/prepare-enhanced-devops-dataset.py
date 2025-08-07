#!/usr/bin/env python3
"""
Enhanced DevOps Dataset Preparation
==================================

This script creates a comprehensive DevOps/SRE training dataset using:
1. codefuse-ai/CodeFuse-DevOps-Eval - Specialized DevOps QA pairs
2. Mubeen161/DEVOPS - Community Q&A dataset  
3. Custom synthetic examples for domain coverage
4. Real-world scenarios and troubleshooting cases

The dataset is formatted for Qwen3 chat template training.
"""

import os
import json
import pandas as pd
from datasets import load_dataset, Dataset, DatasetDict
from huggingface_hub import login
import random
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsDatasetBuilder:
    def __init__(self, hf_token: str = None):
        """Initialize the dataset builder with HuggingFace token."""
        if hf_token:
            login(token=hf_token)
            logger.info("✅ Logged into HuggingFace Hub")
        
        self.chat_template = self._get_qwen3_chat_template()
        self.dataset_stats = {}
        
        # Latest datasets discovered January 2025
        self.latest_datasets = {
            'coderepoqa': 'December 2024 - 585k real-world repository QA examples',
            'stackexchange_devops': 'Community-curated DevOps troubleshooting',
            'devops_guide_demo': 'Structured conceptual DevOps Q&A'
        }
        
    def _get_qwen3_chat_template(self) -> str:
        """Get the Qwen3 chat template format."""
        return "<|im_start|>system\nYou are a helpful DevOps and SRE assistant with expertise in cloud infrastructure, CI/CD, monitoring, troubleshooting, and automation.<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
    
    def load_codefuse_devops_dataset(self) -> List[Dict[str, str]]:
        """Load CodeFuse DevOps evaluation dataset."""
        logger.info("📥 Loading CodeFuse-DevOps-Eval dataset...")
        
        try:
            # Load the CodeFuse DevOps dataset
            dataset = load_dataset("codefuse-ai/CodeFuse-DevOps-Eval", split="train")
            logger.info(f"✅ Loaded {len(dataset)} examples from CodeFuse-DevOps-Eval")
            
            processed_data = []
            for item in dataset:
                # Extract question and answer from the dataset
                instruction = item.get('question', item.get('instruction', ''))
                output = item.get('answer', item.get('output', ''))
                
                if instruction and output:
                    processed_data.append({
                        'instruction': instruction.strip(),
                        'input': '',
                        'output': output.strip(),
                        'source': 'codefuse-devops-eval'
                    })
            
            self.dataset_stats['codefuse'] = len(processed_data)
            logger.info(f"✅ Processed {len(processed_data)} CodeFuse examples")
            return processed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load CodeFuse dataset: {e}")
            return []
    
    def load_coderepoqa_dataset(self) -> List[Dict[str, str]]:
        """Load CodeRepoQA - December 2024 repository QA dataset."""
        logger.info("📥 Loading CodeRepoQA dataset (December 2024)...")
        
        try:
            # Load the CodeRepoQA dataset - latest and most comprehensive
            dataset = load_dataset("code-repo-qa/CodeRepoQA", split="train")
            logger.info(f"✅ Loaded {len(dataset)} examples from CodeRepoQA")
            
            processed_data = []
            for item in dataset:
                # Extract question and answer from repository issues
                instruction = item.get('question', item.get('issue_title', ''))
                output = item.get('answer', item.get('solution', item.get('response', '')))
                
                # Handle multi-turn conversations - focus on resolved issues
                if item.get('is_resolved', True) and instruction and output:
                    # Add context if available (repository, language, etc.)
                    context = []
                    if item.get('repository'):
                        context.append(f"Repository: {item['repository']}")
                    if item.get('language'):
                        context.append(f"Language: {item['language']}")
                    if item.get('issue_type'):
                        context.append(f"Issue Type: {item['issue_type']}")
                    
                    # Enhanced instruction with context
                    enhanced_instruction = instruction.strip()
                    if context:
                        enhanced_instruction = f"{' | '.join(context)}\n\n{instruction.strip()}"
                    
                    processed_data.append({
                        'instruction': enhanced_instruction,
                        'input': '',
                        'output': output.strip(),
                        'source': 'coderepoqa-2024'
                    })
            
            self.dataset_stats['coderepoqa'] = len(processed_data)
            logger.info(f"✅ Processed {len(processed_data)} CodeRepoQA examples")
            return processed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load CodeRepoQA dataset: {e}")
            return []
    
    def load_stackexchange_devops_dataset(self) -> List[Dict[str, str]]:
        """Load StackExchange DevOps dataset."""
        logger.info("📥 Loading mlfoundations-dev/stackexchange_devops dataset...")
        
        try:
            # Load the StackExchange DevOps dataset
            dataset = load_dataset("mlfoundations-dev/stackexchange_devops", split="train")
            logger.info(f"✅ Loaded {len(dataset)} examples from StackExchange DevOps")
            
            processed_data = []
            for item in dataset:
                # Extract question and accepted answer
                instruction = item.get('question', item.get('title', ''))
                output = item.get('answer', item.get('accepted_answer', ''))
                
                # Add question body if available
                if item.get('question_body'):
                    instruction += f"\n\n{item['question_body']}"
                
                # Filter for quality (upvoted answers, accepted solutions)
                if (instruction and output and 
                    len(instruction) > 20 and len(output) > 30 and
                    item.get('score', 0) >= 0):  # Only non-negative scored content
                    
                    processed_data.append({
                        'instruction': instruction.strip(),
                        'input': '',
                        'output': output.strip(),
                        'source': 'stackexchange-devops'
                    })
            
            self.dataset_stats['stackexchange'] = len(processed_data)
            logger.info(f"✅ Processed {len(processed_data)} StackExchange examples")
            return processed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load StackExchange dataset: {e}")
            return []
    
    def load_devops_guide_demo_dataset(self) -> List[Dict[str, str]]:
        """Load structured DevOps guide demonstration dataset."""
        logger.info("📥 Loading adeeshajayasinghe/devops-guide-demo dataset...")
        
        try:
            # Load the DevOps guide demo dataset
            dataset = load_dataset("adeeshajayasinghe/devops-guide-demo", split="train")
            logger.info(f"✅ Loaded {len(dataset)} examples from DevOps Guide Demo")
            
            processed_data = []
            for item in dataset:
                # Extract structured Q&A about DevOps concepts
                instruction = item.get('question', item.get('prompt', ''))
                output = item.get('answer', item.get('response', ''))
                
                if instruction and output and len(instruction) > 10 and len(output) > 20:
                    processed_data.append({
                        'instruction': instruction.strip(),
                        'input': '',
                        'output': output.strip(),
                        'source': 'devops-guide-demo'
                    })
            
            self.dataset_stats['devops_guide'] = len(processed_data)
            logger.info(f"✅ Processed {len(processed_data)} DevOps Guide examples")
            return processed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load DevOps Guide dataset: {e}")
            return []

    def load_community_devops_dataset(self) -> List[Dict[str, str]]:
        """Load community DevOps Q&A dataset."""
        logger.info("📥 Loading Mubeen161/DEVOPS dataset...")
        
        try:
            # Load the community DevOps dataset
            dataset = load_dataset("Mubeen161/DEVOPS", split="train")
            logger.info(f"✅ Loaded {len(dataset)} examples from Mubeen161/DEVOPS")
            
            processed_data = []
            for item in dataset:
                # Extract question and answer
                instruction = item.get('question', item.get('text', ''))
                output = item.get('answer', item.get('response', ''))
                
                # Handle different possible field names
                if not instruction:
                    # Try to extract from text field if it contains Q&A format
                    text = item.get('text', '')
                    if 'Q:' in text and 'A:' in text:
                        parts = text.split('A:', 1)
                        if len(parts) == 2:
                            instruction = parts[0].replace('Q:', '').strip()
                            output = parts[1].strip()
                
                if instruction and output and len(instruction) > 10 and len(output) > 10:
                    processed_data.append({
                        'instruction': instruction.strip(),
                        'input': '',
                        'output': output.strip(),
                        'source': 'community-devops'
                    })
            
            self.dataset_stats['community'] = len(processed_data)
            logger.info(f"✅ Processed {len(processed_data)} community examples")
            return processed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load community dataset: {e}")
            return []
    
    def create_synthetic_devops_examples(self) -> List[Dict[str, str]]:
        """Create synthetic DevOps examples covering gaps in real datasets."""
        logger.info("🔧 Creating synthetic DevOps examples...")
        
        synthetic_examples = [
            # Kubernetes Troubleshooting
            {
                'instruction': 'A Kubernetes pod is stuck in CrashLoopBackOff state. How do you troubleshoot this issue?',
                'input': '',
                'output': 'To troubleshoot CrashLoopBackOff: 1) Check pod logs with `kubectl logs <pod-name> --previous`, 2) Describe the pod with `kubectl describe pod <pod-name>` to check events, 3) Verify resource limits and requests, 4) Check if the container image exists and is accessible, 5) Validate environment variables and config maps, 6) Ensure health checks (liveness/readiness probes) are properly configured, 7) Check for port conflicts or dependency issues.',
                'source': 'synthetic-k8s'
            },
            {
                'instruction': 'How do you debug a Kubernetes service that cannot reach its pods?',
                'input': '',
                'output': 'Debug Kubernetes service connectivity: 1) Verify pod labels match service selector with `kubectl get pods --show-labels`, 2) Check service endpoints with `kubectl get endpoints <service-name>`, 3) Test DNS resolution with `nslookup <service-name>` from within cluster, 4) Verify network policies are not blocking traffic, 5) Check if pods are in Ready state, 6) Test direct pod IP connectivity, 7) Validate port configurations in service and deployment, 8) Use `kubectl port-forward` to test pod accessibility.',
                'source': 'synthetic-k8s'
            },
            
            # CI/CD Pipeline Issues
            {
                'instruction': 'A Jenkins pipeline is failing intermittently with "workspace cleanup" errors. How do you resolve this?',
                'input': '',
                'output': 'Resolve Jenkins workspace cleanup issues: 1) Check disk space on Jenkins agents with `df -h`, 2) Review workspace cleanup configuration in pipeline, 3) Add explicit workspace cleanup steps: `cleanWs()` at pipeline end, 4) Check for file permission issues with `ls -la workspace/`, 5) Verify no processes are holding file handles, 6) Consider using Docker agents for isolated environments, 7) Implement workspace retention policies, 8) Add retry logic for cleanup operations, 9) Monitor agent health and restart if necessary.',
                'source': 'synthetic-cicd'
            },
            {
                'instruction': 'How do you implement blue-green deployment with zero downtime in a CI/CD pipeline?',
                'input': '',
                'output': 'Implement blue-green deployment: 1) Maintain two identical environments (blue=current, green=new), 2) Deploy new version to green environment, 3) Run automated tests against green environment, 4) Switch load balancer/ingress to green environment atomically, 5) Monitor green environment for issues, 6) Keep blue environment as immediate rollback option, 7) Use feature flags for gradual traffic shifting, 8) Implement health checks and automated rollback triggers, 9) Clean up old blue environment after confidence period.',
                'source': 'synthetic-cicd'
            },
            
            # Monitoring and Alerting
            {
                'instruction': 'How do you set up effective alerting for a microservices architecture without alert fatigue?',
                'input': '',
                'output': 'Set up effective microservices alerting: 1) Focus on symptoms (user impact) not causes (individual service failures), 2) Implement SLI/SLO-based alerting for business metrics, 3) Use alert severity levels (P0=immediate, P1=urgent, P2=important), 4) Group related alerts with intelligent routing, 5) Set up escalation policies with time-based escalation, 6) Implement alert suppression during maintenance windows, 7) Use correlation to reduce noise from cascading failures, 8) Create runbooks for common alerts, 9) Review and tune alerts weekly to reduce false positives.',
                'source': 'synthetic-monitoring'
            },
            {
                'instruction': 'Prometheus is showing high memory usage and slow queries. How do you optimize it?',
                'input': '',
                'output': 'Optimize Prometheus performance: 1) Review retention settings and reduce if necessary, 2) Implement metric relabeling to drop unnecessary labels, 3) Use recording rules for expensive queries, 4) Increase scrape intervals for less critical metrics, 5) Implement federation for scaling across multiple Prometheus instances, 6) Add more memory and optimize storage, 7) Use metric filtering at target level, 8) Implement alerting on query performance, 9) Consider Thanos or Cortex for long-term storage and horizontal scaling.',
                'source': 'synthetic-monitoring'
            },
            
            # Security and Compliance
            {
                'instruction': 'How do you implement secure secrets management in a Kubernetes environment?',
                'input': '',
                'output': 'Implement secure Kubernetes secrets management: 1) Use external secret management (HashiCorp Vault, AWS Secrets Manager), 2) Enable encryption at rest for etcd, 3) Implement RBAC for secret access control, 4) Use service accounts with minimal permissions, 5) Rotate secrets regularly with automated tools, 6) Never store secrets in container images or code, 7) Use sealed secrets or external secret operators for GitOps, 8) Implement secret scanning in CI/CD pipelines, 9) Monitor secret access with audit logging, 10) Use init containers or sidecar patterns for secret injection.',
                'source': 'synthetic-security'
            },
            
            # Infrastructure as Code
            {
                'instruction': 'What are the best practices for managing Terraform state in a team environment?',
                'input': '',
                'output': 'Terraform state management best practices: 1) Use remote state backends (S3 with DynamoDB locking, Terraform Cloud), 2) Enable state versioning and backup, 3) Implement state locking to prevent concurrent modifications, 4) Use separate state files for different environments, 5) Never commit state files to version control, 6) Implement least privilege access to state storage, 7) Use workspaces for environment isolation, 8) Regular state file backups and disaster recovery testing, 9) Implement state file encryption, 10) Use terraform import for existing resources.',
                'source': 'synthetic-iac'
            },
            
            # Docker and Containerization
            {
                'instruction': 'How do you optimize Docker images for security and performance in production?',
                'input': '',
                'output': 'Optimize Docker images for production: 1) Use minimal base images (alpine, distroless), 2) Implement multi-stage builds to reduce final image size, 3) Run containers as non-root user, 4) Remove package managers and unnecessary tools from final image, 5) Use specific version tags, never "latest", 6) Implement image vulnerability scanning, 7) Use .dockerignore to exclude unnecessary files, 8) Minimize layers and combine RUN commands, 9) Use health checks for container monitoring, 10) Implement image signing and verification.',
                'source': 'synthetic-docker'
            },
            
            # Database and Storage
            {
                'instruction': 'How do you implement database backup and disaster recovery for a production PostgreSQL cluster?',
                'input': '',
                'output': 'PostgreSQL backup and disaster recovery: 1) Implement automated daily full backups with pg_dump/pg_basebackup, 2) Set up continuous WAL archiving for point-in-time recovery, 3) Use streaming replication with read replicas, 4) Test backup restoration regularly, 5) Implement cross-region backup storage, 6) Set up monitoring for backup success/failure, 7) Document RTO/RPO requirements and test procedures, 8) Use tools like pgBackRest for advanced backup management, 9) Implement automated failover with tools like Patroni, 10) Create runbooks for disaster recovery scenarios.',
                'source': 'synthetic-database'
            },
            
            # Cloud-specific scenarios
            {
                'instruction': 'How do you implement cost optimization for AWS infrastructure without impacting performance?',
                'input': '',
                'output': 'AWS cost optimization strategies: 1) Use Reserved Instances for predictable workloads, 2) Implement auto-scaling for variable loads, 3) Use Spot Instances for non-critical workloads, 4) Right-size instances based on actual usage metrics, 5) Implement lifecycle policies for S3 storage classes, 6) Use CloudWatch for resource monitoring and alerting, 7) Implement resource tagging for cost allocation, 8) Use AWS Cost Explorer for usage analysis, 9) Implement automated shutdown for dev/test environments, 10) Use AWS Trusted Advisor recommendations.',
                'source': 'synthetic-aws'
            }
        ]
        
        self.dataset_stats['synthetic'] = len(synthetic_examples)
        logger.info(f"✅ Created {len(synthetic_examples)} synthetic examples")
        return synthetic_examples
    
    def create_troubleshooting_scenarios(self) -> List[Dict[str, str]]:
        """Create realistic troubleshooting scenarios with logs and artifacts."""
        logger.info("🔍 Creating troubleshooting scenarios...")
        
        scenarios = [
            {
                'instruction': 'Analyze this Kubernetes pod crash log and provide troubleshooting steps.',
                'input': '''
Pod log excerpt:
2024-01-15 10:30:42 ERROR: Failed to connect to database: connection timeout
2024-01-15 10:30:42 FATAL: Could not establish database connection after 3 retries
2024-01-15 10:30:42 ERROR: Application startup failed
Pod events:
- Warning: FailedMount: Unable to mount volumes for pod
- Warning: Unhealthy: Readiness probe failed
                ''',
                'output': 'Based on the log analysis: 1) **Root cause**: Database connection timeout causing app startup failure, 2) **Immediate steps**: Check database service status with `kubectl get svc,endpoints`, 3) **Network troubleshooting**: Verify database pod is running and accessible, test connectivity with `kubectl exec -it <pod> -- nc -zv <db-service> <port>`, 4) **Configuration check**: Verify database connection string, credentials in secrets/configmaps, 5) **Resource check**: Ensure database has sufficient resources, 6) **Volume issue**: Investigate mount failure - check PVC status and storage class, 7) **Health checks**: Adjust readiness probe timeout if database connection is slow.',
                'source': 'troubleshooting-k8s'
            },
            {
                'instruction': 'This Docker build is failing. Help troubleshoot the issue.',
                'input': '''
Dockerfile:
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

Build error:
Step 4/7 : RUN npm ci --only=production
npm ERR! code ENOTFOUND
npm ERR! errno ENOTFOUND
npm ERR! network request to https://registry.npmjs.org failed
                ''',
                'output': 'Docker build troubleshooting: 1) **Network issue**: Build environment cannot reach npm registry, 2) **Solutions**: Add DNS configuration `--dns=8.8.8.8` to docker build, 3) **Corporate firewall**: If behind proxy, add proxy settings to Dockerfile: `ENV HTTP_PROXY=http://proxy:port`, 4) **Alternative registries**: Use internal npm registry or cache, 5) **Build optimization**: Use .dockerignore to exclude node_modules, 6) **Multi-stage improvement**: Use build stage for dependencies, 7) **Retry logic**: Add `RUN npm config set registry https://registry.npmjs.org/` before npm ci, 8) **Security**: Consider using npm audit and vulnerability scanning.',
                'source': 'troubleshooting-docker'
            }
        ]
        
        self.dataset_stats['troubleshooting'] = len(scenarios)
        logger.info(f"✅ Created {len(scenarios)} troubleshooting scenarios")
        return scenarios
    
    def format_for_qwen3_training(self, examples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format examples for Qwen3 chat template training."""
        logger.info("🎯 Formatting examples for Qwen3 chat template...")
        
        formatted_examples = []
        for example in examples:
            # Create the chat-formatted text
            instruction = example['instruction']
            if example.get('input'):
                instruction += f"\n\nInput:\n{example['input']}"
            
            formatted_text = self.chat_template.format(
                instruction=instruction,
                output=example['output']
            )
            
            formatted_examples.append({
                'text': formatted_text,
                'source': example.get('source', 'unknown'),
                'instruction': example['instruction'],
                'output': example['output']
            })
        
        return formatted_examples
    
    def build_comprehensive_dataset(self) -> Dataset:
        """Build the comprehensive DevOps training dataset."""
        logger.info("🏗️ Building comprehensive DevOps dataset...")
        
        all_examples = []
        
        # Load latest external datasets (January 2025)
        logger.info("📥 Loading latest datasets from 2024-2025...")
        coderepoqa_examples = self.load_coderepoqa_dataset()  # December 2024 - 585k examples
        stackexchange_examples = self.load_stackexchange_devops_dataset()  # Community curated
        devops_guide_examples = self.load_devops_guide_demo_dataset()  # Structured concepts
        
        # Load previous datasets for comprehensive coverage
        codefuse_examples = self.load_codefuse_devops_dataset()
        community_examples = self.load_community_devops_dataset()
        
        # Create custom examples to fill gaps
        synthetic_examples = self.create_synthetic_devops_examples()
        troubleshooting_examples = self.create_troubleshooting_scenarios()
        
        # Combine all examples with prioritization (latest first)
        all_examples.extend(coderepoqa_examples)  # Priority: Latest 2024 data
        all_examples.extend(stackexchange_examples)  # Priority: Community expertise
        all_examples.extend(devops_guide_examples)  # Priority: Structured learning
        all_examples.extend(codefuse_examples)
        all_examples.extend(community_examples)
        all_examples.extend(synthetic_examples)
        all_examples.extend(troubleshooting_examples)
        
        # Shuffle for good distribution
        random.shuffle(all_examples)
        
        # Format for training
        formatted_examples = self.format_for_qwen3_training(all_examples)
        
        # Create HuggingFace Dataset
        dataset = Dataset.from_list(formatted_examples)
        
        # Print comprehensive statistics
        total_examples = len(formatted_examples)
        logger.info(f"\n📊 Comprehensive Dataset Statistics:")
        logger.info(f"=" * 50)
        logger.info(f"🎯 Total examples: {total_examples:,}")
        logger.info(f"📅 Latest data: December 2024 (CodeRepoQA)")
        logger.info(f"🔥 Repository issues: Real-world troubleshooting")
        logger.info(f"💡 Community expertise: StackExchange + forums")
        logger.info(f"📚 Structured learning: Conceptual DevOps guides")
        logger.info(f"\n📈 Source Breakdown:")
        
        # Enhanced statistics with quality metrics
        source_priority = [
            'coderepoqa', 'stackexchange', 'devops_guide', 
            'codefuse', 'community', 'synthetic', 'troubleshooting'
        ]
        
        for source in source_priority:
            count = self.dataset_stats.get(source, 0)
            if count > 0:
                percentage = (count / total_examples) * 100
                quality_rating = "🔥" if source in ['coderepoqa', 'stackexchange'] else "⭐"
                logger.info(f"   {quality_rating} {source}: {count:,} ({percentage:.1f}%)")
        
        # Quality metrics
        avg_instruction_length = sum(len(ex['instruction']) for ex in formatted_examples) / len(formatted_examples)
        avg_output_length = sum(len(ex['output']) for ex in formatted_examples) / len(formatted_examples)
        
        logger.info(f"\n📏 Quality Metrics:")
        logger.info(f"   Average instruction length: {avg_instruction_length:.0f} chars")
        logger.info(f"   Average response length: {avg_output_length:.0f} chars")
        logger.info(f"   Dataset size estimate: ~{total_examples * (avg_instruction_length + avg_output_length) / 1024 / 1024:.1f}MB")
        logger.info(f"=" * 50)
        
        return dataset
    
    def save_dataset(self, dataset: Dataset, output_dir: str = "devops_sre_comprehensive_dataset"):
        """Save the dataset locally and optionally to HuggingFace Hub."""
        logger.info(f"💾 Saving dataset to {output_dir}...")
        
        # Save locally
        dataset.save_to_disk(output_dir)
        
        # Also save as JSON for inspection
        with open(f"{output_dir}.jsonl", 'w') as f:
            for example in dataset:
                f.write(json.dumps(example) + '\n')
        
        logger.info(f"✅ Dataset saved locally to {output_dir}")
        
        # Optionally upload to HuggingFace Hub
        try:
            dataset.push_to_hub(
                "devops-sre-comprehensive-training",
                private=True
            )
            logger.info("✅ Dataset uploaded to HuggingFace Hub")
        except Exception as e:
            logger.warning(f"⚠️ Could not upload to HuggingFace Hub: {e}")
        
        return output_dir

def main():
    """Main function to build the enhanced DevOps dataset."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build enhanced DevOps training dataset")
    parser.add_argument("--hf-token", help="HuggingFace token")
    parser.add_argument("--output-dir", default="devops_sre_comprehensive_dataset", help="Output directory")
    args = parser.parse_args()
    
    # Initialize builder
    builder = DevOpsDatasetBuilder(hf_token=args.hf_token)
    
    # Build dataset
    dataset = builder.build_comprehensive_dataset()
    
    # Save dataset
    output_path = builder.save_dataset(dataset, args.output_dir)
    
    print(f"\n🎉 Enhanced DevOps dataset created successfully!")
    print(f"📁 Location: {output_path}")
    print(f"📊 Total examples: {len(dataset)}")
    print(f"💡 Ready for Qwen3 fine-tuning!")

if __name__ == "__main__":
    main()