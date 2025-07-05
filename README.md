# Stay Screened And Safe

**Stay Screened And Safe** is a desktop security application that combines **Two-Factor Authentication (2FA)** and **facial recognition** to ensure robust user authentication. The application is built using **Python**, **PyQt5**, and **OpenCV**, and stores user data securely in a **MySQL** database.

---

## Features

* **User Registration and Login**
* **Two-Factor Authentication (2FA)** using TOTP and QR code
* **Face Recognition** using the DeepFace library
* Display of registered face images
* **Periodic Face Verification** every configurable interval
* GUI built with **PyQt5** and system tray integration
* Webcam integration via OpenCV

---

## Installation

### Requirements

Make sure the following Python packages are installed:

```bash
pip install pyqt5 pyotp qrcode opencv-python deepface mysql-connector-python numpy
```

You will also need:

* A **MySQL server** with the necessary tables created (`users`, `two_factor_data`, `face_data`)
* A working **webcam**
* Python 3.8+

---

## Database Schema

You'll need to create the following tables in your MySQL database:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE two_factor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    secret_key VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE face_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    image_path TEXT,
    image LONGTEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## How to Run

1. Clone this repository.
2. Make sure `mysqlconnect.py` contains your MySQL connection logic.
3. Run the main application:

```bash
python qtui.py
```

---

## Usage

* Register a new user (username, email, password)
* Generate and scan the QR code with a TOTP authenticator (like Google Authenticator)
* Register your face via webcam
* Login and perform face verification or fallback to 2FA code
* Configure how often face recognition should be repeated

---

## File Structure

* `qtui.py`: Main GUI logic and application control
* `two_factor_auth.py`: Handles 2FA generation, storage, and verification
* `faceVerified.py`: Handles face capture and verification
* `mysqlconnect.py`: (Not provided) Handles MySQL connection
* `sssLogo.png`: Icon used in system tray and GUI

---

## Notes

* Face recognition may prompt multiple retries in case of error.
* The application locks the session if 2FA fails (on Windows).
* Ensure your webcam has proper lighting for better recognition.

---

## License

MIT License

