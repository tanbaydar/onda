# Deploy Danced to one AWS EC2 instance

This runbook deploys Danced to an ARM64 Ubuntu `t4g.small` with Docker
Compose. Caddy terminates TLS and serves the React build, Django static files,
and uploaded media. Django runs behind Caddy with Gunicorn, and MySQL is
reachable only on the private Compose network.

Replace these placeholders before using commands:

- `DANCED_DOMAIN`: the real application hostname, such as `danced.example.com`.
- `YOUR_IP/32`: your current public IPv4 address in CIDR notation.
- `YOUR_BUCKET_NAME`: a globally unique S3 bucket name.
- `YOUR_REGION`: the AWS region containing the instance and bucket.
- `YOUR_REPOSITORY_URL`: the HTTPS or SSH Git clone URL.
- `YOUR_BILLING_THRESHOLD`: the monthly USD threshold for the billing alarm.

The frontend is served by Caddy rather than Django/WhiteNoise. The React app is
already a static Vite build, and Caddy is already required for TLS and reverse
proxying. Serving it there avoids another Python dependency and keeps all public
file delivery at the edge process.

## 1. Create the backup bucket

1. Open **AWS Console → S3 → General purpose buckets → Create bucket**.
2. Select `YOUR_REGION` and enter `YOUR_BUCKET_NAME`.
3. Leave **Block all public access** enabled. Do not add a public bucket policy.
4. Leave versioning disabled; the timestamped dumps are distinct objects.
5. Enable default encryption with **SSE-S3** and create the bucket.
6. Open the bucket → **Management → Lifecycle rules → Create lifecycle rule**.
7. Name it `expire-danced-backups`, apply it to all objects, acknowledge that
   scope, select **Expire current versions of objects**, enter `30` days, and
   create the rule.

Verify in **S3 → bucket → Properties** that default encryption is enabled and in
**Management** that `expire-danced-backups` is enabled with a 30-day expiration.

## 2. Create a least-privilege EC2 role

1. Open **IAM → Policies → Create policy → JSON** and enter the following,
   replacing both bucket placeholders:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "WriteDancedBackupsOnly",
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:AbortMultipartUpload"
         ],
         "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
       }
     ]
   }
   ```

2. Choose **Next**, name it `DancedBackupWriter`, and create it.
3. Open **IAM → Roles → Create role → AWS service → EC2**.
4. Attach `DancedBackupWriter`, name the role `DancedEC2Role`, and create it.

Verify the role's **Trust relationships** allows `ec2.amazonaws.com`, and its
permissions contain only the bucket-scoped policy above.

## 3. Create the security group

1. Open **EC2 → Network & Security → Security Groups → Create security group**.
2. Name it `danced-web`, select the instance VPC, and add inbound rules:

   | Type | Port | Source |
   |---|---:|---|
   | SSH | 22 | `YOUR_IP/32` |
   | HTTP | 80 | `0.0.0.0/0` and `::/0` |
   | HTTPS | 443 | `0.0.0.0/0` and `::/0` |

3. Leave the default allow-all outbound rule and create the group.

Do not open MySQL port 3306. Verify the security group's inbound-rule table has
only the rules above.

## 4. Launch the ARM64 Ubuntu instance

1. Open **EC2 → Instances → Launch instances**.
2. Name it `danced-production`.
3. Choose the current Ubuntu Server LTS AMI whose architecture is **64-bit
   (Arm)** / `arm64`.
4. Choose instance type `t4g.small`.
5. Select or create an SSH key pair and store its private key securely.
6. Under network settings, select the `danced-web` security group. Ensure the
   instance receives a public IPv4 address, or associate an Elastic IP after
   launch so DNS does not change after a stop/start.
7. Under **Advanced details → IAM instance profile**, select `DancedEC2Role`.
8. Use at least a 20 GiB encrypted `gp3` root volume, then launch.

After the instance is running, select it and verify:

- **Details → Instance type** is `t4g.small`.
- **Details → Platform details** is Ubuntu and architecture is `arm64`.
- **Security → IAM role** is `DancedEC2Role`.
- **Security → Inbound rules** matches step 3.

Connect from your workstation:

```sh
chmod 600 /path/to/key.pem
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
```

On the instance, verify the architecture:

```sh
uname -m
```

Expected: `aarch64`.

## 5. Install Docker, Compose, Git, AWS CLI, and flock

Run these commands on the instance. They use Docker's official Ubuntu apt
repository and work on ARM64:

```sh
sudo apt-get update
sudo apt-get install -y ca-certificates curl git awscli util-linux
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and reconnect so group membership refreshes:

