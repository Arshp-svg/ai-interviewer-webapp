# 🚀 CelestiQ AI Interviewer - Streamlit Cloud Deployment Guide

## 📋 Prerequisites
- GitHub account
- Your Firebase project configuration
- Groq API key

## 🔧 Step 1: Prepare Your Repository

### 1.1 Update Your Secrets
Edit `.streamlit/secrets.toml` with your actual configuration:

```toml
# Groq API Configuration
GROQ_API_KEY = "your_actual_groq_api_key"

# Firebase Configuration
[FIREBASE_CONFIG]
apiKey = "your_actual_firebase_api_key"
authDomain = "your-project.firebaseapp.com"
projectId = "your-actual-project-id"
storageBucket = "your-project.appspot.com"
messagingSenderId = "your_actual_sender_id"
appId = "your_actual_app_id"
measurementId = "your_actual_measurement_id"
databaseURL = "https://your-project-default-rtdb.firebaseio.com/"
```

### 1.2 Commit and Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

## 🌐 Step 2: Deploy to Streamlit Cloud

### 2.1 Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 2.2 Configure Deployment
1. **Repository**: Select `ai-interviewer-webapp`
2. **Branch**: `main`
3. **Main file path**: `app.py`
4. **App URL**: Choose a custom name (e.g., `celestiq-ai-interviewer`)

### 2.3 Add Secrets in Streamlit Cloud
1. In the app settings, click "Secrets"
2. Copy the content from your local `.streamlit/secrets.toml`
3. Paste it into the Streamlit Cloud secrets editor
4. **Important**: Use your actual API keys and Firebase config

### 2.4 Deploy
Click "Deploy!" and wait for deployment to complete (2-5 minutes)

## 🎯 Step 3: Test Your Deployment

### Test Checklist:
- [ ] App loads without errors
- [ ] Login/Signup functionality works
- [ ] Firebase authentication is functional
- [ ] Dashboard displays correctly
- [ ] Interview features work properly
- [ ] Data persists to Firebase

## 🔍 Troubleshooting

### Common Issues:

#### 1. Import Errors
**Problem**: Module not found
**Solution**: Check `requirements.txt` has all dependencies

#### 2. Firebase Connection Issues
**Problem**: Authentication fails
**Solution**: Verify Firebase config in Streamlit Cloud secrets

#### 3. PyAudio Issues (Fixed)
**Problem**: PyAudio installation fails
**Solution**: ✅ Already removed from requirements.txt

## 🔄 Making Updates

1. Make changes to your code locally
2. Test locally: `streamlit run app.py`
3. Commit and push to GitHub
4. Streamlit Cloud will automatically redeploy

## 📞 Support Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Firebase Docs**: [firebase.google.com/docs](https://firebase.google.com/docs)

## 🔐 Security Notes

✅ **Secrets Protection**: `.streamlit/secrets.toml` is in `.gitignore`  
✅ **Environment Variables**: Properly configured for cloud  
✅ **No PyAudio**: Removed problematic dependency  

## 🎉 Success!

Your app will be available at:
**`https://your-app-name.streamlit.app`**

---

## 🆘 Need Help?

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all secrets are correctly configured
3. Ensure Firebase project settings are correct
4. Test locally first with `streamlit run app.py`