# VITT GENIE - COMPLETE WHATSAPP CHATBOT WITH GEMINI PRO
# Copy this entire file as app.py and run it

import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)

# ==================== CONFIGURATION ====================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# ==================== USER DATA STORAGE ====================
users = {}

# ==================== MESSAGES ====================
WELCOME = """Hi! नमस्ते! 🙏

*Vitt Genie आपका स्वागत करती है!* 📚✨

कृपया भाषा चुनें:
1️⃣ हिंदी
2️⃣ English

Reply: 1 या 2"""

MENU_HI = """✅ हिंदी चुना गया

📚 *Vitt Genie मेनू*

मैं इनमें expert हूँ:
• Commerce (लेखा, व्यापार, अर्थशास्त्र)
• Career (CA, CS, MBA, B.Com)
• Share Market & Investment
• Business & Startup
• AI Tools
• Finance & Money

💬 कुछ भी पूछें!

Commands:
"menu" - मेनू
"lang" - भाषा बदलें"""

MENU_EN = """✅ English Selected

📚 *Vitt Genie Menu*

I'm expert in:
• Commerce (Accounts, Business, Economics)
• Career (CA, CS, MBA, B.Com)
• Share Market & Investment
• Business & Startup
• AI Tools
• Finance & Money

💬 Ask anything!

Commands:
"menu" - Show menu
"lang" - Change language"""

PROMPT_HI = """तुम Vitt Genie हो - Commerce, Business, Finance, Share Market, Career की expert AI teacher।

Rules:
1. हमेशा हिंदी में जवाब दो
2. Simple student-friendly भाषा use करो
3. 150-200 words में जवाब दो
4. Examples दो
5. Encouraging tone रखो
6. Step-by-step समझाओ

Topics तुम cover करती हो:
- Commerce subjects (11th/12th)
- Career after 12th (CA, CS, CMA, MBA, B.Com, BBA)
- Share market, mutual funds, investment
- Business, entrepreneurship, startup
- AI tools for business/finance
- Money management, financial planning
- Company, corporate, marketing

User का सवाल:"""

PROMPT_EN = """You are Vitt Genie - expert AI teacher in Commerce, Business, Finance, Share Market, Career.

Rules:
1. Always reply in English
2. Use simple student-friendly language
3. Answer in 150-200 words
4. Give examples
5. Keep encouraging tone
6. Explain step-by-step

Topics you cover:
- Commerce subjects (11th/12th)
- Career after 12th (CA, CS, CMA, MBA, B.Com, BBA)
- Share market, mutual funds, investment
- Business, entrepreneurship, startup
- AI tools for business/finance
- Money management, financial planning
- Company, corporate, marketing

User's question:"""

# ==================== FUNCTIONS ====================
def get_user(phone):
    if phone not in users:
        users[phone] = {'lang': None, 'history': []}
    return users[phone]

def gemini_reply(question, lang, history):
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = PROMPT_HI if lang == 'hi' else PROMPT_EN
        
        context = prompt + "\n\n"
        if history:
            for h in history[-4:]:
                context += h + "\n"
        context += question
        
        response = model.generate_content(context)
        return response.text
    except Exception as e:
        return "क्षमा करें! कुछ error हो गया। फिर try करें। 🙏" if lang == 'hi' else "Sorry! Some error occurred. Try again. 🙏"

# ==================== WEBHOOK ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    msg = request.values.get('Body', '').strip()
    phone = request.values.get('From', '')
    
    resp = MessagingResponse()
    reply = resp.message()
    
    user = get_user(phone)
    
    # No language set
    if user['lang'] is None:
        if msg == '1':
            user['lang'] = 'hi'
            reply.body(MENU_HI)
        elif msg == '2':
            user['lang'] = 'en'
            reply.body(MENU_EN)
        else:
            reply.body(WELCOME)
        return str(resp)
    
    # Commands
    lower = msg.lower()
    if lower in ['lang', 'language', 'भाषा']:
        user['lang'] = None
        user['history'] = []
        reply.body(WELCOME)
        return str(resp)
    
    if lower in ['menu', 'मेनू', 'help']:
        reply.body(MENU_HI if user['lang'] == 'hi' else MENU_EN)
        return str(resp)
    
    # AI Response
    answer = gemini_reply(msg, user['lang'], user['history'])
    user['history'].append(f"Q: {msg}")
    user['history'].append(f"A: {answer}")
    
    if len(user['history']) > 8:
        user['history'] = user['history'][-8:]
    
    reply.body(answer)
    return str(resp)

@app.route('/')
def home():
    return "<h1>✅ Vitt Genie Running!</h1><p>WhatsApp Bot Active</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))