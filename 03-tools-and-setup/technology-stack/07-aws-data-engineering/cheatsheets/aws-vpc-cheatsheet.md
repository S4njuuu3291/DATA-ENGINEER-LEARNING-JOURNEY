# AWS VPC Cheatsheet

Quick reference for VPC, subnet, and security configuration commands

---

## VPC & Subnet Creation

### VPC Setup

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16
# Returns: VpcId (use in next commands)

# Tag VPC
aws ec2 create-tags \
  --resources vpc-1234567890 \
  --tags Key=Name,Value=DataPipeline

# Create public subnet
aws ec2 create-subnet \
  --vpc-id vpc-1234567890 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a
# Use this subnet for: NAT Gateway, bastion hosts, load balancers

# Create private subnet (no internet)
aws ec2 create-subnet \
  --vpc-id vpc-1234567890 \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a
# Use this subnet for: Lambda, RDS, Glue jobs

# List subnets
aws ec2 describe-subnets --filter Name=vpc-id,Values=vpc-1234567890
```

### Internet Gateway

```bash
# Create Internet Gateway (connects VPC to internet)
aws ec2 create-internet-gateway
# Returns: InternetGatewayId

# Attach to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-1234567890 \
  --vpc-id vpc-1234567890

# Detach from VPC
aws ec2 detach-internet-gateway \
  --internet-gateway-id igw-1234567890 \
  --vpc-id vpc-1234567890

# Delete
aws ec2 delete-internet-gateway --internet-gateway-id igw-1234567890
```

### NAT Gateway (for private subnet outbound internet)

```bash
# Create Elastic IP (required for NAT)
aws ec2 allocate-address --domain vpc
# Returns: AllocationId (e.g., eipalloc-12345678)

# Create NAT Gateway in PUBLIC subnet
aws ec2 create-nat-gateway \
  --subnet-id subnet-public123 \
  --allocation-id eipalloc-12345678
# Returns: NatGatewayId

# Place in PRIVATE subnet to access NAT

# Check NAT status
aws ec2 describe-nat-gateways --nat-gateway-ids natgw-1234567890

# Delete NAT (release Elastic IP)
aws ec2 delete-nat-gateway --nat-gateway-id natgw-1234567890
aws ec2 release-address --allocation-id eipalloc-12345678
```

### Route Tables

```bash
# Create route table
aws ec2 create-route-table --vpc-id vpc-1234567890

# Associate with subnet (PUBLIC)
aws ec2 associate-route-table \
  --route-table-id rtb-1234567890 \
  --subnet-id subnet-public123

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id rtb-1234567890 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-1234567890

# For PRIVATE subnet: route to NAT Gateway
aws ec2 create-route \
  --route-table-id rtb-private \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id natgw-1234567890

# For S3 VPC Endpoint: route to endpoint (see below)
aws ec2 create-route \
  --route-table-id rtb-private \
  --destination-cidr-block 0.0.0.0/0 \
  --vpc-endpoint-id vpce-1234567890

# List routes
aws ec2 describe-route-tables --route-table-ids rtb-1234567890
```

---

## S3 VPC Endpoint (Gateway Type)

```bash
# Create S3 Gateway Endpoint (private access to S3)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-1234567890 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-private123

# Returns: VpcEndpointId

# Automatically adds route to route table: 
# Destination: com.amazonaws.us-east-1.s3 → Target: vpc-endpoint

# Check endpoint
aws ec2 describe-vpc-endpoints --vpc-endpoint-ids vpce-1234567890

# Delete endpoint
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids vpce-1234567890
```

**Why S3 Endpoint?**
- Private access (no internet needed)
- No data egress charges (~$0.02/GB saved)
- Glue job in private subnet can access S3 directly

---

## Security Groups (Stateful Firewall)

```bash
# Create security group
aws ec2 create-security-group \
  --group-name lambda-sg \
  --description "Lambda security group" \
  --vpc-id vpc-1234567890

# Returns: GroupId (sg-1234567890)

# Allow inbound traffic (INBOUND rule)
# Rule: Lambda needs to call API (HTTPS)
aws ec2 authorize-security-group-ingress \
  --group-id sg-lambda \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Rule: Lambda needs to connect to RDS (port 5432 from DB SG)
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds \
  --protocol tcp \
  --port 5432 \
  --source-security-group-id sg-lambda

# Allow outbound traffic (OUTBOUND rule)
# By default, security groups allow all outbound
# Restrict if needed:
aws ec2 authorize-security-group-egress \
  --group-id sg-lambda \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
# Comment: Allows Lambda to call external APIs (443=HTTPS)

# Revoke rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-lambda \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Describe security group
aws ec2 describe-security-groups --group-ids sg-1234567890

# Delete security group (must be unused)
aws ec2 delete-security-group --group-id sg-1234567890
```

### Security Group Pattern: 3-Tier

```bash
# Tier 1: Public (bastion, NAT)
aws ec2 create-security-group \
  --group-name public-sg \
  --vpc-id vpc-1234567890

