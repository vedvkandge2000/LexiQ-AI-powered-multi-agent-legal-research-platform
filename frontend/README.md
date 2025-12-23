# LexiQ Frontend

Modern React.js frontend for the LexiQ AI-powered legal research platform.

## 🎨 Design Features

- **Dark Legal Theme** - Professional navy blue with gold accents
- **Responsive Design** - Mobile-first approach, works on all devices
- **Modern Typography** - Playfair Display for headings, Source Sans Pro for body
- **Smooth Animations** - Framer Motion for delightful interactions
- **Accessibility** - WCAG compliant color contrast

## 🛠️ Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Zustand** - State management
- **Framer Motion** - Animations
- **Axios** - API client
- **React Markdown** - Markdown rendering

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Backend Connection

The frontend proxies API requests to `http://localhost:8000`. Make sure the FastAPI backend is running:

```bash
# From the project root
cd backend
python api.py
```

## 📁 Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── Layout.jsx        # Main app layout with sidebar
│   │   └── ProtectedRoute.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx     # Authentication
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx # Main case analysis
│   │   ├── ChatPage.jsx      # Conversational AI
│   │   └── AnalysisPage.jsx
│   ├── services/
│   │   └── api.js            # API client
│   ├── store/
│   │   ├── authStore.js      # Auth state
│   │   └── analysisStore.js  # Analysis state
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css             # Global styles
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🎯 Features

### Authentication
- Login/Register with form validation
- Session persistence
- Protected routes

### Case Analysis
- Text input for case details
- Configurable agent toggles
- Real-time loading states
- Security/PII protection notice

### Results Display
- Tabbed interface (Precedents, Statutes, News, Bench)
- Markdown rendering for AI analysis
- Expandable case cards
- PDF links to source documents

### Chat Interface
- Real-time conversation
- Message history
- Suggested follow-up questions
- Chat export functionality

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```js
colors: {
  primary: {...},  // Gold accent color
  navy: {...},     // Background blues
}
```

### Fonts

The app uses Google Fonts. To change fonts, edit `index.html`:

```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

And update `tailwind.config.js`:

```js
fontFamily: {
  'display': ['YourFont', 'serif'],
}
```

## 📦 Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

## 🔧 Environment Variables

Create a `.env` file for environment-specific config:

```
VITE_API_URL=http://localhost:8000
```

## 📱 Responsive Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

The sidebar collapses on mobile, and all components adapt to smaller screens.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

