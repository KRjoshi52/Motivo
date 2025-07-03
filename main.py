from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
import random
import re
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
import uuid
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Configure OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api_key)

# User feedback storage (in production, use a database)
user_feedback = {}

# Response history to avoid repetition
response_history = set()

# Session-based response tracking for more variety
session_responses = {}

# Enhanced dynamic response templates for more variety
RESPONSE_TEMPLATES = {
    'funny': [
        "Your brain is like {metaphor} right now - {funny_observation}! 😂",
        "Plot twist: {unexpected_truth}! 🎭",
        "Breaking news: {funny_headline}! 📰",
        "Your feelings are valid, but {humorous_reality}! 🤔",
        "Warning: {funny_warning}! ⚡",
        "Fun fact: {funny_fact}! 🎉",
        "Your brain: '{negative_thought}' Reality: '{positive_truth}' 🎭 vs 📊",
        "Plot armor activated: {encouraging_metaphor}! 🛡️",
        "Your mood is like {weather_metaphor}! ☀️",
        "Emergency broadcast: {funny_encouragement}! ▶️",
        "Your brain is currently {brain_state}. Time for a {brain_action}! 🧠",
        "Alert: {funny_alert}! Your {funny_quality} is showing! 🚨",
        "Your thoughts are like {thought_metaphor}. Let's {thought_action}! 💭",
        "Breaking: You're not {negative_self}, you're {positive_self}! 📺",
        "Your brain is running {brain_program}. Switch to {better_program}! 💻"
    ],
    'motivational': [
        "You've survived {survival_stat} of your bad days so far. That's {achievement}! 🏆",
        "Your future self is {future_action} you right now for not giving up! 🙌",
        "You're not behind, you're exactly where you need to be. {trust_message}! 🌱",
        "Every {role} was once a {beginner_role} who refused to quit. You're on the right track! 🚀",
        "Your strength is greater than any challenge. {encouragement}! 💪",
        "The only person you need to be better than is {comparison}. {motivation}! 📈",
        "You're not failing, you're learning. {learning_perspective}! 🎯",
        "Your potential is limitless. {potential_message}! ⭐",
        "You're {brave_quality} than you believe, {strong_quality} than you seem, and {smart_quality} than you think! 🧠💪",
        "The world needs your unique {unique_quality}. Don't keep it hidden! ✨",
        "Your {inner_strength} is your superpower. {superpower_message}! 🦸‍♀️",
        "You're not just surviving, you're {thriving_action}! 🌟",
        "Your {resilience_quality} is inspiring others right now! 🌱",
        "You're building {building_what} one {small_step} at a time! 🏗️",
        "Your {courage_quality} is creating ripples of change! 🌊"
    ],
    'scientific': [
        "Science fact: {scientific_fact}! 🔬",
        "Research shows: {research_finding}. Your brain is being {brain_behavior}! 🧠",
        "Psychology tip: {psychology_insight}! 🧠✨",
        "Neuroscience fact: {neuroscience_fact}! 💪🧠",
        "Behavioral science: {behavioral_insight}! 👣",
        "Cognitive psychology: {cognitive_fact}! 🙏",
        "Positive psychology: {positive_psychology_fact}! 🎯",
        "Neuroplasticity fact: {neuroplasticity_fact}! 🔄",
        "Stress research: {stress_fact}! 📈",
        "Mindfulness science: {mindfulness_fact}! 🫁",
        "Your brain is {brain_process} right now. That's {process_meaning}! 🧬",
        "Neuroscience confirms: {neuroscience_confirmation}! 🔍",
        "Psychology research: {psychology_research}! 📊",
        "Your neural pathways are {neural_activity}. This is {activity_meaning}! ⚡",
        "Brain science says: {brain_science_fact}! 🧠🔬"
    ],
    'actionable': [
        "Right now: {immediate_action}! Your {body_part} will thank you! 💃",
        "Quick fix: {quick_exercise}. You're back! 👀👂",
        "Emergency protocol: {emergency_action}! 😊",
        "Immediate action: {social_action}! 📱💕",
        "Power move: {power_action}! 🎵",
        "Instant mood boost: {mood_boost_action}! (Even if you don't believe it yet!) 🪞",
        "Quick win: {quick_win_action}. Small wins create momentum! 🏆",
        "Energy shift: {energy_action}! 🚶‍♀️",
        "Mind reset: {mind_reset_action}! ✍️",
        "Body hack: {body_hack_action}! 💧",
        "Do this now: {now_action}! Your future self will thank you! ⏰",
        "Micro-action: {micro_action}. Tiny steps, big impact! 🐾",
        "Energy boost: {energy_boost_action}! Feel the difference! ⚡",
        "Mind shift: {mind_shift_action}! Notice the change! 🔄",
        "Body reset: {body_reset_action}! Your cells are cheering! 🎉"
    ]
}

