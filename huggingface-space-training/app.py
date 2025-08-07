#!/usr/bin/env python3
"""
HuggingFace Space Training App for Qwen3-8B DevOps Foundation Model
Optimized for ZeroGPU and dedicated GPU hardware
"""

import os

# Fix for HuggingFace CAS/XET infrastructure issues  
os.environ["HF_HUB_DISABLE_XET"] = "1"

import gradio as gr
import torch
import spaces  # HuggingFace Spaces GPU decorator
from datetime import datetime
import json

# Training imports
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import wandb

# Configuration
MODEL_NAME = "Qwen/Qwen3-8B"
OUTPUT_DIR = "./qwen-devops-foundation"

def load_devops_datasets():
    """Load and combine DevOps/SRE datasets with robust error handling"""
    print("📥 Loading DevOps datasets...")
    
    datasets_info = []
    all_examples = []
    
    # Always start with synthetic examples as a reliable base
    synthetic_examples = [
        {
            "instruction": "How do you troubleshoot high CPU usage in a Kubernetes pod?",
            "input": "",
            "output": "To troubleshoot high CPU usage in a Kubernetes pod: 1) Use kubectl top pod to identify the pod, 2) Check pod resource limits with kubectl describe pod, 3) Examine application logs with kubectl logs, 4) Use kubectl exec to access the pod and run top/htop, 5) Check for resource requests/limits configuration, 6) Consider horizontal pod autoscaling if needed."
        },
        {
            "instruction": "Explain how to set up monitoring for a production ML model",
            "input": "",
            "output": "Production ML model monitoring setup: 1) Implement model performance metrics (accuracy, latency, throughput), 2) Set up data drift detection using statistical tests, 3) Monitor prediction distribution changes, 4) Configure alerts for model degradation, 5) Use tools like Prometheus + Grafana for metrics visualization, 6) Implement logging for prediction requests/responses, 7) Set up automated model retraining triggers."
        },
        {
            "instruction": "How do you implement blue-green deployment for a microservice?",
            "input": "",
            "output": "Blue-green deployment implementation: 1) Maintain two identical production environments (blue and green), 2) Deploy new version to inactive environment, 3) Test thoroughly in the green environment, 4) Switch traffic from blue to green using load balancer, 5) Monitor for issues and rollback if needed, 6) Keep blue environment as backup, 7) Use automation tools like ArgoCD or Jenkins for orchestration."
        },
        {
            "instruction": "What are the key considerations for designing a fault-tolerant distributed system?",
            "input": "",
            "output": "Key fault-tolerant distributed system considerations: 1) Implement circuit breakers for external dependencies, 2) Use redundancy across multiple availability zones, 3) Design for graceful degradation, 4) Implement proper retry logic with exponential backoff, 5) Use health checks and automatic failover, 6) Ensure data consistency with appropriate patterns (eventual consistency, ACID), 7) Monitor system health and performance metrics, 8) Plan for disaster recovery scenarios."
        },
        {
            "instruction": "How do you optimize Docker container security?",
            "input": "",
            "output": "Docker container security optimization: 1) Use minimal base images (alpine, distroless), 2) Run containers as non-root user, 3) Implement multi-stage builds to reduce attack surface, 4) Scan images for vulnerabilities using tools like Trivy, 5) Use secrets management instead of environment variables, 6) Configure security contexts and pod security policies, 7) Enable runtime security monitoring, 8) Regularly update base images and dependencies."
        }
    ]
    all_examples.extend(synthetic_examples)
    datasets_info.append(f"✅ Synthetic examples: {len(synthetic_examples)} examples")
    
    # Load VERIFIED external DevOps datasets from HuggingFace Hub (YOUR RECOMMENDED APPROACH!)
    print("Loading VERIFIED external datasets - YOUR RECOMMENDED METHOD!")
    
    # 1. CoSQA - 20,000+ Web Queries for Code Search and Question Answering (VERIFIED!)
    try:
        print("Loading gonglinyuan/CoSQA dataset (20k+ web queries)...")
        dataset = load_dataset("gonglinyuan/CoSQA", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"CoSQA sample fields: {list(dataset[0].keys())}")
        
        for item in dataset.select(range(min(800, len(dataset)))):  # Reduced for memory
            # CoSQA actual field names: ['code_tokens', 'label', 'doc', 'docstring_tokens', 'idx', 'code']
            code = item.get('code', '')
            doc = item.get('doc', '')
            docstring = item.get('docstring_tokens', [])
            
            if code and doc:
                # Create instruction-response format for code Q&A
                instruction = f"Explain what this code does:\n```\n{code}\n```"
                output = doc
                
                examples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": output
                })
                
            elif code:  # If we have code without doc, use docstring
                docstring_text = ' '.join(docstring) if isinstance(docstring, list) else str(docstring)
                if docstring_text:
                    instruction = f"Explain what this code does:\n```\n{code}\n```"
                    output = docstring_text
                    examples.append({
                        "instruction": instruction,
                        "input": "",
                        "output": output
                    })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ CoSQA Web Queries: {len(examples)} examples (20k+ total)")
        print(f"Successfully loaded {len(examples)} examples from CoSQA - PREMIUM DATASET!")
    except Exception as e:
        datasets_info.append(f"⚠️ CoSQA failed: {str(e)}")
        print(f"CoSQA dataset error: {str(e)}")
    
    # 2. StackExchange DevOps - YOUR RECOMMENDED DATASET (VERIFIED!)
    try:
        print("Loading mlfoundations-dev/stackexchange_devops dataset...")
        dataset = load_dataset("mlfoundations-dev/stackexchange_devops", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"StackExchange DevOps sample fields: {list(dataset[0].keys())}")
        
        for item in dataset.select(range(min(600, len(dataset)))):  # Reduced for memory
            # StackExchange DevOps actual field names: ['instruction', 'completion', 'conversations']
            instruction = item.get('instruction', '')
            completion = item.get('completion', '')
            conversations = item.get('conversations', [])
            
            if instruction and completion:
                # Direct instruction-completion format
                examples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": completion
                })
            elif conversations and isinstance(conversations, list) and len(conversations) >= 2:
                # Extract from conversations format
                try:
                    for i in range(0, len(conversations)-1, 2):
                        if i+1 < len(conversations):
                            user_msg = conversations[i].get('value', '') if isinstance(conversations[i], dict) else str(conversations[i])
                            assistant_msg = conversations[i+1].get('value', '') if isinstance(conversations[i+1], dict) else str(conversations[i+1])
                            if user_msg and assistant_msg:
                                examples.append({
                                    "instruction": user_msg,
                                    "input": "",
                                    "output": assistant_msg
                                })
                except Exception as conv_e:
                    print(f"Error processing conversations: {conv_e}")
                    continue
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ StackExchange DevOps: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from StackExchange DevOps - YOUR RECOMMENDATION!")
    except Exception as e:
        datasets_info.append(f"⚠️ StackExchange DevOps failed: {str(e)}")
        print(f"StackExchange DevOps dataset error: {str(e)}")
        
    # 3. CodeQA - Question Answering Dataset for Source Code Comprehension (VERIFIED!)
    try:
        print("Loading jadecxliu/CodeQA dataset...")
        # This might be available as JSON files - let's try different approaches
        dataset = load_dataset("json", data_files="https://raw.githubusercontent.com/jadecxliu/CodeQA/main/data_sample/sample.json")
        examples = []
        for item in dataset['train']:
            question = item.get('question', '')
            answer = item.get('answer', '')
            code = item.get('code', '')
            
            if question and answer:
                if code:
                    instruction = f"Given this code:\n```\n{code}\n```\n\nQuestion: {question}"
                else:
                    instruction = question
                examples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": answer
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ CodeQA: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from CodeQA")
    except Exception as e:
        datasets_info.append(f"⚠️ CodeQA failed: {str(e)}")
        print(f"CodeQA dataset error: {str(e)}")
        
    # 4. Kubernetes StackOverflow Questions (VERIFIED!)
    try:
        print("Loading mcipriano/stackoverflow-kubernetes-questions dataset...")
        dataset = load_dataset("mcipriano/stackoverflow-kubernetes-questions", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"Kubernetes SO sample fields: {list(dataset[0].keys())}")
        
        for item in dataset.select(range(min(400, len(dataset)))):  # Reduced for memory
            # Kubernetes SO actual field names: ['Question', 'QuestionAuthor', 'Answer', 'AnswerAuthor']
            question = item.get('Question', '')
            answer = item.get('Answer', '')
            question_author = item.get('QuestionAuthor', '')
            answer_author = item.get('AnswerAuthor', '')
            
            if question and answer:
                # Create instruction-response format for Kubernetes Q&A
                full_question = f"[Kubernetes] {question}"
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": answer
                })
            elif question:  # If we only have question
                output = f"This is a Kubernetes question: {question}. It requires expertise in container orchestration and troubleshooting."
                full_question = f"[Kubernetes] {question}"
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": output
                })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ Kubernetes StackOverflow: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Kubernetes StackOverflow")
    except Exception as e:
        datasets_info.append(f"⚠️ Kubernetes StackOverflow failed: {str(e)}")
        print(f"Kubernetes StackOverflow dataset error: {str(e)}")
        
    # 5. Docker Commands - Natural Language to Docker (VERIFIED!)
    try:
        print("Loading MattCoddity/dockerNLcommands dataset...")
        dataset = load_dataset("MattCoddity/dockerNLcommands", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"Docker Commands sample fields: {list(dataset[0].keys())}")
        
        for item in dataset:
            # Try different field combinations
            instruction = item.get('Instruction', item.get('instruction', item.get('natural_language', item.get('prompt', ''))))
            command = item.get('Command', item.get('docker_command', item.get('command', item.get('output', ''))))
            
            if instruction and command:
                examples.append({
                    "instruction": f"Translate this requirement to a Docker command: {instruction}",
                    "input": "",
                    "output": f"Docker command: {command}"
                })
            elif instruction:  # If we only have instruction
                examples.append({
                    "instruction": f"How do you accomplish this with Docker: {instruction}",
                    "input": "",
                    "output": f"This Docker task involves: {instruction}. Requires containerization expertise."
                })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ Docker Commands: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Docker Commands")
    except Exception as e:
        datasets_info.append(f"⚠️ Docker Commands failed: {str(e)}")
        print(f"Docker Commands dataset error: {str(e)}")
        
    # 6. Python StackOverflow - Programming Q&A (VERIFIED!)
    try:
        print("Loading koutch/stackoverflow_python dataset...")
        dataset = load_dataset("koutch/stackoverflow_python", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"Python SO sample fields: {list(dataset[0].keys())}")
        
        # Filter for DevOps/infrastructure related Python questions
        devops_keywords = ['deployment', 'docker', 'kubernetes', 'ci/cd', 'automation', 'infrastructure', 'monitoring', 'logging']
        
        for item in dataset.select(range(min(300, len(dataset)))):  # Reduced for memory
            # Python SO actual field names: ['title', 'question_id', 'question_body', 'question_score', 'question_date', 'answer_id', 'answer_body', 'answer_score', 'answer_date', 'tags']
            title = item.get('title', '')
            question_body = item.get('question_body', '')
            answer_body = item.get('answer_body', '')
            tags = item.get('tags', '')
            
            # Check if question is DevOps-related
            text_to_check = f"{title} {question_body} {tags}".lower()
            is_devops_related = any(keyword in text_to_check for keyword in devops_keywords)
            
            if title and (is_devops_related or len(examples) < 200):
                # Combine title and body for instruction
                full_question = f"{title}\n{question_body}".strip() if question_body else title
                
                if answer_body:
                    output = answer_body
                else:
                    output = f"This is a Python programming question: {title}. Requires programming and automation expertise."
                
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": output
                })
                
                if len(examples) >= 300:  # Limit total examples
                    break
        
        all_examples.extend(examples)
        datasets_info.append(f"✅ Python StackOverflow: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Python StackOverflow")
    except Exception as e:
        datasets_info.append(f"⚠️ Python StackOverflow failed: {str(e)}")
        print(f"Python StackOverflow dataset error: {str(e)}")
    
    # 6. Incident Response Playbooks - SRE focused
    try:
        print("Loading agamage/incident-response-playbook-samples dataset...")
        dataset = load_dataset("agamage/incident-response-playbook-samples", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"Incident Response sample fields: {list(dataset[0].keys())}")
        
        for item in dataset:
            # Handle the actual dataset structure (fields: ['0'])
            if '0' in item and item['0']:
                content = str(item['0']).strip()
                if content and len(content) > 20:  # Ensure we have meaningful content
                    examples.append({
                        "instruction": "Create an incident response playbook based on this scenario:",
                        "input": "",
                        "output": f"Incident Response Playbook: {content}"
                    })
            else:
                # Fallback: try other field combinations
                playbook = item.get('playbook', item.get('content', item.get('response', item.get('procedure', ''))))
                title = item.get('title', item.get('name', item.get('incident_type', '')))
                description = item.get('description', item.get('summary', ''))
                
                if playbook and title:
                    instruction = f"Create an incident response playbook for: {title}"
                    if description:
                        instruction = f"{instruction}\nDescription: {description}"
                    examples.append({
                        "instruction": instruction,
                        "input": "",
                        "output": playbook
                    })
                elif title:  # If we only have title
                    examples.append({
                        "instruction": f"Create an incident response playbook for: {title}",
                        "input": "",
                        "output": f"This requires an SRE incident response playbook for: {title}. Include detection, assessment, response, and recovery procedures."
                    })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ Incident Response Playbooks: {len(examples)} SRE examples")
        print(f"Successfully loaded {len(examples)} SRE incident response examples")
    except Exception as e:
        datasets_info.append(f"⚠️ Incident Response Playbooks failed: {str(e)}")
        print(f"Incident Response Playbooks dataset error: {str(e)}")
        
    # 7. General Incident Dataset - Q&A format  
    try:
        print("Loading atishayj281/incident-dataset dataset...")
        dataset = load_dataset("atishayj281/incident-dataset", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"Incident Dataset sample fields: {list(dataset[0].keys())}")
        
        for item in dataset:
            # Handle the actual dataset structure
            # Fields: ['Number', 'Description', 'Short description', 'Close notes', 'Full description', 'group_id']
            description = item.get('Description', '')
            short_desc = item.get('Short description', '')
            full_desc = item.get('Full description', '')
            close_notes = item.get('Close notes', '')
            
            # Use the best available description
            incident_desc = full_desc or description or short_desc
            resolution = close_notes
            
            if incident_desc and resolution and len(incident_desc.strip()) > 10:
                examples.append({
                    "instruction": f"How to handle this incident: {incident_desc.strip()}",
                    "input": "",
                    "output": f"Resolution: {resolution.strip()}"
                })
            elif incident_desc and len(incident_desc.strip()) > 10:
                examples.append({
                    "instruction": f"How to handle this incident: {incident_desc.strip()}",
                    "input": "",
                    "output": f"This incident requires systematic investigation and resolution. Incident description: {incident_desc.strip()}. Follow standard incident management procedures."
                })
            else:
                # Fallback: try original field combinations
                question = item.get('Question', item.get('question', item.get('incident_description', item.get('problem', ''))))
                answer = item.get('Answer', item.get('answer', item.get('resolution', item.get('response', ''))))
                
                if question and answer:
                    examples.append({
                        "instruction": f"How to handle this incident: {question}",
                        "input": "",
                        "output": answer
                    })
                elif question:  # If we only have question
                    examples.append({
                        "instruction": f"How to handle this incident: {question}",
                        "input": "",
                        "output": f"This is an incident management scenario: {question}. Requires systematic incident response and problem resolution procedures."
                    })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ Incident Management: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} incident management examples")
    except Exception as e:
        datasets_info.append(f"⚠️ Incident Management failed: {str(e)}")
        print(f"Incident Management dataset error: {str(e)}")
    
    # Add comprehensive synthetic examples for robust training
    comprehensive_examples = [
        {
            "instruction": "How do you troubleshoot a failing Kubernetes deployment?",
            "input": "",
            "output": "Troubleshooting Kubernetes deployment failures: 1) Check deployment status with kubectl get deployments, 2) Examine pod status with kubectl get pods, 3) Review pod logs using kubectl logs, 4) Describe pod for events with kubectl describe pod, 5) Check resource quotas and limits, 6) Verify image pull secrets and registry access, 7) Examine service account permissions, 8) Check node capacity and scheduling constraints, 9) Review network policies and ingress rules, 10) Validate configuration and environment variables."
        },
        {
            "instruction": "Explain how to implement CI/CD pipeline security best practices",
            "input": "",
            "output": "CI/CD pipeline security best practices: 1) Use separate service accounts with minimal permissions, 2) Store secrets in dedicated secret management systems, 3) Implement code scanning (SAST/DAST) in pipeline, 4) Use container image scanning for vulnerabilities, 5) Implement dependency scanning for packages, 6) Use signed commits and protected branches, 7) Implement approval workflows for production deployments, 8) Audit and log all pipeline activities, 9) Use ephemeral environments for testing, 10) Implement infrastructure as code security scanning."
        },
        {
            "instruction": "How do you set up log aggregation with ELK stack?",
            "input": "",
            "output": "ELK stack log aggregation setup: 1) Deploy Elasticsearch cluster with proper sizing, 2) Configure Logstash for log parsing and transformation, 3) Set up Kibana for visualization and dashboards, 4) Configure Filebeat/Fluentd on application nodes, 5) Implement index lifecycle management for retention, 6) Set up alerting rules for critical events, 7) Configure authentication and authorization, 8) Implement log rotation and compression, 9) Set up monitoring for ELK components, 10) Create standardized log formats across services."
        },
        {
            "instruction": "What are Docker security best practices for production?",
            "input": "",
            "output": "Docker production security practices: 1) Use minimal base images (Alpine, distroless), 2) Run containers as non-root users, 3) Implement multi-stage builds to reduce attack surface, 4) Scan images for vulnerabilities regularly, 5) Use secrets management instead of environment variables, 6) Enable Docker Content Trust for image signing, 7) Configure resource limits and cgroups, 8) Use read-only filesystems where possible, 9) Implement network segmentation and firewalls, 10) Regular security updates and patch management."
        },
        {
            "instruction": "How do you implement disaster recovery for cloud infrastructure?",
            "input": "",
            "output": "Cloud disaster recovery implementation: 1) Define RPO (Recovery Point Objective) and RTO (Recovery Time Objective), 2) Implement automated backup strategies across regions, 3) Use infrastructure as code for rapid environment recreation, 4) Set up database replication and point-in-time recovery, 5) Implement DNS failover mechanisms, 6) Create detailed runbooks and recovery procedures, 7) Regular testing of disaster recovery plans, 8) Monitor backup integrity and restoration processes, 9) Implement cross-region data synchronization, 10) Establish communication plans for incidents."
        },
        {
            "instruction": "Explain how to optimize Kubernetes cluster performance",
            "input": "",
            "output": "Kubernetes cluster performance optimization: 1) Right-size node instances based on workload requirements, 2) Configure resource requests and limits properly, 3) Implement horizontal and vertical pod autoscaling, 4) Use node affinity and anti-affinity rules, 5) Optimize container images and startup times, 6) Configure appropriate QoS classes, 7) Use persistent volume performance classes, 8) Implement cluster autoscaling for dynamic scaling, 9) Monitor and tune network performance, 10) Regular cluster maintenance and updates."
        },
        {
            "instruction": "How do you implement GitOps workflow with ArgoCD?",
            "input": "",
            "output": "GitOps with ArgoCD implementation: 1) Install ArgoCD in Kubernetes cluster, 2) Configure Git repositories for application manifests, 3) Create ArgoCD applications pointing to Git repos, 4) Set up automated sync policies and health checks, 5) Implement multi-environment promotion workflows, 6) Configure RBAC for team access control, 7) Set up notifications and alerts for deployment status, 8) Implement secret management integration, 9) Use ApplicationSets for multi-cluster deployments, 10) Monitor application health and sync status."
        },
        {
            "instruction": "What are Terraform best practices for infrastructure as code?",
            "input": "",
            "output": "Terraform best practices: 1) Use remote state storage (S3, Azure Blob) with state locking, 2) Organize code with modules for reusability, 3) Pin provider versions to avoid breaking changes, 4) Use variables and locals for parameterization, 5) Implement proper naming conventions and tagging, 6) Use terraform plan before apply in CI/CD, 7) Store sensitive data in parameter stores or vaults, 8) Use workspaces for environment separation, 9) Validate configurations with terraform validate and tflint, 10) Implement automated testing with Terratest."
        },
        {
            "instruction": "How do you implement blue-green deployment in Kubernetes?",
            "input": "",
            "output": "Blue-green deployment in Kubernetes: 1) Create two identical environments (blue and green) using different selectors, 2) Deploy new version to inactive environment (green), 3) Test thoroughly with readiness/liveness probes, 4) Switch traffic by updating service selector labels, 5) Monitor metrics and logs post-switch, 6) Rollback by reverting service selector if issues occur, 7) Use tools like Argo Rollouts or Flagger for automation."
        },
        {
            "instruction": "Explain Prometheus monitoring setup for microservices",
            "input": "",
            "output": "Prometheus microservices monitoring: 1) Install Prometheus server via Helm chart, 2) Configure service discovery for automatic target detection, 3) Expose metrics endpoints (/metrics) in each microservice, 4) Set up alerting rules for SLA violations, 5) Configure Grafana dashboards for visualization, 6) Implement distributed tracing with Jaeger, 7) Monitor golden signals: latency, traffic, errors, saturation, 8) Use PushGateway for batch jobs, 9) Set up federation for multi-cluster monitoring."
        },
        {
            "instruction": "How do you conduct an effective post-incident review (PIR)?",
            "input": "",
            "output": "Effective Post-Incident Review process: 1) Schedule PIR within 24-48 hours while details are fresh, 2) Include all stakeholders involved in incident response, 3) Create blameless timeline of events and decisions, 4) Identify contributing factors and root causes, 5) Document what worked well and what didn't, 6) Generate actionable items with owners and deadlines, 7) Update runbooks and documentation, 8) Review monitoring and alerting effectiveness, 9) Share learnings with broader team, 10) Track implementation of improvement actions."
        },
        {
            "instruction": "What are the key SLA/SLO/SLI metrics for web applications?",
            "input": "",
            "output": "Key SRE metrics for web applications: SLIs (Service Level Indicators): 1) Request latency (95th/99th percentile), 2) Availability/uptime percentage, 3) Throughput (requests per second), 4) Error rate percentage. SLOs (Service Level Objectives): 1) 99.9% availability target, 2) <200ms 95th percentile latency, 3) <1% error rate. SLA (Service Level Agreement): 1) Customer-facing commitments with penalties, 2) Usually more conservative than SLOs, 3) Include compensation terms for breaches. Monitor with error budgets to balance reliability and feature velocity."
        },
        {
            "instruction": "How do you implement effective on-call rotation and incident escalation?",
            "input": "",
            "output": "On-call rotation and escalation best practices: 1) Create sustainable rotation schedule (weekly/bi-weekly), 2) Define clear escalation tiers (primary, secondary, manager), 3) Implement follow-the-sun model for global teams, 4) Use automated escalation after timeout periods, 5) Maintain runbooks for common incidents, 6) Provide on-call compensation and time off, 7) Set up effective alerting (not too noisy, not too quiet), 8) Train team members on incident response procedures, 9) Implement handoff procedures between shifts, 10) Regular review and improvement of on-call experience."
        },
        {
            "instruction": "Explain chaos engineering principles and implementation",
            "input": "",
            "output": "Chaos engineering implementation: 1) Start with hypothesis about system behavior under failure, 2) Design experiments that simulate real-world failures, 3) Begin with small, controlled experiments in non-production, 4) Gradually increase scope and impact, 5) Automate chaos experiments as part of CI/CD, 6) Monitor system behavior during experiments, 7) Use tools like Chaos Monkey, Litmus, or Gremlin, 8) Focus on learning and improving system resilience, 9) Document findings and implement improvements, 10) Build team confidence in system reliability through controlled failure testing."
        },
        {
            "instruction": "How do you design and implement effective alerting strategies?",
            "input": "",
            "output": "Effective alerting strategy design: 1) Alert on symptoms, not causes (user-facing issues), 2) Implement tiered alerting (critical, warning, info), 3) Use meaningful alert descriptions with context, 4) Set appropriate thresholds based on historical data, 5) Implement alert correlation to reduce noise, 6) Use different notification channels by severity, 7) Include runbook links in alerts, 8) Regularly review and tune alert thresholds, 9) Implement alert fatigue metrics and remediation, 10) Test alerting during incident simulations and chaos engineering exercises."
        }
    ]
    all_examples.extend(comprehensive_examples)
    datasets_info.append(f"✅ Comprehensive synthetic examples: {len(comprehensive_examples)} examples")
    
    print(f"📊 Total training examples loaded: {len(all_examples)}")
    
    # Ensure we have enough examples for training
    if len(all_examples) < 10:
        synthetic_examples = [
            {
                "instruction": "How do you troubleshoot high CPU usage in a Kubernetes pod?",
                "input": "",
                "output": "To troubleshoot high CPU usage in a Kubernetes pod: 1) Use kubectl top pod to identify the pod, 2) Check pod resource limits with kubectl describe pod, 3) Examine application logs with kubectl logs, 4) Use kubectl exec to access the pod and run top/htop, 5) Check for resource requests/limits configuration, 6) Consider horizontal pod autoscaling if needed."
            },
            {
                "instruction": "Explain how to set up monitoring for a production ML model",
                "input": "",
                "output": "Production ML model monitoring setup: 1) Implement model performance metrics (accuracy, latency, throughput), 2) Set up data drift detection using statistical tests, 3) Monitor prediction distribution changes, 4) Configure alerts for model degradation, 5) Use tools like Prometheus + Grafana for metrics visualization, 6) Implement logging for prediction requests/responses, 7) Set up automated model retraining triggers."
            },
            {
                "instruction": "How do you implement blue-green deployment for a microservice?",
                "input": "",
                "output": "Blue-green deployment implementation: 1) Maintain two identical production environments (blue and green), 2) Deploy new version to inactive environment, 3) Test thoroughly in the green environment, 4) Switch traffic from blue to green using load balancer, 5) Monitor for issues and rollback if needed, 6) Keep blue environment as backup, 7) Use automation tools like ArgoCD or Jenkins for orchestration."
            }
        ]
        all_examples.extend(synthetic_examples)
        datasets_info.append(f"✅ Synthetic examples: {len(synthetic_examples)} examples")
    
    return all_examples, datasets_info

