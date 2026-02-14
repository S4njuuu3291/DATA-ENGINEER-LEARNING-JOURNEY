# Chapter 0: Setup & Provider Connection

> **Learning Objective**: Memahami fondasi Terraform, cara setup AWS provider, dan workflow Terraform initialization.

---

## 📋 Table of Contents

1. [Teori: Declarative vs Imperative](#teori-declarative-vs-imperative)
2. [Anatomi File Terraform](#anatomi-file-terraform)
3. [Struktur Project](#struktur-project)
4. [Workflow CLI](#workflow-cli)
5. [Hands-on Guide](#hands-on-guide)
6. [Credentials Management](#credentials-management)
7. [Catatan Arsitek](#catatan-arsitek)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference](#quick-reference)

---

## Teori: Declarative vs Imperative

### **Declarative (Terraform)**

Anda mendeskripsikan **state yang DIINGINKAN**. Terraform handle prosesnya.

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}
```

**Keuntungan:**
- ✅ Idempotent (jalankan 100x = hasil sama)
- ✅ Version-controllable (bisa di-git)
- ✅ Readable dan maintainable
- ✅ Mudah rollback & disaster recovery

### **Imperative (Boto3/AWS CLI)**

Anda menjalankan serangkaian perintah step-by-step.

```python
ec2 = boto3.client('ec2')
ec2.run_instances(ImageId='ami-0c55...', MinCount=1, MaxCount=1)
```

**Masalah:**
- ❌ NOT idempotent (jalankan 2x = 2 resources)
- ❌ Manual changes tidak tercatat
- ❌ Drift detection nightmare
- ❌ Kolaborasi sulit

### **Mengapa Data Engineer Butuh Terraform?**

Data pipelines perlu infrastruktur yang **immutable & auditable**:

| Aspek | Terraform | Manual Console |
|-------|-----------|----------------|
| Code Review | Via PR di git | No audit |
| Reproducibility | Copy & apply | Manual steps |
| Disaster Recovery | Seconds | Hours |
| Team Collaboration | Centralized | Chaotic |
| Version History | Full audit trail | None |

**Kesimpulan:** Terraform = **Infrastructure Reliability** 

---

## Anatomi File Terraform

### **`.terraform/` Directory (Working Directory)**

Auto-generated folder setelah `terraform init`. Berisi:
- Provider binaries (e.g., terraform-provider-aws)
- Module files
- Plugin cache
- Dependency lock files

⚠️ **Aman di-delete:** File akan di-recreate otomatis saat `terraform init`

⚠️ **JANGAN commit ke git:** Tambahkan ke `.gitignore`

### **`terraform.tfstate` - The Brain**

Adalah JSON file yang menyimpan **current infrastructure state**. Terraform gunakan untuk:
- Mapping resource code  AWS resource ID
- Track attribute changes  
- Detect configuration drift
- Enable destroy & updates

**🔒 SECURITY CRITICAL - 3 Hal Penting:**

1. ⛔ **JANGAN commit ke git** (contains sensitive data & secret keys)
2. 💾 **Backup regularly** (adalah single source of truth untuk infrastructure)
3. 🚫 **JANGAN edit manual** (akan menyebabkan inconsistency)

**Production Tip:** Gunakan remote state di Terraform Cloud atau S3 dengan encryption & versioning.

### **`terraform.tfvars` - Variable Values**

File untuk menyimpan runtime values seperti:
- Region (ap-southeast-1)
- Instance types (t2.micro, t2.small)
- Credentials (AWS Access Key & Secret)
- Environment-specific values

**🔐 Security Best Practice:**

```
terraform.tfvars         ← JANGAN commit (sensitive data)
terraform.tfvars.example ← OK commit (template only)
*.tfvars                 ← JANGAN commit (gitignore)
```

### **`terraform.lock.hcl` - Dependency Lock File**

Mencatat exact versions dari semua providers & modules yang digunakan.

✅ **HARUS commit ke git** untuk memastikan team menggunakan versi yang sama.

### **`.terraform.lock.hcl` Example:**

```hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.0.0"
  constraints = "~> 5.0"
  # ... (lock information)
}
```

---

## Struktur Project

Direktori `00-setup-provider` berisi file-file untuk konfigurasi AWS provider:

```
00-setup-provider/
├── provider.tf              # AWS provider configuration
├── variables.tf             # Variable declarations
├── locals.tf                # Local constants
├── outputs.tf               # Output values after apply
├── terraform.tfvars.example # Template untuk credentials
└── README.md                # Dokumentasi (file ini)
```

### **File-File Penjelasan:**

#### **`provider.tf`** - Cloud Provider Setup
```hcl
provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  
  default_tags {
    tags = {
      Environment = "Learning"
      Project     = "Terraform-Fundamentals"
    }
  }
}
```
**Fungsi:**
- Mendefinisikan cloud provider (AWS, Azure, GCP, dll)
- Mengkonfigurasi authentication credentials
- Setting default values seperti region
- Mendefinisikan default tags yang ditambahkan ke semua resources

#### **`variables.tf`** - Deklarasi Variable
```hcl
variable "aws_region" {
  type        = string
  default     = "ap-southeast-1"
  description = "AWS region untuk deploy"
}

variable "aws_access_key" {
  type        = string
  sensitive   = true
  description = "AWS Access Key ID"
}

variable "aws_secret_key" {
  type        = string
  sensitive   = true
  description = "AWS Secret Access Key"
}
```
**Fungsi:**
- Mendeklarasikan input variables
- Mendefinisikan type (string, number, list, map, bool)
- Setting default values
- Adding descriptions untuk dokumentasi
- Mark sensitive = true untuk credentials (hidden di output)

#### **`locals.tf`** - Local Constants
```hcl
locals {
  terraform_version = "1.0+"
  
  common_tags = {
    terraform_version = local.terraform_version
    created_date      = "2026-02-13"
  }
}
```
**Fungsi:**
- Mendefinisikan values yang di-reuse dalam file yang sama
- NOT input dari user (berbeda dengan variables.tf)
- Mengcompute derived values
- Membantu DRY (Don't Repeat Yourself) principle

#### **`outputs.tf`** - Output Values
```hcl
output "aws_account_id" {
  description = "AWS Account ID yang digunakan"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region_configured" {
  description = "AWS Region yang dikonfigurasi"
  value       = var.aws_region
}

output "aws_caller_arn" {
  description = "ARN dari AWS caller (user/role)"
  value       = data.aws_caller_identity.current.arn
}
```
**Fungsi:**
- Export nilai penting setelah `terraform apply`
- Digunakan untuk referencing antar modules/projects
- Ditampilkan di terminal setelah apply
- Bisa di-query dengan: `terraform output aws_account_id`

#### **`terraform.tfvars.example`** - Template Variables
```hcl
aws_region     = "ap-southeast-1"
aws_access_key = ""
aws_secret_key = ""
```
**Fungsi:**
- Template untuk `terraform.tfvars` yang actual
- Dicommit ke git untuk memberikan contoh kepada team
- User copy ini & isi dengan credentials mereka
- File ini send-message tidak sensitive, hanya example

## Workflow CLI

### **Commands Overview**

| Command | Fungsi |
|---------|--------|
| `terraform init` | Initialize Terraform, download providers & modules |
| `terraform validate` | Syntax check untuk semua .tf files |
| `terraform fmt` | Auto-format semua .tf files (prettier) |
| `terraform plan` | Preview changes yang akan di-apply (dry-run) |
| `terraform apply` | Execute changes dan update state |
| `terraform destroy` | Delete semua resources yang di-manage |
| `terraform state list` | List semua managed resources |
| `terraform state show` | Detail info satu resource |
| `terraform refresh` | Sync state dari actual AWS resources |

### **Standard Workflow**

```
1. terraform init      ← Download providers & initialize
2. terraform validate  ← Check for syntax errors
3. terraform fmt       ← Format code (optional but recommended)
4. terraform plan      ← Preview changes (REVIEW CAREFULLY)
5. terraform apply     ← Deploy (type 'yes' to confirm)
6. terraform state     ← Monitor & inspect resources
```

### **Debugging Commands**

```bash
# List semua resources yang di-manage
terraform state list

# Show detail satu resource
terraform state show aws_instance.web

# Sync state dengan actual AWS infrastructure
terraform refresh

# Show current Terraform version & plugins
terraform version

# Validate configuration files
terraform validate
```

### **Advanced Commands**

```bash
# Apply dengan auto-approve (gunakan hati-hati!)
terraform apply -auto-approve

# Create file plan untuk review (separasi plan & apply)
terraform plan -out=tfplan
terraform apply tfplan

# Destroy specific resource
terraform destroy -target aws_instance.web
```

---

## Hands-on Guide

### **Prerequisites**

- ✅ AWS Account dengan access permissions
- ✅ AWS Access Key ID & Secret Access Key
- ✅ Terraform installed (v1.0+)
- ✅ Git (untuk version control)

**Check Terraform Installation:**
```bash
terraform version
# Output: Terraform v1.x.x
```

### **Step 1: Setup AWS Credentials**

Pilih salah satu method:

#### **Option A: AWS Credentials File (Recommended)**

```bash
# Create credentials file
mkdir -p ~/.aws
nano ~/.aws/credentials

# Add format:
[default]
aws_access_key_id     = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[production]
aws_access_key_id     = PROD_ACCESS_KEY
aws_secret_access_key = PROD_SECRET_KEY
```

**Keuntungan:**
- Support multiple AWS accounts
- Secure (file permissions 600)
- CI/CD friendly

#### **Option B: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_REGION="ap-southeast-1"
```

**Keuntungan:**
- No file creation needed
- Good untuk CI/CD pipelines

#### **Option C: Hardcode di terraform.tfvars (NOT RECOMMENDED)**

```hcl
aws_access_key = "YOUR_KEY"
aws_secret_key = "YOUR_SECRET"
```

⚠️ **JANGAN TERAPKAN** - Risiko credential exposure!

### **Step 2: Prepare terraform.tfvars**

```bash
# Copy template
cp terraform.tfvars.example terraform.tfvars

# Edit dengan values Anda
nano terraform.tfvars
```

**Content of terraform.tfvars:**
```hcl
aws_region     = "ap-southeast-1"    # Default already set, customize if needed
aws_access_key = ""                   # Leave empty if using credentials file
aws_secret_key = ""                   # Leave empty if using credentials file
```

💡 **Tip:** Jika menggunakan `~/.aws/credentials`, field `aws_access_key` dan `aws_secret_key` bisa dikosongkan. Terraform akan auto-detect dari credentials file.

### **Step 3: Initialize Terraform**

```bash
# Download AWS provider & setup .terraform directory
terraform init

# Output:
# Initializing the backend...
# Initializing modules...
# Initializing provider plugins...
# - Reusing previous version of hashicorp/aws from...
# - Using previously-installed hashicorp/aws v5.0.0
# 
# Terraform has been successfully initialized!
```

✅ Success indicators:
- `.terraform/` directory created
- `.terraform.lock.hcl` file generated
- Providers downloaded

### **Step 4: Validate Configuration**

```bash
# Check untuk syntax errors
terraform validate

# Output:
# Success! The configuration is valid.
```

### **Step 5: Review Plan**

```bash
# Preview changes tanpa apply
terraform plan

# Output:
# No changes. Your infrastructure matches the configuration.
#
# Outputs:
# 
# aws_account_id = "123456789012"
# aws_caller_arn = "arn:aws:iam::123456789012:user/username"
# aws_region_configured = "ap-southeast-1"
# terraform_version = "1.0+"
```

⚠️ **Review Carefully:** Plan menunjukkan persis apa yang akan di-deploy

### **Step 6: Apply Configuration**

```bash
# Deploy infrastructure ke AWS
terraform apply

# Akan diminta confirmation:
# Do you want to perform these actions?
# Type 'yes' to confirm
```

**Success Output:**
```
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

aws_account_id = "123456789012"
aws_caller_arn = "arn:aws:iam::123456789012:user/username"
aws_region_configured = "ap-southeast-1"
terraform_version = "1.0+"
```

✅ Chapter 0 selesai! Infrastructure setup validated & credentials working.

### **Step 7: Verify State** (Optional)

```bash
# List managed resources
terraform state list

# Show detail satu resource
terraform state show data.aws_caller_identity.current

# Show all outputs
terraform output
```

---

## Troubleshooting

### **Common Errors & Solutions**

| Error | Root Cause | Solution |
|-------|-----------|----------|
| `Error: error configuring Terraform AWS Provider: access denied` | Invalid credentials | Verify AWS key & secret di `terraform.tfvars` atau `~/.aws/credentials` |
| `Error: InvalidClientTokenId` | Expired atau wrong credentials | Generate new AWS Access Keys di AWS Console |
| `Error: AuthFailure` | Wrong region sudah deprecated | Update `aws_region` ke region yang valid |
| `Error: validation of values failed` | Wrong variable type | Check `variables.tf` untuk expected types |
| `Error: Module not found` | Provider cache corrupted | Run: `rm -rf .terraform && terraform init` |
| `Error: The configured AWS provider version is too old` | Provider version mismatch | Run: `terraform init --upgrade` |
| `Error: resource already exists` | State mismatch dengan AWS | Run: `terraform refresh` untuk sync state |

### **Debug Commands**

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan

# Show detailed error information
terraform validate -json

# Check current state
terraform show

# Check provider configuration
terraform providers
```

### **Best Practices untuk Avoid Issues**

1. **Always `terraform plan` before apply**
   ```bash
   terraform plan -out=tfplan
   # Review output
   terraform apply tfplan
   ```

2. **Keep state file safe**
   ```bash
   # Backup state regularly
   cp terraform.tfstate terraform.tfstate.backup
   
   # Use remote state in production
   # (covered di chapters selanjutnya)
   ```

3. **Use `.terraformignore`** untuk exclude files
   ```
   .env
   *.log
   /local/
   ```

4. **Version control best practices**
   ```
   ✅ Commit: *.tf, .terraform.lock.hcl, terraform.tfvars.example
   ❌ Exclude: terraform.tfvars, .tfstate, .tfstate.backup, .terraform/
   ```

---

## Credentials Management

### **AWS Credential Methods Comparison**

| Aspek | AWS File | Env Vars | Terraform Cloud | IAM Role |
|-------|----------|----------|---|---|
| Security | Local | Memory | Remote Encrypted | Built-in |
| Multi-Account | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| Production | ⚠️ Dev only | ⚠️ Temporary | ✅ Recommended | ✅ Recommended |

### **Quick Setup**

**Option A: AWS Credentials File (Recommended)**
```bash
mkdir -p ~/.aws && nano ~/.aws/credentials

[default]
aws_access_key_id     = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
```

**Option C: Multiple Profiles**
```bash
[dev]
aws_access_key_id     = DEV_KEY
aws_secret_access_key = DEV_SECRET

[prod]  
aws_access_key_id     = PROD_KEY
aws_secret_access_key = PROD_SECRET

# Use: export AWS_PROFILE=prod
```

### **Security Checklist**

✅ DO:
- Store credentials dalam `~/.aws/credentials`
- Use `sensitive = true` di variables
- Rotate credentials regularly
- Use IAM roles untuk production

❌ DON'T:
- Hardcode credentials di `.tf` files
- Commit `terraform.tfvars` ke git
- Share AWS keys di chat/email
- Use root AWS account

---

## Catatan Arsitek

### **File Separation Principle = Scalability**

Setiap file punya responsibility yang jelas:

```
provider.tf         ← Cloud provider setup only (AWS, Azure, GCP)
variables.tf        ← Variable declarations (inputs)
locals.tf           ← Local constants (internal only)
outputs.tf          ← Exports (outputs)
terraform.tfvars    ← Values only (git-ignored)
.terraform/         ← Cache files (git-ignored)
.tfstate            ← State file (git-ignored)
.tfstate.backup     ← State backup (git-ignored)
.gitignore          ← Git ignore rules
```

**Keuntungan File Separation:**
- Single responsibility principle
- Easy to review & understand
- Less conflicts dalam team
- Better organization untuk large projects

### **Core Architecture Principles**

#### **1. Single Responsibility**
Setiap file punya satu job:
- `provider.tf` → hanya cloud provider config
- `variables.tf` → hanya variable declarations
- `outputs.tf` → hanya export values
- `locals.tf` → hanya local constants

#### **2. Infrastructure as Code (IaC)**
- ✅ All changes di version control (git)
- ✅ Code review sebelum deploy
- ✅ Full audit trail
- ❌ No manual AWS console changes

#### **3. Multi-Environment Support**
Sama code, berbeda `.tfvars`:
```
dev/terraform.tfvars
staging/terraform.tfvars
prod/terraform.tfvars
```

#### **4. Drift Detection**
Terraform detect jika ada manual changes di AWS:
```bash
terraform plan  # Will show changes jika infrastructure was manually modified
```

#### **5. Disaster Recovery**
Infrastructure bisa di-rebuild dalam hitungan menit:
```bash
terraform apply  # Recreate everything dari .tf files
```

### **Why Data Engineers Need Terraform**

- ✅ Version control: Audit trail untuk semua changes
- ✅ Reproducible: Same code = consistent infrastructure
- ✅ Disaster recovery: Rebuild dalam minutes
- ✅ Team collaboration: Code review via git

---

## Quick Reference

### **Commands Cheat Sheet**

```bash
# === INITIALIZATION ===
terraform init                          # Initialize project (download providers)
terraform init --upgrade                # Upgrade provider versions

# === VALIDATION & FORMATTING ===
terraform validate                      # Syntax check
terraform validate -json                # JSON format validation output
terraform fmt                           # Auto-format all .tf files
terraform fmt -recursive                # Format recursively dalam subdirectories

# === PLANNING & APPLYING ===
terraform plan                          # Preview changes (dry-run)
terraform plan -out=tfplan              # Save plan to file
terraform apply PLAN_FILE               # Apply saved plan
terraform apply -auto-approve           # Apply without confirmation (caution!)

# === STATE MANAGEMENT ===
terraform state list                    # List all resources
terraform state show RESOURCE           # Show resource details
terraform state rm RESOURCE             # Remove resource from state
terraform state mv SRC DEST             # Move/rename resource
terraform refresh                       # Sync state dengan AWS

# === DESTROYING ===
terraform destroy                       # Delete all resources
terraform destroy -auto-approve         # Delete without confirmation
terraform destroy -target RESOURCE      # Delete specific resource

# === DEBUGGING ===
export TF_LOG=DEBUG                     # Enable debug logging
terraform providers                     # Show providers versions
terraform show                          # Show entire state
terraform output                        # Show outputs only
terraform version                       # Show Terraform version
```

### **Common Workflows**

**Workflow 1: Initial Setup**
```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars                   # Edit dengan credentials Anda
terraform init
terraform validate
terraform plan
terraform apply
```

**Workflow 2: Update Existing Infrastructure**
```bash
git pull                                # Get latest changes
terraform plan                          # Review changes
terraform apply
```

**Workflow 3: Multi-Environment Management**
```bash
# For dev environment
terraform -chdir=dev apply

# For production environment
export AWS_PROFILE=production
terraform -chdir=prod apply
```

**Workflow 4: Disaster Recovery**
```bash
# Entire infrastructure hilang? Rebuild dengan:
terraform init
terraform apply -auto-approve          # Instant reconstruction!
```

---

## Resources & Links

- [Terraform Docs](https://www.terraform.io/language)
- [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [AWS Examples](https://github.com/hashicorp/terraform-provider-aws/tree/main/examples)

---

## FAQ

**Q: Apa perbedaan `.terraform` dan `.tfstate`?**  
A: `.terraform/` adalah cache folder (bisa di-delete), `.tfstate` adalah the brain (JANGAN delete!)

**Q: Bisakah menggunakan Terraform tanpa AWS credentials?**  
A: Tidak. Terraform butuh credentials untuk authenticate ke AWS.

**Q: Bagaimana jika `.tfstate` hilang?**  
A: Tragedy! Infrastructure tidak bisa di-manage. Gunakan remote state untuk backup.

**Q: Apakah boleh mengedit `.tfstate` secara manual?**  
A: Tidak! JANGAN PERNAH. State corruption = infrastructure chaos.

**Q: Berapa kali perlu run `terraform init`?**  
A: Hanya sekali per project (atau jika provider berubah).

**Q: Apakah `terraform plan` akan mengubah infrastructure?**  
A: Tidak. Plan hanya preview (dry-run). Apply yang melakukan perubahan.

**Q: Bisakah menggunakan Terraform untuk non-AWS cloud?**  
A: Ya! Terraform support 1000+ providers (Azure, GCP, Kubernetes, etc).

---

**Version History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-13 | Initial release with full documentation |
| 1.1 | TBD | Add video tutorials & more examples |
| 1.2 | TBD | Add Terraform Cloud integration guide |

**Created By:** Data Engineering Team  
**Last Updated:** 2026-02-13  
**Status:** Production Ready ✅  
**Maintenance:** Active
