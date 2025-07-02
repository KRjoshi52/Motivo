# Motivo ✨

A beautiful, beginner-friendly Flask web app that helps users feel better using OpenAI's GPT-3.5. Share your mood and get personalized, uplifting messages to brighten your day!

## Features

- 🌟 **Beautiful Design**: Clean, calming interface with soft pastel colors
- 🤖 **AI-Powered Responses**: Get personalized, uplifting messages from GPT-3.5
- 📱 **Mobile Responsive**: Works perfectly on all devices
- ⚡ **Quick & Easy**: Simple one-click mood sharing
- 🧠 **The 5 Second Rule**: Built-in motivation technique by Mel Robbins
- 🔒 **Secure**: OpenAI API key stored safely in environment variables

## Screenshots

The app features:
- A welcoming headline: "You're weirdly amazing. Don't change."
- A text area for sharing your mood
- A beautiful "Spark Me ✨" button with hover effects
- AI-generated uplifting responses
- The 5 Second Rule section for motivation

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- An OpenAI API key

### Step 1: Clone or Download
Download this project to your computer.

### Step 2: Install Dependencies
Open your terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Your OpenAI API Key
1. Get your API key from [OpenAI's website](https://platform.openai.com/api-keys)
2. Create a file called `.env` in the project root
3. Add your API key to the file:

```
OPENAI_API_KEY=your_api_key_here
```

**Important**: Replace `your_api_key_here` with your actual OpenAI API key.

### Step 4: Run the App
In your terminal, run:

```bash
python main.py
```

### Step 5: Open in Browser
Open your web browser and go to: `http://localhost:5000`

## How to Use

1. **Share Your Mood**: Type how you're feeling in the text area
2. **Get Sparked**: Click the "Spark Me ✨" button
3. **Read Your Message**: Get a personalized, uplifting response
4. **Try the 5 Second Rule**: Use the technique to take action

## Project Structure

```
Motivo/
├── main.py              # Flask backend
├── templates/
│   └── index.html       # Frontend template
├── static/
│   └── style.css        # Beautiful styling
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .env                # Your API key (create this)
```

## Customization

### Colors
The app uses a calming color palette with:
- Primary: Lavender and light blue gradients
- Accent: Soft purples and greens
- Background: Gentle gradient from light blue to lavender

### Styling
All styles are in `static/style.css`. The design is fully responsive and includes:
- Smooth animations
- Hover effects
- Mobile optimization
- Accessibility features

## Troubleshooting

### Common Issues

**"Module not found" errors:**
- Make sure you've installed the requirements: `pip install -r requirements.txt`

**"OpenAI API key not found":**
- Check that your `.env` file exists and contains your API key
- Make sure the key is correct and has credits

**App won't start:**
- Ensure you're running the command from the project directory
- Check that Python 3.7+ is installed

### Getting Help
If you encounter any issues:
1. Check that all files are in the correct locations
2. Verify your OpenAI API key is valid
3. Make sure all dependencies are installed

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Bootstrap 5 + Custom CSS
- **AI**: OpenAI GPT-3.5-turbo
- **Environment**: python-dotenv

## Contributing

This is a beginner-friendly project! Feel free to:
- Add new features
- Improve the design
- Fix bugs
- Add more uplifting content

## License

This project is open source and available under the MIT License.

---

**Made with ❤️ for anyone who needs a little spark in their day!** 