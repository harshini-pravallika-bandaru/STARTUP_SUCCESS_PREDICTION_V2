# Startup Success Prediction Platform

## Local Development
1. Create virtual environment: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Run: `python app.py` (debug mode, port 5000)

## AWS EC2 Deployment (Free Tier t2.micro)

1. Launch Ubuntu 22.04 EC2 instance, open ports 22 (SSH), 80 (HTTP), 5000 (optional).
2. SSH into instance.
3. Update and install dependencies:
   sudo apt update && sudo apt install -y python3-pip python3-venv nginx
4. Copy project files to `/home/ubuntu/startup_platform/` (e.g., using `scp` or `git clone`).
5. Set up virtual environment and install requirements:
cd /home/ubuntu/startup_platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
6. Test manually: `python app.py` (should see "Running on http://0.0.0.0:5000").
7. Set up systemd service:
sudo cp deploy/startup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable startup
sudo systemctl start startup
8. Configure Nginx:
sudo cp deploy/nginx.conf /etc/nginx/sites-available/startup
sudo ln -s /etc/nginx/sites-available/startup /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
9. Your app is now live at `http://<EC2_PUBLIC_IP>`.

## Notes
- The database is SQLite (file-based). For production, switch to PostgreSQL (AWS RDS free tier).
- Change `secret_key` in `app.py` to a random secret.
- Ensure `rf_model.pkl` and `scaler.pkl` are present in the root directory.
