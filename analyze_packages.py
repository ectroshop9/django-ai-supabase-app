import subprocess

packages = [
    ('Django==5.0.2', 'django'),
    ('djangorestframework==3.14.0', 'djangorestframework'),
    ('djangorestframework-simplejwt==5.3.0', 'djangorestframework_simplejwt'),
    ('Pillow==12.0.0', 'PIL'),
    ('boto3==1.34.0', 'boto3'),
    ('redis==7.1.0', 'redis'),
    ('django-redis==6.0.0', 'django_redis'),
    ('supabase==1.1.1', 'supabase'),
    ('psycopg2-binary==2.9.11', 'psycopg2'),
]

print("📦 تحليل حجم packages:")
total = 0
for pkg, name in packages:
    cmd = f"pip install --no-cache-dir --target /tmp/test {pkg} >/dev/null 2>&1"
    subprocess.run(cmd, shell=True)
    size_cmd = "du -sh /tmp/test 2>/dev/null | cut -f1"
    result = subprocess.run(size_cmd, shell=True, capture_output=True, text=True)
    size_str = result.stdout.strip().replace('M', '').replace('K', '')
    try:
        size = float(size_str) if 'M' in result.stdout else float(size_str)/1000
    except:
        size = 0
    total += size
    print(f"{name}: {size}MB")
    subprocess.run("rm -rf /tmp/test", shell=True)

print(f"\n🎯 المجموع: {total:.1f}MB")
print(f"📊 مع النظام: {total + 65:.1f}MB")
