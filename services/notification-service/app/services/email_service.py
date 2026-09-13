class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        print(f"[MOCK EMAIL DISPATCH] To: {to_email} | Subject: {subject} | Body: {body}")
        return True