def format_training_data(examples, tokenizer, max_length=2048):
    """Format data for instruction following training"""
    # Validate and clean examples
    valid_examples = []
    for i, item in enumerate(examples):
        if (isinstance(item, dict) and 
            'instruction' in item and 'output' in item and
            isinstance(item['instruction'], str) and isinstance(item['output'], str) and
            item['instruction'].strip() and item['output'].strip()):
            valid_examples.append(item)
        else:
            print(f"⚠️ Skipping invalid example {i}: {type(item)} - {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
    
    print(f"✅ Valid examples after cleaning: {len(valid_examples)} / {len(examples)}")
    
    formatted_data = []
    
    for item in valid_examples:
        # Create instruction-following format
        input_text = item.get('input', '').strip()
        if input_text:
            text = f"### Instruction:\n{item['instruction']}\n\n### Input:\n{input_text}\n\n### Response:\n{item['output']}"
        else:
            text = f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['output']}"
        
        formatted_data.append({"text": text})
    
    # Tokenize with proper padding and validation
    def tokenize_function(examples):
        # Ensure all texts are strings and not empty
        texts = []
        for text in examples["text"]:
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
            else:
                # Fallback for invalid text
                texts.append("### Instruction:\nWhat is DevOps?\n\n### Response:\nDevOps is a set of practices that combines software development and IT operations.")
        
        tokens = tokenizer(
            texts,
            truncation=True,
            padding="max_length",  # Ensure consistent tensor shapes
            max_length=max_length,
            return_overflowing_tokens=False,
            return_tensors=None,  # Return lists, not tensors yet
        )
        
        # Create labels - copy input_ids for causal LM
        tokens["labels"] = []
        for input_ids in tokens["input_ids"]:
            labels = input_ids.copy()
            tokens["labels"].append(labels)
        
        return tokens
    
    dataset = Dataset.from_list(formatted_data)
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing dataset"
    )
    
    # Validate tokenized dataset
    print(f"📊 Tokenized dataset size: {len(tokenized_dataset)}")
    if len(tokenized_dataset) > 0:
        sample = tokenized_dataset[0]
        print(f"📏 Sample input_ids length: {len(sample['input_ids'])}")
        print(f"📏 Sample labels length: {len(sample['labels'])}")
        print(f"🔢 Input IDs type: {type(sample['input_ids'])}")
        print(f"🔢 Labels type: {type(sample['labels'])}")
    
    return tokenized_dataset

