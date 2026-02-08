# 01. Why VPC Exists: Network Isolation

> **Duration:** 45 minutes  
> **Difficulty:** ⭐ (Conceptual)  
> **Key Takeaway:** VPC = Private network. Data stays within your infrastructure (doesn't touch internet)

---

## The Problem: Public vs Private Data

### Scenario: Unprotected Data

```
Your S3 bucket (data-lake) on public internet:
┌──────────────S3 Bucket─────────────┐
│  contains customer data (PII)       │
│  - Emails                           │
│  - Phone numbers                    │
│  - Payment info                     │
└─────────────────────────────────────┘
           ↑ exposed to internet
           ↓ hacker accesses

Risk: Data breach, GDPR fine, reputational damage
```

### Solution: VPC (Private Network)

```
Your VPC (private network):
┌────────────────────VPC────────────────────┐
│  Private "company network"                 │
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │ S3 bucket (private, no internet)    │  │
│  │ contains customer data (SAFE)       │  │
│  │ - Emails, phone numbers, payments   │  │
│  └─────────────────────────────────────┘  │
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │ Lambda (processing, private)        │  │
│  │ Glue job (ETL, private)             │  │
│  │ RDS database (queries, private)     │  │
│  └─────────────────────────────────────┘  │
│                                            │
└────────────────────────────────────────────┘
           VPC boundary (firewall)
           ↓ No internet exposure
           ↓ Hacker can't reach

Result: Data protected (unless hacker penetrates VPC)
```

---

## What is a VPC?

**VPC (Virtual Private Cloud)** = Your own isolated network in AWS

```
Properties:
- Isolated from other AWS customers ✅
- You control CIDR block (IP address range)
- You control routing (how traffic flows)
- You control security (what's allowed in/out)
- No charge for VPC itself (pay only for resources)
```

### Traditional Network vs VPC

```
Traditional (On-Premises):
- Buy servers, routers, firewalls
- Setup network infrastructure
- Monthly cost: $5000+ (hardware rental)
- Configuration: Takes weeks

VPC (AWS):
- Logical network in AWS
- AWS manages hardware
- Configuration: Minutes (via API)
- Cost: Minimal (only data transfer)
```

---

## VPC Components

### 1. CIDR Block (IP Address Range)

```
VPC needs IP address range for internal devices

Example CIDR: 10.0.0.0/16
- First address: 10.0.0.1
- Last address: 10.0.255.255
- Total: 65,536 IP addresses

Why needed:
- Lambda needs internal IP
- RDS database needs internal IP
- EC2 instances need internal IP
```

### 2. Subnets (Subdivisions)

**Subnet** = Slice of VPC with own address range

```
VPC: 10.0.0.0/16 (65K addresses)
  ├─ Public Subnet: 10.0.1.0/24 (256 addresses, exposed to internet)
  ├─ Private Subnet: 10.0.2.0/24 (256 addresses, internal only)
  └─ Private Subnet: 10.0.3.0/24 (256 addresses, internal only)

Analogy: VPC = Building, Subnets = Floors
```

### 3. Public vs Private Subnets

**Public Subnet:**
- Has route to internet (via Internet Gateway)
- Resources: Can receive traffic from internet
- Use: Load balancers, NAT gateways, bastion hosts
- Risk: Exposed to attacks

**Private Subnet:**
- No route to internet (no Internet Gateway)
- Resources: Can't be reached from internet
- Use: Databases, Lambda, Glue, internal services
- Safer: Protected by lack of internet route

### 4. Internet Gateway

**Gateway** = Door that allows internet traffic IN/OUT

```
Without Gateway:
VPC (Private)
  └─ No way out to internet
     └─ Lambda can't call external API

With Gateway:
VPC (Private)
  └─ Internet Gateway attached
     └─ Lambda can call external API (but Lambda still private)
```

### 5. NAT Gateway

**NAT** = Network Address Translation (hide internal IPs)

```
Private resource (Lambda in private subnet):
- Wants to call external API (example.com)
- Can't connect directly (no internet route)
- Solution: NAT gateway in public subnet

Process:
1. Lambda sends request to NAT gateway
2. NAT replaces source IP (internal IP → NAT IP)
3. NAT sends to Internet Gateway
4. Request reaches example.com
5. Response returns
6. NAT translates (example.com IP → Lambda internal IP)
7. Lambda receives response

Result: Lambda got external API response without being publicly accessible
```

---

## Data Pipeline Security Architecture

### Standard 3-Tier Pattern

```
┌──────────────────────────────────────┐
│ Internet (Public)                    │
│  └─ Attackers ↓                      │
│                                       │
│ Internet Gateway                     │
└──────────────────────────────────────┘
              ↓↑
┌──────────────────────────────────────┐
│ PUBLIC SUBNET (Bastion Host)         │
│  - NAT Gateway (allows outbound)     │
│  - Load Balancer (accepts inbound)   │
│  - Bastion Host (SSH access)         │
└──────────────────────────────────────┘
              ↓↑
┌──────────────────────────────────────┐
│ PRIVATE SUBNET (Application Tier)    │
│  - Lambda functions                  │
│  - Glue jobs                         │
│  - ECS containers                    │
│  - No internet access (protected)    │
└──────────────────────────────────────┘
              ↓↑
┌──────────────────────────────────────┐
│ PRIVATE SUBNET (Data Tier)           │
│  - S3 (via VPC endpoint)             │
│  - RDS database                      │
│  - ElastiCache                       │
│  - No internet access (protected)    │
└──────────────────────────────────────┘
```

---

## VPC Endpoints: Accessing AWS Services Privately

### Problem Without Endpoint

```
Lambda in private subnet needs to access S3:
Lambda →  (request goes to public internet)
   ↓
Internet Gateway
   ↓
S3 (AWS public endpoint)
   ↓
Internet Gateway
   ↓
Lambda (receives response)

Issues:
- Traffic exposed to internet (not private!)
- Data egres charges ($0.02 per GB)
- Latency (goes through internet)
- Risk: Hacker intercepts traffic
```

### Solution: VPC Endpoint

```
Lambda in private subnet + S3 VPC endpoint:
Lambda → (direct private connection)
   ↓
S3 VPC Endpoint (in VPC)
   ↓
S3 (AWS S3 backend, via private AWS network)

Benefits:
✅ All private (never touches internet)
✅ No data egress charges (free)
✅ Lower latency (direct connection)
✅ More secure (no internet exposure)
```

---

## Real Data Pipeline Example

```
Architecture:
1. S3 bucket (Bronze layer)
   ↓ (VPC endpoint: private access)
2. Lambda function (in private subnet)
   ↓ (processes data)
3. S3 bucket (Silver layer)
   ↓ (VPC endpoint: private access)
4. Glue job (in private subnet)
   ↓ (transforms data)
5. S3 bucket (Gold layer)
   ↓ (VPC endpoint: private access)
6. Athena (in public but secured)
   ↓ (analysts query from office network)

All data movement: Private (no internet exposure)
Cost: Minimal (no egress charges)
Security: High (no data leaves AWS network)
```

---

## VPC Limits & Considerations

### Subnet Size

```
Maximum IPs per subnet:
- /24 subnet = 256 addresses (250 usable)
- /23 subnet = 512 addresses (508 usable)
- /22 subnet = 1024 addresses (1020 usable)

Reserve IPs for:
- AWS reserved: First 4 + last 1 per subnet
- Future growth: Plan for 2-3x current needs
```

### Multi-AZ (Availability Zone)

```
Best practice: Spread subnets across AZs

Scenario 1 (All in 1 AZ - risky):
AZ1: Has all resources
AZ2: Empty

If AZ1 fails → All resources down

Scenario 2 (Multi-AZ - safe):
AZ1: Half resources
AZ2: Half resources (replicate setup)

If AZ1 fails → AZ2 continues
```

---

## Cost Implications

```
VPC (free):
- Creating VPC: $0
- Subnets: $0
- Internet Gateway: $0

Data Transfer (small cost):
- Within VPC: $0
- Out to internet: $0.02/GB (use NAT gateway)
- To S3 via VPC endpoint: $0

Typical 1TB data pipeline:
- Through internet: $20 (1000 GB × $0.02)
- Through VPC endpoint: $0 (free!)

Savings: Using VPC endpoint = $20/month per TB
```

---

## Key Takeaways

1. **VPC = Private network** (data stays in AWS network)
2. **Public/Private subnets** (expose bastion, protect data)
3. **VPC endpoints** (access AWS services without internet)
4. **NAT gateway** (allow private resources to call external APIs)
5. **Multi-AZ** (high availability across zones)

---

## Hands-On Intuition Check ✓

After reading, you should know:

- [ ] Why you need VPC (data privacy)
- [ ] Difference between public and private subnets
- [ ] Purpose of Internet Gateway and NAT
- [ ] How VPC endpoints avoid data egress charges
- [ ] When to use multi-AZ architecture

---

## Next Up

**→ [02-vpc-subnets-basics.md](./02-vpc-subnets-basics.md)** dives into VPC and subnet creation

