# 🏔️ Kashmir Hotel Analytics

A modern hotel analytics dashboard built with **Streamlit** for hotel managers to track bookings, revenue, occupancy, and guest insights in real-time.

## Features

✨ **Key Features:**
- 📊 **Revenue Dashboard** - Track monthly revenue and trends
- 👥 **Guest Analytics** - Analyze guest origins and booking patterns
- 🛏️ **Room Management** - Monitor room type occupancy
- 📈 **Performance Metrics** - KPIs for bookings, revenue, and occupancy
- 🔐 **Multi-Hotel Support** - Secure login for multiple hotels
- 💾 **Cloud Integration** - Syncs data with Google Sheets
- 🌙 **Dark Mode** - Modern, sleek UI

## Tech Stack

- **Frontend**: Streamlit
- **Database**: Google Sheets
- **Charts**: Plotly
- **Authentication**: Session-based login

## Installation

### Prerequisites
- Python 3.8+
- Google Service Account credentials
- Google Sheets API enabled

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

3. **Set up Google Sheets credentials:**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Download service account JSON credentials
   - Save as `credentials.json` in the project root
   - OR add to Streamlit Cloud secrets as `gcp_service_account`

4. **Run the app:**
```bash
streamlit run app.py
```

## Google Sheets Structure

Your Google Sheet "Kashmir Hotel Bookings" should have:

### Sheet 1: Bookings
Columns: `Guest Name`, `Check-in`, `Check-out`, `Nights`, `Room Type`, `Guests`, `Source`, `Amount (₹)`, `Status`, `Notes`, `Hotel ID`

### Sheet 2: Hotels
Columns: `hotel_id`, `name`, `username`, `password`, `email`, `plan`

## Usage

1. **Login** with your hotel credentials
2. **View Dashboard** - See all your analytics
3. **Select Season** - Filter by season (Winter, Spring, Summer, Autumn)
4. **Refresh Data** - Update bookings from Google Sheets
5. **Logout** - Secure session end

## File Structure

```
kashmir-hotel-analytics/
├── app.py              # Main dashboard app
├── login.py            # Login page component
├── sheets_db.py        # Google Sheets integration
├── style.py            # UI styling
├── requirements.txt    # Python dependencies
├── credentials.json    # Google Service Account (local only)
└── README.md           # This file
```

## Environment Variables (Streamlit Cloud)

For Streamlit Cloud deployment, add to `.streamlit/secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

## Troubleshooting

### "Spreadsheet not found"
- Verify the sheet name is exactly "Kashmir Hotel Bookings"
- Ensure service account has access to the sheet
- Check credentials permissions

### "Hotel ID column not found"
- Verify bookings sheet has "Hotel ID" column
- Check column spelling and case sensitivity

### Google Sheets connection errors
- Verify credentials.json is in the root directory
- Check Google Sheets API is enabled in Cloud Console
- Ensure service account has Editor access to the sheet

## Deployment

### Streamlit Cloud
```bash
git push origin main
# Then connect your repo at https://share.streamlit.io
```

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
