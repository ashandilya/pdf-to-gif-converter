const config = {
    apiUrl: process.env.NODE_ENV === 'production' 
        ? 'https://your-app-name.vercel.app/api'  // Replace with your Vercel deployment URL
        : 'http://localhost:8000'
};

export default config; 