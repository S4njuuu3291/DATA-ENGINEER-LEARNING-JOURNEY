# 04. Network Security Patterns & Data Pipelines

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** Security groups + NACLs + private subnets = defense in depth

---

## Security Groups (Stateful Firewall)

### Inbound Rules (Incoming Traffic)

```
Default: Deny all inbound (deny by default)

Example: Allow SSH from office
┌─────────────────────────┐
│ Inbound Rule            │
├─────────────────────────┤
│ Protocol: TCP           │
│ Port: 22 (SSH)          │
│ Source: 203.0.113.0/24  │
│ Action: Allow           │
└─────────────────────────┘
```

### Outbound Rules (Outgoing Traffic)

```
Default: Allow all outbound (allow by default)

Example: Deny all outbound (more restrictive)
┌─────────────────────────┐
│ Outbound Rule           │
├─────────────────────────┤
│ Protocol: All           │
│ Port: All               │
│ Destination: Anywhere   │
│ Action: Deny            │
└─────────────────────────┘
```

### Creating Security Groups

```bash
# Create security group
aws ec2 create-security-group \
  --group-name data-pipeline-sg \
  --description "Security group for data pipeline" \
  --vpc-id vpc-12345678

# Allow Lambda to call API (outbound)
aws ec2 authorize-security-group-egress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow RDS queries from Lambda (inbound on RDS side)
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds \
  --protocol tcp \
  --port 5432 \
  --source-group-id sg-lambda
```

---

## NACLs (Network ACLs)

### Stateless Firewall (Subnet-level)

```
Security Group: Instance-level (attached to instance)
NACL: Subnet-level (applies to all resources in subnet)

Key difference:
- Security Group: Stateful (response auto-allowed)
- NACL: Stateless (inbound AND outbound rules required)

Example:
Request: 203.0.113.45:1024 → 10.0.1.10:443
Response: 10.0.1.10:443 → 203.0.113.45:1024

Security Group:
- Inbound 443: ✅ Allow
- Outbound > 1024: ✅ Auto-allowed (stateful)

NACL:
- Inbound 443: ✅ Allow
- Outbound > 1024: Explicitly allow needed
```

### When to Use NACLs

```
Usually security groups enough.
Use NACLs when:
- Need subnet-wide blocking (don't need instance granularity)
- Want explicit deny rules
- Need stateless behavior
```

---

## Typical Data Pipeline Security Design

### 3-Tier Pattern (DMZ)

```
┌───────────────────────────────────────────┐
│  Internet                                  │
│  Attackers ↓                              │
└───────────────────────────────────────────┘
         ↓↑ Internet Gateway
┌───────────────────────────────────────────┐
│  PUBLIC SUBNET (DMZ)                      │
│  ┌─────────────────────────────────────┐  │
│  │ Bastion Host (SSH entry point)      │  │
│  │ - Security group: Allow SSH port 22 │  │
│  │ - From: Office IPs only             │  │
│  └─────────────────────────────────────┘  │
│  ┌─────────────────────────────────────┐  │
│  │ NAT Gateway                         │  │
│  │ Enables private subnet → internet   │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
         ↓↑ Private route
┌───────────────────────────────────────────┐
│ PRIVATE SUBNET (Application)              │
│ ┌─────────────────────────────────────┐  │
│ │ Lambda Function                     │  │
│ │ - Security group: Allow 443         │  │
│ │ - Outbound to: NAT gateway          │  │
│ │ - Inbound from: Nowhere (no ssh)    │  │
│ └─────────────────────────────────────┘  │
│ ┌─────────────────────────────────────┐  │
│ │ Glue Job                            │  │
│ │ - Runs in private subnet            │  │
│ │ - No direct internet access         │  │
│ └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
         ↓↑ VPC Endpoint
┌───────────────────────────────────────────┐
│ PRIVATE SUBNET (Data)                     │
│ ┌─────────────────────────────────────┐  │
│ │ S3 (via VPC endpoint)               │  │
│ │ - No internet access needed         │  │
│ │ - Private routing only              │  │
│ └─────────────────────────────────────┘  │
│ ┌─────────────────────────────────────┐  │
│ │ RDS Database                        │  │
│ │ - Security group: Allow MySQL 3306  │  │
│ │ - From: Lambda security group only  │  │
│ └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

---

## Complete Data Pipeline Flow

### Request Path: User → Dashboard

```
1. User (office IP): Accesses dashboard
   ↓
2. Internet Gateway: Routes to load balancer
   ↓
3. Public Subnet: Load balancer (security group: allow 443)
   ↓
4. Private Subnet: Application server
   ↓
5. VPC Endpoint: Routes to S3 (private)
   ↓
6. S3: Serves data via private network
   ↓
7. Response comes back

Security:
✅ Direct S3 access only via VPC endpoint
✅ Data never touches internet
✅ Application hidden (unreachable from internet)
✅ Access logged (CloudTrail)
```

---

## Common Patterns

### Pattern 1: API on Private RDS

```
Lambda -(ask RDS)→ RDS in private subnet

Security Group (Lambda):
- Outbound: 5432 to RDS SG

Security Group (RDS):
- Inbound: 5432 from Lambda SG
```

### Pattern 2: Scheduled Job with External API

```
Lambda -(call API)→ External Service -(stored in)→ S3

Lambda Security Group:
- Outbound: 443 (HTTPS) to 0.0.0.0/0 (internet)
  └─ Actually route through NAT (in public subnet)

NAT Gateway:
- Translates Lambda IP → NAT IP
- Internet sees: NAT IP (Lambda's real IP hidden)

Result:
- Lambda can call external API (protected by NAT)
- Lambda remains unreachable from internet
```

---

## Security Checklist

- [ ] **Default deny:** Inbound = deny (add only what needed)
- [ ] **Specific CIDR:** Use office IPs (not 0.0.0.0/0)
- [ ] **Private data:** In private subnets (not public)
- [ ] **VPC endpoints:** For S3, DynamoDB (no internet)
- [ ] **NAT for external:** Private resources calling internet APIs
- [ ] **Least privilege:** Minimum security groups needed
- [ ] **Logging:** VPC Flow Logs (debug security issues)
- [ ] **Multi-AZ:** Resources across availability zones

---

## Debugging Network Issues

###  VPC Flow Logs

```bash
# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type cloudwatch-logs

# Analyze logs
aws logs filter-log-events \
  --log-group-name /aws/vpc/vpc-flow-logs \
  --filter-pattern "REJECT"

# Shows rejected traffic (debugging connectivity)
```

### Common Issues & Fixes

```
Issue: Lambda can't reach S3
Fix: Check route table has VPC endpoint, endpoint policy allows

Issue: Lambda can't call external API
Fix: Add NAT gateway, Lambda security group allows outbound 443

Issue: RDS rejects connection
Fix: Check RDS security group allows inbound from Lambda SG

Issue: Bastion can't SSH to private instance
Fix: Private instance SG needs inbound 22 from Bastion SG
```

---

## Key Takeaways

1. **Security Groups** = Instance-level firewall (allow/deny)
2. **NACLs** = Subnet-level firewall (stateless)
3. **VPC Endpoints** = Private access to AWS services
4. **NAT Gateway** = Outbound internet for private resources
5. **Defense in depth** = Multiple layers of security

---

## Next Up

You've completed VPC theory! Now:

**→ [../exercises/](../../exercises/)** Practice with 14 hands-on exercises

