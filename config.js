const config = {
    apiUrl: process.env.NODE_ENV === 'production' 
        ? 'https://your-vercel-app-name.vercel.app'  // This will be updated after deployment
        : 'http://localhost:8000'
};

export default config; 