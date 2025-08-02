# MLOps S3 Bucket CloudFormation Template

This CloudFormation template creates a production-ready S3 bucket for MLOps data versioning using DVC (Data Version Control) and ML artifact storage.

## 🎯 Purpose

The template provisions:
- **S3 Bucket** for DVC data versioning and ML artifacts
- **IAM Roles & Policies** for secure access
- **Security Controls** (encryption, access blocking, SSL enforcement)
- **Cost Optimization** (lifecycle policies for storage classes)
- **Monitoring** (CloudWatch logs and S3 access logging)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MLOps S3 Infrastructure              │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│ │   S3 Bucket     │  │   IAM Role      │  │ CloudWatch │ │
│ │ mlops-data-     │  │ DVC Access      │  │ Logs       │ │
│ │ bucket          │  │ Role            │  │            │ │
│ │                 │  │                 │  │            │ │
│ │ • Versioning    │  │ • EC2 Profile   │  │ • S3 Access│ │
│ │ • Encryption    │  │ • S3 Permissions│  │ • Audit    │ │
│ │ • Lifecycle     │  │ • CloudWatch    │  │ • Monitor  │ │
│ └─────────────────┘  └─────────────────┘  └────────────┘ │
│          │                      │                  │     │
│          └──────────────────────┼──────────────────┘     │
│                                 │                        │
│ ┌─────────────────┐  ┌─────────────────┐               │
│ │   IAM User      │  │ Bucket Policy   │               │
│ │ CI/CD Pipeline  │  │ Security Rules  │               │
│ │                 │  │                 │               │
│ │ • Access Keys   │  │ • SSL Required  │               │
│ │ • S3 Access     │  │ • Role Access   │               │
│ │ • CI/CD Ready   │  │ • Public Block  │               │
│ └─────────────────┘  └─────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

## 📋 Features

### 🔒 Security
- **Server-side encryption** with AES-256
- **Public access blocked** by default
- **SSL/TLS enforcement** for all connections
- **IAM-based access control** with least privilege
- **Access logging** to CloudWatch

### 💰 Cost Optimization
- **Intelligent lifecycle policies**:
  - Standard IA after 30 days
  - Glacier after 90 days
  - Deep Archive after 365 days
- **Cleanup rules** for incomplete uploads
- **Delete marker optimization**

### 📊 Monitoring & Compliance
- **CloudWatch integration** for access logging
- **S3 metrics** and monitoring
- **Versioning support** for data lineage
- **Audit trail** for compliance requirements

### 🚀 DVC Integration
- **Optimized for DVC** data versioning
- **Multiple access methods** (IAM roles, access keys)
- **CI/CD ready** with dedicated user and keys
- **Multi-environment support**

## 🚀 Quick Start

### 1. Deploy the Stack

```bash
# Basic deployment (development environment)
./deploy-s3-bucket.sh

# Production deployment with custom bucket name
./deploy-s3-bucket.sh production my-mlops-bucket-prod

# Custom environment
./deploy-s3-bucket.sh staging mlops-staging-bucket
```

### 2. Configure DVC

```bash
# Add S3 remote to DVC
dvc remote add -d s3 s3://mlops-data-bucket/dvc
dvc remote modify s3 region us-east-1

# For local development with access keys
dvc remote modify s3 access_key_id YOUR_ACCESS_KEY
dvc remote modify s3 secret_access_key YOUR_SECRET_KEY

# For EC2/EKS with IAM roles (recommended)
dvc remote modify s3 profile default
```

### 3. Test DVC Connection

```bash
# Test connection
dvc remote list

# Push data to S3
dvc add data/
dvc push

# Pull data from S3
dvc pull
```

## 📚 Parameters

| Parameter          | Description                   | Default             | Values                                 |
| ------------------ | ----------------------------- | ------------------- | -------------------------------------- |
| `BucketName`       | S3 bucket name                | `mlops-data-bucket` | Valid S3 bucket name                   |
| `Environment`      | Environment type              | `development`       | `development`, `staging`, `production` |
| `EnableVersioning` | Enable S3 versioning          | `true`              | `true`, `false`                        |
| `EnableEncryption` | Enable server-side encryption | `true`              | `true`, `false`                        |

## 📤 Outputs

The template provides these outputs:

| Output                  | Description                             |
| ----------------------- | --------------------------------------- |
| `BucketName`            | Created S3 bucket name                  |
| `BucketArn`             | S3 bucket ARN                           |
| `DVCAccessRoleArn`      | IAM role ARN for EC2/EKS                |
| `CIUserAccessKeyId`     | Access key for CI/CD                    |
| `CIUserSecretAccessKey` | Secret key for CI/CD (NoEcho)           |
| `DVCConfigCommands`     | Ready-to-use DVC configuration commands |

## 🔧 Advanced Configuration

### Custom Lifecycle Policies

Modify the lifecycle rules in the template:

```yaml
LifecycleConfiguration:
  Rules:
    - Id: CustomStorageOptimization
      Status: Enabled
      Transitions:
        - Days: 7
          StorageClass: STANDARD_IA
        - Days: 30
          StorageClass: GLACIER
```

### Additional IAM Permissions

Add custom permissions to the DVC access policy:

```yaml
PolicyDocument:
  Statement:
    - Effect: Allow
      Action:
        - s3:GetObject
        - s3:PutObject
        - your-custom-action
      Resource: !Sub '${MLOpsDataBucket}/*'
```

### Cross-Region Replication

For production environments, consider adding cross-region replication:

```yaml
ReplicationConfiguration:
  Role: !GetAtt ReplicationRole.Arn
  Rules:
    - Id: ReplicateToSecondaryRegion
      Status: Enabled
      Prefix: important/
      Destination:
        Bucket: !Sub 'arn:aws:s3:::${BucketName}-replica'
        StorageClass: STANDARD_IA
```

## 🧹 Cleanup

To delete the entire stack:

```bash
aws cloudformation delete-stack \
  --stack-name mlops-s3-bucket-development \
  --region us-east-1
```

**⚠️ Warning**: This will delete the S3 bucket and all data. Ensure you have backups!

## 🔍 Troubleshooting

### Common Issues

1. **Bucket name already exists**
   ```bash
   # Use a unique bucket name
   ./deploy-s3-bucket.sh development my-unique-bucket-name-123
   ```

2. **DVC cannot access bucket**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Test S3 access
   aws s3 ls s3://your-bucket-name/
   ```

3. **Permission denied errors**
   ```bash
   # Verify IAM permissions
   aws iam get-role --role-name mlops-data-bucket-dvc-access-role
   ```

### Monitoring

Check CloudWatch logs for S3 access:

```bash
aws logs describe-log-groups --log-group-name-prefix '/aws/s3/mlops-data-bucket'
```

## 📖 Best Practices

### Security
- ✅ Use IAM roles instead of access keys when possible
- ✅ Regularly rotate access keys
- ✅ Monitor S3 access patterns
- ✅ Enable CloudTrail for API auditing

### Cost Optimization
- ✅ Review storage classes quarterly
- ✅ Monitor data access patterns
- ✅ Use S3 Analytics for insights
- ✅ Implement data retention policies

### Operations
- ✅ Tag resources consistently
- ✅ Use Infrastructure as Code (this template)
- ✅ Monitor costs with AWS Cost Explorer
- ✅ Backup critical data to another region

## 🔗 Related Resources

- [DVC Documentation](https://dvc.org/doc)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [MLOps on AWS](https://aws.amazon.com/solutions/implementations/mlops-workload-orchestrator/)

## 📝 License

This CloudFormation template is provided under the MIT License. See the main repository license for details.