# Enhanced dynamic content generators
METAPHORS = [
    "a drama queen", "a GPS with wrong directions", "a weather forecast", "a broken record",
    "a conspiracy theorist", "a toddler having a tantrum", "a broken calculator", "a faulty alarm clock",
    "a confused tour guide", "a pessimistic fortune teller", "a broken compass", "a malfunctioning robot",
    "a broken GPS", "a faulty weather app", "a confused DJ", "a broken calculator", "a drama club president",
    "a conspiracy podcast host", "a broken fortune cookie", "a malfunctioning crystal ball"
]

FUNNY_OBSERVATIONS = [
    "tell it to take a chill pill", "it's giving you the scenic route", "sometimes it's wrong and the sun comes out anyway",
    "it's stuck on repeat", "it's seeing patterns that don't exist", "it's having a moment", "it's doing math with feelings",
    "it's stuck in the past", "it's giving you the wrong directions", "it's predicting doom and gloom", "it's pointing north when you need south",
    "it's running on drama mode", "it's like a broken record player", "it's having an existential crisis", "it's playing the wrong playlist",
    "it's stuck in a loop", "it's reading the wrong script", "it's playing the wrong movie", "it's stuck in the wrong channel"
]

UNEXPECTED_TRUTHS = [
    "you're way more awesome than your brain is letting you believe right now",
    "you're actually winning at life, your brain just hasn't updated the scoreboard yet",
    "you're not a mess, you're a masterpiece in progress",
    "you're doing better than 90% of people who are pretending to have it together",
    "you're the main character of your story, and main characters always bounce back",
    "you're not stuck, you're just paused",
    "you're not broken, you're just human",
    "you're not failing, you're just learning in public",
    "you're not behind, you're exactly where you need to be",
    "you're not alone in feeling this way",
    "you're actually crushing it, your brain just hasn't caught up yet",
    "you're not the disaster your brain thinks you are",
    "you're way more capable than your thoughts are telling you",
    "you're not falling behind, you're taking the scenic route",
    "you're not a failure, you're just having a human moment"
]

FUNNY_HEADLINES = [
    "You're not a failure, you're just a human having a human moment!",
    "Local person discovers they're actually doing great!",
    "Breaking: You're more resilient than you think!",
    "Exclusive: Your potential is still intact!",
    "Update: You're still awesome despite current circumstances!",
    "Alert: Your awesomeness level remains unchanged!",
    "News flash: You're handling this better than you realize!",
    "Report: You're not the disaster your brain thinks you are!",
    "Breaking news: You're actually winning at life!",
    "Exclusive: Your awesomeness is still intact!",
    "Update: You're doing better than you think!",
    "Alert: Your potential is still unlimited!"
]

HUMOROUS_REALITIES = [
    "so is the fact that you're probably overthinking this",
    "so is the fact that your brain is being dramatic",
    "so is the fact that you're actually doing fine",
    "so is the fact that you're probably being too hard on yourself",
    "so is the fact that you're more capable than you think",
    "so is the fact that you're not alone in this feeling",
    "so is the fact that this feeling is temporary",
    "so is the fact that you're stronger than this moment",
    "so is the fact that your brain is being a drama queen",
    "so is the fact that you're probably overreacting",
    "so is the fact that you're doing better than you realize",
    "so is the fact that this too shall pass"
]

FUNNY_WARNINGS = [
    "Your brain is currently running on drama mode. Switch to awesome mode immediately!",
    "Overthinking detected! Please proceed to action mode!",
    "Self-doubt virus detected! Activating confidence booster!",
    "Pessimism levels critical! Initiating optimism protocol!",
    "Worry mode activated! Switching to solution mode!",
    "Catastrophic thinking detected! Engaging reality check!",
    "Imposter syndrome alert! Activating truth serum!",
    "Negative spiral detected! Deploying positive intervention!",
    "Drama mode activated! Switching to chill mode!",
    "Panic mode detected! Engaging calm protocol!",
    "Stress overload! Initiating relaxation sequence!",
    "Anxiety spike detected! Deploying peace protocol!"
]

