# 🏔️ Kashmir Hotel Analytics

A modern hotel analytics dashboard built with **Streamlit** for hotel managers to track bookings, revenue, occupancy, and guest insights in real-time.

## Features

✨ **Key Features:**
- 📊 **Revenue Dashboard** - Track monthly revenue and trends
- 👥 **Guest Analytics** - Analyze guest origins and booking patterns
- 🛏️ **Room Management** - Monitor room type occupancy
- 📈 **Performance Metrics** - KPIs for bookings, revenue, and occupancy
- 🔐 **Multi-Hotel Support** - Secure login for multiple hotels
- 💾 **Cloud Integration** - Powered by Firebase Firestore
- 🌙 **Dark Mode** - Modern, sleek UI

## Tech Stack

- **Frontend**: Streamlit
- **Database**: Firebase Firestore
- **Charts**: Plotly
- **Authentication**: Session-based login

## Installation

### Prerequisites
- Python 3.8+
* Firebase Service Account credentials

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yousufshahzaman1992-beep/kashmir-hotel-analytics.git
cd kashmir-hotel-analytics
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Firebase credentials:**
   - Create a Firebase project
   - Generate a New Private Key from Project Settings > Service Accounts
   - Save as `firebase_credentials.json` in the project root
   - OR add to Streamlit Cloud secrets under the `[firebase]` section

4. **Run the app:**
```bash
streamlit run app.py
```

## Usage

1. **Login** with your hotel credentials
2. **View Dashboard** - See all your analytics
3. **Select Season** - Filter by season (Winter, Spring, Summer, Autumn)
4. **Refresh Data** - Sync latest records from Firebase
5. **Logout** - Secure session end

## File Structure

```
kashmir-hotel-analytics/
├── app.py              # Main dashboard app
├── login.py            # Login page component
├── sheets_db.py        # Firebase Firestore integration
├── style.py            # UI styling
├── requirements.txt    # Python dependencies
├── firebase_credentials.json # Firebase Service Account (local only)
└── README.md           # This file
```

## Environment Variables (Streamlit Cloud)

For Streamlit Cloud deployment, add your Firebase service account details to the Secrets management console under the `[firebase]` section:
```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
...
```

## Troubleshooting

### "Firebase connection failed"
- Verify `firebase_credentials.json` is in the root directory.
- Check if the Firebase project is active in the Google Cloud Console.
- Ensure your Streamlit Cloud Secrets match the structure in `st.secrets`.

### "Data not updating"
- Click the **Refresh Data** button in the sidebar.
- Check your Firestore rules to ensure read/write permissions are correct.

### Other Platforms
Streamlit can be deployed on:
- Heroku
- AWS
- Google Cloud Run
- Azure

## Security Notes

⚠️ **Important:**
- Never commit `credentials.json` to version control (add to `.gitignore`)
- Use strong passwords for hotel accounts
- Store credentials in Streamlit Cloud secrets, not in code
- Passwords are stored in plain text in Google Sheets (consider hashing for production)

## Future Enhancements

- [ ] Add booking management (edit/delete)
- [ ] Export reports as PDF
- [ ] Email notifications for new bookings
- [ ] Advanced filtering and search
- [ ] Payment integration
- [ ] SMS alerts
- [ ] Multi-language support

## Contact

📧 **Email:** Kashmirhotels6@gmail.com  
📱 **WhatsApp:** +91 8491828292

## License

This project is private and proprietary.

---

**Made with ❤️ for Kashmir Hotels**