# Allow SSH from internet
aws ec2 authorize-security-group-ingress \
  --group-id sg-public \
  --protocol tcp --port 22 --cidr 1.2.3.4/32  # Your IP only!

# Tier 2: Application (Lambda, ECS)
aws ec2 create-security-group \
  --group-name app-sg \
  --vpc-id vpc-1234567890

# Allow from public tier
aws ec2 authorize-security-group-ingress \
  --group-id sg-app \
  --protocol tcp --port 443 \
  --source-security-group-id sg-public

# Tier 3: Data (RDS, S3 endpoint)
aws ec2 create-security-group \
  --group-name data-sg \
  --vpc-id vpc-1234567890

# Allow from app tier (RDS port 5432)
aws ec2 authorize-security-group-ingress \
  --group-id sg-data \
  --protocol tcp --port 5432 \
  --source-security-group-id sg-app
```

---

## Network ACL (Optional - Stateless Firewall)

```bash
# Create NACL (network access control list)
aws ec2 create-network-acl --vpc-id vpc-1234567890

# Add inbound rule (allow HTTP)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-1234567890 \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --ingress

# Add outbound rule
aws ec2 create-network-acl-entry \
  --network-acl-id acl-1234567890 \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --egress

# Describe NACL
aws ec2 describe-network-acls --network-acl-ids acl-1234567890
```

**Security Group vs NACL:**

| Feature | Security Group | NACL |
|---------|---|---|
| **Level** | Instance level | Subnet level |
| **State** | Stateful (return traffic automatic) | Stateless (need both directions) |
| **Scope** | EC2, RDS, Lambda | Entire subnet |
| **Default** | Deny inbound, allow outbound | Allow all |

→ Usually: Use Security Groups. Use NACL for subnet-wide blocking.

---

## VPC Flow Logs (Debugging)

```bash
# Enable VPC Flow Logs (see approved/rejected traffic)
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-1234567890 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs

# Check if traffic was rejected
# CloudWatch Logs → filter for "REJECT" in logs
# Example: Your Lambda couldn't reach S3 endpoint?
# → Check Flow Logs: Was traffic rejected by NACL or SG?

# Describe flow logs
aws ec2 describe-flow-logs
```

---

## CIDR Notation Quick Reference

| Notation | Addresses | Use Case |
|----------|-----------|----------|
| `/32` | 1 | Single IP |
| `/30` | 4 | Point-to-point |
| `/28` | 16 | Small subnet |
| `/26` | 64 | Medium subnet |
| `/24` | 256 | Standard subnet (most common) |
| `/22` | 1,024 | Large subnet |
| `/16` | 65,536 | VPC (typical) |
| `/8` | 16M | Very large network |

**Example:** `10.0.1.0/24` means IPs from `10.0.1.0` to `10.0.1.255`

---

## VPC Endpoints (Non-S3)

```bash
# For RDS endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-1234567890 \
  --service-name com.amazonaws.us-east-1.rds \
  --vpc-endpoint-type Interface

# For DynamoDB endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-1234567890 \
  --service-name com.amazonaws.us-east-1.dynamodb \
  --vpc-endpoint-type Gateway
```

---

## Verify Connectivity

```bash
# Check if instance can reach endpoint
aws ec2 describe-vpc-endpoints \
  --filters Name=service-name,Values=*s3* \
  --query 'VpcEndpoints[].VpcEndpointId'

# Ping endpoint from EC2
ping <endpoint-ip>

# Telnet on port (from EC2)
telnet s3.amazonaws.com 443

# Check route table (ensure endpoint listed)
aws ec2 describe-route-tables --route-table-ids rtb-12345
```

---

## Common Issues & Fixes

❌ **Lambda can't reach S3**
✅ Solutions:
- [ ] Is Lambda in private subnet? (Should be)
- [ ] Is security group allowing outbound 443? (Check egress rules)
- [ ] Is S3 endpoint attached to route table? (Check `describe-vpc-endpoints`)
- [ ] Does IAM role have S3 permissions? (Check policy)

❌ **RDS connection timeout**
✅ Solutions:
- [ ] Is RDS in private subnet? (Should be)
- [ ] Are both Lambda & RDS in same VPC? (Must be)
- [ ] Does RDS SG allow inbound 5432 from Lambda SG?
- [ ] Is route table allowing traffic? (Check NACLs)

❌ **No internet from private subnet**
✅ Solutions:
- [ ] Is NAT Gateway created and running? (`describe-nat-gateways`)
- [ ] Is route table pointing to NAT? (Check routes)
- [ ] Is Elastic IP attached to NAT? (Must have)
- [ ] Is ENI in public subnet? (NAT must be in public)

---

**Pro Tips:**
- 🔒 Always use private subnets for databases
- 🚀 S3 endpoints save ~$0.02/GB outbound
- 📊 Enable Flow Logs to debug network issues
- 🛡️ Use Security Groups first (simpler than NACLs)
- ✅ Test connectivity before deploying jobs