FUNNY_FACTS = [
    "Every successful person has felt exactly like you do right now. You're in good company!",
    "Your brain processes 70,000 thoughts per day, and most of them are probably wrong!",
    "You're more likely to win the lottery than to be as bad as you think you are!",
    "Your brain is like a conspiracy theorist - it sees patterns that don't exist!",
    "You're not the first person to feel this way, and you won't be the last!",
    "Your feelings are like a weather forecast - sometimes they're just wrong!",
    "You're probably overthinking this by about 300%!",
    "Your brain is like a broken record - it keeps playing the same negative track!",
    "Your brain is like a faulty GPS - it's giving you the wrong directions!",
    "You're not alone - even Beyoncé has bad days!",
    "Your brain is like a drama club - sometimes it needs to be told to take a break!",
    "You're probably being way too hard on yourself!"
]

NEGATIVE_THOUGHTS = [
    "This is the worst!", "I can't handle this!", "Everything is going wrong!",
    "I'm a failure!", "This is impossible!", "I'm not good enough!",
    "This will never work!", "I'm stuck forever!", "I'm falling behind!",
    "This is too hard!", "I'm not cut out for this!", "This is hopeless!",
    "I'm a disaster!", "I can't do anything right!", "I'm worthless!",
    "This is never going to get better!", "I'm a mess!", "I'm not smart enough!"
]

POSITIVE_TRUTHS = [
    "Actually, you're doing fine!", "You've handled worse!", "You're stronger than this!",
    "You're learning and growing!", "You're making progress!", "You're capable of this!",
    "You're figuring it out!", "You're moving forward!", "You're exactly where you need to be!",
    "You're doing better than you think!", "You've got this!", "You're not alone!",
    "You're actually crushing it!", "You're way more capable than you think!",
    "You're not a failure, you're just learning!", "You're doing great!",
    "You're stronger than you realize!", "You're making a difference!"
]

ENCOURAGING_METAPHORS = [
    "You're the main character of your story, and main characters always bounce back!",
    "You're like a phoenix - you'll rise from these ashes!",
    "You're like a superhero - your powers are just recharging!",
    "You're like a diamond - pressure makes you stronger!",
    "You're like a butterfly - transformation is messy but beautiful!",
    "You're like a seed - you're growing even when you can't see it!",
    "You're like a star - you shine even in darkness!",
    "You're like a mountain - you're solid and unshakeable!",
    "You're like a river - you find your way around obstacles!",
    "You're like a tree - you grow stronger with each storm!",
    "You're like a lighthouse - you guide others through darkness!",
    "You're like a rainbow - you bring color after the storm!"
]

WEATHER_METAPHORS = [
    "Right now it's cloudy, but sunshine is coming!",
    "It's just a passing storm, clear skies ahead!",
    "You're in a fog, but it will lift!",
    "It's raining now, but rainbows follow rain!",
    "You're in a winter season, but spring always comes!",
    "It's dark now, but dawn is approaching!",
    "You're in a hurricane, but calm waters are ahead!",
    "It's stormy now, but every storm runs out of rain!",
    "It's overcast now, but the sun is still there!",
    "You're in a thunderstorm, but they always pass!",
    "It's windy now, but wind brings change!",
    "It's cold now, but warmth is returning!"
]

FUNNY_ENCOURAGEMENTS = [
    "You're not stuck, you're just paused. Press play and keep going!",
    "Your brain is like a broken GPS. You're still going somewhere amazing!",
    "You're not failing, you're just collecting data for success!",
    "Your brain is like a drama club. Sometimes it needs to be told to take a break!",
    "You're not behind, you're just taking the scenic route!",
    "Your brain is like a broken calculator. The math is still correct!",
    "You're not lost, you're just exploring new territory!",
    "Your brain is like a faulty alarm clock. It's just a false alarm!",
    "You're not broken, you're just updating your software!",
    "Your brain is like a broken record. Time to change the track!",
    "You're not a failure, you're just having a system update!",
    "Your brain is like a broken compass. You'll find your way!"
]

# New dynamic content for enhanced variety
BRAIN_STATES = [
    "in panic mode", "running on empty", "stuck in a loop", "having a moment",
    "in drama mode", "overthinking everything", "stuck in the past", "predicting doom",
    "in worry mode", "running scenarios", "stuck in reverse", "having an existential crisis"
]

BRAIN_ACTIONS = [
    "reboot", "software update", "mode switch", "reset", "calibration", "restart",
    "system refresh", "power cycle", "factory reset", "upgrade", "patch", "debug"
]

FUNNY_ALERTS = [
    "Awesomeness detected!", "Potential overload!", "Awesome person alert!",
    "Greatness in progress!", "Amazing human detected!", "Awesome vibes incoming!",
    "Potential explosion!", "Awesome alert!", "Greatness detected!", "Amazing alert!"
]

