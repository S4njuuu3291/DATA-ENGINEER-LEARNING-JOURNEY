# 02. VPC Subnets & Routing Basics

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)

---

## Creating a VPC

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Returns:
# {
#   "Vpc": {
#     "VpcId": "vpc-12345678",
#     "CidrBlock": "10.0.0.0/16",
#     "State": "available"
#   }
# }
```

---

## Creating Subnets

### Public Subnet (Internet-facing)

```bash
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a

# Subnet has IPs: 10.0.1.0 through 10.0.1.255
```

### Private Subnet (Internal only)

```bash
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b
```

---

## Internet Gateway & Routing

### Attach Internet Gateway

```bash
# Create gateway
aws ec2 create-internet-gateway

# Attach to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-12345678 \
  --vpc-id vpc-12345678
```

### Route Table (Determines Traffic Flow)

```bash
# Create route table
aws ec2 create-route-table --vpc-id vpc-12345678

# Add route: "Traffic to 0.0.0.0/0 (internet) goes to Internet Gateway"
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-12345678

# Associate route table with public subnet
aws ec2 associate-route-table \
  --route-table-id rtb-12345678 \
  --subnet-id subnet-12345678
```

---

## NAT Gateway (Outbound Internet Access)

### For Private Subnets

```bash
# Create Elastic IP (static IP for NAT)
aws ec2 allocate-address --domain vpc

# Create NAT gateway in PUBLIC subnet
aws ec2 create-nat-gateway \
  --subnet-id subnet-public-12345678 \
  --allocation-id eipalloc-12345678

# Create route for private subnet:
# "Traffic to external internet (0.0.0.0/0) goes through NAT"
aws ec2 create-route \
  --route-table-id rtb-private \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-12345678
```

---

## Security Groups (Firewall Rules)

### Allow Inbound

```bash
# Example: Allow SSH from corporate IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24
```

### Allow Outbound

```bash
# Example: Allow all outbound (default)
aws ec2 authorize-security-group-egress \
  --group-id sg-12345678 \
  --protocol -1 \
  --cidr 0.0.0.0/0
```

---

## Multi-AZ Setup

### Standard Pattern

```
VPC: 10.0.0.0/16

AZ-1 (us-east-1a):
├─ Public Subnet: 10.0.1.0/24
│  └─ NAT Gateway
└─ Private Subnet: 10.0.11.0/24
   └─ Lambda, Glue

AZ-2 (us-east-1b):
├─ Public Subnet: 10.0.2.0/24
│  └─ NAT Gateway (2nd for HA)
└─ Private Subnet: 10.0.12.0/24
   └─ Lambda, Glue (replicated)
```

### RDS Multi-AZ

```bash
aws rds create-db-instance \
  --db-instance-identifier my-database \
  --multi-az \
  --db-subnet-group-name my-subnet-group

# RDS automatically replicates to 2nd AZ
# If primary fails → failover automatic (30-60 sec)
```

---

## Key Concepts

| Concept | Purpose |
|---------|---------|
| **VPC CIDR** | IP address range (example: 10.0.0.0/16) |
| **Subnet** | Slice of VPC (example: 10.0.1.0/24) |
| **IGW** | Door to internet (public access) |
| **NAT** | Outbound internet for private (inbound blocked) |
| **Route Table** | Directs traffic (where does IP X.X.X.X go?) |
| **Security Group** | Firewall rules (allow/deny ports) |
| **NACL** | Network-level firewall (subnet level) |

---

## Data Flow Example

```
Scenario: Lambda in private subnet calls external API

1. Lambda code: requests.get("https://api.example.com")
2. Lambda needs outbound internet
3. Route table says: "10.0.2.0/24 → use NAT"
4. Request goes to NAT gateway (in public subnet)
5. NAT replaces source IP: 10.0.2.10 → NAT IP
6. Request goes to Internet Gateway
7. Request exits VPC → reaches example.com
8. Response returns to NAT
9. NAT translates back: → 10.0.2.10
10. Response reaches Lambda

Result: Lambda can access external API (protected by NAT)
```

---

## Next Up

**→ [03-s3-vpc-integration.md](./03-s3-vpc-integration.md)** covers S3 VPC endpoints

