# Controllerhub

Controllerhub is an online gaming store built with Django. It features a modern storefront, product catalog, shopping cart, and more.

## Features

- Browse premium gaming gear (keyboards, mice, audio, monitors, chairs, PC components)
- Product cards with badges and animated effects
- Shopping cart functionality
- Responsive design
- Modern UI with custom CSS animations

## Project Structure

```
C:.
│   .gitignore
│   mypy.ini
│   Pipfile
│   README.md
│   requirements.txt
│
├───ecommerce
│   │   .coverage
│   │   db.sqlite3
│   │   manage.py
│   │   Pipfile
│   │   Pipfile.lock
│   │
│   ├───ecommerce
│   │       asgi.py
│   │       settings.py
│   │       urls.py
│   │       wsgi.py
│   │       __init__.py
│   │   
│   │
│   ├───media
│   │   └───uploads
│   │       └───products
│   │               Aeron-chair-Brooklyn-Museum_from-wiki-no-bg.png
│   │               Aeron-chair-Brooklyn-Museum_from-wiki-no-bg_xuS7ZX5.png
│   │               Aeron-chair-Brooklyn-Museum_from-wiki.jpg
│   │               gaming-chair_from-amazon-listing-no-bg.png
│   │               gaming-chair_from-amazon-listing-no-bg_vvoJqry.png
│   │               gaming-chair_from-amazon-listing.jpg
│   │               Scorpion-Chair_from-h3-wiki-fandom-no-bg.png
│   │               Scorpion-Chair_from-h3-wiki-fandom-no-bg_bkWVoeZ.png
│   │               Scorpion-Chair_from-h3-wiki-fandom.webp
│   │               standard-keyboard_from-wiki-no-bg.png
│   │               standard-keyboard_from-wiki-no-bg_gmxkANN.png
│   │               standard-keyboard_from-wiki-no-bg_vN3009w.png
│   │               standard-keyboard_from-wiki.jpg
│   │               standard-mouse_from-wiki-no-bg.png
│   │               standard-mouse_from-wiki-no-bg_Px8z5FV.png
│   │               standard-mouse_from-wiki.jpg
│   │
│   ├───static
│   │   ├───assets
│   │   ├───css
│   │   │       styles.css
│   │   │
│   │   └───js
│   │           script.js
│   │
│   └───storefront
│       │   admin.py
│       │   apps.py
│       │   models.py
│       │   tests.py
│       │   urls.py
│       │   views.py
│       │   __init__.py
│       │
│       └───templates
│            │   about.html
│            │   account.html
│            │   base.html
│            │   cart.html
│            │   checkout.html
│            │   checkoutsuccess.html
│            │   contact.html
│            │   index.html
│            │   product.html
│            │   products.html
│            │
│            └───registration
│                   login.html   
│
└───pipelines
    │   build.yml
    │
    └───template
            pipeline.yml
```

## Getting Started

1. **Clone the repository:**
   ```
   git clone https://github.com/MasterGitExpert/Controllerhub.git
   cd controllerhub
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```
   python manage.py migrate
   ```

4. **Run the development server:**
   ```
   python manage.py runserver
   ```

5. **Access the site:**
   Open [http://localhost:8000](http://localhost:8000) in your browser.

## Task Distribution

- Home Feature @martymash
- Product Catalogue Feature @MasterGitExpert
- Individual Product Feature @MasterGitExpert
  - @MasterGitExpert Products Tests From line 194
- About Feature @martymash
- Contact Feature @martymash
- Login/ Account Feature @ayden8383
- Cart Feature @scaraliyose
- Checkout Feature @scaraliyose
- Review Management Feature @ayden8383
- Admin Feature @MasterGitExpert

## Serving uploaded media on Azure App Service (no external storage)

By default, production deployments use external storage (recommended). If you prefer to serve media files from the App Service filesystem (not recommended for scale but fine for small projects), follow these steps:

1. Ensure media files are present under `ecommerce/media/` in the repository before the pipeline runs, or are written to a persistent path at runtime.
2. Configure the following Application Settings in Azure (Portal or CLI) for your Web App:

   - `DJANGO_SERVE_MEDIA` = `1`
   - `DJANGO_MEDIA_ROOT` = `/home/site/wwwroot/media`
   - `DJANGO_SETTINGS_MODULE` = `ecommerce.settings`
   - `DJANGO_SECRET_KEY` = (a secure value)
   - `DJANGO_DEBUG` = `False`

3. In the pipeline we set `DJANGO_MEDIA_ROOT=/home/site/wwwroot/media` so the deployed app will use Azure's writable path for media. When `DJANGO_SERVE_MEDIA` is enabled the app will add URL patterns to serve media.

Caveats:

- The built-in Django media serving is not optimized for high traffic. For a production-ready setup, consider using Azure Blob Storage or another dedicated object store.
- Files under the app's package may be replaced on deployment. If you want uploads to persist across deployments, write them to `/home` (which is persisted across restarts) or an external storage service.


