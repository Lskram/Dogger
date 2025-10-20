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

เปิดเว็บ: http://localhost:8000 (ตอนนี้หน้าแรกเป็น Profile)

> หมายเหตุ: ใน Production ใช้ Whitenoise เสิร์ฟ static files แล้ว (collectstatic ทำในขั้นตอน build)

## ปรับแต่ง
- ปรับแต่ง Tailwind config: `tailwind.config.js` (กำหนด content path ไว้สำหรับ JIT)
- CSS entry: `assets/css/input.css` (เพิ่ม component/utility ตามต้องการ)
- Template หลัก: `templates/base.html`
- หน้าเริ่มต้น: `core/templates/core/index.html`

## หน้า (Pages)
- Profile: `/` และ `/profile/` — หน้าโปรไฟล์ (เป็นหน้าแรก)

## ENV ที่สำคัญ
- `DEBUG` (ค่าเริ่มต้น: 1) ตั้งเป็น `0` สำหรับ production
- `SECRET_KEY` ระบุค่าเองใน production
- `ALLOWED_HOSTS` กำหนด host ที่อนุญาตเมื่อ DEBUG=0 (เช่น `ALLOWED_HOSTS=example.com,www.example.com`)

## หมายเหตุด้าน dependencies
- Python: ดูที่ `requirements.txt`
- Node/Tailwind: ดูที่ `package.json`

หากต้องการความง่ายสุดใน Dev ก็ใช้เฉพาะ `docker-compose.yml` ให้ container tailwind ช่วย watch/build CSS และ container web รัน `runserver` พร้อม hot reload จาก volume ครับ

---

## Deploy (GHCR + Docker)

โปรเจ็คนี้มี GitHub Actions สำหรับ build และ push อิมเมจขึ้น GHCR อัตโนมัติเมื่อ push ไปยัง `main` อยู่ที่ `.github/workflows/docker-ghcr.yml`

ขั้นตอน:
- Push โค้ดขึ้น `main` แล้วดูสถานะที่ GitHub Actions
- ดึงอิมเมจไปเปิดที่เครื่อง/เซิร์ฟเวอร์สาธารณะได้ด้วย:

```
docker login ghcr.io -u <github_user> -p <github_token>
docker pull ghcr.io/<owner>/<repo>:latest
docker run -p 8000:8000 --env-file .env ghcr.io/<owner>/<repo>:latest
```

ตั้งค่า `.env` ให้ครบก่อน (ดู `.env.example`) เพื่อให้หน้าโปรไฟล์/สถานะใช้งานได้จริง


---

## เริ่มพัฒนาหน้าเว็บแบบทีละขั้น (มือใหม่ Docker + Django)

คำอธิบายสั้น: Docker คือโปรแกรมที่ช่วยรันแอปของเราใน “กล่อง” ที่พร้อมทุกอย่าง โดยโค้ดในโฟลเดอร์นี้ถูกผูกเข้ากับกล่อง ทำให้แก้ไฟล์แล้วเห็นผลทันทีเหมือนรัน Django ปกติ

1) เปิด Docker และสตาร์ทโปรเจ็ค

```
# เปิด Docker Desktop แล้วรอจนขึ้น Running
docker compose up --build
# หรือให้รันเบื้องหลัง
docker compose up -d --build
# ดู log ของ Django web
docker compose logs -f web
# ดู log ของ Tailwind watcher
docker compose logs -f tailwind
```

เปิดเว็บ: http://localhost:8000

2) แก้หน้าเพจที่มีอยู่ (เห็นผลเรียลไทม์)

- หน้าแรก: แก้ไฟล์ `core/templates/core/index.html`
- หน้า About: แก้ไฟล์ `core/templates/core/about.html`
- หน้า Contact: แก้ไฟล์ `core/templates/core/contact.html`
- Layout หลัก: แก้ไฟล์ `templates/base.html`
- สไตล์ Tailwind: แก้ไฟล์ `assets/css/input.css` (ระบบจะคอมไพล์ไปที่ `static/css/styles.css` อัตโนมัติ)

บันทึกไฟล์ แล้วรีเฟรชหน้าเว็บเพื่อดูผล (ไม่ต้อง rebuild image)

3) เพิ่มหน้าใหม่ทีละขั้น (ตัวอย่างเพจชื่อ "features")

- เพิ่ม view: `core/views.py`

```python
def features(request):
    return render(request, "core/features.html")
```

- ผูก URL: `core/urls.py`

```python
from .views import features  # เพิ่ม import

urlpatterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
    path("features/", features, name="features"),  # เส้นทางใหม่
]
```

