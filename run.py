

from app import create_app
from flask_migrate import upgrade
from app.utils import detect_suspicious_transactions
from app.seed import seedData
from app.models import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        upgrade()

        seedData(db)

        #  kontroll för misstänkta transaktioner
        suspicious = detect_suspicious_transactions()
        if suspicious:
            print("🚨 Misstänkta transaktioner hittade:")
            for entry in suspicious:
                print(entry)

    app.run(debug=True)