FUNNY_QUALITIES = [
    "awesomeness", "greatness", "amazingness", "awesomeness", "brilliance",
    "genius", "awesomeness", "magnificence", "awesomeness", "splendor"
]

THOUGHT_METAPHORS = [
    "a broken record", "a stuck song", "a broken radio", "a faulty playlist",
    "a broken jukebox", "a stuck CD", "a broken speaker", "a faulty microphone"
]

THOUGHT_ACTIONS = [
    "change the station", "skip this track", "turn down the volume", "play something else",
    "change the playlist", "find a new song", "adjust the frequency", "switch channels"
]

NEGATIVE_SELVES = [
    "a failure", "a mess", "a disaster", "a loser", "stupid", "worthless",
    "not good enough", "a disappointment", "a mistake", "broken"
]

POSITIVE_SELVES = [
    "awesome", "amazing", "incredible", "wonderful", "brilliant", "fantastic",
    "extraordinary", "remarkable", "outstanding", "phenomenal"
]

BRAIN_PROGRAMS = [
    "drama.exe", "panic.exe", "worry.exe", "stress.exe", "anxiety.exe",
    "overthink.exe", "catastrophe.exe", "doom.exe", "fear.exe", "doubt.exe"
]

BETTER_PROGRAMS = [
    "awesome.exe", "calm.exe", "peace.exe", "confidence.exe", "strength.exe",
    "courage.exe", "hope.exe", "joy.exe", "love.exe", "success.exe"
]

# Google OAuth setup (replace with your credentials)
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = True  # Remove in production!
google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret'),
    scope=["profile", "email"],
    redirect_url="/google_login/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# In-memory community chat (for MVP; use DB for production)
community_messages = []  # Each message: {'user': name/email, 'text': msg, 'timestamp': ...}
community_users = set()

# Conversational fallback templates for chat-like responses
CONVERSATIONAL_TEMPLATES = [
    "Oh wow, I totally get how you feel. Want to talk more about it? 😊",
    "Honestly, that sounds tough. If you want to vent, I'm here!",
    "Haha, I've been there too. Sometimes you just need to let it out, right?",
    "That makes so much sense. What's on your mind right now?",
    "If I were in your shoes, I'd probably feel the same. Anything I can do to help?",
    "I hear you. It's okay to feel this way. Do you want some advice or just to chat?",
    "You're not alone in this. I'm here for you, no judgment!",
    "That's super relatable. Want to share more?",
    "I'm glad you told me. How can I support you right now?",
    "Sometimes just saying it out loud helps. I'm listening! 👂",
    "I get it, and I'm rooting for you. What would make today a little better?",
    "That's a lot to deal with. Take your time, I'm here whenever you need to talk.",
    "You're stronger than you think, but you don't have to be strong all the time."
]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256))  # hashed password
    name = db.Column(db.String(150))
    google_id = db.Column(db.String(256), unique=True)
    # New fields for profile features
    profile_pic = db.Column(db.String(256))  # path to profile picture
    journal = db.Column(db.Text)  # user's private journal
    last_login = db.Column(db.Date)
    streak = db.Column(db.Integer, default=0)
    total_chats = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)
    
    def __init__(self, email, password=None, name=None, google_id=None, profile_pic=None, journal=None):
        self.email = email
        self.password = password
        self.name = name
        self.google_id = google_id
        self.profile_pic = profile_pic
        self.journal = journal

# New model for favorite responses/quotes
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# New model for Mood Circles
class Circle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CircleMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    circle_id = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reaction = db.Column(db.String(20))  # e.g. 'hug', 'sparkle', etc.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        if not email or not password:
            return render_template('register.html', error='Email and password required')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        user = User(email=email, password=password, name=name)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # TODO: use password hash check
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        return redirect(url_for('login'))
    info = resp.json()
    email = info['email']
    google_id = info['id']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=info.get('name'), google_id=google_id)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('index'))