- สร้างเทมเพลต: `core/templates/core/features.html`

```html
{% extends 'base.html' %}
{% block title %}Features{% endblock %}
{% block content %}
<h2 class="text-2xl font-bold">Features</h2>
<p class="mt-2 text-gray-600">รายละเอียดคุณสมบัติของเว็บเพจ</p>
{% endblock %}
```

- เพิ่มลิงก์ในเมนู: `templates/base.html` (ถ้าใช้ layout หลักนี้)

```html
<a href="{% url 'features' %}" class="px-2 py-1 rounded hover:bg-gray-100 {% with current=request.resolver_match.url_name %}{% if current == 'features' %}text-indigo-600 font-medium{% endif %}{% endwith %}">Features</a>
```

บันทึกไฟล์ แล้วเปิด http://localhost:8000/features/

4) ทำงานกับฐานข้อมูล (เวลามี Model ใหม่หรือแก้ไข Model)

```
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

สร้างผู้ใช้แอดมิน (ครั้งแรก):

```
docker compose run --rm web python manage.py createsuperuser
```

5) เมื่อไหร่ต้อง rebuild image?

- เปลี่ยน dependencies Python (`requirements.txt`) หรือ Node (`package.json`) → ใช้คำสั่ง

```
docker compose up --build
```

- แก้ไขไฟล์ Python/HTML/CSS/JS ทั่วไป → ไม่ต้อง build ใหม่ แค่บันทึกไฟล์แล้วรีเฟรชหน้าเว็บ

6) คำสั่งที่ใช้บ่อย

```
# รันและดู log สด (สองหน้าต่าง)
docker compose up --build
docker compose logs -f web
docker compose logs -f tailwind

# หยุดบริการทั้งหมด
docker compose down

# สถานะคอนเทนเนอร์
docker compose ps

# เข้าเชลล์ในคอนเทนเนอร์ web (ถ้าต้องการ)
docker compose exec web sh
```

7) แก้ปัญหาที่พบบ่อย

- CSS ไม่อัปเดต: ดู log `tailwind`; ถ้าจำเป็น สั่ง build ด้วย

```
docker compose exec tailwind sh -lc "npm run build"
```

- เปิดเว็บไม่ขึ้น: ตรวจสถานะด้วย `docker compose ps` และ log ของ `web`
- เปลี่ยนค่าตั้งค่า: ดู `config/settings.py` โดยเฉพาะ `DEBUG`, `ALLOWED_HOSTS`

---

## Discord OAuth (สำรวจและใช้งานได้จริงในโปรเจ็ค)

เราสร้าง endpoints สำหรับเชื่อมต่อ Discord OAuth2 ด้วย scope `identify` เพื่อดึงข้อมูลผู้ใช้

- เริ่มเชื่อมต่อ: `/auth/discord/login/`
- Callback: `/auth/discord/callback/`
- ดูข้อมูลผู้ใช้ที่เก็บในเซสชัน: `/auth/discord/me/`

ตั้งค่า ENV (อย่า commit ค่า Secret จริง). แนะนำสร้างไฟล์ `.env` จากตัวอย่าง:

```
cp .env.example .env
# แล้วแก้ไขค่าในไฟล์ .env ให้ถูกต้อง
```

```
DISCORD_CLIENT_ID=ใส่ค่าของคุณ
DISCORD_CLIENT_SECRET=ใส่ค่าของคุณ
DISCORD_REDIRECT_URI=http://localhost:8000/auth/discord/callback/
DISCORD_SCOPE=identify
```

Compose จะอ่านไฟล์ `.env` อัตโนมัติ และเราได้ตั้งค่า `env_file: .env` ไว้แล้วใน service `web`

URL Authorize ตัวอย่าง:

```
https://discord.com/oauth2/authorize?client_id=<CLIENT_ID>&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fdiscord%2Fcallback%2F&scope=identify
```

โฟลว์:
1) ผู้ใช้กด `/auth/discord/login/` → Redirect ไป Discord
2) Discord redirect กลับมาที่ callback พร้อม `code`
3) เซิร์ฟเวอร์แลก `code` เป็น token และเรียก `/users/@me` ได้ข้อมูลผู้ใช้ → เก็บไว้ในเซสชัน → Redirect ไปหน้าแรก

หมายเหตุการ build ถาวร:
- เมื่อ Docker Hub พร้อม ให้รัน `docker compose up -d --build` เพื่อรวม dependency (requests) เข้าอิมเมจถาวร

---

## สรุปงานที่ทำ และสิ่งที่ต้องทำต่อ (Checklist)

สิ่งที่พร้อมใช้งานแล้ว
- Django + Tailwind + Docker ครบ (Dev/Prod)
- หน้าแรก (Profile) แสดงรูปโปรไฟล์/ชื่อจาก Discord
  - ชื่อใช้ `username` (ถ้ามี discriminator และไม่ใช่ "0" จะแสดง `username#1234`)
  - สถานะออนไลน์: online/idle/dnd/offline (offline จะมีเวลาเป็นภาษาอังกฤษ เช่น `offline (2 hours 5 minutes)`)
