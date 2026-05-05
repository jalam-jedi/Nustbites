🍔 NUST Bites

**NUST Bites** is a modern, full-stack food ordering and delivery platform designed specifically for the NUST community. It streamlines ordering from various on-campus and nearby restaurants, providing a premium experience for students and staff.

---

## ✨ Features

### For Users
- **Premium UI/UX**: Modern, responsive design powered by Tailwind CSS and DaisyUI.
- **Multi-Restaurant Support**: Browse menus from various campus restaurants (KFC, etc.).
- **Smart Bucket (Cart)**: Add items with persistence and easy checkout.
- **Flexible Delivery**: Choose between Standard and Express delivery to campus locations.
- **Order Tracking**: Monitor order status from your personalized account dashboard.

### For Admins
- **New Admin Dashboard**: Centralized management of orders, riders, and restaurant content.
- **Role-Based Access**: Secure admin-only management views.
- **Payment Oversight**: Verify payments and manage order fulfillment.

---

## 🛠️ Tech Stack

- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: [Aiven MySQL](https://aiven.io/) (Managed Cloud Database)
- **Frontend**: HTML5, [Tailwind CSS](https://tailwindcss.com/), [DaisyUI](https://daisyui.com/)
- **Deployment**: Ready for [Vercel](https://vercel.com/) or [Render](https://render.com/)

---

## ⚙️ Quick Start

### 1. Installation
```bash
git clone https://github.com/jalam-jedi/Nustbites.git
cd Nustbites
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the root directory based on `.env.example`:
```env
DATABASE_URL=mysql+pymysql://avnadmin:PASSWORD@HOST:PORT/defaultdb
SECRET_KEY=your_secret_key
FLASK_DEBUG=False
```

### 3. Database Initialize
The project is configured for **Aiven MySQL**. Ensure `ca.pem` is in the root for SSL connectivity.
```bash
python -m flask --app run.py db upgrade
python adddata.py  # Seed initial menu data
```

### 4. Run Locally
```bash
python run.py
```
Access the app at `http://127.0.0.1:5000`.

---

## 🌍 Deployment

### Deploying to Vercel
1. Install [Vercel CLI](https://vercel.com/download).
2. Run `vercel` in the root directory.
3. Add environment variables in the Vercel dashboard.

---

## 📂 Project Structure
- `templates/`: Modernized Jinja2 HTML templates.
- `static/`: Compiled styles and premium assets.
- `models.py`: Database schema and relationships.
- `routes.py`: Core application logic and API endpoints.
- `setup.py`: Application factory and configuration.

---

## 🔐 Security
The project uses `python-dotenv` for secret management. **Never commit your `.env` file.**

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.