```sh
exit
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
```

Verify each prerequisite:

```sh
docker version
docker compose version
git --version
aws --version
flock --version
sudo systemctl is-active docker
aws sts get-caller-identity
```

The final command should identify the attached `DancedEC2Role`; no access keys
belong on the server.

## 6. Clone the repository and configure production

Clone into the path used by the cron examples:

```sh
cd /home/ubuntu
git clone YOUR_REPOSITORY_URL danced
cd /home/ubuntu/danced
git switch main
cp .env.example .env
chmod 600 .env
openssl rand -base64 48
openssl rand -base64 36
openssl rand -base64 36
nano .env
```

Use the three generated values for `DJANGO_SECRET_KEY`,
`DANCED_DB_PASSWORD`, and `DANCED_DB_ROOT_PASSWORD`, respectively. Set:

```dotenv
DANCED_DOMAIN=DANCED_DOMAIN
CADDY_ACME_EMAIL=YOUR_REAL_EMAIL
DJANGO_SECRET_KEY=GENERATED_SECRET
DJANGO_DEBUG=false
EMAIL_VERIFICATION_ENFORCED=false
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DJANGO_DEFAULT_FROM_EMAIL=noreply@DANCED_DOMAIN
DANCED_DB_NAME=danced
DANCED_DB_USER=danced
DANCED_DB_PASSWORD=GENERATED_APP_DATABASE_PASSWORD
DANCED_DB_ROOT_PASSWORD=GENERATED_DISTINCT_ROOT_PASSWORD
DANCED_DB_HOST=db
DANCED_DB_PORT=3306
BACKUP_BUCKET=s3://YOUR_BUCKET_NAME/danced
AWS_REGION=YOUR_REGION
```

Verify permissions and required keys without printing secrets:

```sh
stat -c '%a %n' .env
grep -E '^(DANCED_DOMAIN|DANCED_DB_NAME|DANCED_DB_USER|BACKUP_BUCKET|AWS_REGION)=' .env
docker compose config --quiet
```

Expected permissions are `600`; Compose must exit zero.

## 7. Run the first deployment

The first certificate cannot be issued until the hostname resolves to this
instance. It is still safe to build and start the stack first:

```sh
cd /home/ubuntu/danced
./deploy.sh
docker compose ps
docker compose logs --tail=100 web
docker compose logs --tail=100 caddy
```

The first build can take several minutes on a `t4g.small`. `db` and `web` should
be healthy. Caddy may temporarily log DNS/certificate errors until step 8.

Verify Django from inside its private network:

```sh
docker compose exec -T web python manage.py check --deploy
docker compose exec -T web python manage.py showmigrations
curl -I -H 'Host: DANCED_DOMAIN' http://127.0.0.1
```

`showmigrations` should show `[X]` for every migration. The HTTP response should
include `X-Robots-Tag: noindex` (it may redirect to HTTPS).

## 8. Point DNS at the instance

In your DNS provider—or **Route 53 → Hosted zones → your zone → Create
record**—create an `A` record for `DANCED_DOMAIN` pointing to the instance's
Elastic/public IPv4 address. Use a 300-second TTL during rollout. If the
instance has IPv6 connectivity and a stable IPv6 address, add the corresponding
`AAAA` record; otherwise do not create one.

Verify publicly from your workstation:

```sh
dig +short DANCED_DOMAIN A
```

Expected: the instance's public IPv4 address.

## 9. Verify automatic HTTPS and the application

Caddy obtains a public certificate automatically after DNS and ports 80/443 are
reachable. From your workstation run:

```sh
curl -fsSIL https://DANCED_DOMAIN
curl -fsSI https://DANCED_DOMAIN/api/cities/
```

Both responses must be HTTPS without certificate warnings and include:

