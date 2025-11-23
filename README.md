# Vertebrae - Girl's Frontline 2: Exilium Gacha Tracker

A simple, fan-made desktop application for tracking and analyzing your gacha pull history in **Girl's Frontline 2: Exilium**. Get detailed statistics, filter your pulls, and visualize your spending across all banners.

---

## 🚀 Features

### 📥 Smart Data Import
- **Secure API Integration**: Uses the same official API as the game client
- **Automatic Deduplication**: Never records the same pull twice
- **Multi-Server Support**: Works with all GF2 servers worldwide
- **Batch Processing**: Import thousands of pulls in minutes

### 📊 Advanced Statistics
- **Visual Analytics**: Interactive pie charts showing banner distribution (WIP)
- **Multi-Pull Detection**: Automatically identifies 10-pull multis
- **Time Range Analysis**: Track your pulling habits over time
- **Rarity Breakdown**: See your luck distribution across rarities

### 🔍 Powerful Filtering
- **Banner Filtering**: Filter by character, weapon, permanent, or event (placeholder) banners
- **Rarity Search**: Find all your 5-star pulls instantly
- **Text Search**: Search for specific characters or weapons by name
- **Real-time Filtering**: See results update as you type

### 💾 Data Management
- **Local Storage**: All data stays on your computer - no cloud storage
- **Configurable Limits**: Set your own import limits

---

## 🛠️ Installation

### 📦 Direct Download (Recommended)
1. Go to the [Releases page](https://github.com/your-username/vertebrae/releases)
2. Download the latest `Vertebrae_vX.X.X.exe` file
3. Run the executable - no installation required!

### 🐍 Python Source (Developers)
1. Download the source code of the language you choose
2. Run main.py with Python

```bash
python main.py
```

---

## 📖 Quick Start Guide

### Step 1: Get Your Authorization Token
1. **Download Fiddler Classic** from the official website
2. **Run Fiddler** and start capturing traffic
3. **Launch Girls Frontline 2** and go to any banner details page
4. **In Fiddler**, find the request starting with `https://gf2-gacha-record`
5. **Copy the Authorization header** value (right-click → Copy Value)

### Step 2: Import Your Data
1. **Open Vertebrae** and go to the Import tab
2. **Paste your token** (Deleting any text before the token) and enter the account email
3. **Select your server** from the dropdown menu
4. **Click "Start Import"** and watch your history load!

### Step 3: Explore Your Data
- **History Tab**: Browse and filter all your pulls
- **Statistics Tab**: View visual charts and detailed analytics (WIP)
- **Use Search**: Find specific characters or weapons instantly

---

## 🌐 Supported Servers

| Server | Region | Status |
|--------|--------|---------|
| Darkwinter | US/EU | ✅ Fully Supported |
| Haoplay Asia | Asia | ✅ Fully Supported |
| Haoplay Japan | Japan | ✅ Fully Supported |
| Haoplay Korea | Korea | ✅ Fully Supported |
| Haoplay International | Global | ✅ Fully Supported |
| CN Server | China | ✅ Fully Supported |

---

## ⚙️ Configuration

### API Settings
- **Page Limit**: Control how many pages to import
- **Request Timeout**: Adjust timeout for slow connections
- **Max Retries**: Set retry attempts for failed requests

### Application Settings
- **Language**: English and Spanish support (WIP - For future versions, it will be only one exe, no multiple languages)
- **Theme**: Light/Dark/System themes (placeholder, will be implemented)

---

## 🔒 Privacy & Security

### Your Data is Yours
- ✅ **100% Local Storage**: No data leaves your computer
- ✅ **No Account Required**: Email is only used for API calls
- ✅ **No Personal Data**: It only stores pull history, no personal info
- ✅ **Open Source**: You can verify the code yourself if you want

### Security Features
- **SSL Verification**: Secure API communication
- **Token Encryption**: Local token storage protection
- **No Persistent Login**: Tokens aren't saved between sessions

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| "Invalid token" error | Check the text you pasted. It cannot have anything else apart from the token itself, no spaces or anything |
| "No data found" | Check server selection and ensure you've pulled recently |
| Import very slow | Reduce page limit in settings or check internet connection |
| App won't start | Install [Visual C++ Redistributable](https://aka.ms/vs/16/release/vc_redist.x64.exe) if you don't have it |

### Roadmap:

1 - Make a better interface to replace this ugly one it has right now

2 - Implement a pity counter, with 50/50 analyzer (to check if your next 5 star is 50/50 or guaranteed)

3 - Combine both EN and ES versions into the same app, and add more languages if required/requested

4 - Add dark and gray themes, selectable from the menu

5 - Add multiple account support

6 - Add images for EACH item, doll and weapon, and make the "History" tab fancier

7 - Add a "Delete Records" button, to make it easier to reset the first state of the app. Meanwhile you can just delete the "backup.json" file to do so. Note that this will erase ALL of the pulls data the app was showing


### Known bugs and fixes:


1 - The pie graphic in the statistic tab doesn't work properly. I'll check it when got time

2 - The "Event" filter doesn't filter sh**. This is "intended" to a certain extreme, as it is the placeholder for the "Skin" banner

3 - The "History" tab works poorly, concretely the filters does. Will optimize it later

4 - The language and theme selector doesn't do anything, or if they do, is badly implemented. Will finish this also when I merge both versions

5 - Right now, date is shown in the yyyy/mm/dd format. I want to add an option to let the user choose which format it should use. I myself prefer the dd/mm/yyyy

6 - The token has to be writen perfectly into the token tab. Buuuh... I want to make it intelligent, so if you paste a bunch of unrelated text, it finds automatically your token

7 - The dictionaries (dolls/weapons/item names and localizations) are updated enough for now, but I'll need a better way to update them



### Getting Help
1. Check this README and the in-app help guide
2. Search existing [GitHub Issues]
3. Create a new issue with detailed information

---

## 🛡️ Legal Disclaimer

**Vertebrae** is a **fan-made, unofficial tool** and is not affiliated with, sponsored by, or endorsed by:
- **Sunborn Network Technology Co.**
- **MICA Team** 
- **Girl's Frontline 2: Exilium**

This project is developed by fans for educational and personal use purposes. All game assets and data belong to their respective owners.

### User Responsibility
By using this software, you acknowledge that:
- You understand the risks of using third-party tools
- The developer is not responsible for any account penalties (Though there shouldn't be any problem)
- You comply with the game's Terms of Service
- You use this tool at your own discretion

---

## 🤝 Contributing

I welcome contributions! Here's how you can help:

### 🐛 Report Bugs
- Use the GitHub Issues template
- Include detailed steps to reproduce

### 💡 Suggest Features
- Check existing feature requests first
- Explain the use case and benefits
- Consider if it aligns with project goals

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### 🌍 Translations
Help us translate Vertebrae into more languages!

---

## 📄 License

This project is licensed under the **GNU GPL3 License v3.0** - see the [LICENSE](LICENSE) file for details.

---

**Happy Pulling!** 🎮✨

*If you find Vertebrae useful, consider giving it a ⭐ on GitHub!*