def get_fallback_response(response_type):
    """Get a fallback response when templates don't work"""
    fallbacks = {
        'funny': [
            "Your brain is having a moment, but you're actually doing great! 😂",
            "Plot twist: You're way more awesome than you think! 🎭",
            "Breaking news: You're not a disaster, you're just human! 📰",
            "Your brain is like a drama queen right now - tell it to chill! 😂",
            "Warning: Awesomeness detected! You're doing better than you think! ⚡"
        ],
        'motivational': [
            "You've got this! Every challenge makes you stronger! 💪",
            "You're exactly where you need to be right now! 🌱",
            "Your potential is limitless! Keep going! ⭐",
            "You're stronger than you know! Your resilience is inspiring! 🛡️",
            "You're building something amazing! One step at a time! 🏗️"
        ],
        'scientific': [
            "Your brain is amazing and constantly adapting! 🧠",
            "Science shows you're more resilient than you think! 🔬",
            "Your neural pathways are getting stronger! ⚡",
            "Psychology confirms: You're doing great! 📊",
            "Your brain is evolving beautifully! 🧬"
        ],
        'actionable': [
            "Take a deep breath right now! 🫁",
            "Do one small thing that makes you feel good! 🎯",
            "Move your body for 2 minutes! 💃",
            "Call someone who makes you smile! 📱",
            "Write down one thing you're grateful for! ✍️"
        ]
    }
    return random.choice(fallbacks.get(response_type, fallbacks['motivational']))

def generate_dynamic_response(response_type, mood, context):
    """Generate a truly unique response using templates and dynamic content"""
    # 50% chance to use a conversational template for realism
    if random.random() < 0.5:
        template = random.choice(CONVERSATIONAL_TEMPLATES)
        # Optionally, personalize with mood/context
        if mood != 'general':
            template = template.replace("I totally get how you feel", f"I totally get how it feels to be {mood}")
            template = template.replace("that sounds tough", f"feeling {mood} sounds tough")
        if context != 'general':
            template += f" (about {context})"
        return template
    if response_type not in RESPONSE_TEMPLATES:
        return get_fallback_response(response_type)
    template = random.choice(RESPONSE_TEMPLATES[response_type])
    
    # Generate dynamic content based on template placeholders
    if '{metaphor}' in template:
        template = template.replace('{metaphor}', random.choice(METAPHORS))
    if '{funny_observation}' in template:
        template = template.replace('{funny_observation}', random.choice(FUNNY_OBSERVATIONS))
    if '{unexpected_truth}' in template:
        template = template.replace('{unexpected_truth}', random.choice(UNEXPECTED_TRUTHS))
    if '{funny_headline}' in template:
        template = template.replace('{funny_headline}', random.choice(FUNNY_HEADLINES))
    if '{humorous_reality}' in template:
        template = template.replace('{humorous_reality}', random.choice(HUMOROUS_REALITIES))
    if '{funny_warning}' in template:
        template = template.replace('{funny_warning}', random.choice(FUNNY_WARNINGS))
    if '{funny_fact}' in template:
        template = template.replace('{funny_fact}', random.choice(FUNNY_FACTS))
    if '{negative_thought}' in template:
        template = template.replace('{negative_thought}', random.choice(NEGATIVE_THOUGHTS))
    if '{positive_truth}' in template:
        template = template.replace('{positive_truth}', random.choice(POSITIVE_TRUTHS))
    if '{encouraging_metaphor}' in template:
        template = template.replace('{encouraging_metaphor}', random.choice(ENCOURAGING_METAPHORS))
    if '{weather_metaphor}' in template:
        template = template.replace('{weather_metaphor}', random.choice(WEATHER_METAPHORS))
    if '{funny_encouragement}' in template:
        template = template.replace('{funny_encouragement}', random.choice(FUNNY_ENCOURAGEMENTS))
    
    # New dynamic content replacements
    if '{brain_state}' in template:
        template = template.replace('{brain_state}', random.choice(BRAIN_STATES))
    if '{brain_action}' in template:
        template = template.replace('{brain_action}', random.choice(BRAIN_ACTIONS))
    if '{funny_alert}' in template:
        template = template.replace('{funny_alert}', random.choice(FUNNY_ALERTS))
    if '{funny_quality}' in template:
        template = template.replace('{funny_quality}', random.choice(FUNNY_QUALITIES))
    if '{thought_metaphor}' in template:
        template = template.replace('{thought_metaphor}', random.choice(THOUGHT_METAPHORS))
    if '{thought_action}' in template:
        template = template.replace('{thought_action}', random.choice(THOUGHT_ACTIONS))
    if '{negative_self}' in template:
        template = template.replace('{negative_self}', random.choice(NEGATIVE_SELVES))
    if '{positive_self}' in template:
        template = template.replace('{positive_self}', random.choice(POSITIVE_SELVES))
    if '{brain_program}' in template:
        template = template.replace('{brain_program}', random.choice(BRAIN_PROGRAMS))
    if '{better_program}' in template:
        template = template.replace('{better_program}', random.choice(BETTER_PROGRAMS))
    
    # Add more dynamic content based on mood and context
    if mood == 'stressed':
        stressed_msg = random.choice(["One breath at a time", "You've got this", "This too shall pass", "You're stronger than stress"])
        template += f" Remember: {stressed_msg}! 💪"
    elif mood == 'anxious':
        anxious_msg = random.choice(["You're safe", "This feeling will pass", "You're okay", "Breathe through it"])
        template += f" Remember: {anxious_msg}! 🫁"
    elif mood == 'sad':
        sad_msg = random.choice(["Brighter days are coming", "You're not alone", "Your feelings are valid", "This is temporary"])
        template += f" Remember: {sad_msg}! 🌟"
    
    return template