```text
X-Robots-Tag: noindex
```

Open `https://DANCED_DOMAIN` in a private browser window. Verify Discover loads,
an event detail opens, registration/login works with a disposable account, and
the browser reports a valid certificate. On the server, confirm all services:

```sh
cd /home/ubuntu/danced
docker compose ps
docker compose logs --tail=100 caddy
```

## 10. Verify a backup, then install both cron jobs

First run a supervised backup:

```sh
cd /home/ubuntu/danced
./backup.sh
latest_dump=$(find backups -type f -name 'danced-*.sql.gz' -print | sort | tail -1)
gzip -t "$latest_dump"
gzip -dc "$latest_dump" | sed -n '1,20p'
```

The dump must pass `gzip -t` and begin with a MySQL dump header. Because the
instance role is deliberately write-only, verify the uploaded object through
**S3 → YOUR_BUCKET_NAME → danced** in the AWS console; the instance cannot read
or list the bucket.

Create durable log and lock locations:

```sh
mkdir -p /home/ubuntu/danced/logs
sudo install -d -o ubuntu -g ubuntu /var/lock/danced
crontab -e
```

Install exactly these two entries (UTC on a default Ubuntu host):

```cron
15 2 * * * /usr/bin/flock -n /var/lock/danced/backup.lock /home/ubuntu/danced/backup.sh >> /home/ubuntu/danced/logs/backup.log 2>&1
15 3 * * * /usr/bin/flock -n /var/lock/danced/sync-ra.lock /usr/bin/docker compose --project-directory /home/ubuntu/danced exec -T web python manage.py sync_ra >> /home/ubuntu/danced/logs/sync-ra.log 2>&1
```

The independent locks prevent overlap within each job type. The backup runs one
hour before ingestion. Do not suppress stderr: sync failures are operator alarms.

Verify cron saved the exact entries and that each lockable command can execute:

```sh
crontab -l
/usr/bin/flock -n /var/lock/danced/backup.lock /home/ubuntu/danced/backup.sh
/usr/bin/flock -n /var/lock/danced/sync-ra.lock /usr/bin/docker compose --project-directory /home/ubuntu/danced exec -T web python manage.py sync_ra
tail -n 100 /home/ubuntu/danced/logs/backup.log
tail -n 100 /home/ubuntu/danced/logs/sync-ra.log
```

The sync makes live RA requests and may take time, so run that verification only
when an operator-supervised production sync is appropriate.

## 11. Create a CloudWatch billing alarm

1. Open **Billing and Cost Management → Billing preferences → Alert
   preferences → Edit**.
2. Enable **Receive CloudWatch Billing Alerts** and save. Initial metrics can
   take about 15 minutes to appear.
3. Switch the console region to **US East (N. Virginia) / us-east-1**; billing
   metrics live there even if the instance does not.
4. Open **CloudWatch → Alarms → All alarms → Create alarm → Select metric →
   Billing → Total Estimated Charge**.
5. Select `EstimatedCharges` in USD. Choose **Maximum**, period **6 hours**,
   static threshold **Greater than `YOUR_BILLING_THRESHOLD`**, one datapoint out
   of one, and treat missing data as missing.
6. Create or select an SNS topic with your email address, finish the alarm, then
   confirm the SNS subscription from the email AWS sends.
7. Name the alarm `DancedMonthlyEstimatedCharges`.

Verify **CloudWatch → Alarms → All alarms** shows the alarm as `OK` or
`Insufficient data`, not `Configuration error`, and **SNS → Subscriptions** shows
the email subscription as `Confirmed`.

## 12. Routine deployments and recovery checks

For each approved release:

```sh
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
cd /home/ubuntu/danced
./deploy.sh
docker compose ps
curl -fsSI https://DANCED_DOMAIN/api/cities/
```

`deploy.sh` performs a fast-forward-only pull, rebuilds images, starts services,
runs migrations, and prunes unused images. It never removes volumes. Do not run
`docker compose down -v`; `-v` deletes the database and media volumes.

To confirm the database volume survives an ordinary restart:

```sh
docker compose down
docker compose up -d
docker compose ps
```

The named `mysql_data` volume remains. Confirm application data is still visible
after services return healthy.
