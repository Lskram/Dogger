# Dogger – Django + Tailwind + Docker (Simple Template)

โปรเจ็คตัวอย่าง Django + Tailwind CSS พร้อม Docker และ docker-compose สำหรับใช้งานทั้ง Development และ Build แบบ Production อย่างง่าย

## โครงสร้างหลัก
- Django project: `config/` + `manage.py`
- App เริ่มต้น: `core/` (มีหน้า Home)
- เทมเพลต: `templates/` และ `core/templates/`
- Tailwind: `assets/css/input.css` -> build ออกที่ `static/css/styles.css`
- Dockerfile แบบ multi-stage (Node สร้าง CSS แล้วค่อยไป Python)
- `docker-compose.yml` สำหรับ Dev (แยก service web กับ tailwind watcher)

## เริ่มต้น (Dev)
1) สร้างไฟล์ CSS ด้วย Tailwind แบบ watch และรัน Django พร้อมกัน

```
# สตาร์ททั้งสองบริการ (ครั้งแรกอาจใช้เวลาติดตั้ง dependencies)
docker compose up --build
```

2) เปิดเว็บ: http://localhost:8000

3) รัน migrations (ครั้งแรกเท่านั้น):
```
docker compose run --rm web python manage.py migrate
```

ถ้าต้องการ user สำหรับ admin:
```
docker compose run --rm web python manage.py createsuperuser
```

หยุดบริการ: กด Ctrl+C หรือ `docker compose down`

## Build แบบ Production
สร้างอิมเมจที่รวม static files และรันผ่าน Gunicorn

```
docker build -t django-tailwind-app .
docker run -p 8000:8000 --env DEBUG=0 django-tailwind-app
```

เปิดเว็บ: http://localhost:8000

> หมายเหตุ: ใน Production ใช้ Whitenoise เสิร์ฟ static files แล้ว (collectstatic ทำในขั้นตอน build)

## ปรับแต่ง
- ปรับแต่ง Tailwind config: `tailwind.config.js` (กำหนด content path ไว้สำหรับ JIT)
- CSS entry: `assets/css/input.css` (เพิ่ม component/utility ตามต้องการ)
- Template หลัก: `templates/base.html`
- หน้าเริ่มต้น: `core/templates/core/index.html`

## หน้า (Pages)
- Home: `/` — หน้าเริ่มต้นพร้อมตัวอย่าง Tailwind
- About: `/about/` — หน้าแนะนำโปรเจ็คดีไซน์สวยด้วย gradient + cards

## ENV ที่สำคัญ
- `DEBUG` (ค่าเริ่มต้น: 1) ตั้งเป็น `0` สำหรับ production
- `SECRET_KEY` ระบุค่าเองใน production
- `ALLOWED_HOSTS` กำหนด host ที่อนุญาตเมื่อ DEBUG=0 (เช่น `ALLOWED_HOSTS=example.com,www.example.com`)

## หมายเหตุด้าน dependencies
- Python: ดูที่ `requirements.txt`
- Node/Tailwind: ดูที่ `package.json`

หากต้องการความง่ายสุดใน Dev ก็ใช้เฉพาะ `docker-compose.yml` ให้ container tailwind ช่วย watch/build CSS และ container web รัน `runserver` พร้อม hot reload จาก volume ครับ