def create_ai_prompt(mood, response_type, context):
    """Create a highly specific AI prompt for unique responses"""
    
    mood_contexts = {
        'stressed': 'feeling overwhelmed, pressured, or under stress',
        'anxious': 'experiencing worry, nervousness, or anxiety',
        'sad': 'feeling down, blue, or experiencing sadness',
        'depressed': 'feeling hopeless, empty, or experiencing depression',
        'lonely': 'feeling isolated, alone, or missing connection',
        "overwhelmed": "feeling like there's too much to handle",
        'tired': 'feeling exhausted, drained, or fatigued',
        'frustrated': 'feeling stuck, annoyed, or frustrated'
    }
    
    context_prompts = {
        'work': 'in a work or professional context',
        'relationships': 'involving relationships, love, or social connections',
        'health': 'related to physical or mental health',
        'future': 'about future goals, career, or life plans',
        'past': 'about past experiences, regrets, or memories'
    }
    
    style_prompts = {
        'funny': 'Use humor, wit, and lightheartedness. Make them laugh while being supportive.',
        'motivational': 'Be inspiring, encouraging, and empowering. Focus on strength and potential.',
        'scientific': 'Include psychology, neuroscience, or behavioral science insights. Be educational but warm.',
        'actionable': 'Provide specific, immediate steps they can take right now. Be practical and actionable.',
        'random': 'Mix different approaches - be creative, authentic, and genuinely helpful.'
    }
    
    mood_desc = mood_contexts.get(mood, 'experiencing difficult emotions')
    context_desc = context_prompts.get(context, 'in their current situation')
    style_desc = style_prompts.get(response_type, 'be genuinely supportive and helpful')
    
    prompt = f"""The user is {mood_desc} {context_desc}. 

Create a short, unique, and authentic response (under 30 words) that will genuinely help them feel better.

Requirements:
- {style_desc}
- Be specific to their situation
- Use natural, conversational language
- Include an appropriate emoji
- Make it completely different from typical responses
- Be genuinely understanding and supportive
- Avoid generic advice or clichés

Make this response feel like it's coming from a caring friend who really understands what they're going through."""

    return prompt

def analyze_mood_and_context(user_mood):
    """Analyze user mood and context to provide more natural responses"""
    mood = user_mood.lower()
    
    # Detect mood keywords
    mood_keywords = {
        'stressed': ['stress', 'overwhelm', 'pressure', 'busy', 'rushed'],
        'anxious': ['anxiety', 'worry', 'nervous', 'panic', 'fear'],
        'sad': ['sad', 'down', 'blue', 'depressed', 'unhappy'],
        'depressed': ['depression', 'hopeless', 'worthless', 'empty'],
        'lonely': ['lonely', 'alone', 'isolated', 'missing', 'no friends'],
        "overwhelmed": ["overwhelm", "too much", "can't cope", "drowning"],
        'tired': ['tired', 'exhausted', 'fatigue', 'sleepy', 'drained'],
        'frustrated': ['frustrated', 'angry', 'mad', 'annoyed', 'stuck']
    }
    
    # Detect context keywords
    context_keywords = {
        'work': ['work', 'job', 'office', 'meeting', 'deadline', 'boss'],
        'relationships': ['relationship', 'partner', 'friend', 'family', 'love'],
        'health': ['health', 'sick', 'pain', 'body', 'medical'],
        'future': ['future', 'career', 'goals', 'dreams', 'plan'],
        'past': ['past', 'regret', 'mistake', 'memory', 'childhood']
    }
    
    detected_mood = 'general'
    detected_context = 'general'
    
    for mood_type, keywords in mood_keywords.items():
        if any(keyword in mood for keyword in keywords):
            detected_mood = mood_type
            break
    
    for context_type, keywords in context_keywords.items():
        if any(keyword in mood for keyword in keywords):
            detected_context = context_type
            break
    
    return detected_mood, detected_context