@spaces.GPU(duration=360)  # Request 6 hours for L40S GPU
def train_model(wandb_project, learning_rate, epochs, batch_size, resume_from_checkpoint=None):
    """Main training function with GPU acceleration - L40S optimized"""
    
    # Import required modules
    import gc
    import os
    
    # Initialize wandb if key provided
    wandb_key = os.environ.get("WANDB_API_KEY")
    if wandb_key:
        wandb.login(key=wandb_key)
        wandb.init(
            project=wandb_project,
            name=f"qwen-devops-l40s-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            config={
                "model": MODEL_NAME,
                "learning_rate": learning_rate,
                "epochs": epochs,
                "batch_size": batch_size,
                "training_approach": "LoRA",
                "gpu_type": "L40S",
                "vram": "48GB"
            }
        )
    
    try:
        # Load datasets
        yield "📥 Loading DevOps datasets..."
        examples, dataset_info = load_devops_datasets()
        yield f"✅ Loaded {len(examples)} training examples\n" + "\n".join(dataset_info)
        
        # Load model and tokenizer
        yield "🔄 Loading Qwen3-8B model and tokenizer..."
        
        # L40S memory optimization
        # Set PyTorch memory allocation optimization for L40S
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        os.environ["CUDA_LAUNCH_BLOCKING"] = "0"
        
        # Aggressive GPU memory clearing for L40S
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
            # Force another round of cleanup
            torch.cuda.empty_cache()
            gc.collect()
        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # L40S has 48GB VRAM - optimized configuration (Updated for L40S)
        print("🚀 Using L40S GPU with 48GB VRAM - performance optimized!")
        print(f"📊 Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print("🔧 L40S Configuration Active - Updated v2")
        
        # Load model with L40S optimization
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            use_cache=False,  # Disable cache for training
            max_memory={0: "24GB"},  # Use 24GB of 44.4GB VRAM (20GB buffer for training overhead)
        )
        
        # Configure LoRA for L40S - optimized configuration
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,   # Minimal rank for L40S memory constraints
            lora_alpha=16, # Proportionally reduced
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
        
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        yield f"✅ Model loaded with LoRA configuration\n📊 Trainable parameters: {model.get_nb_trainable_parameters()}"
        
        # Prepare dataset
        yield "🔄 Preparing training dataset..."
        tokenized_dataset = format_training_data(examples, tokenizer)
        
        # Split dataset
        split_dataset = tokenized_dataset.train_test_split(test_size=0.1, seed=42)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]
        
        yield f"✅ Dataset prepared: {len(train_dataset)} train, {len(eval_dataset)} eval examples"
        
        # Training arguments optimized for L40S GPU (48GB VRAM)
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=epochs,
            per_device_train_batch_size=1,        # Ultra conservative for L40S to avoid OOM
            per_device_eval_batch_size=1,         # Ultra conservative for L40S to avoid OOM
            gradient_accumulation_steps=16,       # Compensate for smaller batch size (effective batch = 16)
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_steps=10,
            eval_steps=50,
            save_steps=100,
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            warmup_steps=100,
            lr_scheduler_type="cosine",
            fp16=True,
            dataloader_pin_memory=False,          # Disable to save memory
            dataloader_num_workers=0,             # Disable to save memory
            remove_unused_columns=True,
            max_grad_norm=1.0,
            report_to="wandb" if wandb_key else "none",
            run_name=f"qwen-devops-l40s-{datetime.now().strftime('%Y%m%d_%H%M')}",
            resume_from_checkpoint=resume_from_checkpoint,
        )
        
        # Data collator with proper padding
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8,  # Optimize for GPU efficiency
        )
        
        # Initialize trainer (use processing_class for future compatibility)
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            processing_class=tokenizer,  # Use processing_class instead of tokenizer
        )
        
        # Final memory cleanup before training
        yield "🧹 Final memory cleanup for L40S..."
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        
        yield "🚀 Starting training with ultra-conservative L40S settings..."
        
        # Train the model
        trainer.train()
        
        yield "💾 Saving model..."
        
        # Save the final model
        trainer.save_model(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        
        # Save training metrics
        metrics = trainer.state.log_history
        with open(f"{OUTPUT_DIR}/training_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        # Final evaluation
        final_metrics = trainer.evaluate()
        
        if wandb_key:
            wandb.log(final_metrics)
            wandb.finish()
        
        yield f"✅ Training completed successfully!\n📊 Final eval loss: {final_metrics.get('eval_loss', 'N/A'):.4f}"
        
        return f"🎉 Model saved to {OUTPUT_DIR}"
        
    except Exception as e:
        error_msg = f"❌ Training failed: {str(e)}"
        yield error_msg
        return error_msg

def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(title="Qwen3-8B DevOps Foundation Model Training") as app:
        gr.Markdown("# 🤖 Qwen3-8B DevOps Foundation Model Training")
        gr.Markdown("Train a specialized DevOps/SRE model using the latest Qwen3-8B base model")
        
        with gr.Row():
            with gr.Column():
                wandb_project = gr.Textbox(
                    label="W&B Project Name",
                    value="qwen-devops-foundation",
                    placeholder="Enter Weights & Biases project name"
                )
                learning_rate = gr.Slider(
                    minimum=1e-5,
                    maximum=1e-3,
                    value=2e-4,
                    step=1e-5,
                    label="Learning Rate"
                )
                epochs = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Training Epochs"
                )
                batch_size = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=2,
                    step=1,
                    label="Batch Size"
                )
                
                train_btn = gr.Button("🚀 Start Training", variant="primary")
            
            with gr.Column():
                output = gr.Textbox(
                    label="Training Progress",
                    lines=20,
                    max_lines=30,
                    show_copy_button=True
                )
        
        # Training progress
        train_btn.click(
            fn=train_model,
            inputs=[wandb_project, learning_rate, epochs, batch_size],
            outputs=output,
            show_progress=True
        )
        
        gr.Markdown("""
        ## 📋 Setup Instructions:
        
        1. **HuggingFace Token**: Add your HF token as a secret named `HF_TOKEN`
        2. **W&B API Key**: Add your Weights & Biases API key as a secret named `WANDB_API_KEY`
        3. **Hardware**: Use ZeroGPU (free with PRO) or dedicated GPU for faster training
        
        ## 💰 Cost Estimates:
        - **ZeroGPU**: FREE with PRO subscription ($9/month)
        - **L4 GPU**: $0.80/hour (~$4.80 per training run)
        - **A100 GPU**: $2.50/hour (~$7.50 per training run)
        """)
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)