- OAuth Discord (scope `identify`) + Owner token cache (OWNER_ID)
- Realtime presence (เลือกใช้):
  - Bot (Gateway) เขียนไฟล์ `runtime/presence.json`
  - หรือ Server Widget ของกิลด์ (ไม่ realtime เท่า bot)
- Health endpoint: `/healthz`
- VS Code tasks + docker-compose สำหรับ Dev
- CI: GitHub Actions build/push image ไป GHCR
- Render-ready: มี `render.yaml` (Blueprint) + Dockerfile bind `${PORT}`

สิ่งที่ต้องทำต่อ (เพื่อให้เพื่อนดูได้แบบถาวร)
1) Deploy บน Render (แนะนำ)
   - Render → New → Blueprint → เลือก repo นี้ → ใช้ `render.yaml` → Apply
   - ตั้ง ENV ของ service `dogger-web` (สำคัญ):
     - `DEBUG=0`
     - `SECRET_KEY=<สุ่มยาวๆ>`
     - `ALLOWED_HOSTS=<your-subdomain>.onrender.com`
     - `CSRF_TRUSTED_ORIGINS=https://<your-subdomain>.onrender.com`
     - `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`
     - `DISCORD_REDIRECT_URI=https://<your-subdomain>.onrender.com/auth/discord/callback/`
     - `DISCORD_SCOPE=identify`
     - `DISCORD_OWNER_ID=<YourUserID>`
     - `DISCORD_OWNER_ABOUT=ข้อความแนะนำตัว`
   - Deploy → ทดสอบ `/healthz` และหน้า `/`
   - อัปเดต Redirect URI ใน Discord Developer Portal ให้ตรงโดเมนจริง

2) (ตัวเลือก) เปิด Realtime Presence ด้วยบอท
   - เปิด intents (Presence + Server Members) ใน Discord Developer Portal
   - เชิญบอทเข้ากิลด์
   - ตั้ง ENV ของ worker `dogger-bot`:
     - `DISCORD_BOT_TOKEN`
     - `DISCORD_PRESENCE_USER_ID=<YourUserID>` (ไม่ใส่จะใช้ OWNER_ID)
     - `DISCORD_PRESENCE_FILE=runtime/presence.json`
     - `DISCORD_WIDGET_GUILD_ID=<GuildID>` (ถ้าจะ fallback Widget)
   - Deploy worker

3) แชร์ทันที (ชั่วคราว) แบบท่อจากเครื่อง
   - ใช้ ngrok/localtunnel เปิดพอร์ต `8000`
   - อัปเดต `DISCORD_REDIRECT_URI` ให้ตรง URL ชั่วคราว แล้ว restart `web`

Known issues / Next work
- Tailwind watcher ใน container บางครั้ง error; แก้ด้วย:
  - `docker compose stop tailwind && rm -rf node_modules && docker compose run --rm tailwind sh -lc "npm ci && npm run build"`
- ติดตั้ง `requests` ถาวรใน image: เมื่อ Docker Hub พร้อม ให้ `docker compose up -d --build` (image จะ bake ไลบรารี)
- Production ENV ต้องตั้งให้ครบ: `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DISCORD_REDIRECT_URI`
- บอท Presence: ต้องเปิด intents + เชิญบอท + ถ้ารีสตาร์ทบอท ตัวนับเวลา offline จะเริ่มใหม่ (จำย้อนหลังไม่ได้)
- Template โปรไฟล์มีสคริปต์/เอฟเฟกต์ยาว อาจพิจารณารีแฟคเตอร์หรือแยก component เพิ่มความอ่านง่าย
- Favicon ตอนนี้เป็น placeholder → ใส่ของจริงได้ที่ `static/favicon.ico`
- Security: อย่า commit secrets ลง repo; ถ้า token หลุดให้ rotate ทันที

Quick commands
- Dev: `docker compose up --build` → เปิด http://localhost:8000
- Migrate: `docker compose run --rm web python manage.py migrate`
- Tailwind build: `docker compose exec tailwind sh -lc "npm run build"`
- Prod local: `IMAGE=ghcr.io/<owner>/<repo>:latest docker compose -f docker-compose.prod.yml up -d`