def get_contextual_response(mood, context, response_type, user_id=None):
    """Get a response that's contextual to the user's specific situation"""
    # Try AI first for truly unique responses
    try:
        prompt = create_ai_prompt(mood, response_type, context)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive, authentic friend who helps people feel better with genuine, natural responses. Always provide unique, varied responses that feel personal and specific."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.9  # High temperature for maximum creativity
        )
        ai_response = response.choices[0].message.content
        if ai_response:
            ai_response = ai_response.strip()
        # Check if response is unique
        if ai_response and ai_response not in response_history:
            response_history.add(ai_response)
            return ai_response
        else:
            # If AI response is repeated or empty, generate dynamic response
            return generate_dynamic_response(response_type, mood, context)
    except Exception as e:
        print(f"AI Error: {str(e)}")
        # If AI fails, use dynamic response generation
        return generate_dynamic_response(response_type, mood, context)

def get_dynamic_slogan(mood, response_type):
    """Get a dynamic slogan based on mood and response type"""
    
    # Dynamic slogans with more variety
    slogans = {
        'funny': [
            "You're weirdly amazing. Don't change.",
            "Your brain is a comedy goldmine! 🎭",
            "Plot twist: You're actually awesome! 📰",
            "Warning: Awesomeness detected! ⚡",
            "Breaking news: You're doing great! 📺",
            "Your humor level: Expert! 😎",
            "Comedy gold, right here! 🏆",
            "You're the main character! 🎬",
            "Plot armor activated! 🛡️",
            "Your brain: Certified funny! 🎪",
            "Drama queen mode: Activated! 👑",
            "Your awesomeness is showing! ✨"
        ],
        'motivational': [
            "You're stronger than you know. 💪",
            "Your potential is limitless. ⭐",
            "You've got this, warrior! 🛡️",
            "Rise and shine, champion! 🌅",
            "You're unstoppable! 🚀",
            "Your strength inspires others! 🌟",
            "You're building something amazing! 🏗️",
            "Your courage is contagious! 🦁",
            "You're a force of nature! 🌪️",
            "Your determination is legendary! 👑",
            "You're a resilience machine! ⚡",
            "Your power is unmatched! 🔥"
        ],
        'scientific': [
            "Your brain is fascinating! 🧠",
            "Science says you're amazing! 🔬",
            "Neuroscience backs your awesomeness! 🧬",
            "Research proves you're incredible! 📊",
            "Your mind is a wonder! 🌟",
            "Psychology supports your growth! 📈",
            "Your brain is evolving beautifully! 🧬",
            "Science confirms: You're special! 🔍",
            "Your neural pathways are impressive! ⚡",
            "Research shows your potential! 📋",
            "Your brain is a masterpiece! 🎨",
            "Science validates your awesomeness! 🔬"
        ],
        'actionable': [
            "Small steps, big changes! 👣",
            "Action creates momentum! ⚡",
            "You're one step away from amazing! 🎯",
            "Move forward, you've got this! 🚶‍♀️",
            "Progress over perfection! 📈",
            "Every action builds your future! 🏗️",
            "Your next move matters! 🎯",
            "Action is your superpower! 💫",
            "You're creating change! 🌱",
            "Your steps are leading somewhere! 🗺️",
            "Movement creates magic! ✨",
            "Your actions inspire others! 🌟"
        ]
    }
    
    # Get slogans for the response type
    available_slogans = slogans.get(response_type, slogans['funny'])
    
    # Filter out recently used slogans
    unused_slogans = [s for s in available_slogans if s not in response_history]
    
    if unused_slogans:
        slogan = random.choice(unused_slogans)
        response_history.add(slogan)
        return slogan
    else:
        # If all slogans used, clear history and start fresh
        response_history.clear()
        return random.choice(available_slogans)

def store_feedback(user_id, response, feedback_type):
    """Store user feedback for learning preferences"""
    if user_id not in user_feedback:
        user_feedback[user_id] = {
            'liked_responses': [],
            'disliked_responses': [],
            'preferred_types': [],
            'feedback_count': 0
        }
    
    user_data = user_feedback[user_id]
    user_data['feedback_count'] += 1
    
    if feedback_type == 'like':
        user_data['liked_responses'].append(response)
    elif feedback_type == 'dislike':
        user_data['disliked_responses'].append(response)
    
    # Keep only last 10 feedback items to prevent memory issues
    user_data['liked_responses'] = user_data['liked_responses'][-10:]
    user_data['disliked_responses'] = user_data['disliked_responses'][-10:]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spark', methods=['POST'])
