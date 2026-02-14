# Chapter 1: IAM Identity

## Teori Singkat

### IAM User vs IAM Role
- IAM User: identitas untuk manusia atau aplikasi yang punya kredensial tetap.
- IAM Role: identitas sementara yang di-assume oleh service, tidak punya kredensial permanen.

### Kenapa Access Key untuk Script Scraper?
Script scraper berjalan di luar AWS dan butuh akses programatik. Access key memberikan akses API ke AWS (misalnya S3 atau CloudWatch). Gunakan user khusus dengan permission minimal.

---

## Hands-on

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Setelah apply, catat output `access_key_id` dan `secret_access_key`.

---

## Security Tip

Output sensitif disembunyikan. Untuk melihat nilainya:

```bash
terraform output -json
```

Cari field `secret_access_key` di JSON output.