def spark():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        user_mood = data.get('mood', '')
        response_type = data.get('type', 'random')
        user_id = data.get('user_id', 'anonymous')
        if not user_mood.strip():
            return jsonify({'error': 'Please tell us how you\'re feeling!'}), 400
        # Add a random string to the prompt for uniqueness
        randomizer = str(uuid.uuid4())[:8]
        user_mood += f" [unique:{randomizer}]"
        # Use session-based chat history
        if 'chat_history' not in session:
            session['chat_history'] = []
        session['chat_history'].append({"role": "user", "content": user_mood})
        last_ai_reply = session['chat_history'][-2]['content'] if len(session['chat_history']) >= 2 and session['chat_history'][-2]['role'] == 'assistant' else None
        # Special prompt for 'friend' type
        system_prompt = "You are a supportive, authentic friend who helps people feel better with genuine, natural responses. Always provide unique, varied responses that feel personal and specific."
        if response_type == 'friend':
            system_prompt = "You are a supportive, caring peer. Respond as a friendly, understanding friend would—warm, casual, and encouraging. Avoid sounding like a therapist or coach."
        try:
            ai_reply = None
            for _ in range(3):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt}
                    ] + session['chat_history'],
                    max_tokens=100,
                    temperature=1.2  # Higher temperature for more variety
                )
                candidate = response.choices[0].message.content
                if candidate is not None:
                    candidate = candidate.strip()
                if not last_ai_reply or candidate != last_ai_reply:
                    ai_reply = candidate
                    break
            if not ai_reply:
                # fallback to template
                detected_mood, detected_context = analyze_mood_and_context(user_mood)
                ai_reply = generate_dynamic_response(response_type, detected_mood, detected_context)
            session['chat_history'].append({"role": "assistant", "content": ai_reply})
            dynamic_slogan = get_dynamic_slogan('random', response_type)
            return jsonify({
                'response': ai_reply,
                'slogan': dynamic_slogan,
                'response_id': len(response_history)
            })
        except Exception as e:
            print(f"AI Error: {str(e)}")
            detected_mood, detected_context = analyze_mood_and_context(user_mood)
            fallback_response = generate_dynamic_response(response_type, detected_mood, detected_context)
            dynamic_slogan = get_dynamic_slogan(detected_mood, response_type)
            session['chat_history'].append({"role": "assistant", "content": fallback_response})
            return jsonify({
                'response': fallback_response,
                'slogan': dynamic_slogan,
                'response_id': len(response_history)
            })
    except Exception as e:
        print(f"General Error: {str(e)}")
        fallback_response = generate_dynamic_response('random', 'general', 'general')
        dynamic_slogan = get_dynamic_slogan('general', 'random')
        response_history.add(fallback_response)
        return jsonify({
            'response': fallback_response,
            'slogan': dynamic_slogan,
            'response_id': len(response_history)
        })

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        user_id = data.get('user_id', 'anonymous')
        response = data.get('response', '')
        feedback_type = data.get('type', '')  # 'like' or 'dislike'
        response_id = data.get('response_id', 0)
        
        if feedback_type in ['like', 'dislike']:
            store_feedback(user_id, response, feedback_type)
            return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
        else:
            return jsonify({'error': 'Invalid feedback type'}), 400
            
    except Exception as e:
        print(f"Feedback Error: {str(e)}")
        return jsonify({'error': 'Failed to store feedback'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip() if data else ''
    if not user_message:
        return jsonify({'reply': "Please type a message!"}), 400
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive, authentic friend who helps people feel better with genuine, natural responses. Always provide unique, varied responses that feel personal and specific."}
            ] + session['chat_history'],
            max_tokens=100,
            temperature=0.9
        )
        ai_reply = response.choices[0].message.content
        if ai_reply is None:
            ai_reply = "I'm here to chat!"
        session['chat_history'].append({"role": "assistant", "content": ai_reply})
        return jsonify({'reply': ai_reply})
    except Exception as e:
        print(f"AI Error: {str(e)}")
        # fallback to template
        mood, context = analyze_mood_and_context(user_message)
        fallback_reply = generate_dynamic_response('random', mood, context)
        session['chat_history'].append({"role": "assistant", "content": fallback_reply})
        return jsonify({'reply': fallback_reply})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/profile')
@login_required
def profile():
    chat_history = session.get('chat_history', [])
    return render_template('profile.html', chat_history=chat_history)

@app.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    global community_messages, community_users
    if request.method == 'POST':
        msg = request.form.get('message')
        if msg is not None:
            msg = msg.strip()
            if msg:
                community_messages.append({
                    'user': current_user.name or current_user.email,
                    'text': msg,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                # Limit to last 100 messages
                community_messages = community_messages[-100:]
        return redirect(url_for('community'))
    # Add user to online list
    community_users.add(current_user.name or current_user.email)
    return render_template('community.html', messages=community_messages, users=list(community_users))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 